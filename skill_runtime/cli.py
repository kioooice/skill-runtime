import argparse
import json
import webbrowser
from dataclasses import asdict
from pathlib import Path

from skill_runtime.api.models import (
    AgentOrchestrationResult,
    AgentTaskRequest,
    CodexTaskClassification,
    LearningDecision,
    ReuseDecision,
)
from skill_runtime.api.orchestration import AgentOrchestrationService
from skill_runtime.api.host import classify_codex_task, finalize_codex_task, run_codex_task, start_codex_task
from skill_runtime.api.service import RuntimeService, RuntimeServiceError
from skill_runtime.dashboard.collector import collect_dashboard_data, collect_global_dashboard_data
from skill_runtime.dashboard.render import render_dashboard_html
from skill_runtime.importers.local_skill_importer import SkillImportError, import_local_skill_to_staging
from skill_runtime.platforms.export_plan import plan_platform_export


ROOT = Path(__file__).resolve().parent.parent

EXIT_OK = 0
EXIT_RUNTIME_ERROR = 1
EXIT_ARGUMENT_ERROR = 2
EXIT_NOT_FOUND = 3
EXIT_VALIDATION_ERROR = 4
EXIT_POLICY_BLOCKED = 5


def service_for_args(args: argparse.Namespace) -> RuntimeService:
    return RuntimeService(Path(args.root).resolve())


def orchestration_for_args(args: argparse.Namespace) -> AgentOrchestrationService:
    return AgentOrchestrationService(Path(args.root).resolve())


def load_json_file(path: str) -> object:
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def load_json_arg(raw_value: str | None, *, file_path: str | None, error_flag: str) -> object:
    if bool(raw_value) == bool(file_path):
        raise ValueError(f"provide exactly one of {error_flag} or {error_flag}-file")
    if file_path:
        return load_json_file(file_path)
    return json.loads(raw_value)


def extract_execute_data(payload: object) -> dict:
    if not isinstance(payload, dict):
        raise ValueError("execute response must decode to a JSON object")
    if isinstance(payload.get("data"), dict):
        return payload["data"]
    return payload


def extract_rollback_request(payload: object) -> tuple[object, list[str] | None, bool]:
    execute_data = extract_execute_data(payload)
    operations = execute_data.get("available_host_operations")
    if not isinstance(operations, list):
        raise ValueError("execute response is missing available_host_operations")
    for operation in operations:
        if not isinstance(operation, dict):
            continue
        if operation.get("tool_name") != "rollback_operations":
            continue
        arguments = operation.get("arguments")
        if not isinstance(arguments, dict):
            raise ValueError("rollback host operation is missing arguments")
        operation_log = arguments.get("operation_log")
        if operation_log is None:
            raise ValueError("rollback host operation is missing operation_log")
        operation_ids = arguments.get("operation_ids")
        dry_run = bool(arguments.get("dry_run", False))
        return operation_log, operation_ids, dry_run
    raise ValueError("execute response does not contain a rollback_operations host operation")


def ok(data: dict) -> int:
    print(json.dumps({"status": "ok", "data": data}, ensure_ascii=False))
    return EXIT_OK


def error(
    message: str,
    code: str,
    details: dict | None = None,
    exit_code: int = EXIT_RUNTIME_ERROR,
) -> int:
    print(
        json.dumps(
            {
                "status": "error",
                "message": message,
                "code": code,
                "details": details or {},
            },
            ensure_ascii=False,
        )
    )
    return exit_code


def cmd_search(args: argparse.Namespace) -> int:
    try:
        return ok(service_for_args(args).search(args.query, top_k=args.top_k))
    except RuntimeServiceError as exc:
        return error(exc.message, exc.code, exc.details, exit_code=EXIT_VALIDATION_ERROR)


