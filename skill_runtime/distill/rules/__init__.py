"""Rule registry for trajectory-to-skill distillation."""

from skill_runtime.distill.rules import (
    batch_rename_case,
    batch_rename_extension,
    batch_rename_replace,
    batch_rename,
    batch_rename_suffix,
    csv_to_json,
    directory_csv_to_json,
    directory_json_transform,
    directory_json_to_csv,
    directory_copy,
    directory_move,
    directory_text_transform,
    directory_text_replace,
    json_to_csv,
    single_json_transform,
    single_file_copy,
    single_file_move,
    single_file_transform,
    text_merge,
    text_replace,
)
from skill_runtime.distill.rules.registry import get_rule_priority


RULES = [
    directory_text_replace,
    directory_copy,
    directory_move,
    csv_to_json,
    directory_csv_to_json,
    directory_json_transform,
    directory_json_to_csv,
    directory_text_transform,
    json_to_csv,
    single_json_transform,
    text_merge,
    text_replace,
    single_file_copy,
    single_file_move,
    single_file_transform,
    batch_rename_case,
    batch_rename_extension,
    batch_rename_replace,
    batch_rename_suffix,
    batch_rename,
]

RULES.sort(key=get_rule_priority, reverse=True)
