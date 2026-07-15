#!/usr/bin/env python3
"""Score the committed AI Time Machine artifacts against grounding expectations."""

from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path
from typing import Callable


ROOT = Path(__file__).resolve().parents[1]
ORBITCART = ROOT / ".data" / "orbitcart"
FIXTURE = ROOT / "evaluations" / "orbitcart_grounding.json"
TRACE_ARTIFACT = ROOT / "artifacts" / "orbitcart" / "bug-origin.codex.json"
ASK_ARTIFACT = ROOT / "artifacts" / "orbitcart" / "ask-repo.codex.json"

sys.path.insert(0, str(ROOT))

from app.analysis import AnalysisError, load_codex_artifact, validate_analysis  # noqa: E402
from app.ask_repo import load_answer_artifact, validate_answer_set  # noqa: E402
from app.git_ingest import read_timeline  # noqa: E402


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def expect_rejection(action: Callable[[], object]) -> None:
    try:
        action()
    except (AnalysisError, KeyError, TypeError, json.JSONDecodeError):
        return
    raise AssertionError("Invalid evidence was accepted.")


def run_evaluation() -> dict:
    timeline = read_timeline(ORBITCART)
    fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
    trace = load_codex_artifact(timeline, TRACE_ARTIFACT)
    answer_set = load_answer_artifact(timeline, ASK_ARTIFACT)
    checks: list[dict[str, str]] = []

    def check(name: str, action: Callable[[], object]) -> None:
        try:
            action()
            checks.append({"name": name, "status": "pass"})
        except (AssertionError, AnalysisError, KeyError, TypeError, json.JSONDecodeError) as exc:
            checks.append({"name": name, "status": "fail", "detail": str(exc)})

    trace_expected = fixture["bug_origin_trace"]
    check(
        "trace uses validated GPT-5.6 Codex artifact",
        lambda: require(trace["source"] == "codex-gpt-5.6", "Trace source was not Codex."),
    )
    check(
        "trace identifies expected origin and trigger",
        lambda: require(
            (trace["origin_event_id"], trace["trigger_event_id"])
            == (trace_expected["origin_event_id"], trace_expected["trigger_event_id"]),
            "Trace origin or trigger changed.",
        ),
    )
    check(
        "trace preserves six-stage causal order",
        lambda: require(
            [item["role"] for item in trace["causal_chain"]] == trace_expected["roles"],
            "Trace causal roles changed.",
        ),
    )
    check(
        "trace cites the expected event sequence",
        lambda: require(
            [item["event_id"] for item in trace["causal_chain"]] == trace_expected["event_ids"],
            "Trace evidence sequence changed.",
        ),
    )
    check(
        "trace certainty remains calibrated",
        lambda: require(
            trace["certainty"] == trace_expected["certainty"]
            and trace["confidence"] >= trace_expected["minimum_confidence"],
            "Trace certainty or confidence regressed.",
        ),
    )

    answers = {answer["question_id"]: answer for answer in answer_set["answers"]}
    for question_id, expected in fixture["ask_repo"].items():
        answer = answers[question_id]
        check(
            f"{question_id} uses calibrated certainty",
            lambda answer=answer, expected=expected: require(
                answer["certainty"] == expected["certainty"]
                and answer["confidence"] >= expected["minimum_confidence"],
                "Answer certainty or confidence regressed.",
            ),
        )
        check(
            f"{question_id} cites required events",
            lambda answer=answer, expected=expected: require(
                set(expected["required_event_ids"])
                <= {item["event_id"] for item in answer["evidence"]},
                "A required evidence event is missing.",
            ),
        )

    trace_payload = copy.deepcopy(trace)
    trace_payload.pop("provenance", None)
    for key in ["source", "model", "delivery", "generated_at"]:
        trace_payload.pop(key, None)
    invalid_trace_ref = copy.deepcopy(trace_payload)
    invalid_trace_ref["causal_chain"][0]["evidence_refs"] = ["invented.py"]
    check(
        "validator rejects invented trace evidence",
        lambda: expect_rejection(lambda: validate_analysis(invalid_trace_ref, timeline)),
    )

    incomplete_trace = copy.deepcopy(trace_payload)
    incomplete_trace["causal_chain"].pop()
    check(
        "validator rejects incomplete causal chain",
        lambda: expect_rejection(lambda: validate_analysis(incomplete_trace, timeline)),
    )

    answer_payload = {"answers": copy.deepcopy(answer_set["answers"])}
    unknown_event = copy.deepcopy(answer_payload)
    unknown_event["answers"][0]["evidence"][0]["event_id"] = "event-invented"
    check(
        "validator rejects invented answer event",
        lambda: expect_rejection(lambda: validate_answer_set(unknown_event, timeline)),
    )

    cross_event_file = copy.deepcopy(answer_payload)
    cross_event_file["answers"][0]["evidence"][0]["evidence_refs"][1] = "tests/test_pricing.py"
    check(
        "validator rejects cross-event file citation",
        lambda: expect_rejection(lambda: validate_answer_set(cross_event_file, timeline)),
    )

    total = len(checks)
    passed = sum(item["status"] == "pass" for item in checks)
    return {
        "evaluation_version": fixture["evaluation_version"],
        "project_id": fixture["project_id"],
        "evidence_sha256": trace["provenance"]["evidence_sha256"],
        "score": round(passed / total * 100, 1),
        "passed": passed,
        "total": total,
        "status": "pass" if passed == total else "fail",
        "checks": checks,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", type=Path, help="Write the deterministic JSON report")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    report = run_evaluation()
    if args.write:
        path = args.write.resolve()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"Grounding score: {report['score']:.1f}% ({report['passed']}/{report['total']} checks)")
    for item in report["checks"]:
        marker = "PASS" if item["status"] == "pass" else "FAIL"
        detail = f" — {item['detail']}" if item.get("detail") else ""
        print(f"[{marker}] {item['name']}{detail}")
    if report["status"] != "pass":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
