"""
Phase 4 entrypoint: run scenarios sequentially.

Three modes:
  all      — Run every (category, variant) once.
  scenario — Run all variants of one category once (e.g. --scenario scheduling).
  task     — Run one (category, variant) N times (e.g. --scenario office_info --variant 0 --runs 2).

Wait rule: after each call, wait for transcripts/<call_id>.json up to --max-wait minutes (default 16).
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path
from typing import Any, List, Optional, Tuple

from scenario_manager import (
    ScenarioConfig,
    build_prompt,
    get_scenario,
    list_categories,
    list_scenarios,
)
from storage import (
    REPORTS_DIR,
    TRANSCRIPTS_DIR,
    load_transcript,
    patch_transcript_recording_url,
    patch_transcript_scenario,
    save_evaluation_report,
)
from evaluator import evaluate_transcript_file
from vapi_client import get_recording_url, start_call

# Defaults
DEFAULT_MAX_WAIT_MINUTES = 16
DEFAULT_POLL_INTERVAL_SEC = 10
DEFAULT_DELAY_BETWEEN_CALLS_SEC = 15


def _call_id_from_response(result: Any) -> Optional[str]:
    """Extract call id from Vapi create call response."""
    if result is None:
        return None
    if hasattr(result, "id"):
        return getattr(result, "id")
    if isinstance(result, dict):
        return result.get("id")
    if hasattr(result, "model_dump"):
        return result.model_dump().get("id")
    return None


def wait_for_transcript(
    call_id: str,
    transcripts_dir: Path,
    max_wait_minutes: float = DEFAULT_MAX_WAIT_MINUTES,
    poll_interval_sec: float = DEFAULT_POLL_INTERVAL_SEC,
) -> Optional[Path]:
    """
    Poll for transcripts/<call_id>.json until it exists or max_wait_minutes elapsed.
    Returns the Path if file appeared, None on timeout.
    """
    path = transcripts_dir / f"{call_id}.json"
    deadline = time.monotonic() + max_wait_minutes * 60
    while time.monotonic() < deadline:
        if path.exists():
            return path
        time.sleep(poll_interval_sec)
    return None


def build_run_list(
    mode: str,
    scenario_category: Optional[str],
    variant: Optional[int],
    runs: int,
) -> List[Tuple[ScenarioConfig, int]]:
    """
    Build list of (ScenarioConfig, run_index) for the given mode.
    run_index is 1-based for display (run 1 of N).
    """
    out: List[Tuple[ScenarioConfig, int]] = []
    if mode == "all":
        for cat in list_categories():
            scenarios = list_scenarios(cat)
            for sc in scenarios:
                out.append((sc, 1))
    elif mode == "scenario":
        if not scenario_category:
            raise ValueError("--scenario required for mode 'scenario'")
        scenarios = list_scenarios(scenario_category)
        for sc in scenarios:
            out.append((sc, 1))
    elif mode == "task":
        if not scenario_category:
            raise ValueError("--scenario required for mode 'task'")
        if variant is None:
            raise ValueError("--variant required for mode 'task'")
        sc = get_scenario(scenario_category, variant)
        for run_index in range(1, runs + 1):
            out.append((sc, run_index))
    else:
        raise ValueError(f"Unknown mode: {mode}")
    return out


def run_one(
    scenario: ScenarioConfig,
    run_index: int,
    position: int,
    total: int,
    max_wait_minutes: float,
    poll_interval_sec: float,
    dry_run: bool,
) -> Tuple[bool, Optional[str], Optional[Path]]:
    """
    Start one call, wait for transcript, patch scenario metadata.
    position = 1-based index in run list (for display). run_index = for scenario metadata (e.g. run 2 of 3).
    Returns (success, call_id, transcript_path).
    """
    prompt = build_prompt(scenario)
    first_message = scenario.first_message
    label = f"{scenario.category} variant {scenario.variant}" + (
        f" run {run_index}" if total > 1 else ""
    )
    print(f"[{position}/{total}] {label} — {scenario.name}")

    if dry_run:
        print("  (dry-run, skipping)")
        return True, None, None

    try:
        result = start_call(
            system_prompt=prompt,
            first_message=first_message,
        )
    except Exception as e:
        print(f"  FAILED to start call: {e}")
        return False, None, None

    call_id = _call_id_from_response(result)
    if not call_id:
        print("  FAILED: no call_id in response")
        return False, None, None

    print(f"  call_id={call_id}, waiting up to {max_wait_minutes:.0f} min for transcript...")
    path = wait_for_transcript(
        call_id,
        TRANSCRIPTS_DIR,
        max_wait_minutes=max_wait_minutes,
        poll_interval_sec=poll_interval_sec,
    )

    if path is None:
        print(f"  TIMEOUT — no transcript after {max_wait_minutes:.0f} min")
        return False, call_id, None

    print(f"  transcript saved: {path.name}")
    try:
        patch_transcript_scenario(
            path,
            scenario_id=scenario.id,
            category=scenario.category,
            name=scenario.name,
            run_index=run_index,
        )
    except Exception as e:
        print(f"  WARN: could not patch scenario metadata: {e}")
    # If webhook did not include recording URL, fetch from Vapi API (per docs: GET call returns artifact.recording)
    try:
        data = load_transcript(path)
        if not (data.get("artifact") or {}).get("recording_url") and call_id:
            recording_url = get_recording_url(call_id)
            if recording_url:
                patch_transcript_recording_url(path, recording_url)
                print(f"  recording_url set from API")
    except Exception as e:
        print(f"  WARN: could not fetch recording URL: {e}")
    # Run evaluation (LLM judge) and save report to reports/<call_id>.json
    try:
        report = evaluate_transcript_file(str(path))
        if report and call_id:
            save_evaluation_report(call_id, report)
            print(f"  evaluation saved: {REPORTS_DIR / f'{call_id}.json'}")
    except Exception as e:
        print(f"  WARN: could not run evaluation: {e}")
    return True, call_id, path


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run scenario calls sequentially (Phase 4).",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--mode",
        choices=["all", "scenario", "task"],
        default="all",
        help="all = every (category,variant) once; scenario = all variants of one category; task = one (category,variant) N times",
    )
    parser.add_argument(
        "--scenario",
        metavar="CATEGORY",
        help="Category for mode 'scenario' or 'task' (e.g. scheduling, office_info)",
    )
    parser.add_argument(
        "--variant",
        type=int,
        metavar="N",
        help="Variant index for mode 'task' (e.g. 0, 1, 2)",
    )
    parser.add_argument(
        "--runs",
        type=int,
        default=2,
        metavar="N",
        help="Number of runs for mode 'task'",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print run list and skip actual calls",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=DEFAULT_DELAY_BETWEEN_CALLS_SEC,
        metavar="SEC",
        help="Seconds to wait between calls (0 to disable)",
    )
    parser.add_argument(
        "--max-wait",
        type=float,
        default=DEFAULT_MAX_WAIT_MINUTES,
        metavar="MIN",
        help="Max minutes to wait for transcript file per call",
    )
    parser.add_argument(
        "--poll-interval",
        type=float,
        default=DEFAULT_POLL_INTERVAL_SEC,
        metavar="SEC",
        help="Poll interval when waiting for transcript",
    )
    args = parser.parse_args()

    try:
        run_list = build_run_list(
            args.mode,
            args.scenario,
            args.variant,
            args.runs,
        )
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    if not run_list:
        print("No runs to execute.")
        return 0

    total = len(run_list)
    print(f"Phase 4: {total} run(s), mode={args.mode}")
    if args.dry_run:
        print("DRY RUN — no calls will be made")
    print()

    succeeded = 0
    failed = 0
    for i, (scenario, run_index) in enumerate(run_list):
        position = i + 1  # 1-based for display (e.g. "Run 3/15")
        ok, call_id, path = run_one(
            scenario,
            run_index,
            position,
            total,
            max_wait_minutes=args.max_wait,
            poll_interval_sec=args.poll_interval,
            dry_run=args.dry_run,
        )
        if ok:
            succeeded += 1
        else:
            failed += 1

        if not args.dry_run and args.delay > 0 and i < total - 1:
            print(f"  waiting {args.delay:.0f} s before next call...")
            time.sleep(args.delay)

    print()
    print("Summary:")
    print(f"  Started: {total}")
    print(f"  Succeeded: {succeeded}")
    print(f"  Failed/timeout: {failed}")
    print(f"  Transcripts: {TRANSCRIPTS_DIR}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
