"""Rule registry for trajectory-to-skill distillation."""

from skill_runtime.distill.rules import (
    batch_rename,
    csv_to_json,
    directory_copy,
    directory_move,
    directory_text_replace,
    json_to_csv,
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
    json_to_csv,
    text_merge,
    text_replace,
    single_file_transform,
    batch_rename,
]

RULES.sort(key=get_rule_priority, reverse=True)