def cmd_execute(args: argparse.Namespace) -> int:
    if bool(args.args) == bool(args.args_file):
        return error(
            "provide exactly one of --args or --args-file",
            "INVALID_EXECUTE_INPUT",
            exit_code=EXIT_ARGUMENT_ERROR,
        )

    try:
        if args.args_file:
            parsed_args = load_json_file(args.args_file)
        else:
            parsed_args = json.loads(args.args)
    except FileNotFoundError:
        return error(
            "args file not found",
            "ARGS_FILE_NOT_FOUND",
            details={"path": args.args_file},
            exit_code=EXIT_NOT_FOUND,
        )
    except json.JSONDecodeError as exc:
        return error(
            "invalid JSON for execute args",
            "INVALID_JSON_ARGS",
            details={"reason": str(exc)},
            exit_code=EXIT_ARGUMENT_ERROR,
        )

    if not isinstance(parsed_args, dict):
        return error(
            "--args must decode to a JSON object",
            "INVALID_ARGS_OBJECT",
            details={"received_type": type(parsed_args).__name__},
            exit_code=EXIT_ARGUMENT_ERROR,
        )

    try:
        return ok(service_for_args(args).execute(args.skill, parsed_args, dry_run=args.dry_run))
    except RuntimeServiceError as exc:
        exit_code = EXIT_NOT_FOUND if exc.code == "SKILL_NOT_FOUND" else EXIT_RUNTIME_ERROR
        if exc.code == "INVALID_ARGS_OBJECT":
            exit_code = EXIT_ARGUMENT_ERROR
        return error(exc.message, exc.code, exc.details, exit_code=exit_code)


def cmd_distill(args: argparse.Namespace) -> int:
    try:
        return ok(service_for_args(args).distill(args.trajectory, skill_name=args.skill_name))
    except RuntimeServiceError as exc:
        exit_code = EXIT_NOT_FOUND if exc.code == "TRAJECTORY_NOT_FOUND" else EXIT_VALIDATION_ERROR
        return error(exc.message, exc.code, exc.details, exit_code=exit_code)


def cmd_audit(args: argparse.Namespace) -> int:
    try:
        return ok(service_for_args(args).audit(args.file, trajectory_path=args.trajectory))
    except RuntimeServiceError as exc:
        return error(exc.message, exc.code, exc.details, exit_code=EXIT_NOT_FOUND)


def cmd_promote(args: argparse.Namespace) -> int:
    try:
        return ok(service_for_args(args).promote(args.file))
    except RuntimeServiceError as exc:
        exit_code = EXIT_POLICY_BLOCKED if exc.code in {"INVALID_PROMOTION_SOURCE", "AUDIT_NOT_PASSED"} else EXIT_NOT_FOUND
        return error(exc.message, exc.code, exc.details, exit_code=exit_code)


def cmd_promote_global_codex_skill(args: argparse.Namespace) -> int:
    try:
        return ok(
            service_for_args(args).promote_to_global_codex_skill(
                args.file,
                global_skills_dir=args.global_skills_dir,
                global_skill_name=args.global_skill_name,
                overwrite=args.overwrite,
            )
        )
    except RuntimeServiceError as exc:
        exit_code = EXIT_POLICY_BLOCKED if exc.code in {
            "INVALID_PROMOTION_SOURCE",
            "AUDIT_NOT_PASSED",
            "GLOBAL_SKILL_EXISTS",
        } else EXIT_NOT_FOUND
        return error(exc.message, exc.code, exc.details, exit_code=exit_code)


def cmd_log_trajectory(args: argparse.Namespace) -> int:
    try:
        return ok(service_for_args(args).log_trajectory(args.file))
    except RuntimeServiceError as exc:
        exit_code = EXIT_NOT_FOUND if exc.code == "TRAJECTORY_NOT_FOUND" else EXIT_VALIDATION_ERROR
        return error(exc.message, exc.code, exc.details, exit_code=exit_code)


def cmd_capture_trajectory(args: argparse.Namespace) -> int:
    if sum(
        1
        for value in (
            args.file,
            args.observed_task_json,
            args.observed_task_json_file,
        )
        if value
    ) != 1:
        return error(
            "provide exactly one of --file, --observed-task-json, or --observed-task-json-file",
            "INVALID_CAPTURE_INPUT",
            exit_code=EXIT_ARGUMENT_ERROR,
        )

    observed_task = None
    if args.observed_task_json or args.observed_task_json_file:
        try:
            if args.observed_task_json_file:
                observed_task = load_json_file(args.observed_task_json_file)
            else:
                observed_task = json.loads(args.observed_task_json)
        except FileNotFoundError:
            return error(
                "observed task JSON file not found",
                "OBSERVED_TASK_JSON_FILE_NOT_FOUND",
                details={"path": args.observed_task_json_file},
                exit_code=EXIT_NOT_FOUND,
            )
        except json.JSONDecodeError as exc:
            return error(
                "invalid JSON for observed task payload",
                "INVALID_OBSERVED_TASK_JSON",
                details={"reason": str(exc)},
                exit_code=EXIT_ARGUMENT_ERROR,
            )

    try:
        return ok(
            service_for_args(args).capture_trajectory(
                args.file,
                observed_task=observed_task,
                task_id=args.task_id,
                session_id=args.session_id,
            )
        )
    except RuntimeServiceError as exc:
        exit_code = EXIT_NOT_FOUND if exc.code == "OBSERVED_TASK_NOT_FOUND" else EXIT_VALIDATION_ERROR
        return error(exc.message, exc.code, exc.details, exit_code=exit_code)


