from __future__ import annotations

import asyncio
import shutil
import sys
from contextlib import contextmanager
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any


def validate_host_operation(operation: dict[str, Any] | None, *, label: str) -> list[str]:
    violations: list[str] = []
    if not isinstance(operation, dict):
        return [f"{label} must be a dict host operation."]

    required_string_fields = (
        "operation_id",
        "tool_name",
        "display_label",
        "effect_summary",
    )
    for field_name in required_string_fields:
        if not isinstance(operation.get(field_name), str) or not operation[field_name].strip():
            violations.append(f"{label} missing required string field: {field_name}")

    if operation.get("type") != "mcp_tool_call":
        violations.append(f"{label} must set type='mcp_tool_call'")
    if not isinstance(operation.get("arguments"), dict):
        violations.append(f"{label} must include dict arguments")
    if not isinstance(operation.get("argument_schema"), dict):
        violations.append(f"{label} must include dict argument_schema")
    if operation.get("risk_level") not in {"low", "medium", "high"}:
        violations.append(f"{label} has invalid risk_level")
    if operation.get("operation_role") not in {"primary", "default", "preview"}:
        violations.append(f"{label} has invalid operation_role")
    if not isinstance(operation.get("requires_confirmation"), bool):
        violations.append(f"{label} must include boolean requires_confirmation")

    confirmation_message = operation.get("confirmation_message")
    if operation.get("requires_confirmation"):
        if not isinstance(confirmation_message, str) or not confirmation_message.strip():
            violations.append(f"{label} must include confirmation_message when confirmation is required")
    elif confirmation_message is not None:
        violations.append(f"{label} must not include confirmation_message when confirmation is not required")

    source_ref = operation.get("source_ref")
    if source_ref is not None and not isinstance(source_ref, str):
        violations.append(f"{label} has invalid source_ref")
    operation_group = operation.get("operation_group")
    if operation_group is not None and not isinstance(operation_group, str):
        violations.append(f"{label} has invalid operation_group")
    delivery_mode = operation.get("delivery_mode")
    if delivery_mode is not None and not isinstance(delivery_mode, str):
        violations.append(f"{label} has invalid delivery_mode")
    variant_role = operation.get("variant_role")
    if variant_role is not None and variant_role not in {"preferred", "alternate"}:
        violations.append(f"{label} has invalid variant_role")

    preview = operation.get("preview")
    if preview is not None:
        violations.extend(validate_host_operation(preview, label=f"{label}.preview"))
        if isinstance(preview, dict) and preview.get("operation_role") != "preview":
            violations.append(f"{label}.preview must use operation_role='preview'")

    return violations


def validate_recommendation_payload(payload: dict[str, Any], *, label: str) -> list[str]:
    violations: list[str] = []
    for field_name in (
        "recommended_next_action",
        "recommended_reason",
        "recommended_host_operation",
        "available_host_operations",
    ):
        if field_name not in payload:
            violations.append(f"{label} missing recommendation field: {field_name}")

    operations = payload.get("available_host_operations")
    if not isinstance(operations, list):
        violations.append(f"{label}.available_host_operations must be a list")
        operations = []

    recommended_operation = payload.get("recommended_host_operation")
    if recommended_operation is None:
        if payload.get("recommended_next_action") is not None:
            violations.append(f"{label} must set recommended_next_action to None when no operation is recommended")
        if operations:
            violations.append(f"{label} must not expose available_host_operations when no recommendation exists")
        return violations

    violations.extend(validate_host_operation(recommended_operation, label=f"{label}.recommended_host_operation"))

    if not isinstance(payload.get("recommended_next_action"), str) or not payload["recommended_next_action"].strip():
        violations.append(f"{label} must include recommended_next_action when a host operation is present")
    if operations:
        first = operations[0]
        violations.extend(validate_host_operation(first, label=f"{label}.available_host_operations[0]"))
        if isinstance(first, dict) and isinstance(recommended_operation, dict):
            if first.get("operation_id") != recommended_operation.get("operation_id"):
                violations.append(f"{label} must place the recommended host operation first in available_host_operations")
            if first.get("operation_role") != "primary":
                violations.append(f"{label} must mark the first available host operation as primary")
    else:
        violations.append(f"{label} must expose available_host_operations when a recommendation exists")

    for index, operation in enumerate(operations):
        violations.extend(validate_host_operation(operation, label=f"{label}.available_host_operations[{index}]"))

    return violations


