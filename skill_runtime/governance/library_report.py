from collections import Counter, defaultdict
from pathlib import Path
import re

from skill_runtime.api.models import SkillMetadata
from skill_runtime.mcp.host_operations import (
    action_host_operations,
    archive_duplicate_candidates_action,
    review_archive_volume_action,
)
from skill_runtime.retrieval.skill_index import SkillIndex


class LibraryReport:
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
    FAMILY_STOPWORDS = {
        "all",
        "and",
        "another",
        "across",
        "candidate",
        "directory",
        "file",
        "files",
        "from",
        "input",
        "input_dir",
        "input_path",
        "into",
        "matching",
        "one",
        "output",
        "output_dir",
        "output_path",
        "path",
        "pattern",
        "text",
        "the",
        "them",
        "value",
        "with",
        "write",
        "read",
    }

    def __init__(self, root: str | Path, index: SkillIndex) -> None:
        self.root = Path(root)
        self.index = index

    def build(self) -> dict:
        skills = self.index.load_all()
        status_counts = Counter(skill.status for skill in skills)
        duplicates = self._duplicate_candidates(skills)
        recommended_actions = self._recommended_actions(duplicates, status_counts)
        return {
            "status_counts": dict(status_counts),
            "duplicate_candidates": duplicates,
            "recommended_actions": recommended_actions,
            "available_host_operations": self._available_host_operations(recommended_actions),
            "staging_count": self._count_files(self.root / "skill_store" / "staging"),
            "archive_count": self._count_files(self.root / "skill_store" / "archive"),
            "active_count": status_counts.get("active", 0),
        }

    def _duplicate_candidates(self, skills: list[SkillMetadata]) -> list[dict]:
        groups: dict[tuple, list[str]] = defaultdict(list)
        for skill in skills:
            key = (
                skill.rule_name or "",
                self._family_signature(skill),
            )
            groups[key].append(skill.skill_name)

        duplicates: list[dict] = []
        for (rule_name, family_signature), names in groups.items():
            if len(names) < 2:
                continue
            group_skills = [skill for skill in skills if skill.skill_name in names]
            canonical_summary = max(
                (skill.summary.strip().lower() for skill in group_skills),
                key=len,
            )
            input_keys = sorted(
                {
                    key
                    for skill in group_skills
                    for key in skill.input_schema.keys()
                }
            )
            ranked_group = sorted(group_skills, key=self._governance_rank, reverse=True)
            duplicates.append(
                {
                    "rule_name": rule_name or None,
                    "summary": canonical_summary,
                    "family_signature": list(family_signature),
                    "input_keys": list(input_keys),
                    "skill_names": sorted(names),
                    "count": len(names),
                    "canonical_skill": ranked_group[0].skill_name,
                    "archive_candidates": [skill.skill_name for skill in ranked_group[1:]],
                }
            )

        duplicates.sort(key=lambda item: item["count"], reverse=True)
        return duplicates

    def _count_files(self, directory: Path) -> int:
        if not directory.exists():
            return 0
        return len(list(directory.glob("*.py")))

    def _governance_rank(self, skill: SkillMetadata) -> tuple[int, int, int, int]:
        library_tier = 0 if self._is_non_production(skill.skill_name) else 1
        audit_score = skill.audit_score or 0
        return (
            library_tier,
            skill.usage_count,
            audit_score,
            -len(skill.skill_name),
        )

    def _is_non_production(self, skill_name: str) -> bool:
        lowered = skill_name.lower()
        return any(pattern in lowered for pattern in self.NON_PRODUCTION_PATTERNS)

    def _family_signature(self, skill: SkillMetadata) -> tuple[str, ...]:
        raw_tokens = self._tokenize(" ".join([skill.summary, " ".join(skill.tags)]))
        filtered = sorted(
            token
            for token in raw_tokens
            if token not in self.FAMILY_STOPWORDS and not token.endswith("_dir") and not token.endswith("_path")
        )
        if not filtered:
            filtered = sorted(token for token in self._tokenize(skill.summary) if token not in self.FAMILY_STOPWORDS)
        return tuple(filtered[:6])

    def _tokenize(self, text: str) -> set[str]:
        return {
            token.lower()
            for token in re.findall(r"[A-Za-z0-9_]+", text)
            if len(token) >= 3
        }

    def _recommended_actions(self, duplicates: list[dict], status_counts: Counter) -> list[dict]:
        actions: list[dict] = []
        for cluster in duplicates:
            if not cluster["archive_candidates"]:
                continue
            actions.append(
                archive_duplicate_candidates_action(
                    cluster["archive_candidates"],
                    canonical_skill=cluster["canonical_skill"],
                    cluster_count=cluster["count"],
                    rule_name=cluster["rule_name"],
                )
            )

        if status_counts.get("archived", 0) > status_counts.get("active", 0):
            actions.append(review_archive_volume_action())

        return actions

    def _available_host_operations(self, actions: list[dict]) -> list[dict]:
        return action_host_operations(actions)