def cmd_reindex(args: argparse.Namespace) -> int:
    try:
        return ok(service_for_args(args).reindex())
    except RuntimeServiceError as exc:
        return error(exc.message, exc.code, exc.details, exit_code=EXIT_NOT_FOUND)


def cmd_archive_cold(args: argparse.Namespace) -> int:
    try:
        return ok(service_for_args(args).archive_cold(args.days))
    except RuntimeServiceError as exc:
        return error(exc.message, exc.code, exc.details, exit_code=EXIT_ARGUMENT_ERROR)


def cmd_backfill_provenance(args: argparse.Namespace) -> int:
    return ok(service_for_args(args).backfill_provenance())


def cmd_governance_report(args: argparse.Namespace) -> int:
    return ok(service_for_args(args).governance_report())


def cmd_distill_coverage_report(args: argparse.Namespace) -> int:
    try:
        return ok(
            service_for_args(args).distill_coverage_report(
                observed_task_scope=args.observed_task_scope,
                max_family_items=args.max_family_items,
                min_family_count=args.min_family_count,
            )
        )
    except RuntimeServiceError as exc:
        return error(exc.message, exc.code, exc.details, exit_code=EXIT_ARGUMENT_ERROR)


def cmd_rollback_operations(args: argparse.Namespace) -> int:
    source_count = sum(
        1
        for value in (
            args.operation_log,
            args.operation_log_file,
            args.execute_result_json,
            args.execute_result_file,
        )
        if value
    )
    if source_count != 1:
        return error(
            "provide exactly one rollback source: --operation-log, --operation-log-file, --execute-result-json, or --execute-result-file",
            "INVALID_ROLLBACK_INPUT",
            exit_code=EXIT_ARGUMENT_ERROR,
        )

    try:
        if args.execute_result_json or args.execute_result_file:
            execute_payload = load_json_arg(
                args.execute_result_json,
                file_path=args.execute_result_file,
                error_flag="--execute-result-json",
            )
            operation_log, default_operation_ids, default_dry_run = extract_rollback_request(execute_payload)
        else:
            operation_log = load_json_arg(
                args.operation_log,
                file_path=args.operation_log_file,
                error_flag="--operation-log",
            )
            default_operation_ids = None
            default_dry_run = False
    except ValueError as exc:
        return error(str(exc), "INVALID_ROLLBACK_INPUT", exit_code=EXIT_ARGUMENT_ERROR)
    except FileNotFoundError:
        return error(
            "rollback input file not found",
            "ROLLBACK_INPUT_FILE_NOT_FOUND",
            details={"path": args.operation_log_file or args.execute_result_file},
            exit_code=EXIT_NOT_FOUND,
        )
    except json.JSONDecodeError as exc:
        return error(
            "invalid JSON for rollback payload",
            "INVALID_ROLLBACK_JSON",
            details={"reason": str(exc)},
            exit_code=EXIT_ARGUMENT_ERROR,
        )

    try:
        return ok(
            service_for_args(args).rollback_operations(
                operation_log,
                operation_ids=args.operation_id or default_operation_ids,
                dry_run=args.dry_run or default_dry_run,
            )
        )
    except RuntimeServiceError as exc:
        return error(exc.message, exc.code, exc.details, exit_code=EXIT_RUNTIME_ERROR)


def cmd_archive_duplicate_candidates(args: argparse.Namespace) -> int:
    return ok(service_for_args(args).archive_duplicate_candidates(skill_names=args.skill_name, dry_run=args.dry_run))


def cmd_archive_fixture_skills(args: argparse.Namespace) -> int:
    return ok(service_for_args(args).archive_fixture_skills(skill_names=args.skill_name, dry_run=args.dry_run))


