import argparse
import json
import sys
import time
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


class TimingResult(unittest.TextTestResult):
    def __init__(self, *args, top: int = 20, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.top = top
        self._started_at = 0.0
        self.timings: list[tuple[float, str]] = []

    def startTest(self, test) -> None:
        self._started_at = time.perf_counter()
        super().startTest(test)

    def stopTest(self, test) -> None:
        elapsed = time.perf_counter() - self._started_at
        self.timings.append((elapsed, test.id()))
        super().stopTest(test)

    def stopTestRun(self) -> None:
        super().stopTestRun()
        self.stream.writeln("")
        self.stream.writeln(f"Top {self.top} slowest runtime tests:")
        for elapsed, test_id in sorted(self.timings, reverse=True)[: self.top]:
            self.stream.writeln(f"{elapsed:8.2f}s  {test_id}")


class TimingRunner(unittest.TextTestRunner):
    resultclass = TimingResult

    def __init__(self, *args, top: int = 20, **kwargs) -> None:
        self.top = top
        super().__init__(*args, **kwargs)

    def _makeResult(self):
        return self.resultclass(
            self.stream,
            self.descriptions,
            self.verbosity,
            top=self.top,
        )


def timing_payload(
    *,
    timings: list[tuple[float, str]],
    top: int,
    tests_run: int,
    total_elapsed: float,
    successful: bool,
) -> dict:
    return {
        "successful": successful,
        "tests_run": tests_run,
        "total_elapsed_seconds": round(total_elapsed, 4),
        "slowest_tests": [
            {
                "test_id": test_id,
                "elapsed_seconds": round(elapsed, 4),
            }
            for elapsed, test_id in sorted(timings, reverse=True)[:top]
        ],
    }


def write_timing_json_report(
    output_path: str | Path,
    *,
    timings: list[tuple[float, str]],
    top: int,
    tests_run: int,
    total_elapsed: float,
    successful: bool,
) -> dict:
    payload = timing_payload(
        timings=timings,
        top=top,
        tests_run=tests_run,
        total_elapsed=total_elapsed,
        successful=successful,
    )
    target = Path(output_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the runtime suite and print the slowest tests.")
    parser.add_argument(
        "--suite",
        default="tests.test_runtime",
        help="unittest suite name to profile, for example tests.test_runtime_fast",
    )
    parser.add_argument("--top", type=int, default=20, help="number of slow tests to print")
    parser.add_argument("--json-output", help="optional path to write a machine-readable timing report")
    args = parser.parse_args()

    suite = unittest.defaultTestLoader.loadTestsFromName(args.suite)
    started_at = time.perf_counter()
    result = TimingRunner(verbosity=2, top=args.top).run(suite)
    total_elapsed = time.perf_counter() - started_at
    if args.json_output:
        write_timing_json_report(
            args.json_output,
            timings=result.timings,
            top=args.top,
            tests_run=result.testsRun,
            total_elapsed=total_elapsed,
            successful=result.wasSuccessful(),
        )
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
