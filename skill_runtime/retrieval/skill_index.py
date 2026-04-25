import json
import re
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

from skill_runtime.api.models import SkillMetadata
from skill_runtime.mcp.host_operations import search_result_payload


class SkillIndexError(ValueError):
    pass


class SkillIndex:
    NON_PRODUCTION_PATTERNS = (
        "test",
        "demo",
        "readme",
        "bridge",
        "provenance",
        "cli_",
        "mcp_",
        "service_",
        "codex_",
        "generated",
    )

    def __init__(self, index_path: str | Path) -> None:
        self.index_path = Path(index_path)
        self.index_path.parent.mkdir(parents=True, exist_ok=True)

    def load_all(self) -> list[SkillMetadata]:
        if not self.index_path.exists():
            return []
        payload = json.loads(self.index_path.read_text(encoding="utf-8-sig"))
        return [self._from_dict(item) for item in payload.get("skills", [])]

    def save_all(self, skills: list[SkillMetadata]) -> Path:
        self.index_path.write_text(
            json.dumps({"skills": [asdict(skill) for skill in skills]}, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return self.index_path

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
            self.save_all(skills)

            metadata_path = Path(metadata.file_path).with_name(f"{metadata.skill_name}.metadata.json")
            if metadata_path.exists():
                metadata_path.write_text(
                    json.dumps(asdict(metadata), ensure_ascii=False, indent=2),
                    encoding="utf-8",
                )

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

    def search(self, query: str, top_k: int = 5) -> list[dict]:
        if not query.strip():
            raise SkillIndexError("query cannot be empty")

        query_terms = self._tokenize(query)
        results: list[dict] = []
        for skill in self.load_all():
            if skill.status != "active":
                continue
            score, matched_terms, library_tier, score_breakdown = self._score_skill(skill, query_terms)
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
        self, skill: SkillMetadata, query_terms: set[str]
    ) -> tuple[float, list[str], str, dict[str, float]]:
        name_terms = self._tokenize(skill.skill_name)
        summary_terms = self._tokenize(skill.summary)
        docstring_terms = self._tokenize(skill.docstring)
        tag_terms = {tag.lower() for tag in skill.tags}
        input_terms = {key.lower() for key in skill.input_schema.keys()}
        output_terms = {key.lower() for key in skill.output_schema.keys()}
        rule_terms = self._tokenize(" ".join(filter(None, [skill.rule_name or "", skill.rule_reason or ""])))

        corpus_terms = name_terms | summary_terms | docstring_terms | tag_terms | input_terms | output_terms | rule_terms
        matched_terms = sorted(query_terms & corpus_terms)
        if not matched_terms:
            return 0.0, [], "hidden", {}

        lexical_score = len(matched_terms) / max(len(query_terms), 1)
        summary_overlap = len(query_terms & summary_terms) / max(len(query_terms), 1)
        schema_overlap = len(query_terms & (input_terms | output_terms)) / max(len(query_terms), 1)
        tags_overlap = len(query_terms & tag_terms) / max(len(query_terms), 1)
        provenance_overlap = len(query_terms & rule_terms) / max(len(query_terms), 1)

        base_score = lexical_score
        score_breakdown = {
            "lexical": round(lexical_score, 4),
            "summary": round(summary_overlap * 0.2, 4),
            "schema": round(schema_overlap * 0.15, 4),
            "tags": round(tags_overlap * 0.1, 4),
            "provenance": round(provenance_overlap * 0.1, 4),
            "audit": 0.0,
            "usage": 0.0,
            "status": 0.0,
            "library_penalty": 0.0,
        }
        base_score += summary_overlap * 0.2
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
        return max(base_score, 0.0), matched_terms, library_tier, score_breakdown

    def _why_matched(self, matched_terms: list[str], score_breakdown: dict[str, float]) -> str:
        if not matched_terms:
            return "No strong match terms found."
        components = [
            name
            for name in ("summary", "schema", "tags", "provenance", "usage", "audit")
            if score_breakdown.get(name, 0.0) > 0
        ]
        suffix = f" Boosted by: {', '.join(components)}." if components else ""
        return f"Matched on keywords: {', '.join(matched_terms)}.{suffix}"

    def _tokenize(self, text: str) -> set[str]:
        return {
            token.lower()
            for token in re.findall(r"[A-Za-z0-9_]+", text)
            if len(token) >= 2
        }

    def _library_tier(self, skill: SkillMetadata) -> str:
        name = skill.skill_name.lower()
        if any(pattern in name for pattern in self.NON_PRODUCTION_PATTERNS):
            return "experimental"
        return "stable"

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
            tags=payload.get("tags", []),
        )