def _build_agent_task_request(args: argparse.Namespace) -> AgentTaskRequest:
    task_description = getattr(args, "task_description", None)
    if not isinstance(task_description, str) or not task_description.strip():
        raise ValueError("--task-description is required unless --plan-json already provides the request")

    known_inputs = {}
    if getattr(args, "known_inputs_json", None):
        known_inputs = json.loads(args.known_inputs_json)
        if not isinstance(known_inputs, dict):
            raise ValueError("--known-inputs-json must decode to a JSON object")

    expected_outputs = []
    if getattr(args, "expected_outputs_json", None):
        expected_outputs = json.loads(args.expected_outputs_json)
        if not isinstance(expected_outputs, list) or not all(isinstance(item, str) for item in expected_outputs):
            raise ValueError("--expected-outputs-json must decode to a JSON array of strings")

    return AgentTaskRequest(
        task_description=task_description,
        working_directory=getattr(args, "working_directory", None),
        known_inputs=known_inputs,
        expected_outputs=expected_outputs,
        risk_level=getattr(args, "risk_level", "medium"),
        task_kind=getattr(args, "task_kind", "workflow"),
        allow_silent_reuse=not getattr(args, "disable_silent_reuse", False),
        allow_learning=not getattr(args, "disable_learning", False),
    )


def cmd_agent_plan(args: argparse.Namespace) -> int:
    try:
        request = _build_agent_task_request(args)
    except (ValueError, json.JSONDecodeError) as exc:
        return error(str(exc), "INVALID_AGENT_PLAN_INPUT", exit_code=EXIT_ARGUMENT_ERROR)

    plan = start_codex_task(Path(args.root).resolve(), request)
    return ok(asdict(plan))


def _build_agent_orchestration_result(raw_plan: object) -> AgentOrchestrationResult:
    if not isinstance(raw_plan, dict):
        raise ValueError("--plan-json must decode to a JSON object")

    raw_request = raw_plan.get("request")
    raw_reuse = raw_plan.get("reuse_decision")
    if not isinstance(raw_request, dict) or not isinstance(raw_reuse, dict):
        raise ValueError("--plan-json must contain request and reuse_decision objects")

    request = AgentTaskRequest(**raw_request)
    reuse_decision = ReuseDecision(**raw_reuse)

    raw_learning = raw_plan.get("learning_decision")
    learning_decision = LearningDecision(**raw_learning) if isinstance(raw_learning, dict) else None

    selected_skill_name = raw_plan.get("selected_skill_name")
    selected_skill_args = raw_plan.get("selected_skill_args", {})
    execution_payload = raw_plan.get("execution_payload")
    learning_capture_payload = raw_plan.get("learning_capture_payload")
    runtime_lane_status = raw_plan.get("runtime_lane_status")
    runtime_lane_reason = raw_plan.get("runtime_lane_reason")
    if not isinstance(selected_skill_args, dict):
        raise ValueError("selected_skill_args in --plan-json must be an object")

    return AgentOrchestrationResult(
        request=request,
        reuse_decision=reuse_decision,
        learning_decision=learning_decision,
        runtime_lane_status=runtime_lane_status if isinstance(runtime_lane_status, str) else None,
        runtime_lane_reason=runtime_lane_reason if isinstance(runtime_lane_reason, str) else None,
        selected_skill_name=selected_skill_name if isinstance(selected_skill_name, str) else None,
        selected_skill_args=selected_skill_args,
        execution_payload=execution_payload if isinstance(execution_payload, dict) else None,
        learning_capture_payload=learning_capture_payload if isinstance(learning_capture_payload, dict) else None,
    )


def cmd_agent_plan_learning(args: argparse.Namespace) -> int:
    try:
        execution_payload = json.loads(args.execution_json)
        if not isinstance(execution_payload, dict):
            raise ValueError("--execution-json must decode to a JSON object")
        if args.plan_json:
            plan = _build_codex_orchestration_result(json.loads(args.plan_json))
        else:
            request = _build_agent_task_request(args)
            classification = classify_codex_task(request)
            plan = AgentOrchestrationResult(
                request=request,
                reuse_decision=ReuseDecision("skip", "no prior reuse plan was provided"),
                task_classification=classification,
            )
    except (ValueError, json.JSONDecodeError) as exc:
        return error(str(exc), "INVALID_AGENT_PLAN_INPUT", exit_code=EXIT_ARGUMENT_ERROR)

    finalized = finalize_codex_task(Path(args.root).resolve(), plan, execution_payload)
    return ok(asdict(finalized))


