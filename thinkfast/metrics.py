"""Score decision-engine answers against labels.

Every question becomes one `Decision`: a probability per option plus the true
option. Yes/no questions use the options "true" and "false"; score questions
use the level index as a string ("0", "1", ...).
"""

from __future__ import annotations

import math
from collections import defaultdict
from dataclasses import dataclass
from typing import Any

ERROR_BUDGET = 0.05
CALIBRATION_BINS = 10


@dataclass(frozen=True)
class Decision:
    family: str
    qtype: str
    probs: dict[str, float]
    label: str
    failed: bool = False

    @property
    def predicted(self) -> str:
        return max(self.probs, key=self.probs.__getitem__)

    @property
    def confidence(self) -> float:
        return self.probs[self.predicted]

    @property
    def correct(self) -> bool:
        return self.predicted == self.label


def question_options(question: dict[str, Any]) -> list[str]:
    """The option keys an answer is scored over, in request order."""
    qtype = question["type"]
    if qtype == "noul":
        return ["true", "false"]
    if qtype == "choice":
        return list(question["criteria"])
    if qtype == "score":
        return [str(i) for i in range(len(question["criteria"]))]
    raise ValueError(f"unknown question type: {qtype!r}")


def uniform(options: list[str]) -> dict[str, float]:
    return {o: 1.0 / len(options) for o in options}


def probs_from_answer(question: dict[str, Any], answer: dict[str, Any] | None) -> dict[str, float]:
    """Normalise one answer from the decision API into option probabilities.

    A missing or malformed answer counts as a uniform guess, so it scores as an
    unconfident (and usually wrong) decision instead of crashing the run.
    """
    options = question_options(question)
    if not isinstance(answer, dict):
        return uniform(options)
    try:
        if question["type"] == "noul":
            p = min(1.0, max(0.0, float(answer["noul"])))
            return {"true": p, "false": 1.0 - p}
        raw = answer.get("probabilities") or {}
        probs = {o: max(0.0, float(raw.get(o, 0.0))) for o in options}
    except (AttributeError, KeyError, TypeError, ValueError):
        return uniform(options)
    total = sum(probs.values())
    if total <= 0:
        return uniform(options)
    return {o: v / total for o, v in probs.items()}


def brier(d: Decision) -> float:
    """Multi-class Brier score of one decision (0 is perfect, 2 is worst)."""
    return sum((p - (1.0 if o == d.label else 0.0)) ** 2 for o, p in d.probs.items())


def expected_calibration_error(decisions: list[Decision], bins: int = CALIBRATION_BINS) -> float:
    """Gap between confidence and accuracy, averaged over equal-width bins."""
    if not decisions:
        return 0.0
    buckets: dict[int, list[Decision]] = defaultdict(list)
    for d in decisions:
        buckets[min(int(d.confidence * bins), bins - 1)].append(d)
    total = len(decisions)
    gap = 0.0
    for bucket in buckets.values():
        accuracy = sum(d.correct for d in bucket) / len(bucket)
        confidence = sum(d.confidence for d in bucket) / len(bucket)
        gap += abs(accuracy - confidence) * len(bucket) / total
    return gap


def automation_rate(decisions: list[Decision], budget: float = ERROR_BUDGET) -> tuple[float, float]:
    """Largest share of decisions you can automate with at most `budget` errors.

    Decisions are automated from the most confident down. A threshold cannot
    split decisions with equal confidence, so ties are taken or left together.
    Returns (share automated, confidence threshold used); the threshold is 1.0
    when nothing can be automated.
    """
    if not decisions:
        return 0.0, 1.0
    ranked = sorted(decisions, key=lambda d: d.confidence, reverse=True)
    best_k, best_threshold = 0, 1.0
    errors = 0
    i = 0
    while i < len(ranked):
        j = i
        while j < len(ranked) and ranked[j].confidence == ranked[i].confidence:
            errors += not ranked[j].correct
            j += 1
        if errors <= budget * j:
            best_k, best_threshold = j, ranked[i].confidence
        i = j
    return best_k / len(ranked), best_threshold


def percentile(values: list[float], q: float) -> float:
    """Nearest-rank percentile; 0.0 for an empty list."""
    if not values:
        return 0.0
    ordered = sorted(values)
    rank = max(1, min(len(ordered), math.ceil(q / 100 * len(ordered))))
    return ordered[rank - 1]


def summarize(decisions: list[Decision]) -> dict[str, float]:
    if not decisions:
        return {"decisions": 0}
    rate, threshold = automation_rate(decisions)
    return {
        "decisions": len(decisions),
        "accuracy": sum(d.correct for d in decisions) / len(decisions),
        "brier": sum(brier(d) for d in decisions) / len(decisions),
        "ece": expected_calibration_error(decisions),
        "automation_rate_at_5pct": rate,
        "automation_threshold": threshold,
        "failed": sum(d.failed for d in decisions),
    }


def report(decisions: list[Decision], latencies_ms: list[float]) -> dict[str, Any]:
    by_family: dict[str, list[Decision]] = defaultdict(list)
    for d in decisions:
        by_family[d.family].append(d)
    return {
        "overall": summarize(decisions),
        "families": {f: summarize(ds) for f, ds in sorted(by_family.items())},
        "latency_ms": {
            "requests": len(latencies_ms),
            "p50": percentile(latencies_ms, 50),
            "p95": percentile(latencies_ms, 95),
            "mean": sum(latencies_ms) / len(latencies_ms) if latencies_ms else 0.0,
        },
    }
