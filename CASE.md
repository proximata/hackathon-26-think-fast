<!--
proximata Hackathon '26 Case Book entry. Replaces the proximata "[Case title]" template section.
"Tracks at a glance" row: | AI systems and agentic infrastructure | Think Fast: Local Decision Models | proximata | Brief in, brackets marked |
Text in [brackets] is still open.
-->

PROXIMATA HACKATHON '26 · AI SYSTEMS AND AGENTIC INFRASTRUCTURE

**proximata**

# Think Fast: Local Decision Models

**Millions of small judgment calls. No tokens, no cloud, no waiting.**

Build an open decision engine that answers typed questions with calibrated probabilities in milliseconds on your own hardware, then use it to automate the judgment calls in a messy data workflow.

| | |
|---|---|
| Theme | AI systems and agentic infrastructure |
| Track partner | proximata |
| Team size | 2–4 people |
| Prize | [Prize details] |
| Code freeze | Saturday, 14 November, 14:00 sharp [TBC] |

## About proximata

proximata is a Vienna-based builder space and tech agency focusing on the most ambitious technical challenges and enabling top innovation in the EU. [Why proximata is bringing this case. Proposed: "We build data and AI systems for organisations whose data can't leave the building, and we want to find out how far small local models can go."]

## The Problem

**The current state.** Every data pipeline and every AI agent is full of small judgment calls. Is this row a duplicate? What kind of data is in this column? Is this value wrong? Which team gets this ticket? Today these calls are handled by brittle rules, by people, or by sending each row to a large language model in the cloud and parsing the text it writes back.

**Why it matters.** Writing out a sentence to answer a yes/no question is slow, it is paid per call, and at a million rows that adds up. Many organisations in the EU can't send customer data to an external model at all. And a chatbot's answer comes without a confidence you can trust, so nobody knows which of its decisions to automate and which to check.

**What changed.** Decision models skip the writing. They read the input once and return a probability for every answer you defined, in one pass. A closed decision API brought the idea into the spotlight in September 2026, and open models with the same interface followed within days. They run on a laptop.

**Who is affected.** Data scientists and analysts who clean and label data, data engineers running pipelines, and anyone building agents that make dozens of small decisions per step.

## The Challenge

Within 24 hours, build a decision engine that runs entirely on local hardware, answers yes/no, multiple-choice and rating questions with calibrated probabilities, and knows when it doesn't know. Then prove it on real data work: a tool that automates the decisions it is confident about and sends only the uncertain ones to a person.

Done means three things. Your engine serves the open decision API. It is scored on a hidden test suite on the organisers' reference machine with the network switched off. And your tool works live on a messy dataset.

## What You're Building

Each level is a demo on its own; go as far as you can.

- **Serve it:** a local engine behind the open decision API (`POST /v1/systemone`, the format open projects like Kev already use), answering yes/no, choice and score questions. It passes the starter repo's evaluation runner.
- **Make it honest:** calibrated probabilities. Measure the Brier score and calibration error on the dev suite and fix them, for example with temperature scaling. Your confidence decides what gets automated.
- **Make it fast:** answer a request with several questions in [target] ms at p95 on the reference machine. Read the input once and share it across questions, cache, batch, quantise.
- **Make it yours:** fine-tune or distil for data work. For example, train a small student on labels from a bigger local teacher, or a new head on a small model. Show the gain on the dev suite without losing the task families you have never seen.
- **Put it to work:** a tool for a real data workflow, such as deduplication, column typing, validation or ticket routing, on the provided messy product catalogue or your own data. It automates the decisions above a confidence threshold, sends the rest to a review queue, and reports how many decisions it automated at a 5% error budget.

## Data & Resources

