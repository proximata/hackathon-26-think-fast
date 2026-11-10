"""Plumbing tests: suite -> engine -> runner, and the bridge against a fake upstream.

These prove the wiring and the wire format only. They use no real model.
"""

import json
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from thinkfast.bridge import Bridge, make_handler
from thinkfast.metrics import question_options
from thinkfast.messy import build as build_catalogue
from thinkfast.run_eval import run
from thinkfast.suite import build_suite, label_key


def serve(handler) -> tuple[ThreadingHTTPServer, str]:
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server, f"http://127.0.0.1:{server.server_address[1]}"


class JsonHandler(BaseHTTPRequestHandler):
    def reply(self, payload):
        data = json.dumps(payload).encode()
        self.send_response(200)
        self.send_header("content-type", "application/json")
        self.send_header("content-length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def body(self):
        return json.loads(self.rfile.read(int(self.headers["content-length"])))

    def log_message(self, *args):
        pass


def oracle_handler(items):
    """A fake engine that knows the labels and is 90% sure of them."""
    by_state = {json.dumps(i["request"]["state"], sort_keys=True): i for i in items}

    class Oracle(JsonHandler):
        def do_POST(self):
            item = by_state[json.dumps(self.body()["state"], sort_keys=True)]
            answers = {}
            for qid, q in item["request"]["questions"].items():
                options = question_options(q)
                label = label_key(q, item["labels"][qid])
                probs = {o: (0.9 if o == label else 0.1 / (len(options) - 1)) for o in options}
                answers[qid] = {"noul": probs["true"]} if q["type"] == "noul" else {"probabilities": probs}
            self.reply({"answers": answers})

    return Oracle


class FakeUpstream(JsonHandler):
    """An OpenAI-compatible server that always favours option A."""

    def do_POST(self):
        assert self.body()["logprobs"] is True
        top = [{"token": "A", "logprob": -0.2}, {"token": " B", "logprob": -2.0}, {"token": "Hello", "logprob": -3.0}]
        self.reply({"choices": [{"logprobs": {"content": [{"token": "A", "top_logprobs": top}]}}]})


class EndToEndTest(unittest.TestCase):
    def test_suite_is_deterministic_and_labelled(self):
        a, b = build_suite(seed=1, per_family=20), build_suite(seed=1, per_family=20)
        self.assertEqual(a, b)
        for item in a:
            for qid, question in item["request"]["questions"].items():
                self.assertIn(label_key(question, item["labels"][qid]), question_options(question))

    def test_runner_scores_an_oracle_engine(self):
        items = build_suite(seed=3, per_family=10)
        server, base = serve(oracle_handler(items))
        try:
            decisions, latencies, records = run(items, base + "/v1/systemone", "x", 5, 2, None)
        finally:
            server.shutdown()
        self.assertTrue(all(dec.correct for dec in decisions))
        self.assertEqual(len(latencies), len(items) - 2)
        self.assertFalse(any(r["error"] for r in records))

    def test_runner_survives_a_dead_endpoint(self):
        items = build_suite(seed=3, per_family=1)
        decisions, _, records = run(items, "http://127.0.0.1:9/v1/systemone", "x", 1, 0, None)
        self.assertTrue(all(dec.failed for dec in decisions))
        self.assertTrue(all(r["error"] for r in records))

    def test_bridge_reads_letter_probabilities(self):
        upstream, upstream_url = serve(FakeUpstream)
        bridge = Bridge(upstream_url, "fake", parallel=2)
        engine, engine_url = serve(make_handler(bridge))
        try:
            item = next(i for i in build_suite(seed=5, per_family=5) if i["family"] == "ticket_triage")
            decisions, _, records = run([item], engine_url + "/v1/systemone", "x", 5, 0, None)
        finally:
            engine.shutdown()
            upstream.shutdown()
        answers = records[0]["answers"]
        self.assertGreater(answers["needs_human"]["noul"], 0.8)  # A = Yes
        self.assertEqual(answers["team"]["choice"], "billing")  # A = first option
        self.assertAlmostEqual(sum(answers["urgency"]["probabilities"].values()), 1.0)
        self.assertEqual(len(decisions), 3)

    def test_catalogue_key_matches_rows(self):
        rows, key = build_catalogue(seed=1, products=50)
        ids = {r["row_id"] for r in rows}
        self.assertTrue(set(key["problems"]) <= ids)
        self.assertTrue(all(set(group) <= ids for group in key["duplicate_groups"]))


if __name__ == "__main__":
    unittest.main()
