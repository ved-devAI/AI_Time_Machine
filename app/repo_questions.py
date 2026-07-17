"""Deterministic, evidence-grounded questions for ordinary repositories."""

from __future__ import annotations

from collections import Counter
from itertools import combinations
from typing import Any

from app.analysis import AnalysisError
from app.git_ingest import NOT_RECORDED


QUESTIONS = [
    {
        "id": "recent-changes",
        "question": "What changed recently?",
        "short_label": "Summarize recent changes",
    },
    {
        "id": "files-change-together",
        "question": "Which files change together?",
        "short_label": "Find connected files",
    },
    {
        "id": "branch-problem-history",
        "question": "What parts of this branch have caused problems before?",
        "short_label": "Review problem history",
    },
    {
        "id": "missing-rationale",
        "question": "Where is engineering rationale missing?",
        "short_label": "Find missing rationale",
    },
]

QUESTION_BY_ID = {item["id"]: item for item in QUESTIONS}


def _events_with_files(timeline: dict[str, Any]) -> list[dict[str, Any]]:
    return [event for event in timeline["events"] if event["files"]]


def _citation(event: dict[str, Any], claim: str, paths: list[str] | None = None) -> dict[str, Any]:
    event_paths = [item["path"] for item in event["files"]]
    selected_paths = [path for path in (paths or event_paths[:1]) if path in event_paths]
    return {
        "event_id": event["id"],
        "claim": claim,
        "evidence_refs": [event["short_hash"], *selected_paths],
    }


def _base_answer(question_id: str) -> dict[str, Any]:
    question = QUESTION_BY_ID[question_id]
    return {
        "question_id": question_id,
        "question": question["question"],
        "source": "local-evidence-engine",
        "model": None,
        "delivery": "deterministic",
    }


def _recent_answer(timeline: dict[str, Any]) -> dict[str, Any]:
    recent = _events_with_files(timeline)[-3:]
    if not recent:
        return {
            **_base_answer("recent-changes"),
            "headline": "Git records commits but no changed files",
            "answer": "The selected history does not contain diff-derived file evidence to summarize.",
            "certainty": "missing-evidence",
            "confidence": 1.0,
            "evidence": [],
            "missing_evidence": ["No commit in the selected history records a changed file."],
        }
    titles = "; ".join(f"{event['short_hash']} {event['title']}" for event in recent)
    return {
        **_base_answer("recent-changes"),
        "headline": f"The latest {len(recent)} file-changing commits define the current direction",
        "answer": f"In chronological order, the recent Git evidence is: {titles}.",
        "certainty": "confirmed",
        "confidence": 0.99,
        "evidence": [
            _citation(
                event,
                f"Commit {event['short_hash']} changed {len(event['files'])} file(s): {event['title']}.",
            )
            for event in recent
        ],
        "missing_evidence": [
            "Git confirms what changed, but unrecorded product intent cannot be reconstructed."
        ],
    }


def _cochange_answer(timeline: dict[str, Any]) -> dict[str, Any]:
    events = _events_with_files(timeline)
    pair_counts: Counter[tuple[str, str]] = Counter()
    for event in events:
        paths = sorted({item["path"] for item in event["files"]})
        pair_counts.update(combinations(paths, 2))

    if pair_counts:
        pair, count = sorted(pair_counts.items(), key=lambda item: (-item[1], item[0]))[0]
        supporting = [
            event
            for event in events
            if set(pair).issubset({item["path"] for item in event["files"]})
        ][-3:]
        return {
            **_base_answer("files-change-together"),
            "headline": f"{pair[0]} and {pair[1]} are the strongest observed pair",
            "answer": (
                f"These files appear together in {count} commit(s). This is an observed overlap, "
                "not proof that they must always change together."
            ),
            "certainty": "inferred",
            "confidence": min(0.95, 0.68 + count * 0.08),
            "evidence": [
                _citation(event, "This commit changed both files.", list(pair))
                for event in supporting
            ],
            "missing_evidence": [
                "Co-change frequency does not prove an architectural dependency."
            ],
        }

    if events:
        event = events[-1]
        path = event["files"][0]["path"]
        return {
            **_base_answer("files-change-together"),
            "headline": "No repeated file pair is recorded yet",
            "answer": f"The available history does not establish a recurring pair; {path} is the latest file evidence.",
            "certainty": "missing-evidence",
            "confidence": 1.0,
            "evidence": [_citation(event, "This is the latest file-changing commit.", [path])],
            "missing_evidence": ["At least one multi-file commit is needed to observe co-change."],
        }
    return {
        **_base_answer("files-change-together"),
        "headline": "No file-overlap evidence is available",
        "answer": "The selected history contains no changed files to compare.",
        "certainty": "missing-evidence",
        "confidence": 1.0,
        "evidence": [],
        "missing_evidence": ["Git does not record changed files in the selected history."],
    }