def _build_codex_orchestration_result(raw_plan: object) -> AgentOrchestrationResult:
    plan = _build_agent_orchestration_result(raw_plan)
    if not isinstance(raw_plan, dict):
        raise ValueError("--plan-json must decode to a JSON object")
    raw_classification = raw_plan.get("task_classification")
    classification = CodexTaskClassification(**raw_classification) if isinstance(raw_classification, dict) else None
    return AgentOrchestrationResult(
        request=plan.request,
        reuse_decision=plan.reuse_decision,
        learning_decision=plan.learning_decision,
        task_classification=classification,
        runtime_lane_status=plan.runtime_lane_status,
        runtime_lane_reason=plan.runtime_lane_reason,
        selected_skill_name=plan.selected_skill_name,
        selected_skill_args=dict(plan.selected_skill_args),
        execution_payload=plan.execution_payload,
        learning_capture_payload=plan.learning_capture_payload,
    )


def cmd_codex_classify(args: argparse.Namespace) -> int:
    try:
        request = _build_agent_task_request(args)
    except (ValueError, json.JSONDecodeError) as exc:
        return error(str(exc), "INVALID_CODEX_TASK_INPUT", exit_code=EXIT_ARGUMENT_ERROR)
    return ok(asdict(classify_codex_task(request)))


def cmd_codex_run(args: argparse.Namespace) -> int:
    try:
        request = _build_agent_task_request(args)
    except (ValueError, json.JSONDecodeError) as exc:
        return error(str(exc), "INVALID_CODEX_TASK_INPUT", exit_code=EXIT_ARGUMENT_ERROR)

    result = run_codex_task(Path(args.root).resolve(), request)
    return ok(asdict(result))


def cmd_codex_finalize(args: argparse.Namespace) -> int:
    try:
        execution_payload = json.loads(args.execution_json)
        if not isinstance(execution_payload, dict):
            raise ValueError("--execution-json must decode to a JSON object")
        if args.plan_json:
            plan = _build_codex_orchestration_result(json.loads(args.plan_json))
        else:
            request = _build_agent_task_request(args)
            classification = classify_codex_task(request)
            plan = AgentOrchestrationResult(
                request=request,
                reuse_decision=ReuseDecision("skip", classification.reason),
                learning_decision=None,
                task_classification=classification,
            )
    except (ValueError, json.JSONDecodeError) as exc:
        return error(str(exc), "INVALID_CODEX_TASK_INPUT", exit_code=EXIT_ARGUMENT_ERROR)

    finalized = finalize_codex_task(Path(args.root).resolve(), plan, execution_payload)
    return ok(asdict(finalized))


def cmd_distill_and_promote(args: argparse.Namespace) -> int:
    if sum(
        1
        for value in (
            args.trajectory,
            args.observed_task,
            args.observed_task_json,
            args.observed_task_json_file,
        )
        if value
    ) != 1:
        return error(
            "provide exactly one of --trajectory, --observed-task, --observed-task-json, or --observed-task-json-file",
            "INVALID_DISTILL_PROMOTE_INPUT",
            exit_code=EXIT_ARGUMENT_ERROR,
        )

    observed_task = None
    if args.observed_task_json or args.observed_task_json_file:
        try:
            if args.observed_task_json_file:
                observed_task = load_json_file(args.observed_task_json_file)
            else:
                observed_task = json.loads(args.observed_task_json)
        except FileNotFoundError:
            return error(
                "observed task JSON file not found",
                "OBSERVED_TASK_JSON_FILE_NOT_FOUND",
                details={"path": args.observed_task_json_file},
                exit_code=EXIT_NOT_FOUND,
            )
        except json.JSONDecodeError as exc:
            return error(
                "invalid JSON for observed task payload",
                "INVALID_OBSERVED_TASK_JSON",
                details={"reason": str(exc)},
                exit_code=EXIT_ARGUMENT_ERROR,
            )

    try:
        return ok(
            service_for_args(args).distill_and_promote(
                trajectory_path=args.trajectory,
                observed_task_path=args.observed_task,
                observed_task=observed_task,
                skill_name=args.skill_name,
                register_trajectory=not args.skip_log,
                promotion_target=args.promotion_target,
                global_skills_dir=args.global_skills_dir,
                global_skill_name=args.global_skill_name,
                overwrite_global_skill=args.overwrite_global_skill,
            )
        )
    except RuntimeServiceError as exc:
        exit_code = (
            EXIT_NOT_FOUND
            if exc.code in {"TRAJECTORY_NOT_FOUND", "SKILL_FILE_NOT_FOUND", "OBSERVED_TASK_NOT_FOUND"}
            else EXIT_VALIDATION_ERROR
        )
        return error(exc.message, exc.code, exc.details, exit_code=exit_code)


