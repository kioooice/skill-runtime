import json
import re
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

from skill_runtime.api.models import SkillMetadata
from skill_runtime.library_tiers import classify_skill_name
from skill_runtime.mcp.host_operations import search_result_payload

STOPWORDS = {
    "a",
    "an",
    "and",
    "as",
    "by",
    "for",
    "from",
    "in",
    "into",
    "of",
    "on",
    "or",
    "the",
    "to",
    "with",
}


class SkillIndexError(ValueError):
    pass


class SkillIndex:
    def __init__(self, index_path: str | Path) -> None:
        self.index_path = Path(index_path)
        self.index_path.parent.mkdir(parents=True, exist_ok=True)
        self.usage_state_path = self.index_path.parent.parent / ".skill_runtime" / "usage.json"

    def load_all(self) -> list[SkillMetadata]:
        if not self.index_path.exists():
            return []
        payload = json.loads(self.index_path.read_text(encoding="utf-8-sig"))
        skills = [self._from_dict(item) for item in payload.get("skills", [])]
        usage_state = self._load_usage_state()
        if not usage_state:
            return skills

        for metadata in skills:
            usage_payload = usage_state.get(metadata.skill_name)
            if usage_payload is None:
                continue
            self._apply_usage_state(metadata, usage_payload)
        return skills

    def save_all(self, skills: list[SkillMetadata]) -> Path:
        self.index_path.write_text(
            json.dumps({"skills": [asdict(skill) for skill in skills]}, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return self.index_path

    def save_merged(self, skills: list[SkillMetadata]) -> Path:
        current_skills = {skill.skill_name: skill for skill in self.load_all()}
        for metadata in skills:
            current_skills[metadata.skill_name] = metadata
        return self.save_all(list(current_skills.values()))

    def upsert(self, metadata: SkillMetadata) -> Path:
        skills = self.load_all()
        for index, existing in enumerate(skills):
            if existing.skill_name == metadata.skill_name:
                skills[index] = metadata
                break
        else:
            skills.append(metadata)
        return self.save_all(skills)

    def remove(self, skill_name: str) -> Path:
        skills = [skill for skill in self.load_all() if skill.skill_name != skill_name]
        self._remove_usage_state(skill_name)
        return self.save_all(skills)

    def get(self, skill_name: str) -> SkillMetadata | None:
        for skill in self.load_all():
            if skill.skill_name == skill_name:
                return skill
        return None

    def record_usage(self, skill_name: str) -> SkillMetadata:
        skills = self.load_all()
        for index, metadata in enumerate(skills):
            if metadata.skill_name != skill_name:
                continue

            metadata.usage_count += 1
            metadata.last_used_at = datetime.now(timezone.utc).isoformat()
            skills[index] = metadata
            self._save_usage_state(metadata)
            return metadata

        raise SkillIndexError(f"skill not found for usage update: {skill_name}")

    def rebuild_from_directory(self, active_dir: str | Path) -> Path:
        active_path = Path(active_dir)
        if not active_path.exists():
            raise FileNotFoundError(f"active skill directory not found: {active_path}")
        skills: list[SkillMetadata] = []
        for metadata_path in sorted(active_path.glob("*.metadata.json")):
            payload = json.loads(metadata_path.read_text(encoding="utf-8-sig"))
            skills.append(self._from_dict(payload))
        return self.save_all(skills)

    def _load_usage_state(self) -> dict[str, dict]:
        if not self.usage_state_path.exists():
            return {}
        payload = json.loads(self.usage_state_path.read_text(encoding="utf-8-sig"))
        skills = payload.get("skills", {})
        if not isinstance(skills, dict):
            raise SkillIndexError("usage state must contain a skills object")
        return {str(key): value for key, value in skills.items() if isinstance(value, dict)}

    def _save_usage_state(self, metadata: SkillMetadata) -> Path:
        state = self._load_usage_state()
        state[metadata.skill_name] = {
            "usage_count": metadata.usage_count,
            "last_used_at": metadata.last_used_at,
        }
        self.usage_state_path.parent.mkdir(parents=True, exist_ok=True)
        self.usage_state_path.write_text(
            json.dumps({"skills": state}, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return self.usage_state_path

    def _remove_usage_state(self, skill_name: str) -> None:
        if not self.usage_state_path.exists():
            return
        state = self._load_usage_state()
        if skill_name not in state:
            return
        state.pop(skill_name, None)
        if not state:
            self.usage_state_path.unlink(missing_ok=True)
            return
        self.usage_state_path.write_text(
            json.dumps({"skills": state}, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def _apply_usage_state(self, metadata: SkillMetadata, usage_payload: dict) -> None:
        usage_count = usage_payload.get("usage_count")
        if isinstance(usage_count, int):
            metadata.usage_count = max(metadata.usage_count, usage_count)

        last_used_at = usage_payload.get("last_used_at")
        if not isinstance(last_used_at, str):
            return
        if metadata.last_used_at is None:
            metadata.last_used_at = last_used_at
            return
        try:
            metadata_last_used = datetime.fromisoformat(metadata.last_used_at)
            overlay_last_used = datetime.fromisoformat(last_used_at)
        except ValueError:
            metadata.last_used_at = last_used_at
            return
        if overlay_last_used >= metadata_last_used:
            metadata.last_used_at = last_used_at

    def search(self, query: str, top_k: int = 5) -> list[dict]:
        if not query.strip():
            raise SkillIndexError("query cannot be empty")

        normalized_query = self._normalize_search_text(query)
        query_terms = self._tokenize(query)
        results: list[dict] = []
        for skill in self.load_all():
            if skill.status != "active":
                continue
            score, matched_terms, library_tier, score_breakdown = self._score_skill(
                skill,
                query_terms,
                normalized_query,
            )
            if score <= 0:
                continue
            results.append(
                search_result_payload(
                    skill.skill_name,
                    skill.summary,
                    score,
                    self._why_matched(matched_terms, score_breakdown),
                    skill.input_schema,
                    rule_name=skill.rule_name,
                    rule_priority=skill.rule_priority,
                    rule_reason=skill.rule_reason,
                    library_tier=library_tier,
                    score_breakdown=score_breakdown,
                )
            )
        results.sort(key=lambda item: item["score"], reverse=True)
        return results[:top_k]

    def _score_skill(
        self,
        skill: SkillMetadata,
        query_terms: set[str],
        normalized_query: str,
    ) -> tuple[float, list[str], str, dict[str, float]]:
        name_terms = self._tokenize(skill.skill_name)
        summary_terms = self._tokenize(skill.summary)
        docstring_terms = self._tokenize(skill.docstring)
        alias_terms = self._tokenize(" ".join(skill.search_aliases))
        tag_terms = {tag.lower() for tag in skill.tags}
        input_terms = {key.lower() for key in skill.input_schema.keys()}
        output_terms = {key.lower() for key in skill.output_schema.keys()}
        rule_terms = self._tokenize(" ".join(filter(None, [skill.rule_name or "", skill.rule_reason or ""])))
        alias_match_terms, alias_string_overlap = self._alias_matches(skill.search_aliases, normalized_query)

        corpus_terms = (
            name_terms
            | summary_terms
            | docstring_terms
            | alias_terms
            | tag_terms
            | input_terms
            | output_terms
            | rule_terms
        )
        matched_terms = sorted((query_terms & corpus_terms) | alias_match_terms)
        if not matched_terms and alias_string_overlap <= 0:
            return 0.0, [], "hidden", {}

        lexical_score = len(matched_terms) / max(len(query_terms), 1)
        summary_overlap = len(query_terms & summary_terms) / max(len(query_terms), 1)
        alias_overlap = max(
            len(query_terms & alias_terms) / max(len(query_terms), 1),
            alias_string_overlap,
        )
        schema_overlap = len(query_terms & (input_terms | output_terms)) / max(len(query_terms), 1)
        tags_overlap = len(query_terms & tag_terms) / max(len(query_terms), 1)
        provenance_overlap = len(query_terms & rule_terms) / max(len(query_terms), 1)

        base_score = lexical_score
        score_breakdown = {
            "lexical": round(lexical_score, 4),
            "summary": round(summary_overlap * 0.2, 4),
            "aliases": round(alias_overlap * 0.2, 4),
            "schema": round(schema_overlap * 0.15, 4),
            "tags": round(tags_overlap * 0.1, 4),
            "provenance": round(provenance_overlap * 0.1, 4),
            "audit": 0.0,
            "usage": 0.0,
            "status": 0.0,
            "library_penalty": 0.0,
        }
        base_score += summary_overlap * 0.2
        base_score += alias_overlap * 0.2
        base_score += schema_overlap * 0.15
        base_score += tags_overlap * 0.1
        base_score += provenance_overlap * 0.1
        if skill.status == "active":
            base_score += 0.1
            score_breakdown["status"] = 0.1
        if skill.audit_score:
            audit_boost = min(skill.audit_score / 1000.0, 0.1)
            base_score += audit_boost
            score_breakdown["audit"] = round(audit_boost, 4)
        if skill.usage_count:
            usage_boost = min(skill.usage_count * 0.02, 0.12)
            base_score += usage_boost
            score_breakdown["usage"] = round(usage_boost, 4)
        library_tier = self._library_tier(skill)
        if library_tier == "experimental":
            base_score -= 0.35
            score_breakdown["library_penalty"] = -0.35
        elif library_tier == "fixture":
            base_score -= 0.6
            score_breakdown["library_penalty"] = -0.6
        return max(base_score, 0.0), matched_terms, library_tier, score_breakdown

    def _why_matched(self, matched_terms: list[str], score_breakdown: dict[str, float]) -> str:
        if not matched_terms:
            return "No strong match terms found."
        components = [
            name
            for name in ("summary", "aliases", "schema", "tags", "provenance", "usage", "audit")
            if score_breakdown.get(name, 0.0) > 0
        ]
        suffix = f" Boosted by: {', '.join(components)}." if components else ""
        return f"Matched on keywords: {', '.join(matched_terms)}.{suffix}"

    def _alias_matches(self, aliases: list[str], normalized_query: str) -> tuple[set[str], float]:
        matched_aliases: set[str] = set()
        best_overlap = 0.0
        for alias in aliases:
            if not isinstance(alias, str):
                continue
            normalized_alias = self._normalize_search_text(alias)
            if not normalized_alias:
                continue
            if normalized_alias == normalized_query:
                matched_aliases.add(alias)
                best_overlap = max(best_overlap, 1.0)
                continue
            if normalized_alias in normalized_query or normalized_query in normalized_alias:
                matched_aliases.add(alias)
                best_overlap = max(best_overlap, 0.5)
        return matched_aliases, best_overlap

    def _normalize_search_text(self, text: str) -> str:
        return "".join(text.lower().split())

    def _tokenize(self, text: str) -> set[str]:
        return {
            token.lower()
            for token in re.findall(r"[A-Za-z0-9_]+", text)
            if len(token) >= 2 and token.lower() not in STOPWORDS
        }

    def _library_tier(self, skill: SkillMetadata) -> str:
        return classify_skill_name(skill.skill_name)

    def _from_dict(self, payload: dict) -> SkillMetadata:
        required_fields = {
            "skill_name",
            "file_path",
            "summary",
            "docstring",
            "input_schema",
            "output_schema",
            "source_trajectory_ids",
            "created_at",
            "last_used_at",
            "usage_count",
            "status",
            "audit_score",
        }
        missing = sorted(required_fields - set(payload.keys()))
        if missing:
            raise SkillIndexError(f"metadata missing fields: {missing}")

        return SkillMetadata(
            skill_name=payload["skill_name"],
            file_path=payload["file_path"],
            summary=payload["summary"],
            docstring=payload["docstring"],
            input_schema=payload["input_schema"],
            output_schema=payload["output_schema"],
            source_trajectory_ids=payload["source_trajectory_ids"],
            created_at=payload["created_at"],
            last_used_at=payload["last_used_at"],
            usage_count=payload["usage_count"],
            status=payload["status"],
            audit_score=payload["audit_score"],
            rule_name=payload.get("rule_name"),
            rule_priority=payload.get("rule_priority"),
            rule_reason=payload.get("rule_reason"),
            search_aliases=payload.get("search_aliases", []),
            tags=payload.get("tags", []),
            scope_policy=payload.get("scope_policy"),
        )