def validate_search_result(result: dict[str, Any], *, label: str) -> list[str]:
    violations: list[str] = []
    for field_name in ("skill_name", "summary", "score", "why_matched", "host_operation", "recommended_next_action"):
        if field_name not in result:
            violations.append(f"{label} missing search result field: {field_name}")
    if result.get("recommended_next_action") != "execute_skill":
        violations.append(f"{label} must recommend execute_skill")
    if not isinstance(result.get("score"), float):
        violations.append(f"{label}.score must be a float")
    violations.extend(validate_host_operation(result.get("host_operation"), label=f"{label}.host_operation"))
    return violations


def validate_governance_action(action: dict[str, Any], *, label: str) -> list[str]:
    violations: list[str] = []
    for field_name in ("action", "reason", "skill_names", "canonical_skill", "cluster_count", "host_operation"):
        if field_name not in action:
            violations.append(f"{label} missing governance action field: {field_name}")
    if not isinstance(action.get("skill_names"), list):
        violations.append(f"{label}.skill_names must be a list")
    if not isinstance(action.get("cluster_count"), int):
        violations.append(f"{label}.cluster_count must be an int")
    violations.extend(validate_host_operation(action.get("host_operation"), label=f"{label}.host_operation"))
    return violations


def validate_mcp_tool_result(payload: dict[str, Any] | None, *, label: str) -> list[str]:
    if not isinstance(payload, dict):
        return [f"{label} must return a dict."]

    violations: list[str] = []
    status = payload.get("status")
    if status not in {"ok", "error"}:
        violations.append(f"{label} must set status to 'ok' or 'error'")

    if status == "ok":
        if "data" not in payload:
            violations.append(f"{label} missing data for ok response")
    elif status == "error":
        for field_name in ("message", "code", "details"):
            if field_name not in payload:
                violations.append(f"{label} missing error field: {field_name}")

    return violations


def validate_operation_log_entry(entry: dict[str, Any] | None, *, label: str) -> list[str]:
    if not isinstance(entry, dict):
        return [f"{label} must be a dict operation log entry"]

    violations: list[str] = []
    for field_name in ("operation_id", "tool_name", "observation", "status"):
        if not isinstance(entry.get(field_name), str) or not entry[field_name].strip():
            violations.append(f"{label} missing required string field: {field_name}")
    if not isinstance(entry.get("tool_input"), dict):
        violations.append(f"{label}.tool_input must be a dict")
    if not isinstance(entry.get("mutation"), bool):
        violations.append(f"{label}.mutation must be a bool")
    rollback_hint = entry.get("rollback_hint")
    if rollback_hint is not None and not isinstance(rollback_hint, dict):
        violations.append(f"{label}.rollback_hint must be a dict when present")
    return violations


def validate_wrapped_service_payload(
    wrapped_payload: dict[str, Any] | None,
    service_payload: dict[str, Any] | None,
    *,
    label: str,
) -> list[str]:
    violations = validate_mcp_tool_result(wrapped_payload, label=label)
    if violations:
        return violations
    if not isinstance(wrapped_payload, dict) or wrapped_payload.get("status") != "ok":
        return violations
    if wrapped_payload.get("data") != service_payload:
        violations.append(f"{label} data does not match service payload")
    return violations


@contextmanager
def isolated_runtime_root(source_root: Path):
    with TemporaryDirectory() as temp_dir:
        temp_root = Path(temp_dir)
        for directory_name in (
            "audits",
            "demo",
            "observed_tasks",
            "output",
            "skill_store",
            "trajectories",
        ):
            source_dir = source_root / directory_name
            target_dir = temp_root / directory_name
            if source_dir.exists():
                shutil.copytree(source_dir, target_dir)
            else:
                target_dir.mkdir(parents=True, exist_ok=True)
        yield temp_root