def _problem_answer(
    timeline: dict[str, Any], context: dict[str, Any] | None
) -> dict[str, Any]:
    event_by_id = {event["id"]: event for event in timeline["events"]}
    context_items = (context or {}).get("connected_incidents_and_fixes", [])
    contextual_problems = [
        (event_by_id[item["event_id"]], item.get("files", []))
        for item in context_items
        if item["event_id"] in event_by_id
    ]
    problems = [item[0] for item in contextual_problems]
    branch_specific = bool(contextual_problems)
    if not problems:
        problems = [
            event
            for event in timeline["events"]
            if event["type"] in {"bug", "fix", "rollback"} and event["files"]
        ][-3:]

    if problems:
        scope = "Files changed in this range" if branch_specific else "Repository-wide history"
        return {
            **_base_answer("branch-problem-history"),
            "headline": f"{scope} has {len(problems)} relevant incident or fix event(s)",
            "answer": "Git overlap connects the reviewed files to: "
            + "; ".join(f"{event['short_hash']} {event['title']}" for event in problems)
            + ".",
            "certainty": "confirmed" if branch_specific else "missing-evidence",
            "confidence": 0.97 if branch_specific else 0.82,
            "evidence": [
                _citation(
                    event,
                    f"This {event['type']} event touched reviewed history.",
                    contextual_problems[index][1] if branch_specific else None,
                )
                for index, event in enumerate(problems)
            ],
            "missing_evidence": ([] if branch_specific else [
                "No incident or fix overlaps the selected branch range; these are repository-wide signals."
            ]),
        }

    recent = _events_with_files(timeline)[-1:]
    return {
        **_base_answer("branch-problem-history"),
        "headline": "No incident or fix classification overlaps this branch",
        "answer": "The available Git metadata does not record prior problem events for the reviewed files.",
        "certainty": "missing-evidence",
        "confidence": 1.0,
        "evidence": [
            _citation(recent[0], "This is the latest available file evidence, not a recorded problem.")
        ] if recent else [],
        "missing_evidence": [
            "Conventional bug/fix metadata or explicit incident records are absent for this scope."
        ],
    }


def _rationale_answer(timeline: dict[str, Any]) -> dict[str, Any]:
    missing = [
        event
        for event in timeline["events"]
        if event["why"] == NOT_RECORDED and event["files"]
    ][-3:]
    if missing:
        return {
            **_base_answer("missing-rationale"),
            "headline": f"{len(missing)} recent file-changing commits do not record why",
            "answer": "These commits preserve subject and diff evidence, but their engineering rationale is not recorded: "
            + "; ".join(f"{event['short_hash']} {event['title']}" for event in missing)
            + ".",
            "certainty": "confirmed",
            "confidence": 1.0,
            "evidence": [
                _citation(event, "This commit has file evidence but no recorded Why field.")
                for event in missing
            ],
            "missing_evidence": [
                "The reason cannot be inferred safely from the commit subject or diff alone."
            ],
        }
    recent = _events_with_files(timeline)[-1:]
    return {
        **_base_answer("missing-rationale"),
        "headline": "Structured rationale is present in the selected history",
        "answer": "No file-changing commit in the selected history is missing its recorded Why field.",
        "certainty": "confirmed",
        "confidence": 1.0,
        "evidence": [
            _citation(recent[0], "This recent commit includes recorded rationale.")
        ] if recent else [],
        "missing_evidence": [],
    }


def validate_answer(answer: dict[str, Any], timeline: dict[str, Any]) -> dict[str, Any]:
    question_id = answer.get("question_id")
    if question_id not in QUESTION_BY_ID:
        raise AnalysisError("The repository answer used an unsupported question.")
    if answer.get("question") != QUESTION_BY_ID[question_id]["question"]:
        raise AnalysisError("The repository answer changed the supported question text.")
    if answer.get("source") != "local-evidence-engine" or answer.get("model") is not None:
        raise AnalysisError("The deterministic repository answer source was invalid.")
    confidence = answer.get("confidence")
    if not isinstance(confidence, (int, float)) or not 0 <= confidence <= 1:
        raise AnalysisError("The repository answer confidence was invalid.")
    if answer.get("certainty") not in {"confirmed", "inferred", "missing-evidence"}:
        raise AnalysisError("The repository answer certainty was invalid.")
    if not isinstance(answer.get("answer"), str) or not answer["answer"].strip():
        raise AnalysisError("The repository answer was empty.")

    event_by_id = {event["id"]: event for event in timeline["events"]}
    citations = answer.get("evidence")
    if not isinstance(citations, list):
        raise AnalysisError("The repository answer evidence was invalid.")
    if not citations and answer["certainty"] != "missing-evidence":
        raise AnalysisError("A supported repository answer had no evidence.")
    for citation in citations:
        event = event_by_id.get(citation.get("event_id"))
        if event is None:
            raise AnalysisError("The repository answer referenced an unknown event.")
        refs = citation.get("evidence_refs")
        paths = {item["path"] for item in event["files"]}
        allowed = {event["short_hash"], event["commit_hash"], *paths}
        if (
            not isinstance(refs, list)
            or event["short_hash"] not in refs
            or not paths.intersection(refs)
            or any(ref not in allowed for ref in refs)
        ):
            raise AnalysisError("The repository answer citation was not grounded in its event.")
    return answer


def answer_question(
    timeline: dict[str, Any],
    question_id: str,
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if question_id not in QUESTION_BY_ID:
        raise AnalysisError("That repository question is not supported.")
    answer = {
        "recent-changes": lambda: _recent_answer(timeline),
        "files-change-together": lambda: _cochange_answer(timeline),
        "branch-problem-history": lambda: _problem_answer(timeline, context),
        "missing-rationale": lambda: _rationale_answer(timeline),
    }[question_id]()
    return validate_answer(answer, timeline)
