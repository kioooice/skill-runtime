from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

from skill_runtime.distill.skill_generator import SkillGenerator
from skill_runtime.mcp.host_operations import (
    collect_operations,
    distill_and_promote_recommendation,
    distill_coverage_report_recommendation,
    distill_coverage_report_operation,
    distill_and_promote_operation,
    distill_trajectory_operation,
    distill_trajectory_recommendation,
    no_recommendation,
    source_ref_observed_task,
    source_ref_distill_coverage_report_refresh,
    source_ref_distill_coverage_report_view,
    source_ref_trajectory,
    with_recommendation,
)
from skill_runtime.memory.trajectory_capture import TrajectoryCapture, TrajectoryCaptureError
from skill_runtime.memory.trajectory_store import TrajectoryStore, TrajectoryValidationError


class DistillCoverageReport:
    MAX_EXAMPLES = 3
    OBSERVED_TASK_SCOPES = {"all", "backlog", "execution"}

    def __init__(self, root: str | Path) -> None:
        self.root = Path(root).resolve()
        self.trajectories_dir = self.root / "trajectories"
        self.generator = SkillGenerator(self.root / "skill_store" / "staging")
        self.store = TrajectoryStore(self.trajectories_dir)

    def build(
        self,
        *,
        observed_task_scope: str = "all",
        max_family_items: int | None = None,
        min_family_count: int = 1,
    ) -> dict[str, Any]:
        if observed_task_scope not in self.OBSERVED_TASK_SCOPES:
            raise ValueError(
                f"observed_task_scope must be one of {sorted(self.OBSERVED_TASK_SCOPES)}"
            )
        if max_family_items is not None and max_family_items < 1:
            raise ValueError("max_family_items must be >= 1 when provided")
        if min_family_count < 1:
            raise ValueError("min_family_count must be >= 1")
        rule_counts: Counter[str] = Counter()
        matched_families: dict[tuple[str, tuple[str, ...], tuple[str, ...]], dict[str, Any]] = {}
        hotspots: dict[tuple[tuple[str, ...], tuple[str, ...]], dict[str, Any]] = {}
        observed_task_candidates: dict[tuple[tuple[str, ...], tuple[str, ...]], dict[str, Any]] = {}
        execution_observed_task_families: dict[tuple[tuple[str, ...], tuple[str, ...]], dict[str, Any]] = {}
        trajectory_count = 0
        matched_count = 0
        fallback_count = 0
        invalid_paths: list[str] = []
        invalid_observed_task_paths: list[str] = []
        capture = TrajectoryCapture(self.trajectories_dir)

        for trajectory_path in sorted(self.trajectories_dir.glob("*.json")):
            try:
                trajectory = self.store.load_file(trajectory_path)
            except (json.JSONDecodeError, TrajectoryValidationError):
                invalid_paths.append(str(trajectory_path.resolve()))
                continue

            if trajectory.final_status != "success":
                continue

            trajectory_count += 1
            input_schema = self.generator._infer_input_schema(trajectory)
            input_schema = self.generator._augment_input_schema_for_rules(trajectory, input_schema)
            selected_rule = self.generator._select_rule(trajectory, input_schema)
            rule_name = self._rule_name(selected_rule)
            rule_counts[rule_name] += 1

            if selected_rule:
                matched_count += 1
                family_key = (
                    rule_name,
                    tuple(step.tool_name.lower() for step in trajectory.steps),
                    tuple(sorted(input_schema.keys())),
                )
                matched_family = matched_families.setdefault(
                    family_key,
                    {
                        "rule_name": rule_name,
                        "count": 0,
                        "tool_sequence": list(family_key[1]),
                        "input_keys": list(family_key[2]),
                        "example_task_ids": [],
                        "example_task_descriptions": [],
                        "example_trajectory_paths": [],
                    },
                )
                matched_family["count"] += 1
                self._append_example(matched_family["example_task_ids"], trajectory.task_id)
                self._append_example(matched_family["example_task_descriptions"], trajectory.task_description)
                self._append_example(matched_family["example_trajectory_paths"], str(trajectory_path.resolve()))
                continue

            fallback_count += 1
            hotspot_key = (
                tuple(step.tool_name.lower() for step in trajectory.steps),
                tuple(sorted(input_schema.keys())),
            )
            hotspot = hotspots.setdefault(
                hotspot_key,
                {
                    "count": 0,
                    "tool_sequence": list(hotspot_key[0]),
                    "input_keys": list(hotspot_key[1]),
                    "example_task_ids": [],
                    "example_task_descriptions": [],
                    "example_trajectory_paths": [],
                },
            )
            hotspot["count"] += 1
            self._append_example(hotspot["example_task_ids"], trajectory.task_id)
            self._append_example(hotspot["example_task_descriptions"], trajectory.task_description)
            self._append_example(hotspot["example_trajectory_paths"], str(trajectory_path.resolve()))

        total = matched_count + fallback_count
        trajectory_family_count = len(matched_families) + len(hotspots)
        coverage_ratio = round(matched_count / total, 4) if total else 0.0
        family_coverage_ratio = (
            round(len(matched_families) / trajectory_family_count, 4)
            if trajectory_family_count
            else 0.0
        )

        for observed_task_path in sorted((self.root / "observed_tasks").glob("*.json")):
            try:
                payload = json.loads(observed_task_path.read_text(encoding="utf-8"))
                trajectory = capture._to_trajectory(
                    payload,
                    task_id=observed_task_path.stem,
                    session_id=f"coverage_{observed_task_path.stem}",
                )
            except (json.JSONDecodeError, TrajectoryCaptureError):
                invalid_observed_task_paths.append(str(observed_task_path.resolve()))
                continue

            input_schema = self.generator._infer_input_schema(trajectory)
            input_schema = self.generator._augment_input_schema_for_rules(trajectory, input_schema)
            hotspot_key = (
                tuple(step.tool_name.lower() for step in trajectory.steps),
                tuple(sorted(input_schema.keys())),
            )
            target_collection = (
                execution_observed_task_families
                if isinstance(payload.get("skill_name"), str) and payload["skill_name"].strip()
                else observed_task_candidates
            )
            if observed_task_scope == "backlog" and target_collection is execution_observed_task_families:
                continue
            if observed_task_scope == "execution" and target_collection is observed_task_candidates:
                continue
            candidate = target_collection.setdefault(
                hotspot_key,
                {
                    "count": 0,
                    "tool_sequence": list(hotspot_key[0]),
                    "input_keys": list(hotspot_key[1]),
                    "example_task_ids": [],
                    "example_task_descriptions": [],
                    "example_observed_task_paths": [],
                },
            )
            candidate["count"] += 1
            self._append_example(candidate["example_task_ids"], trajectory.task_id)
            self._append_example(candidate["example_task_descriptions"], trajectory.task_description)
            self._append_example(
                candidate["example_observed_task_paths"],
                str(observed_task_path.resolve()),
            )

        raw_rule_count_rows = [
            {"rule_name": rule_name, "count": count}
            for rule_name, count in sorted(
                rule_counts.items(),
                key=lambda item: (-item[1], item[0]),
            )
        ]
        raw_matched_family_rows = sorted(
            matched_families.values(),
            key=lambda item: (-item["count"], item["rule_name"], item["tool_sequence"], item["input_keys"]),
        )
        raw_fallback_rows = sorted(
            hotspots.values(),
            key=lambda item: (-item["count"], item["tool_sequence"], item["input_keys"]),
        )
        raw_observed_candidate_rows = sorted(
            observed_task_candidates.values(),
            key=lambda item: (-item["count"], item["tool_sequence"], item["input_keys"]),
        )
        raw_execution_family_rows = sorted(
            execution_observed_task_families.values(),
            key=lambda item: (-item["count"], item["tool_sequence"], item["input_keys"]),
        )

        rule_count_rows = [
            {"rule_name": rule_name, "count": count}
            for rule_name, count in (
                (item["rule_name"], item["count"]) for item in raw_rule_count_rows
            )
            if count >= min_family_count
        ]
        matched_family_rows = [
            item
            for item in raw_matched_family_rows
            if item["count"] >= min_family_count
        ]
        fallback_rows = [
            item
            for item in raw_fallback_rows
            if item["count"] >= min_family_count
        ]
        observed_candidate_rows = [
            item
            for item in raw_observed_candidate_rows
            if item["count"] >= min_family_count
        ]
        execution_family_rows = [
            item
            for item in raw_execution_family_rows
            if item["count"] >= min_family_count
        ]

        payload = {
            "trajectory_count": trajectory_count,
            "matched_count": matched_count,
            "fallback_count": fallback_count,
            "invalid_count": len(invalid_paths),
            "invalid_trajectory_paths": invalid_paths,
            "invalid_observed_task_count": len(invalid_observed_task_paths),
            "invalid_observed_task_paths": invalid_observed_task_paths,
            "observed_task_scope": observed_task_scope,
            "max_family_items": max_family_items,
            "min_family_count": min_family_count,
            "coverage_ratio": coverage_ratio,
            "trajectory_family_count": trajectory_family_count,
            "matched_family_count": len(matched_family_rows),
            "fallback_family_count": len(fallback_rows),
            "family_coverage_ratio": family_coverage_ratio,
            "observed_task_candidate_count": sum(
                candidate["count"] for candidate in observed_candidate_rows
            ),
            "observed_task_candidate_family_count": len(observed_candidate_rows),
            "execution_observed_task_count": sum(
                candidate["count"] for candidate in execution_family_rows
            ),
            "execution_observed_task_family_count": len(execution_family_rows),
            "rule_counts": rule_count_rows,
            "matched_families": matched_family_rows,
            "fallback_hotspots": fallback_rows,
            "observed_task_candidates": observed_candidate_rows,
            "execution_observed_task_families": execution_family_rows,
        }
        payload["concentration_summary"] = {
            "matched_families": self._concentration_summary(
                payload["matched_families"],
                family_count=len(matched_family_rows),
                top_rule_key="rule_name",
            ),
            "fallback_hotspots": self._concentration_summary(
                payload["fallback_hotspots"],
                family_count=len(fallback_rows),
            ),
            "observed_task_candidates": self._concentration_summary(
                payload["observed_task_candidates"],
                family_count=len(observed_candidate_rows),
            ),
            "execution_observed_task_families": self._concentration_summary(
                payload["execution_observed_task_families"],
                family_count=len(execution_family_rows),
            ),
        }
        visible_rule_count_rows = payload["rule_counts"]
        visible_matched_family_rows = payload["matched_families"]
        visible_fallback_rows = payload["fallback_hotspots"]
        visible_observed_candidate_rows = payload["observed_task_candidates"]
        visible_execution_family_rows = payload["execution_observed_task_families"]
        if max_family_items is not None:
            for key in (
                "rule_counts",
                "matched_families",
                "fallback_hotspots",
                "observed_task_candidates",
                "execution_observed_task_families",
            ):
                payload[key] = payload[key][:max_family_items]
            visible_rule_count_rows = payload["rule_counts"]
            visible_matched_family_rows = payload["matched_families"]
            visible_fallback_rows = payload["fallback_hotspots"]
            visible_observed_candidate_rows = payload["observed_task_candidates"]
            visible_execution_family_rows = payload["execution_observed_task_families"]
        payload["visibility_summary"] = {
            "rule_counts": self._visibility_summary(
                raw_rows=raw_rule_count_rows,
                filtered_rows=rule_count_rows,
                visible_rows=visible_rule_count_rows,
            ),
            "matched_families": self._visibility_summary(
                raw_rows=raw_matched_family_rows,
                filtered_rows=matched_family_rows,
                visible_rows=visible_matched_family_rows,
            ),
            "fallback_hotspots": self._visibility_summary(
                raw_rows=raw_fallback_rows,
                filtered_rows=fallback_rows,
                visible_rows=visible_fallback_rows,
            ),
            "observed_task_candidates": self._visibility_summary(
                raw_rows=raw_observed_candidate_rows,
                filtered_rows=observed_candidate_rows,
                visible_rows=visible_observed_candidate_rows,
            ),
            "execution_observed_task_families": self._visibility_summary(
                raw_rows=raw_execution_family_rows,
                filtered_rows=execution_family_rows,
                visible_rows=visible_execution_family_rows,
            ),
        }
        payload["view_host_operations"] = self._view_host_operations(
            observed_task_scope=observed_task_scope,
            max_family_items=max_family_items,
            min_family_count=min_family_count,
            payload=payload,
        )
        fallback_hotspots = payload["fallback_hotspots"]
        observed_task_backlog = payload["observed_task_candidates"]
        execution_observed_task_families = payload["execution_observed_task_families"]
        refresh_operation = distill_coverage_report_operation(
            observed_task_scope=observed_task_scope,
            max_family_items=max_family_items,
            min_family_count=min_family_count,
            display_label="Refresh distill coverage report",
            effect_summary="Refresh coverage after reviewing or extending deterministic handling.",
            risk_level="low",
            requires_confirmation=False,
            source_ref=source_ref_distill_coverage_report_refresh(),
        )
        if not fallback_hotspots and not observed_task_backlog:
            if observed_task_scope == "all" and execution_observed_task_families:
                view_operations = [
                    operation
                    for operation in payload["view_host_operations"]
                    if operation.get("tool_name") == "distill_coverage_report"
                ]
                primary_operation = next(
                    (
                        operation
                        for operation in view_operations
                        if operation.get("arguments", {}).get("observed_task_scope") == "execution"
                    ),
                    None,
                )
                additional_operations = [
                    operation
                    for operation in view_operations
                    if primary_operation is None
                    or operation.get("operation_id") != primary_operation.get("operation_id")
                ]
                if primary_operation is not None:
                    return with_recommendation(
                        payload,
                        distill_coverage_report_recommendation(
                            observed_task_scope="execution",
                            max_family_items=max_family_items,
                            min_family_count=min_family_count,
                            display_label=primary_operation["display_label"],
                            effect_summary=primary_operation["effect_summary"],
                            risk_level="low",
                            requires_confirmation=False,
                            source_ref=primary_operation.get("source_ref"),
                            reason=(
                                "No fallback hotspots or backlog candidates remain. Inspect the execution-only view next to review dogfood and test-heavy execution traffic."
                            ),
                            additional_operations=additional_operations,
                        ),
                    )
            return with_recommendation(
                payload,
                no_recommendation(
                    "No fallback hotspots remain in the saved successful trajectory set, and no observed-task candidates are waiting for distill_and_promote_candidate."
                ),
            )

        if fallback_hotspots:
            top_hotspot = fallback_hotspots[0]
            primary_path = top_hotspot["example_trajectory_paths"][0]
            primary_task_id = top_hotspot["example_task_ids"][0]
            additional_operations: list[dict[str, Any]] = []

            for task_id, trajectory_path in zip(
                top_hotspot["example_task_ids"][1:],
                top_hotspot["example_trajectory_paths"][1:],
                strict=False,
            ):
                additional_operations.append(
                    distill_trajectory_operation(
                        trajectory_path,
                        display_label="Inspect similar fallback hotspot",
                        effect_summary="Distill another representative fallback trajectory from the same hotspot cluster.",
                        risk_level="low",
                        requires_confirmation=False,
                        source_ref=source_ref_trajectory(task_id),
                    )
                )

            additional_operations.append(refresh_operation)

            return with_recommendation(
                payload,
                distill_trajectory_recommendation(
                    primary_path,
                    display_label="Inspect top fallback hotspot",
                    effect_summary="Open the top representative fallback trajectory for deterministic-rule review or promotion.",
                    risk_level="low",
                    requires_confirmation=False,
                    source_ref=source_ref_trajectory(primary_task_id),
                    reason="Fallback hotspots remain. Start from the top representative trajectory and inspect deterministic coverage gaps.",
                    additional_operations=additional_operations,
                ),
            )

        top_candidate = observed_task_backlog[0]
        primary_observed_task_path = top_candidate["example_observed_task_paths"][0]
        additional_operations = []
        for observed_task_path in top_candidate["example_observed_task_paths"][1:]:
            additional_operations.append(
                distill_and_promote_operation(
                    observed_task_path=observed_task_path,
                    display_label="Promote similar observed-task candidate",
                    effect_summary="Capture, distill, audit, and promote another representative observed-task candidate from the same cluster.",
                    argument_schema={
                        "observed_task_path": {"type": "string", "required": True, "prefilled": True},
                    },
                    risk_level="low",
                    requires_confirmation=False,
                    source_ref=source_ref_observed_task(observed_task_path),
                )
            )
        additional_operations.append(refresh_operation)

        return with_recommendation(
            payload,
            distill_and_promote_recommendation(
                observed_task_path=primary_observed_task_path,
                display_label="Promote top observed-task candidate",
                effect_summary="Capture, distill, audit, and promote the top observed-task candidate workflow.",
                argument_schema={
                    "observed_task_path": {"type": "string", "required": True, "prefilled": True},
                },
                risk_level="low",
                requires_confirmation=False,
                source_ref=source_ref_observed_task(primary_observed_task_path),
                reason=(
                    "No fallback hotspots remain, but observed-task candidates are available. Start from the top representative candidate and send it through distill_and_promote_candidate."
                ),
                additional_operations=additional_operations,
            ),
        )

    def _rule_name(self, rule: Any) -> str:
        if rule is None:
            return "llm_fallback"
        return getattr(rule, "RULE_NAME", rule.__name__.split(".")[-1])

    def _append_example(self, examples: list[str], value: str) -> None:
        if len(examples) >= self.MAX_EXAMPLES or value in examples:
            return
        examples.append(value)

    def _concentration_summary(
        self,
        families: list[dict[str, Any]],
        *,
        family_count: int,
        top_rule_key: str | None = None,
    ) -> dict[str, Any]:
        total_count = sum(int(item.get("count", 0)) for item in families)
        if not families or total_count <= 0:
            return {
                "family_count": family_count,
                "total_count": total_count,
                "top_count": 0,
                "top_share": 0.0,
                "top_rule_name": None,
                "top_tool_sequence": [],
                "top_input_keys": [],
            }

        top = families[0]
        return {
            "family_count": family_count,
            "total_count": total_count,
            "top_count": int(top.get("count", 0)),
            "top_share": round(int(top.get("count", 0)) / total_count, 4),
            "top_rule_name": top.get(top_rule_key) if top_rule_key else None,
            "top_tool_sequence": list(top.get("tool_sequence", [])),
            "top_input_keys": list(top.get("input_keys", [])),
        }

    def _view_host_operations(
        self,
        *,
        observed_task_scope: str,
        max_family_items: int | None,
        min_family_count: int,
        payload: dict[str, Any],
    ) -> list[dict[str, Any]]:
        operations: list[dict[str, Any] | None] = []
        if observed_task_scope != "all":
            operations.append(
                distill_coverage_report_operation(
                    observed_task_scope="all",
                    max_family_items=max_family_items,
                    min_family_count=min_family_count,
                    display_label="Show all coverage",
                    effect_summary="Return to the combined distill coverage view across trajectories and observed tasks.",
                    risk_level="low",
                    requires_confirmation=False,
                    source_ref=source_ref_distill_coverage_report_view("all"),
                )
            )

        if payload.get("observed_task_candidate_family_count", 0) > 0 and observed_task_scope != "backlog":
            operations.append(
                distill_coverage_report_operation(
                    observed_task_scope="backlog",
                    max_family_items=max_family_items,
                    min_family_count=min_family_count,
                    display_label="Focus backlog view",
                    effect_summary="Show only observed-task candidates that are still waiting for deterministic distill coverage.",
                    risk_level="low",
                    requires_confirmation=False,
                    source_ref=source_ref_distill_coverage_report_view("backlog"),
                )
            )

        if payload.get("execution_observed_task_family_count", 0) > 0 and observed_task_scope != "execution":
            operations.append(
                distill_coverage_report_operation(
                    observed_task_scope="execution",
                    max_family_items=max_family_items,
                    min_family_count=min_family_count,
                    display_label="Focus execution view",
                    effect_summary="Show only execution-derived observed-task families to inspect dogfood and test-heavy traffic.",
                    risk_level="low",
                    requires_confirmation=False,
                    source_ref=source_ref_distill_coverage_report_view("execution"),
                )
            )

        visibility_summary = payload.get("visibility_summary", {})
        hidden_family_total = sum(
            int((visibility_summary.get(key) or {}).get("hidden_family_count", 0))
            for key in (
                "rule_counts",
                "matched_families",
                "fallback_hotspots",
                "observed_task_candidates",
                "execution_observed_task_families",
            )
        )
        filtered_family_total = sum(
            int((visibility_summary.get(key) or {}).get("raw_family_count", 0))
            - int((visibility_summary.get(key) or {}).get("filtered_family_count", 0))
            for key in (
                "rule_counts",
                "matched_families",
                "fallback_hotspots",
                "observed_task_candidates",
                "execution_observed_task_families",
            )
        )

        if max_family_items is not None and hidden_family_total > 0:
            operations.append(
                distill_coverage_report_operation(
                    observed_task_scope=observed_task_scope,
                    min_family_count=min_family_count,
                    display_label="Show hidden families",
                    effect_summary="Remove the family list cap for the current view so hidden families become visible.",
                    risk_level="low",
                    requires_confirmation=False,
                    source_ref=source_ref_distill_coverage_report_view(f"{observed_task_scope}:expand"),
                )
            )

        if min_family_count > 1 and filtered_family_total > 0:
            operations.append(
                distill_coverage_report_operation(
                    observed_task_scope=observed_task_scope,
                    max_family_items=max_family_items,
                    min_family_count=1,
                    display_label="Show lower-frequency families",
                    effect_summary="Lower the family threshold for the current view to include less frequent families.",
                    risk_level="low",
                    requires_confirmation=False,
                    source_ref=source_ref_distill_coverage_report_view(f"{observed_task_scope}:lower_threshold"),
                )
            )

        return collect_operations(operations)

    def _visibility_summary(
        self,
        *,
        raw_rows: list[dict[str, Any]],
        filtered_rows: list[dict[str, Any]],
        visible_rows: list[dict[str, Any]],
    ) -> dict[str, Any]:
        raw_item_count = sum(int(item.get("count", 0)) for item in raw_rows)
        filtered_item_count = sum(int(item.get("count", 0)) for item in filtered_rows)
        visible_item_count = sum(int(item.get("count", 0)) for item in visible_rows)
        return {
            "raw_family_count": len(raw_rows),
            "filtered_family_count": len(filtered_rows),
            "visible_family_count": len(visible_rows),
            "hidden_family_count": max(len(filtered_rows) - len(visible_rows), 0),
            "raw_item_count": raw_item_count,
            "filtered_item_count": filtered_item_count,
            "visible_item_count": visible_item_count,
            "hidden_item_count": max(filtered_item_count - visible_item_count, 0),
        }
