from collections import Counter, defaultdict
from pathlib import Path
import re

from skill_runtime.api.models import SkillMetadata
from skill_runtime.library_tiers import classify_skill_name
from skill_runtime.mcp.host_operations import (
    archive_duplicate_candidates_action,
    governance_report_payload,
    review_archive_volume_action,
    review_fixture_noise_action,
)
from skill_runtime.retrieval.skill_index import SkillIndex


class LibraryReport:
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
        active_skills = [skill for skill in skills if skill.status == "active"]
        duplicates, hidden_fixture_only_clusters = self._duplicate_candidates(skills)
        library_tier_counts = self._library_tier_counts(active_skills)
        fixture_skill_names = sorted(
            skill.skill_name
            for skill in active_skills
            if classify_skill_name(skill.skill_name) == "fixture"
        )
        recommended_actions = self._recommended_actions(
            duplicates,
            status_counts,
            library_tier_counts=library_tier_counts,
            hidden_fixture_only_clusters=hidden_fixture_only_clusters,
            fixture_skill_names=fixture_skill_names,
        )
        return governance_report_payload(
            dict(status_counts),
            duplicates,
            recommended_actions,
            staging_count=self._count_files(self.root / "skill_store" / "staging"),
            archive_count=self._count_files(self.root / "skill_store" / "archive"),
            active_count=status_counts.get("active", 0),
            library_tier_counts=library_tier_counts,
            library_tier_summary={
                "production_ready_count": library_tier_counts["stable"],
                "experimental_count": library_tier_counts["experimental"],
                "fixture_count": library_tier_counts["fixture"],
                "fixture_only_duplicate_clusters_hidden": hidden_fixture_only_clusters,
            },
        )

    def _duplicate_candidates(self, skills: list[SkillMetadata]) -> tuple[list[dict], int]:
        groups: dict[tuple, list[str]] = defaultdict(list)
        for skill in skills:
            key = (
                skill.rule_name or "",
                self._family_signature(skill),
            )
            groups[key].append(skill.skill_name)

        duplicates: list[dict] = []
        hidden_fixture_only_clusters = 0
        for (rule_name, family_signature), names in groups.items():
            if len(names) < 2:
                continue
            group_skills = [skill for skill in skills if skill.skill_name in names]
            group_tiers = {classify_skill_name(skill.skill_name) for skill in group_skills}
            if group_tiers == {"fixture"}:
                hidden_fixture_only_clusters += 1
                continue
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
        return duplicates, hidden_fixture_only_clusters

    def _count_files(self, directory: Path) -> int:
        if not directory.exists():
            return 0
        return len(list(directory.glob("*.py")))

    def _library_tier_counts(self, skills: list[SkillMetadata]) -> dict[str, int]:
        counts = Counter(classify_skill_name(skill.skill_name) for skill in skills)
        return {
            "stable": counts.get("stable", 0),
            "experimental": counts.get("experimental", 0),
            "fixture": counts.get("fixture", 0),
        }

    def _governance_rank(self, skill: SkillMetadata) -> tuple[int, int, int, int]:
        library_tier = {
            "fixture": 0,
            "experimental": 1,
            "stable": 2,
        }[classify_skill_name(skill.skill_name)]
        audit_score = skill.audit_score or 0
        return (
            library_tier,
            skill.usage_count,
            audit_score,
            -len(skill.skill_name),
        )

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

    def _recommended_actions(
        self,
        duplicates: list[dict],
        status_counts: Counter,
        *,
        library_tier_counts: dict[str, int],
        hidden_fixture_only_clusters: int,
        fixture_skill_names: list[str],
    ) -> list[dict]:
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

        fixture_count = library_tier_counts["fixture"]
        stable_count = library_tier_counts["stable"]
        if hidden_fixture_only_clusters > 0 or (fixture_count > 0 and fixture_count >= stable_count):
            actions.append(
                review_fixture_noise_action(
                    skill_names=fixture_skill_names,
                    fixture_count=fixture_count,
                    hidden_fixture_only_duplicate_clusters=hidden_fixture_only_clusters,
                )
            )

        return actions