- **Starter repo:** the decision API contract; a dev suite of five data-work task families (column typing, product matching, value checks, row problems, ticket triage) with a generator for unlimited training data; an evaluation runner (accuracy, Brier score, calibration error, automation rate at a 5% error budget, latency); a messy product catalogue with an answer key; and a baseline bridge that turns any local model server with token log-probabilities into a decision engine.
- **Open models and code:** Kev (github.com/jaredpalmer/kev, Apache-2.0; decision models from 0.8B to 27B parameters, serving this API), SemIf (github.com/TheoLeeCJ/SemIf-OpenJev, MIT; reads option probabilities from open models, including llama.cpp on CPU and MLX on Mac) and LocalJev (github.com/githubnext/localjev, MIT; a bridge to local model servers). Any open-weight model is allowed.
- **Hidden suite:** the same five families with fresh data, plus task families you haven't seen. It runs on the reference machine after code freeze.
- [Proposed, confirm with mesh applied: a shared GPU server on the venue network running Goethe (github.com/meshapplied/goethe), their open-source inference server, with large open models as teachers for labelling and distillation during the build. Not reachable at grading time.]
- [Reference machine for grading: TBC, announced at kick-off]
- [GPU credits for fine-tuning: sponsor TBC]
- Adaption Labs' workshop on training a model from your own data. The "Best use of Adaption" prize is open to this track.

### House Rules

- Local only: at grading time your engine runs with the network switched off. No calls to hosted model APIs at inference time. Cloud is fine for training.
- Open weights only, and every licence respected. Training data you generate with another model must respect that model's terms.
- Don't train on the hidden suite or look up its items.

## Demo & Pitch Expectations

Show your engine answering live with the network off, your calibration before and after, and your tool on a messy dataset: what it automated, what it sent to a person, and why. [Pitch length]

## What Great Looks Like

- Small and sharp: a sub-1B model, tuned for data work, that beats a bigger general model on the dev families at a fraction of the latency.
- Honest confidence: when the engine says 90%, it is right nine times in ten, so the automation threshold comes from data, not gut feeling.
- Read once, ask many: one pass over a row answers ten questions about it.
- A tool someone would install tomorrow, such as a CLI that cleans a CSV with a review queue, or a `decide(df, question)` function for pandas or DuckDB.

### Out of Scope

- Hosted model APIs at inference time
- Training a foundation model from scratch
- A polished UI
- Benchmarks against closed decision APIs whose terms forbid publishing them

## Judging Criteria

Scoring is out of 100 points. Categories A–C are measured automatically on the hidden suite on the reference machine.

| Category | Points | How it's scored |
|---|---|---|
| A. Automation rate | 25 | Share of hidden-suite decisions automated at ≤5% error. Points = 25 × your rate ÷ best rate in the track |
| B. Accuracy & calibration | 15 | Hidden-suite accuracy (10) and Brier score (5), each relative to the best team |
| C. Speed | 15 | p95 latency per request on the reference machine. [Tiers TBC once the baseline is measured there, e.g. ≤150 ms: 15, ≤500 ms: 10, ≤1.5 s: 5] |
| D. Put it to work | 25 | Jury: the data tool, its review queue and the live demo |
| E. Engineering & reproducibility | 20 | Starts from the README on a clean machine with the network off, tests, honest REPORT.md |
| Total | 100 | |

Hard fails: calling a hosted model API at inference time; training on or looking up the hidden suite. If the engine doesn't start on the reference machine from the README, categories A–C score 0.

Tie-breakers: higher automation rate (A), then lower latency (C).

## Prize

[Prize value and composition for the Track Winner]

## Mentors & Jury

| Role | Who | Notes |
|---|---|---|
| Mentor | [Name, role] | [Contact] |
| Jury | [Name, role] | [What they judge] |

## Submission

Standard submission, see General Rules. In addition:

- One documented command that starts your engine on port 8009 from a clean checkout, with model weights downloaded by a separate setup step (the grading run has no network).
- A `REPORT.md` with your dev-suite numbers from the evaluation runner, the model and hardware you measured on, and what you would do next.
