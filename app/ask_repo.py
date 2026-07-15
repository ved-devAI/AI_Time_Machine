"""Evidence-grounded answers for the three judge-facing repository questions."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.analysis import AnalysisError, evidence_digest


QUESTIONS = [
    {
        "id": "pricing-complexity",
        "question": "Why is pricing complicated?",
        "short_label": "Explain pricing complexity",
    },
    {
        "id": "stale-price-origin",
        "question": "When was the stale-price bug introduced?",
        "short_label": "Find the stale-price origin",
    },
    {
        "id": "change-risk",
        "question": "What would be risky to change now?",
        "short_label": "Map current change risk",
    },
]

QUESTION_BY_ID = {item["id"]: item for item in QUESTIONS}

ASK_REPO_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "answers": {
            "type": "array",
            "minItems": 3,
            "maxItems": 3,
            "items": {
                "type": "object",
                "properties": {
                    "question_id": {"type": "string", "enum": [item["id"] for item in QUESTIONS]},
                    "question": {"type": "string"},
                    "headline": {"type": "string"},
                    "answer": {"type": "string"},
                    "certainty": {
                        "type": "string",
                        "enum": ["confirmed", "inferred", "missing-evidence"],
                    },
                    "confidence": {"type": "number", "minimum": 0, "maximum": 1},
                    "evidence": {
                        "type": "array",
                        "minItems": 1,
                        "items": {
                            "type": "object",
                            "properties": {
                                "event_id": {"type": "string"},
                                "claim": {"type": "string"},
                                "evidence_refs": {
                                    "type": "array",
                                    "minItems": 2,
                                    "items": {"type": "string"},
                                },
                            },
                            "required": ["event_id", "claim", "evidence_refs"],
                            "additionalProperties": False,
                        },
                    },
                    "missing_evidence": {"type": "array", "items": {"type": "string"}},
                },
                "required": [
                    "question_id",
                    "question",
                    "headline",
                    "answer",
                    "certainty",
                    "confidence",
                    "evidence",
                    "missing_evidence",
                ],
                "additionalProperties": False,
            },
        }
    },
    "required": ["answers"],
    "additionalProperties": False,
}


def _find(timeline: dict[str, Any], phrase: str) -> dict[str, Any]:
    lowered = phrase.lower()
    try:
        return next(
            event
            for event in timeline["events"]
            if lowered in f"{event['title']} {event['summary']} {event['why']}".lower()
        )
    except StopIteration as exc:
        raise AnalysisError(f"Required Ask the Repo evidence not found: {phrase}") from exc


def _citation(event: dict[str, Any], claim: str) -> dict[str, Any]:
    return {
        "event_id": event["id"],
        "claim": claim,
        "evidence_refs": [event["short_hash"], event["files"][0]["path"]],
    }


def deterministic_answers(timeline: dict[str, Any]) -> dict[str, Any]:
    """Return a safe fallback derived only from the curated Git timeline."""

    promotions = _find(timeline, "promotional codes")
    timezone = _find(timeline, "timezone expiry")
    centralize = _find(timeline, "centralize totals")
    pressure = _find(timeline, "pricing latency")
    origin = _find(timeline, "cache product prices")
    symptom = _find(timeline, "stale checkout prices")
    resolution = _find(timeline, "catalog version")
    verification = _find(timeline, "stale price regression")

    return {
        "answers": [
            {
                "question_id": "pricing-complexity",
                "question": QUESTION_BY_ID["pricing-complexity"]["question"],
                "headline": "Pricing accumulated policy, time, performance, and correctness constraints",
                "answer": (
                    "Pricing began as a simple total, then promotions introduced combination rules, "
                    "campaign expiry introduced time semantics, and centralization made one module "
                    "responsible for every checkout. That clearer architecture also concentrated "
                    "latency and correctness risk in the same path."
                ),
                "certainty": "confirmed",
                "confidence": 0.97,
                "evidence": [
                    _citation(promotions, "Promotion codes added combination-policy complexity."),
                    _citation(timezone, "Campaign expiry added timezone-sensitive behavior."),
                    _citation(centralize, "Pricing became a critical dependency for every checkout."),
                    _citation(pressure, "Centralized pricing later exposed repeated-work latency."),
                ],
                "missing_evidence": ["The repository does not quantify the maintenance cost of each rule."],
            },
            {
                "question_id": "stale-price-origin",
                "question": QUESTION_BY_ID["stale-price-origin"]["question"],
                "headline": "The stale-price bug most likely began in the March 27 cache change",
                "answer": (
                    f"Commit {origin['short_hash']} introduced an in-memory price cache to address "
                    f"the latency recorded in {pressure['short_hash']}. Its own risk note says cached "
                    f"prices had no invalidation path. Commit {symptom['short_hash']} later documented "
                    "checkout retaining an old catalog value, making the cache change the likely origin."
                ),
                "certainty": "inferred",
                "confidence": 0.98,
                "evidence": [
                    _citation(pressure, "The repository recorded pressure to reduce repeated pricing work."),
                    _citation(origin, "The cache was introduced without a price invalidation path."),
                    _citation(symptom, "OC-52 later recorded stale checkout prices after catalog updates."),
                ],
                "missing_evidence": ["No production trace identifies the first affected order."],
            },
            {
                "question_id": "change-risk",
                "question": QUESTION_BY_ID["change-risk"]["question"],
                "headline": "Version propagation and the centralized pricing path are the sharp edges",
                "answer": (
                    "Changing catalog-version behavior is risky because every price update must advance "
                    "the version or stale values can return. Changing the centralized pricing module is "
                    "also high impact because every checkout depends on it. The regression test protects "
                    "correctness, but production cache performance is still not evidenced."
                ),
                "certainty": "inferred",
                "confidence": 0.94,
                "evidence": [
                    _citation(centralize, "Every checkout now depends on the centralized pricing module."),
                    _citation(resolution, "Safe caching depends on callers incrementing catalog versions."),
                    _citation(verification, "Regression coverage exists, but production-load evidence does not."),
                ],
                "missing_evidence": [
                    "There is no production-load measurement for the versioned cache.",
                    "The repository does not show which external catalog callers advance versions.",
                ],
            },
        ]
    }


def validate_answer_set(payload: dict[str, Any], timeline: dict[str, Any]) -> dict[str, Any]:
    answers = payload.get("answers")
    expected_ids = [item["id"] for item in QUESTIONS]
    if not isinstance(answers, list) or [item.get("question_id") for item in answers] != expected_ids:
        raise AnalysisError("Ask the Repo must contain the three supported questions in order.")

    event_by_id = {event["id"]: event for event in timeline["events"]}
    for answer in answers:
        expected = QUESTION_BY_ID[answer["question_id"]]
        if answer.get("question") != expected["question"]:
            raise AnalysisError("An Ask the Repo question did not match its supported prompt.")
        confidence = answer.get("confidence")
        if not isinstance(confidence, (int, float)) or not 0 <= confidence <= 1:
            raise AnalysisError("An Ask the Repo confidence value was invalid.")
        if answer.get("certainty") not in {"confirmed", "inferred", "missing-evidence"}:
            raise AnalysisError("An Ask the Repo certainty label was invalid.")
        if not isinstance(answer.get("answer"), str) or not answer["answer"].strip():
            raise AnalysisError("An Ask the Repo answer was empty.")
        citations = answer.get("evidence")
        if not isinstance(citations, list) or not citations:
            raise AnalysisError("An Ask the Repo answer had no evidence.")
        for citation in citations:
            event_id = citation.get("event_id")
            if event_id not in event_by_id:
                raise AnalysisError("An Ask the Repo answer referenced an unknown event.")
            event = event_by_id[event_id]
            allowed_refs = {
                event["short_hash"],
                event["commit_hash"],
                *[item["path"] for item in event["files"]],
            }
            refs = citation.get("evidence_refs")
            file_paths = {item["path"] for item in event["files"]}
            if (
                not isinstance(refs, list)
                or event["short_hash"] not in refs
                or not file_paths.intersection(refs)
                or any(ref not in allowed_refs for ref in refs)
            ):
                raise AnalysisError("An Ask the Repo citation was not grounded in its event.")
    return payload


def load_answer_artifact(timeline: dict[str, Any], artifact_path: Path) -> dict[str, Any]:
    envelope = json.loads(artifact_path.read_text(encoding="utf-8"))
    provenance = envelope.get("provenance", {})
    model = provenance.get("model", "")
    if envelope.get("artifact_version") != 1:
        raise AnalysisError("The Ask the Repo artifact version is unsupported.")
    if provenance.get("generator") != "codex exec" or not model.startswith("gpt-5.6"):
        raise AnalysisError("The Ask the Repo provenance is invalid.")
    if provenance.get("evidence_sha256") != evidence_digest(timeline):
        raise AnalysisError("The Ask the Repo artifact does not match the current Git evidence.")
    payload = validate_answer_set(envelope.get("payload", {}), timeline)
    return {
        **payload,
        "source": "codex-gpt-5.6",
        "model": model,
        "delivery": "validated-artifact",
        "generated_at": provenance.get("generated_at"),
        "provenance": provenance,
    }


def ask_repo(timeline: dict[str, Any], question_id: str, artifact_path: Path | None = None) -> dict[str, Any]:
    if question_id not in QUESTION_BY_ID:
        raise AnalysisError("That Ask the Repo question is not supported.")

    answer_set: dict[str, Any] | None = None
    if artifact_path and artifact_path.exists():
        try:
            answer_set = load_answer_artifact(timeline, artifact_path)
        except (AnalysisError, KeyError, json.JSONDecodeError, TypeError):
            pass

    if answer_set is None:
        payload = validate_answer_set(deterministic_answers(timeline), timeline)
        answer_set = {
            **payload,
            "source": "evidence-fallback",
            "model": None,
            "delivery": "fallback",
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }

    answer = next(item for item in answer_set["answers"] if item["question_id"] == question_id)
    return {
        **answer,
        "source": answer_set["source"],
        "model": answer_set["model"],
        "delivery": answer_set["delivery"],
        "generated_at": answer_set["generated_at"],
        "provenance": answer_set.get("provenance"),
    }
