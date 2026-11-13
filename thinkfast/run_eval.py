"""Run a decision suite against a decision API endpoint and score it.

    uv run python -m thinkfast.run_eval --suite data/dev.jsonl \\
        --endpoint http://127.0.0.1:8009/v1/systemone

Requests go one at a time, so the latency numbers are per request. The first
few requests warm the engine up and are left out of the latency figures. It
scores any suite in this format, so you can write your own problem as JSON lines
and measure it the same way.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

from .metrics import Decision, probs_from_answer, question_options, report, uniform
from .suite import label_key, read_jsonl


def post_json(url: str, body: dict[str, Any], timeout: float, api_key: str | None) -> dict[str, Any]:
    headers = {"content-type": "application/json"}
    if api_key:
        headers["authorization"] = f"Bearer {api_key}"
    request = urllib.request.Request(url, data=json.dumps(body).encode(), headers=headers, method="POST")
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.load(response)


def score_item(item: dict[str, Any], answers: dict[str, Any] | None) -> list[Decision]:
    decisions = []
    for qid, question in item["request"]["questions"].items():
        answer = (answers or {}).get(qid)
        failed = answers is None
        probs = uniform(question_options(question)) if failed else probs_from_answer(question, answer)
        decisions.append(Decision(family=item["family"], qtype=question["type"], probs=probs,
                                  label=label_key(question, item["labels"][qid]), failed=failed))
    return decisions


def run(items: list[dict[str, Any]], endpoint: str, model: str, timeout: float, warmup: int,
        api_key: str | None) -> tuple[list[Decision], list[float], list[dict[str, Any]]]:
    decisions: list[Decision] = []
    latencies: list[float] = []
    records: list[dict[str, Any]] = []
    for n, item in enumerate(items):
        body = {"model": model, **item["request"]}
        started = time.perf_counter()
        try:
            answers = post_json(endpoint, body, timeout, api_key).get("answers")
            error = None
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, OSError) as exc:
            answers, error = None, f"{type(exc).__name__}: {exc}"
        elapsed_ms = (time.perf_counter() - started) * 1000
        if n >= warmup:
            latencies.append(elapsed_ms)
        decisions.extend(score_item(item, answers))
        records.append({"id": item["id"], "latency_ms": round(elapsed_ms, 2), "answers": answers, "error": error})
        if error and n == 0:
            print(f"first request failed: {error}", file=sys.stderr)
    return decisions, latencies, records


def print_table(result: dict[str, Any]) -> None:
    columns = ["decisions", "accuracy", "brier", "ece", "automation_rate_at_5pct", "failed"]
    print(f"{'family':<16}" + "".join(f"{c[:12]:>14}" for c in columns))
    rows = list(result["families"].items()) + [("OVERALL", result["overall"])]
    for name, stats in rows:
        cells = "".join(f"{stats.get(c, 0):>14.3f}" if isinstance(stats.get(c), float) else f"{stats.get(c, 0):>14}"
                        for c in columns)
        print(f"{name:<16}{cells}")
    lat = result["latency_ms"]
    print(f"\nlatency per request: p50 {lat['p50']:.1f} ms, p95 {lat['p95']:.1f} ms over {lat['requests']} requests")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--suite", type=Path, default=Path("data/dev.jsonl"))
    parser.add_argument("--endpoint", default="http://127.0.0.1:8009/v1/systemone")
    parser.add_argument("--model", default="local")
    parser.add_argument("--timeout", type=float, default=30.0, help="seconds per request")
    parser.add_argument("--warmup", type=int, default=5, help="requests left out of the latency figures")
    parser.add_argument("--limit", type=int, default=0, help="only run the first N requests")
    parser.add_argument("--out", type=Path, default=Path("results"), help="folder for report.json and answers.jsonl")
    args = parser.parse_args()

    items = read_jsonl(args.suite)
    if args.limit:
        items = items[: args.limit]
    decisions, latencies, records = run(items, args.endpoint, args.model, args.timeout, args.warmup,
                                        os.environ.get("DECISION_API_KEY"))
    result = report(decisions, latencies)
    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / "report.json").write_text(json.dumps(result, indent=2))
    with (args.out / "answers.jsonl").open("w") as f:
        for record in records:
            f.write(json.dumps(record) + "\n")
    print_table(result)
    print(f"report: {args.out / 'report.json'}")


if __name__ == "__main__":
    main()
