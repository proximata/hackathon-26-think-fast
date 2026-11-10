"""Baseline decision engine: read option probabilities from a local chat model.

Serves the decision API on top of any local OpenAI-compatible server that
returns `top_logprobs` for chat completions. Each question becomes a lettered
multiple-choice prompt; the bridge asks for one token and turns the
log-probabilities of the option letters into a probability per option. No
answer text is parsed.

    uv run python -m thinkfast.bridge --upstream http://127.0.0.1:8080 --model my-model

Set UPSTREAM_API_KEY if the upstream server needs a key.

This is a deliberately simple starting point, not a strong engine: it makes one
upstream call per question. The state goes first in the prompt so servers with
prefix caching can reuse it across questions. Check that your server returns
`top_logprobs`; the bridge reports an error if it doesn't.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import ssl
import string
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any

LETTERS = string.ascii_uppercase[:20]
SYSTEM = ("You answer one multiple-choice question about the input. "
          "Reply with the letter of the best option and nothing else.")


class BadRequest(ValueError):
    pass


def render_state(state: Any) -> str:
    return state if isinstance(state, str) else json.dumps(state, ensure_ascii=False, indent=1)


def options_for(question: dict[str, Any]) -> list[tuple[str, str]]:
    """(option key, text shown to the model) in order."""
    qtype, criteria = question.get("type"), question.get("criteria")
    if qtype == "noul":
        criteria = criteria or {}
        return [("true", f"Yes. {criteria.get('true') or ''}".strip()),
                ("false", f"No. {criteria.get('false') or ''}".strip())]
    if qtype == "choice" and isinstance(criteria, dict) and criteria:
        return [(k, f"{k}: {v}" if v else k) for k, v in criteria.items()]
    if qtype == "score" and isinstance(criteria, list) and criteria:
        return [(str(i), str(level)) for i, level in enumerate(criteria)]
    raise BadRequest(f"question needs a valid type and criteria: {question!r}")


def build_messages(state: Any, question: dict[str, Any], options: list[tuple[str, str]]) -> list[dict[str, str]]:
    lines = [f"{LETTERS[i]}. {text}" for i, (_, text) in enumerate(options)]
    instructions = question.get("instructions") or "Choose the best option."
    if not isinstance(instructions, str):
        instructions = json.dumps(instructions, ensure_ascii=False)
    user = (f"Input:\n{render_state(state)}\n\nQuestion: {instructions}\nOptions:\n" + "\n".join(lines)
            + "\n\nAnswer with one letter.")
    return [{"role": "system", "content": SYSTEM}, {"role": "user", "content": user}]


def letter_probs(top_logprobs: list[dict[str, Any]], n_options: int) -> dict[str, float]:
    """Sum probability mass per option letter; letters outside the top-k get a small floor."""
    wanted = set(LETTERS[:n_options])
    mass: dict[str, float] = {}
    for entry in top_logprobs:
        token = str(entry.get("token", "")).strip().strip(".:)(").upper()
        if token in wanted:
            mass[token] = mass.get(token, 0.0) + math.exp(float(entry["logprob"]))
    if not mass:
        raise RuntimeError("no option letter among the upstream top_logprobs")
    floor = min(mass.values()) / 10
    return {letter: mass.get(letter, floor) for letter in LETTERS[:n_options]}


def apply_temperature(probs: list[float], temperature: float) -> list[float]:
    scaled = [p ** (1.0 / temperature) for p in probs]
    total = sum(scaled)
    return [p / total for p in scaled]


def answer_from(question: dict[str, Any], keys: list[str], probs: list[float]) -> dict[str, Any]:
    qtype = question["type"]
    if qtype == "noul":
        return {"type": "noul", "noul": probs[0]}
    best = max(range(len(keys)), key=probs.__getitem__)
    k = len(keys)
    confidence = 1.0 if k == 1 else (probs[best] - 1 / k) / (1 - 1 / k)
    distribution = dict(zip(keys, probs))
    if qtype == "choice":
        return {"type": "choice", "choice": keys[best], "confidence": confidence, "probabilities": distribution}
    return {"type": "score", "score": sum(i * p for i, p in enumerate(probs)), "confidence": confidence,
            "legend": {str(i): level for i, level in enumerate(question["criteria"])}, "probabilities": distribution}


class Bridge:
    def __init__(self, upstream: str, model: str, temperature: float = 1.0, top_logprobs: int = 20,
                 parallel: int = 4, timeout: float = 60.0, api_key: str | None = None,
                 ca_file: str | None = None):
        base = upstream.rstrip("/")
        self.url = (base if base.endswith("/v1") else base + "/v1") + "/chat/completions"
        self.model, self.temperature, self.top_logprobs = model, temperature, top_logprobs
        self.timeout, self.api_key = timeout, api_key
        # servers with a self-signed certificate (e.g. Goethe) need their certificate trusted explicitly
        self.ssl_context = ssl.create_default_context(cafile=ca_file) if ca_file else None
        self.pool = ThreadPoolExecutor(max_workers=parallel)

    def upstream_top_logprobs(self, messages: list[dict[str, str]]) -> list[dict[str, Any]]:
        body = {"model": self.model, "messages": messages, "max_tokens": 1, "temperature": 0,
                "logprobs": True, "top_logprobs": self.top_logprobs}
        headers = {"content-type": "application/json"}
        if self.api_key:
            headers["authorization"] = f"Bearer {self.api_key}"
        request = urllib.request.Request(self.url, data=json.dumps(body).encode(), headers=headers)
        with urllib.request.urlopen(request, timeout=self.timeout, context=self.ssl_context) as response:
            data = json.load(response)
        try:
            return data["choices"][0]["logprobs"]["content"][0]["top_logprobs"]
        except (KeyError, IndexError, TypeError) as exc:
            raise RuntimeError("upstream response has no top_logprobs; does your server support logprobs?") from exc

    def answer(self, state: Any, question: dict[str, Any]) -> dict[str, Any]:
        options = options_for(question)
        if len(options) > len(LETTERS):
            raise BadRequest(f"the baseline supports at most {len(LETTERS)} options")
        by_letter = letter_probs(self.upstream_top_logprobs(build_messages(state, question, options)), len(options))
        probs = apply_temperature([by_letter[LETTERS[i]] for i in range(len(options))], self.temperature)
        return answer_from(question, [key for key, _ in options], probs)

    def decide(self, body: dict[str, Any]) -> dict[str, Any]:
        state, questions = body.get("state"), body.get("questions")
        if state is None or not isinstance(questions, dict) or not questions:
            raise BadRequest("body needs a state and at least one question")
        for question in questions.values():
            options_for(question)  # validate everything before calling upstream
        started = time.perf_counter()
        futures = {qid: self.pool.submit(self.answer, state, q) for qid, q in questions.items()}
        answers = {qid: future.result() for qid, future in futures.items()}
        return {"model": body.get("model", self.model), "answers": answers,
                "latency_ms": round((time.perf_counter() - started) * 1000, 1)}


def make_handler(bridge: Bridge) -> type[BaseHTTPRequestHandler]:
    class Handler(BaseHTTPRequestHandler):
        def send(self, status: int, payload: dict[str, Any]) -> None:
            data = json.dumps(payload).encode()
            self.send_response(status)
            self.send_header("content-type", "application/json")
            self.send_header("content-length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def do_GET(self) -> None:  # noqa: N802 (http.server naming)
            if self.path in ("/health", "/ready"):
                self.send(HTTPStatus.OK, {"ok": True})
            elif self.path == "/v1/models":
                self.send(HTTPStatus.OK, {"data": [{"name": bridge.model, "description": "thinkfast bridge"}]})
            else:
                self.send(HTTPStatus.NOT_FOUND, {"error": "not found"})

        def do_POST(self) -> None:  # noqa: N802
            if self.path != "/v1/systemone":
                self.send(HTTPStatus.NOT_FOUND, {"error": "not found"})
                return
            try:
                length = int(self.headers.get("content-length", 0))
                self.send(HTTPStatus.OK, bridge.decide(json.loads(self.rfile.read(length) or b"{}")))
            except (BadRequest, json.JSONDecodeError) as exc:
                self.send(HTTPStatus.UNPROCESSABLE_ENTITY, {"error": str(exc)})
            except Exception as exc:  # upstream failures: report, keep serving
                self.send(HTTPStatus.BAD_GATEWAY, {"error": f"{type(exc).__name__}: {exc}"})

        def log_message(self, *args: Any) -> None:
            pass

    return Handler


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--upstream", default="http://127.0.0.1:8080", help="OpenAI-compatible base URL")
    parser.add_argument("--model", required=True, help="model name the upstream server expects")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8009)
    parser.add_argument("--temperature", type=float, default=1.0, help="calibration temperature (>1 softens)")
    parser.add_argument("--top-logprobs", type=int, default=20)
    parser.add_argument("--parallel", type=int, default=4, help="questions sent upstream at once")
    parser.add_argument("--ca-file", help="certificate to trust for an HTTPS upstream with a self-signed certificate")
    args = parser.parse_args()
    bridge = Bridge(args.upstream, args.model, args.temperature, args.top_logprobs, args.parallel,
                    api_key=os.environ.get("UPSTREAM_API_KEY"), ca_file=args.ca_file)
    server = ThreadingHTTPServer((args.host, args.port), make_handler(bridge))
    print(f"decision API on http://{args.host}:{args.port}/v1/systemone -> {bridge.url}")
    server.serve_forever()


if __name__ == "__main__":
    main()