def cmd_dashboard(args: argparse.Namespace) -> int:
    root = Path(args.root).resolve()
    global_view = bool(getattr(args, "global_view", False))
    default_output = root / ".skill_runtime" / ("global-dashboard.html" if global_view else "dashboard.html")
    output_path = Path(args.output) if args.output else default_output
    if not output_path.is_absolute():
        output_path = root / output_path
    output_path.parent.mkdir(parents=True, exist_ok=True)
    data = collect_dashboard_data(root)
    if global_view:
        global_data = collect_global_dashboard_data(root, scan_roots=getattr(args, "scan_root", None))
        data["global"] = global_data
    output_path.write_text(render_dashboard_html(data), encoding="utf-8")
    dashboard_url = output_path.resolve().as_uri()
    opened = bool(webbrowser.open(dashboard_url)) if getattr(args, "open", False) else False
    payload = {
        "output_path": str(output_path.resolve()),
        "dashboard_url": dashboard_url,
        "opened": opened,
        "root": str(root),
        "global": global_view,
        "event_count": len(data["global"]["events"]) if global_view else len(data["events"]),
    }
    if global_view:
        payload["project_count"] = data["global"]["overview"]["project_count"]
        payload["scan_roots"] = data["global"]["scan_roots"]
    payload["active_count"] = data["overview"]["active_count"]
    return ok(payload)


def cmd_platform_export_plan(args: argparse.Namespace) -> int:
    return ok(
        plan_platform_export(
            Path(args.root).resolve(),
            args.skill,
            args.platform,
            target_dir=args.target_dir,
            force_copy=args.copy,
        )
    )


