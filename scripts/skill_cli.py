import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from skill_runtime.api.service import RuntimeService, RuntimeServiceError


EXIT_OK = 0
EXIT_RUNTIME_ERROR = 1
EXIT_ARGUMENT_ERROR = 2
EXIT_NOT_FOUND = 3
EXIT_VALIDATION_ERROR = 4
EXIT_POLICY_BLOCKED = 5


def service_for_args(args: argparse.Namespace) -> RuntimeService:
    return RuntimeService(Path(args.root).resolve())


def load_json_file(path: str) -> object:
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


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
        return ok(service_for_args(args).execute(args.skill, parsed_args))
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


def cmd_archive_duplicate_candidates(args: argparse.Namespace) -> int:
    return ok(service_for_args(args).archive_duplicate_candidates(skill_names=args.skill_name, dry_run=args.dry_run))


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
            )
        )
    except RuntimeServiceError as exc:
        exit_code = (
            EXIT_NOT_FOUND
            if exc.code in {"TRAJECTORY_NOT_FOUND", "SKILL_FILE_NOT_FOUND", "OBSERVED_TASK_NOT_FOUND"}
            else EXIT_VALIDATION_ERROR
        )
        return error(exc.message, exc.code, exc.details, exit_code=exit_code)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="skill_cli")
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
    distill_promote_parser.set_defaults(func=cmd_distill_and_promote)

    audit_parser = subparsers.add_parser("audit")
    audit_parser.add_argument("--file", required=True)
    audit_parser.add_argument("--trajectory")
    audit_parser.set_defaults(func=cmd_audit)

    promote_parser = subparsers.add_parser("promote")
    promote_parser.add_argument("--file", required=True)
    promote_parser.set_defaults(func=cmd_promote)

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

    distill_coverage_parser = subparsers.add_parser("distill-coverage-report")
    distill_coverage_parser.add_argument(
        "--observed-task-scope",
        choices=("all", "backlog", "execution"),
        default="all",
    )
    distill_coverage_parser.add_argument("--max-family-items", type=int)
    distill_coverage_parser.add_argument("--min-family-count", type=int, default=1)
    distill_coverage_parser.set_defaults(func=cmd_distill_coverage_report)

    archive_duplicates_parser = subparsers.add_parser("archive-duplicate-candidates")
    archive_duplicates_parser.add_argument("--skill-name", action="append")
    archive_duplicates_parser.add_argument("--dry-run", action="store_true")
    archive_duplicates_parser.set_defaults(func=cmd_archive_duplicate_candidates)

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


if __name__ == "__main__":
    raise SystemExit(main())