def validate_execute_skill_equivalence(
    service_payload: dict[str, Any],
    wrapped_mcp_payload: dict[str, Any] | None,
    *,
    label: str,
) -> list[str]:
    violations = validate_mcp_tool_result(wrapped_mcp_payload, label=label)
    if violations:
        return violations
    if not isinstance(wrapped_mcp_payload, dict) or wrapped_mcp_payload.get("status") != "ok":
        return violations

    mcp_payload = wrapped_mcp_payload.get("data")
    if not isinstance(mcp_payload, dict):
        return [*violations, f"{label} must return dict data for ok responses"]

    violations.extend(validate_recommendation_payload(service_payload, label=f"{label}.service"))
    violations.extend(validate_recommendation_payload(mcp_payload, label=f"{label}.mcp"))

    for payload_label, payload in (("service", service_payload), ("mcp", mcp_payload)):
        if payload.get("skill_name") != "merge_text_files":
            violations.append(f"{label}.{payload_label} must preserve the executed skill name")
        result = payload.get("result")
        if not isinstance(result, dict) or result.get("status") != "completed":
            violations.append(f"{label}.{payload_label} must report a completed execution result")
        observed_task_record = payload.get("observed_task_record")
        if not isinstance(observed_task_record, str) or not observed_task_record.strip():
            violations.append(f"{label}.{payload_label} must expose observed_task_record")
            continue
        if not Path(observed_task_record).exists():
            violations.append(f"{label}.{payload_label} observed_task_record must exist on disk")
        operation_log = payload.get("operation_log")
        if not isinstance(operation_log, list) or not operation_log:
            violations.append(f"{label}.{payload_label} must expose non-empty operation_log")
        else:
            for index, entry in enumerate(operation_log):
                violations.extend(
                    validate_operation_log_entry(
                        entry,
                        label=f"{label}.{payload_label}.operation_log[{index}]",
                    )
                )
        planned_changes = payload.get("planned_changes")
        if not isinstance(planned_changes, list):
            violations.append(f"{label}.{payload_label} must expose planned_changes as a list")

        recommended_operation = payload.get("recommended_host_operation")
        if isinstance(recommended_operation, dict):
            if recommended_operation.get("tool_name") != "distill_and_promote_candidate":
                violations.append(
                    f"{label}.{payload_label} must recommend distill_and_promote_candidate after execution"
                )
            if recommended_operation.get("arguments", {}).get("observed_task_path") != observed_task_record:
                violations.append(
                    f"{label}.{payload_label} follow-up must target the emitted observed_task_record"
                )
            if recommended_operation.get("source_ref") != f"observed_task:{observed_task_record}":
                violations.append(
                    f"{label}.{payload_label} follow-up source_ref must point to the emitted observed task"
                )

    if service_payload.get("recommended_next_action") != mcp_payload.get("recommended_next_action"):
        violations.append(f"{label} service and mcp must recommend the same next action")
    if service_payload.get("recommended_reason") != mcp_payload.get("recommended_reason"):
        violations.append(f"{label} service and mcp must expose the same recommendation reason")

    return violations


def validate_promote_skill_equivalence(
    service_payload: dict[str, Any],
    wrapped_mcp_payload: dict[str, Any] | None,
    *,
    label: str,
) -> list[str]:
    violations = validate_mcp_tool_result(wrapped_mcp_payload, label=label)
    if violations:
        return violations
    if not isinstance(wrapped_mcp_payload, dict) or wrapped_mcp_payload.get("status") != "ok":
        return violations

    mcp_payload = wrapped_mcp_payload.get("data")
    if not isinstance(mcp_payload, dict):
        return [*violations, f"{label} must return dict data for ok responses"]

    violations.extend(validate_recommendation_payload(service_payload, label=f"{label}.service"))
    violations.extend(validate_recommendation_payload(mcp_payload, label=f"{label}.mcp"))

    for payload_label, payload in (("service", service_payload), ("mcp", mcp_payload)):
        skill_name = payload.get("skill_name")
        if not isinstance(skill_name, str) or not skill_name.strip():
            violations.append(f"{label}.{payload_label} must expose the promoted skill name")
            continue
        for path_field in ("active_file", "metadata_file"):
            path_value = payload.get(path_field)
            if not isinstance(path_value, str) or not path_value.strip():
                violations.append(f"{label}.{payload_label} must expose {path_field}")
            elif not Path(path_value).exists():
                violations.append(f"{label}.{payload_label} {path_field} must exist on disk")

        recommended_operation = payload.get("recommended_host_operation")
        if isinstance(recommended_operation, dict):
            if recommended_operation.get("tool_name") != "execute_skill":
                violations.append(f"{label}.{payload_label} must recommend execute_skill after promotion")
            if recommended_operation.get("arguments", {}).get("skill_name") != skill_name:
                violations.append(
                    f"{label}.{payload_label} follow-up must target the promoted skill name"
                )

    if service_payload.get("skill_name") != mcp_payload.get("skill_name"):
        violations.append(f"{label} service and mcp must expose the same promoted skill name")
    if service_payload.get("audit_score") != mcp_payload.get("audit_score"):
        violations.append(f"{label} service and mcp must preserve the same audit score")
    if service_payload.get("recommended_next_action") != mcp_payload.get("recommended_next_action"):
        violations.append(f"{label} service and mcp must recommend the same next action")

    return violations