def cmd_import_skill_to_staging(args: argparse.Namespace) -> int:
    try:
        return ok(import_local_skill_to_staging(Path(args.root).resolve(), args.source))
    except SkillImportError as exc:
        return error(exc.message, exc.code, exc.details, exit_code=EXIT_VALIDATION_ERROR)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="skill-runtime")
    parser.add_argument("--root", default=str(ROOT))
    subparsers = parser.add_subparsers(dest="command", required=True)

    search_parser = subparsers.add_parser("search")
    search_parser.add_argument("--query", required=True)
    search_parser.add_argument("--top-k", type=int, default=5)
    search_parser.set_defaults(func=cmd_search)

    execute_parser = subparsers.add_parser("execute")
    execute_parser.add_argument("--skill", required=True)
    execute_parser.add_argument("--args")
    execute_parser.add_argument("--args-file")
    execute_parser.add_argument("--dry-run", action="store_true")
    execute_parser.set_defaults(func=cmd_execute)

    distill_parser = subparsers.add_parser("distill")
    distill_parser.add_argument("--trajectory", required=True)
    distill_parser.add_argument("--skill-name")
    distill_parser.set_defaults(func=cmd_distill)

    distill_promote_parser = subparsers.add_parser("distill-and-promote")
    distill_promote_parser.add_argument("--trajectory")
    distill_promote_parser.add_argument("--observed-task")
    distill_promote_parser.add_argument("--observed-task-json")
    distill_promote_parser.add_argument("--observed-task-json-file")
    distill_promote_parser.add_argument("--skill-name")
    distill_promote_parser.add_argument("--skip-log", action="store_true")
    distill_promote_parser.add_argument(
        "--promotion-target",
        choices=("active", "global-codex", "global_codex"),
        default="active",
    )
    distill_promote_parser.add_argument("--global-skills-dir")
    distill_promote_parser.add_argument("--global-skill-name")
    distill_promote_parser.add_argument("--overwrite-global-skill", action="store_true")
    distill_promote_parser.set_defaults(func=cmd_distill_and_promote)

    audit_parser = subparsers.add_parser("audit")
    audit_parser.add_argument("--file", required=True)
    audit_parser.add_argument("--trajectory")
    audit_parser.set_defaults(func=cmd_audit)

    promote_parser = subparsers.add_parser("promote")
    promote_parser.add_argument("--file", required=True)
    promote_parser.set_defaults(func=cmd_promote)

    promote_global_parser = subparsers.add_parser("promote-global-codex-skill")
    promote_global_parser.add_argument("--file", required=True)
    promote_global_parser.add_argument("--global-skills-dir")
    promote_global_parser.add_argument("--global-skill-name")
    promote_global_parser.add_argument("--overwrite", action="store_true")
    promote_global_parser.set_defaults(func=cmd_promote_global_codex_skill)

    log_parser = subparsers.add_parser("log-trajectory")
    log_parser.add_argument("--file", required=True)
    log_parser.set_defaults(func=cmd_log_trajectory)

    capture_parser = subparsers.add_parser("capture-trajectory")
    capture_parser.add_argument("--file")
    capture_parser.add_argument("--observed-task-json")
    capture_parser.add_argument("--observed-task-json-file")
    capture_parser.add_argument("--task-id")
    capture_parser.add_argument("--session-id")
    capture_parser.set_defaults(func=cmd_capture_trajectory)

    reindex_parser = subparsers.add_parser("reindex")
    reindex_parser.set_defaults(func=cmd_reindex)

    archive_parser = subparsers.add_parser("archive-cold")
    archive_parser.add_argument("--days", type=int, default=30)
    archive_parser.set_defaults(func=cmd_archive_cold)

    backfill_parser = subparsers.add_parser("backfill-provenance")
    backfill_parser.set_defaults(func=cmd_backfill_provenance)

    governance_parser = subparsers.add_parser("governance-report")
    governance_parser.set_defaults(func=cmd_governance_report)

    dashboard_parser = subparsers.add_parser("dashboard")
    dashboard_parser.add_argument("--output")
    dashboard_parser.add_argument("--open", action="store_true", help="Open the generated dashboard in the default browser")
    dashboard_parser.add_argument(
        "--global",
        dest="global_view",
        action="store_true",
        help="Render the normal read-only dashboard plus aggregated runtime lane events across project roots",
    )
    dashboard_parser.add_argument(
        "--scan-root",
        action="append",
        help="Directory whose immediate child projects should be scanned for runtime lane events",
    )
    dashboard_parser.set_defaults(func=cmd_dashboard)

    platform_export_parser = subparsers.add_parser("platform-export-plan")
    platform_export_parser.add_argument("--skill", required=True)
    platform_export_parser.add_argument("--platform", required=True)
    platform_export_parser.add_argument("--target-dir")
    platform_export_parser.add_argument("--copy", action="store_true", help="Plan copy fallback instead of symlink export")
    platform_export_parser.set_defaults(func=cmd_platform_export_plan)

    import_skill_parser = subparsers.add_parser("import-skill-to-staging")
    import_skill_parser.add_argument("--source", required=True)
    import_skill_parser.set_defaults(func=cmd_import_skill_to_staging)

    distill_coverage_parser = subparsers.add_parser("distill-coverage-report")
    distill_coverage_parser.add_argument(
        "--observed-task-scope",
        choices=("all", "backlog", "execution"),
        default="all",
    )
    distill_coverage_parser.add_argument("--max-family-items", type=int)
    distill_coverage_parser.add_argument("--min-family-count", type=int, default=1)
    distill_coverage_parser.set_defaults(func=cmd_distill_coverage_report)

    rollback_parser = subparsers.add_parser("rollback-operations")
    rollback_parser.add_argument("--operation-log")
    rollback_parser.add_argument("--operation-log-file")
    rollback_parser.add_argument("--execute-result-json")
    rollback_parser.add_argument("--execute-result-file")
    rollback_parser.add_argument("--operation-id", action="append")
    rollback_parser.add_argument("--dry-run", action="store_true")
    rollback_parser.set_defaults(func=cmd_rollback_operations)

    archive_duplicates_parser = subparsers.add_parser("archive-duplicate-candidates")
    archive_duplicates_parser.add_argument("--skill-name", action="append")
    archive_duplicates_parser.add_argument("--dry-run", action="store_true")
    archive_duplicates_parser.set_defaults(func=cmd_archive_duplicate_candidates)

    archive_fixture_parser = subparsers.add_parser("archive-fixture-skills")
    archive_fixture_parser.add_argument("--skill-name", action="append")
    archive_fixture_parser.add_argument("--dry-run", action="store_true")
    archive_fixture_parser.set_defaults(func=cmd_archive_fixture_skills)

    agent_plan_parser = subparsers.add_parser("agent-plan")
    agent_plan_parser.add_argument("--task-description", required=True)
    agent_plan_parser.add_argument("--working-directory")
    agent_plan_parser.add_argument("--known-inputs-json")
    agent_plan_parser.add_argument("--expected-outputs-json")
    agent_plan_parser.add_argument("--risk-level", default="medium")
    agent_plan_parser.add_argument("--task-kind", default="workflow")
    agent_plan_parser.add_argument("--disable-silent-reuse", action="store_true")
    agent_plan_parser.add_argument("--disable-learning", action="store_true")
    agent_plan_parser.set_defaults(func=cmd_agent_plan)

    agent_learning_parser = subparsers.add_parser("agent-plan-learning")
    agent_learning_parser.add_argument("--plan-json")
    agent_learning_parser.add_argument("--task-description")
    agent_learning_parser.add_argument("--working-directory")
    agent_learning_parser.add_argument("--known-inputs-json")
    agent_learning_parser.add_argument("--expected-outputs-json")
    agent_learning_parser.add_argument("--risk-level", default="medium")
    agent_learning_parser.add_argument("--task-kind", default="workflow")
    agent_learning_parser.add_argument("--disable-silent-reuse", action="store_true")
    agent_learning_parser.add_argument("--disable-learning", action="store_true")
    agent_learning_parser.add_argument("--execution-json", required=True)
    agent_learning_parser.set_defaults(func=cmd_agent_plan_learning)

    codex_classify_parser = subparsers.add_parser("codex-classify")
    codex_classify_parser.add_argument("--task-description", required=True)
    codex_classify_parser.add_argument("--working-directory")
    codex_classify_parser.add_argument("--known-inputs-json")
    codex_classify_parser.add_argument("--expected-outputs-json")
    codex_classify_parser.add_argument("--risk-level", default="medium")
    codex_classify_parser.add_argument("--task-kind", default="workflow")
    codex_classify_parser.add_argument("--disable-silent-reuse", action="store_true")
    codex_classify_parser.add_argument("--disable-learning", action="store_true")
    codex_classify_parser.set_defaults(func=cmd_codex_classify)

    codex_run_parser = subparsers.add_parser("codex-run")
    codex_run_parser.add_argument("--task-description", required=True)
    codex_run_parser.add_argument("--working-directory")
    codex_run_parser.add_argument("--known-inputs-json")
    codex_run_parser.add_argument("--expected-outputs-json")
    codex_run_parser.add_argument("--risk-level", default="medium")
    codex_run_parser.add_argument("--task-kind", default="workflow")
    codex_run_parser.add_argument("--disable-silent-reuse", action="store_true")
    codex_run_parser.add_argument("--disable-learning", action="store_true")
    codex_run_parser.set_defaults(func=cmd_codex_run)

    codex_finalize_parser = subparsers.add_parser("codex-finalize")
    codex_finalize_parser.add_argument("--plan-json")
    codex_finalize_parser.add_argument("--task-description")
    codex_finalize_parser.add_argument("--working-directory")
    codex_finalize_parser.add_argument("--known-inputs-json")
    codex_finalize_parser.add_argument("--expected-outputs-json")
    codex_finalize_parser.add_argument("--risk-level", default="medium")
    codex_finalize_parser.add_argument("--task-kind", default="workflow")
    codex_finalize_parser.add_argument("--disable-silent-reuse", action="store_true")
    codex_finalize_parser.add_argument("--disable-learning", action="store_true")
    codex_finalize_parser.add_argument("--execution-json", required=True)
    codex_finalize_parser.set_defaults(func=cmd_codex_finalize)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        return args.func(args)
    except Exception as exc:
        return error(
            "unhandled runtime error",
            "UNHANDLED_EXCEPTION",
            details={"reason": str(exc)},
            exit_code=EXIT_RUNTIME_ERROR,
        )


__all__ = [
    "EXIT_ARGUMENT_ERROR",
    "EXIT_NOT_FOUND",
    "EXIT_OK",
    "EXIT_POLICY_BLOCKED",
    "EXIT_RUNTIME_ERROR",
    "EXIT_VALIDATION_ERROR",
    "ROOT",
    "build_parser",
    "extract_execute_data",
    "extract_rollback_request",
    "load_json_arg",
    "load_json_file",
    "main",
    "service_for_args",
]


if __name__ == "__main__":
    raise SystemExit(main())
