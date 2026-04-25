import json
from pathlib import Path

from skill_runtime.api.models import SkillMetadata
from skill_runtime.retrieval.skill_index import SkillIndex


class ProvenanceBackfill:
    def __init__(self, active_dir: str | Path, index: SkillIndex) -> None:
        self.active_dir = Path(active_dir)
        self.index = index

    def run(self) -> list[dict[str, str | int]]:
        updated: list[dict[str, str | int]] = []
        skills = self.index.load_all()
        changed = False

        for metadata in skills:
            if metadata.rule_name:
                continue

            inferred = self._infer_from_source(metadata)
            if not inferred:
                continue

            rule_name, rule_priority, rule_reason = inferred
            metadata.rule_name = rule_name
            metadata.rule_priority = rule_priority
            metadata.rule_reason = rule_reason
            self._write_metadata_file(metadata)

            updated.append(
                {
                    "skill_name": metadata.skill_name,
                    "rule_name": rule_name,
                    "rule_priority": rule_priority,
                }
            )
            changed = True

        if changed:
            self.index.save_all(skills)

        return updated

    def _write_metadata_file(self, metadata: SkillMetadata) -> None:
        metadata_path = Path(metadata.file_path).with_name(f"{metadata.skill_name}.metadata.json")
        if metadata_path.exists():
            metadata_path.write_text(
                json.dumps(metadata.__dict__, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )

    def _infer_from_source(self, metadata: SkillMetadata) -> tuple[str, int, str] | None:
        source_path = Path(metadata.file_path)
        if not source_path.exists():
            return None

        source = source_path.read_text(encoding="utf-8")
        summary = metadata.summary.lower()
        tags = {tag.lower() for tag in metadata.tags}
        keys = set(metadata.input_schema.keys())

        if "tools.copy_file(" in source:
            if "tools.list_files(" not in source:
                return (
                    "single_file_copy",
                    65,
                    "Backfilled single_file_copy because the skill source copies one file from an input path to an output path.",
                )
            return (
                "directory_copy",
                85,
                "Backfilled directory_copy because the skill source copies files from an input directory to an output directory.",
            )
        if "tools.move_file(" in source:
            if "tools.list_files(" not in source:
                return (
                    "single_file_move",
                    65,
                    "Backfilled single_file_move because the skill source moves one file from an input path to an output path.",
                )
            return (
                "directory_move",
                85,
                "Backfilled directory_move because the skill source moves files from an input directory to an output directory.",
            )
        if "tools.rename_path(" in source and "prefix" not in source:
            return (
                "single_file_move",
                65,
                "Backfilled single_file_move because the skill source renames or moves one file from an input path to an output path.",
            )
        if "tools.rename_path(" in source and "prefix" in source:
            return (
                "batch_rename",
                80,
                "Backfilled batch_rename because the skill source renames files using a prefix.",
            )
        if "csv.DictReader" in source and "tools.write_json(" in source:
            return (
                "csv_to_json",
                75,
                "Backfilled csv_to_json because the skill source parses CSV rows and writes JSON output.",
            )
        if "csv.DictWriter" in source and "tools.read_json(" in source:
            return (
                "json_to_csv",
                75,
                "Backfilled json_to_csv because the skill source reads JSON rows and writes CSV output.",
            )
        if "tools.read_json(" in source and "tools.write_json(" in source:
            return (
                "single_json_transform",
                30,
                "Backfilled single_json_transform because the skill source reads one JSON file and writes one JSON file.",
            )
        if "tools.list_files(" in source and "old_text" in source and "new_text" in source:
            return (
                "directory_text_replace",
                100,
                "Backfilled directory_text_replace because the skill source iterates directory files and replaces text across them.",
            )
        if ".replace(old_text, new_text)" in source:
            return (
                "text_replace",
                90,
                "Backfilled text_replace because the skill source replaces one string with another in a text file.",
            )
        if "tools.list_files(" in source and "tools.read_text(" in source and "tools.write_text(" in source:
            return (
                "text_merge",
                70,
                "Backfilled text_merge because the skill source lists files, reads text, and writes merged output.",
            )
        if "tools.read_text(" in source and "tools.write_text(" in source:
            return (
                "single_file_transform",
                20,
                "Backfilled single_file_transform because the skill source reads one file and writes one file.",
            )

        if "merge" in summary and "txt" in summary and {"input_dir", "output_path"}.issubset(keys):
            return (
                "text_merge",
                70,
                "Backfilled text_merge from legacy metadata because the summary and inputs describe merging txt files from a directory into an output path.",
            )
        if "merge" in tags and "txt" in tags and {"input_dir", "output_path"}.issubset(keys):
            return (
                "text_merge",
                70,
                "Backfilled text_merge from legacy metadata because the tags and inputs indicate directory txt merging.",
            )

        return None