def check_runtime_contracts() -> list[str]:
    from skill_runtime.api.service import RuntimeService
    from skill_runtime.mcp.server import build_mcp_server
    from skill_runtime.mcp.host_operations import (
        archive_duplicate_candidates_action,
        review_fixture_noise_action,
        executed_skill_promotion_recommendation,
        governance_report_payload,
        no_recommendation,
        search_no_match_recommendation,
        search_response_payload,
        search_result_payload,
    )

    violations: list[str] = []

    search_result = search_result_payload(
        "merge_text_files",
        "Merge text files.",
        0.91,
        "Matched on keywords: merge, text.",
        {"input_dir": "str", "output_path": "str"},
        rule_name="text_merge",
        rule_priority=70,
        rule_reason="Matched text_merge.",
        library_tier="stable",
        score_breakdown={"lexical": 0.8},
    )
    violations.extend(validate_search_result(search_result, label="search_result_payload"))

    search_recommendation = search_no_match_recommendation(reason="No strong match found.")
    violations.extend(validate_recommendation_payload(search_recommendation, label="search_no_match_recommendation"))

    execution_recommendation = executed_skill_promotion_recommendation("D:/tmp/observed.json")
    violations.extend(
        validate_recommendation_payload(
            execution_recommendation,
            label="executed_skill_promotion_recommendation",
        )
    )

    response_payload = search_response_payload(
        "merge text files",
        [search_result],
        "merge_text_files",
        execution_recommendation,
    )
    violations.extend(validate_recommendation_payload(response_payload, label="search_response_payload"))

    governance_action = archive_duplicate_candidates_action(
        ["merge_text_files_generated"],
        canonical_skill="merge_text_files",
        cluster_count=2,
        rule_name="text_merge",
    )
    violations.extend(validate_governance_action(governance_action, label="archive_duplicate_candidates_action"))
    fixture_action = review_fixture_noise_action(
        skill_names=["cli_merge_fixture_test"],
        fixture_count=1,
        hidden_fixture_only_duplicate_clusters=1,
    )
    violations.extend(validate_governance_action(fixture_action, label="review_fixture_noise_action"))

    governance_payload = governance_report_payload(
        {"active": 1, "archived": 0},
        [],
        [governance_action, fixture_action],
        staging_count=0,
        archive_count=0,
        active_count=1,
        library_tier_counts={"stable": 1, "experimental": 0, "fixture": 0},
        library_tier_summary={
            "production_ready_count": 1,
            "experimental_count": 0,
            "fixture_count": 0,
            "fixture_only_duplicate_clusters_hidden": 0,
        },
    )
    available_operations = governance_payload.get("available_host_operations", [])
    if not isinstance(available_operations, list) or not available_operations:
        violations.append("governance_report_payload must expose available_host_operations")
    else:
        for index, operation in enumerate(available_operations):
            violations.extend(validate_host_operation(operation, label=f"governance_report_payload.available_host_operations[{index}]"))

    no_recommendation_payload = no_recommendation("Nothing to do.")
    violations.extend(validate_recommendation_payload(no_recommendation_payload, label="no_recommendation"))

    root = Path(__file__).resolve().parent.parent
    service = RuntimeService(root)
    server = build_mcp_server(root)
    service.reindex()

    search_service_payload = service.search("merge txt files into markdown", top_k=3)
    _, search_mcp_payload = asyncio.run(
        server.call_tool("search_skill", {"query": "merge txt files into markdown", "top_k": 3})
    )
    violations.extend(
        validate_wrapped_service_payload(
            search_mcp_payload,
            search_service_payload,
            label="search_skill",
        )
    )

    no_match_service_payload = service.search("nonexistent workflow phrase for zero matches", top_k=3)
    _, no_match_mcp_payload = asyncio.run(
        server.call_tool(
            "search_skill",
            {"query": "nonexistent workflow phrase for zero matches", "top_k": 3},
        )
    )
    violations.extend(
        validate_wrapped_service_payload(
            no_match_mcp_payload,
            no_match_service_payload,
            label="search_skill.no_match",
        )
    )

    trajectory_path = root / "trajectories" / "demo_merge_text_files.json"
    log_service_payload = service.log_trajectory(trajectory_path)
    _, log_mcp_payload = asyncio.run(
        server.call_tool("log_trajectory", {"file_path": str(trajectory_path)})
    )
    violations.extend(
        validate_wrapped_service_payload(
            log_mcp_payload,
            log_service_payload,
            label="log_trajectory",
        )
    )

    governance_service_payload = service.governance_report()
    _, governance_mcp_payload = asyncio.run(server.call_tool("governance_report", {}))
    violations.extend(
        validate_wrapped_service_payload(
            governance_mcp_payload,
            governance_service_payload,
            label="governance_report",
        )
    )
    distill_coverage_service_payload = service.distill_coverage_report()
    _, distill_coverage_mcp_payload = asyncio.run(server.call_tool("distill_coverage_report", {}))
    violations.extend(
        validate_wrapped_service_payload(
            distill_coverage_mcp_payload,
            distill_coverage_service_payload,
            label="distill_coverage_report",
        )
    )

    with isolated_runtime_root(root) as reindex_root:
        reindex_service = RuntimeService(reindex_root)
        reindex_server = build_mcp_server(reindex_root)
        reindex_service_payload = reindex_service.reindex()
        _, reindex_mcp_payload = asyncio.run(reindex_server.call_tool("reindex_skills", {}))
        violations.extend(
            validate_wrapped_service_payload(
                reindex_mcp_payload,
                reindex_service_payload,
                label="reindex_skills",
            )
        )

    with isolated_runtime_root(root) as backfill_root:
        backfill_service = RuntimeService(backfill_root)
        backfill_server = build_mcp_server(backfill_root)
        backfill_service.reindex()
        backfill_service_payload = backfill_service.backfill_provenance()
        _, backfill_mcp_payload = asyncio.run(
            backfill_server.call_tool("backfill_skill_provenance", {})
        )
        violations.extend(
            validate_wrapped_service_payload(
                backfill_mcp_payload,
                backfill_service_payload,
                label="backfill_skill_provenance",
            )
        )

    with isolated_runtime_root(root) as distill_root:
        distill_service = RuntimeService(distill_root)
        distill_server = build_mcp_server(distill_root)
        distill_service.reindex()
        distill_trajectory_path = distill_root / "trajectories" / "demo_merge_text_files.json"
        distill_service_payload = distill_service.distill(
            distill_trajectory_path,
            skill_name="contract_distill_check",
        )
        _, distill_mcp_payload = asyncio.run(
            distill_server.call_tool(
                "distill_trajectory",
                {
                    "trajectory_path": str(distill_trajectory_path),
                    "skill_name": "contract_distill_check",
                },
            )
        )
        violations.extend(
            validate_wrapped_service_payload(
                distill_mcp_payload,
                distill_service_payload,
                label="distill_trajectory",
            )
        )
        audit_service_payload = distill_service.audit(
            distill_service_payload["staging_file"],
            trajectory_path=distill_service_payload["trajectory_path"],
        )
        _, audit_mcp_payload = asyncio.run(
            distill_server.call_tool(
                "audit_skill",
                {
                    "file_path": distill_service_payload["staging_file"],
                    "trajectory_path": distill_service_payload["trajectory_path"],
                },
            )
        )
        violations.extend(
            validate_wrapped_service_payload(
                audit_mcp_payload,
                audit_service_payload,
                label="audit_skill",
            )
        )

    with isolated_runtime_root(root) as execute_service_root, isolated_runtime_root(root) as execute_mcp_root:
        execute_service = RuntimeService(execute_service_root)
        execute_service.reindex()
        execute_service_payload = execute_service.execute(
            "merge_text_files",
            {
                "input_dir": "demo/input",
                "output_path": "demo/output/contract_execute.md",
            },
        )

        execute_server = build_mcp_server(execute_mcp_root)
        _, execute_mcp_payload = asyncio.run(
            execute_server.call_tool(
                "execute_skill",
                {
                    "skill_name": "merge_text_files",
                    "args": {
                        "input_dir": "demo/input",
                        "output_path": "demo/output/contract_execute.md",
                    },
                },
            )
        )

        violations.extend(
            validate_execute_skill_equivalence(
                execute_service_payload,
                execute_mcp_payload,
                label="execute_skill",
            )
        )

    with isolated_runtime_root(root) as promote_service_root, isolated_runtime_root(root) as promote_mcp_root:
        promote_service = RuntimeService(promote_service_root)
        promote_service.reindex()
        promote_service_trajectory = promote_service_root / "trajectories" / "demo_merge_text_files.json"
        promote_service_distill = promote_service.distill(
            promote_service_trajectory,
            skill_name="contract_promote_check",
        )
        promote_service.audit(
            promote_service_distill["staging_file"],
            trajectory_path=promote_service_distill["trajectory_path"],
        )
        promote_service_payload = promote_service.promote(promote_service_distill["staging_file"])

        promote_server = build_mcp_server(promote_mcp_root)
        promote_mcp_service = RuntimeService(promote_mcp_root)
        promote_mcp_service.reindex()
        promote_mcp_trajectory = promote_mcp_root / "trajectories" / "demo_merge_text_files.json"
        promote_mcp_distill = promote_mcp_service.distill(
            promote_mcp_trajectory,
            skill_name="contract_promote_check",
        )
        promote_mcp_service.audit(
            promote_mcp_distill["staging_file"],
            trajectory_path=promote_mcp_distill["trajectory_path"],
        )
        _, promote_mcp_payload = asyncio.run(
            promote_server.call_tool(
                "promote_skill",
                {"file_path": promote_mcp_distill["staging_file"]},
            )
        )
        violations.extend(
            validate_promote_skill_equivalence(
                promote_service_payload,
                promote_mcp_payload,
                label="promote_skill",
            )
        )

    with isolated_runtime_root(root) as archive_root:
        archive_service = RuntimeService(archive_root)
        archive_server = build_mcp_server(archive_root)
        archive_service.reindex()
        archive_service_payload = archive_service.archive_duplicate_candidates(
            ["merge_text_files_generated"],
            dry_run=True,
        )
        _, archive_mcp_payload = asyncio.run(
            archive_server.call_tool(
                "archive_duplicate_candidates",
                {
                    "skill_names": ["merge_text_files_generated"],
                    "dry_run": True,
                },
            )
        )
        violations.extend(
            validate_wrapped_service_payload(
                archive_mcp_payload,
                archive_service_payload,
                label="archive_duplicate_candidates",
            )
        )

    with isolated_runtime_root(root) as archive_fixture_root:
        archive_fixture_service = RuntimeService(archive_fixture_root)
        archive_fixture_server = build_mcp_server(archive_fixture_root)
        archive_fixture_service.reindex()
        archive_fixture_service_payload = archive_fixture_service.archive_fixture_skills(
            ["cli_merge_fixture_test"],
            dry_run=True,
        )
        _, archive_fixture_mcp_payload = asyncio.run(
            archive_fixture_server.call_tool(
                "archive_fixture_skills",
                {
                    "skill_names": ["cli_merge_fixture_test"],
                    "dry_run": True,
                },
            )
        )
        violations.extend(
            validate_wrapped_service_payload(
                archive_fixture_mcp_payload,
                archive_fixture_service_payload,
                label="archive_fixture_skills",
            )
        )

    with isolated_runtime_root(root) as archive_cold_root:
        archive_cold_service = RuntimeService(archive_cold_root)
        archive_cold_server = build_mcp_server(archive_cold_root)
        archive_cold_service.reindex()
        archive_cold_service_payload = archive_cold_service.archive_cold(30)
        _, archive_cold_mcp_payload = asyncio.run(
            archive_cold_server.call_tool(
                "archive_cold_skills",
                {"days": 30},
            )
        )
        violations.extend(
            validate_wrapped_service_payload(
                archive_cold_mcp_payload,
                archive_cold_service_payload,
                label="archive_cold_skills",
            )
        )

    return violations


def main() -> int:
    root = Path(__file__).resolve().parent.parent
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))

    violations = check_runtime_contracts()
    if not violations:
        print("Runtime contract check passed.")
        return 0

    print("Runtime contract check failed:")
    for violation in violations:
        print(f"- {violation}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
