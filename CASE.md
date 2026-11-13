<!--
proximata Hackathon '26 Case Book entry. Replaces the proximata "[Case title]" template section.
"Tracks at a glance" row: | AI systems and agentic infrastructure | Think Fast: Local Decision Models | proximata | Full brief |
-->

PROXIMATA HACKATHON '26 · AI SYSTEMS AND AGENTIC INFRASTRUCTURE

**proximata**

# Think Fast: Local Decision Models

**Millions of small judgment calls. No tokens, no cloud, no waiting.**

Pick a real problem made of small judgment calls, build a decision model for it that runs on your own hardware, and prove that it works.

| | |
|---|---|
| Theme | AI systems and agentic infrastructure |
| Track partner | proximata |
| Team size | 2–4 people |
| Prize | Build your project with us, with full ecosystem support. The track is also eligible for Best use of Adaption |
| Code freeze | Saturday, 14 November, 15:00 sharp |

## About proximata

proximata is a Vienna-based builder space and tech agency focusing on the most ambitious technical challenges and enabling top innovation in the EU. We build enterprise AI automation and on-premise AI, and we want to find out how far small local models can go.

## The Problem

**The current state.** Every business process, data pipeline and AI agent is full of small judgment calls. Is this a duplicate? Does this ticket go to billing or to shipping? Does this listing break a policy? Is this value wrong? Today these calls are made by brittle rules, by people, or by sending each one to a large language model in the cloud and parsing the text it writes back.

**Why it matters.** Writing out a sentence to answer a yes/no question is slow, it is paid per call, and at a million calls a day that adds up. Many organisations in the EU can't send customer data to an external model at all. And a chatbot's answer comes without a confidence you can trust, so nobody knows which of its decisions to automate and which to check.

**What changed.** Decision models skip the writing: they read the input once and return a probability for every answer you defined. And a small model tuned for one job can now match the big ones at it. Airbnb fine-tuned a 2B open-weight model to check content against one of its policies. Its F1 rose from 0.563 to 0.902, which matched the frontier models it was compared with, at a median latency of 35 ms and "about a hundredth of the cost" ([Frontier quality at 1% of the cost](https://airbnb.tech/ai-ml/frontier-quality-at-1-of-the-cost-a-production-benchmark-of-llm-classifiers/), Clay Gibson and Adel Elmalaha, Airbnb Engineering). Models that size run on a laptop.

**Who is affected.** Support, trust-and-safety and operations teams that make the same call thousands of times a day; data scientists, analysts and data engineers who clean, label and route data; and anyone building agents that make dozens of small decisions per step.

## The Challenge

Within 24 hours, pick a problem made of many small judgment calls and show us it's worth solving. Build a decision model for it that runs on your own hardware, gives a probability you can trust and knows when it doesn't know. Prove it on data it has never seen. Then put it to work: a tool that automates the decisions it is confident about and sends the uncertain ones to a person.

You choose the problem. Bring your own data, take a ready-made task from Dataset Factory, or use our starter problem (data-work questions with a test suite and scorer) if you'd rather spend the time building.

## What You're Building

Each step is a demo on its own; go as far as you can.

- **Pick a problem worth solving:** judgment calls that someone makes often, today by hand, with rules or with a big hosted model. Airbnb's four tests for when a small tuned model pays off: the volume is high, the latency is tight, you need a threshold rather than a verdict, and you have labelled data. Tell us who has the problem, what it costs them today and why it should run locally.
- **Build the engine:** a model that answers your questions with probabilities on your own machine. Start from an open decision model such as Kev, from any small open model through the starter kit's bridge, or from a classic classifier. Serve it behind the open decision API (`POST /v1/systemone`) and the starter kit's runner scores it for you.
- **Prove it:** hold out test data that you never train, prompt or tune on, and split it by time if your data has dates. Put a simple baseline next to your model, such as the most common answer, a few rules or a logistic regression, and a big model as a reference if you can. Report a metric that fits the problem, and show that your confidence is honest.
- **Make it yours:** fine-tune, distil a bigger teacher into a small student, train a new head, or label your own data. Show what each change gained.
- **Make it fast and cheap:** measure latency and the cost per million decisions on your hardware, next to a hosted model doing the same job. Run it with Wi-Fi off.
- **Put it to work:** a tool for the people who have the problem. It automates the decisions above a confidence threshold, sends the rest to a review queue, and reports how many it automated within an error budget you chose, for example 5%.

## Data & Resources

- **[Dataset Factory](https://earino.github.io/dataset-factory-site/)** by E. Ariño de la Rubia: public data turned into ready-made yes/no prediction tasks, such as consumer complaints, vehicle recalls, planning appeals and food inspections. Each task comes with a fixed prediction time, time-ordered train, eval and holdout splits, and measured baselines (AUC and Brier score) to beat. Licences vary by source and some are non-commercial, so check each one, and link the data from your repo instead of committing it.
- **Your own data,** or any public dataset you're allowed to use.
- **The starter problem, in this repo:**
  - five data-work task families (column typing, product matching, value checks, row problems, ticket triage), with a generator for unlimited training data and fresh test sets
  - a messy product catalogue with an answer key, to build your tool on
  - an evaluation runner (accuracy, Brier score, calibration error, automation rate at a 5% error budget, latency). It also scores your own problem if you write it in the same format
  - the open decision API contract, and a baseline bridge that turns any local model server with token log-probabilities into a decision engine
- **Open models and code:** Kev (github.com/jaredpalmer/kev, Apache-2.0; decision models from 0.8B to 27B parameters, serving this API), SemIf (github.com/TheoLeeCJ/SemIf-OpenJev, MIT; reads option probabilities from open models, including llama.cpp on CPU and MLX on Mac) and LocalJev (github.com/githubnext/localjev, MIT; a bridge to local model servers).
- **Adaption:**
  - credits for every participant through the proximata referral link on Discord
  - a 30-minute workshop with an Adaption engineer on training a model from your own data (Saturday 11:00)
  - the Best use of Adaption prize, open to this track

  If you train a model there, check that you can download it and run it on your own machine. Adaption can also generate or clean training data.
- **Reading:** the Airbnb benchmark above, for how a production team decided when a small fine-tuned model beats a frontier one.

### House Rules

- Use any model and any data you're allowed to use. Cloud is fine for training and labelling. Hosted model APIs at decision time are allowed, but they score low on "Local, fast, cheap".
- Respect every licence and terms of service: models, data and APIs. Training data you generate with another model must respect that model's terms. Data you may not redistribute is linked from your repo, not committed.
- Test on data you never trained, prompted or tuned on.
- Every number in your `REPORT.md` comes from a command in your repo.

## Demo & Pitch Expectations

The track jury sees each team for a 5-minute live demo and 3 minutes of questions. If the track is large, the slots may get shorter; we'll announce that on Discord. Use this order, so the jury finds what it scores:

1. **The problem** (about 45 s): who makes these calls, how often, what it costs them, and why it should run locally.
2. **Live** (about 2 min): your tool on real inputs. What it decided on its own, what it sent to a person, and why. If your model runs locally, turn Wi-Fi off on screen first.
3. **The evidence** (about 1.5 min): held-out numbers next to your baseline, your threshold, and how honest your confidence is.
4. **What you built** (about 45 s): what you trained, tuned or invented, what it gained, and your limits.

Follow the same order in your 3-minute video. The jury watches it if the live demo breaks.

## What Great Looks Like

- A problem a real team has, such as a support desk's routing, a marketplace's policy checks or a data team's deduplication, with the volume and what it costs today.
- Small and sharp: a sub-1B model tuned for one job that matches a big hosted model at it, at a fraction of the latency and cost.
- Honest confidence: when the model says 90%, it is right nine times in ten, so the automation threshold comes from data, not gut feeling.
- An honest baseline: if a logistic regression gets close, you say so.
- A tool someone would install tomorrow, such as a CLI that cleans a CSV with a review queue, or a `decide(df, question)` function for pandas or DuckDB.

### Out of Scope

- Training a foundation model from scratch
- A polished UI
- Benchmarks against closed models or APIs whose terms forbid publishing them

## Judging Criteria

The track jury scores every team out of 100 during its demo slot and picks the highest total as Track Winner. There is no hidden test suite: you bring the evidence, and the jury checks it live and in your `REPORT.md` scorecard.

**Gates.** A team that fails one can't win the track:

- The standard submission (see General Rules), plus a `REPORT.md` that starts with the scorecard from [docs/REPORT_TEMPLATE.md](docs/REPORT_TEMPLATE.md).
- Every licence and terms of service respected (see House Rules).
- No made-up results: every number in `REPORT.md` comes from a command in the repo, and live decisions come from the model.

**Score.** Each category has three bands: low is 0–30% of its points, mid 30–70%, high 70–100%.

| Category | Points | Low | Mid | High |
|---|---|---|---|---|
| A. A problem worth solving | 20 | A toy task, or nobody named who has it | A real workflow and user with real data, but volume, cost or why local left vague | Who decides today, how often and at what cost; why it should run locally; data source and licence |
| B. Evidence it works | 30 | A demo only, or numbers on data the model saw | Held-out numbers next to a simple baseline | Also a threshold chosen from data, calibration shown, a big-model reference, and where it fails |
| C. Local, fast, cheap | 20 | A hosted model at decision time, or nothing measured | Runs on your own hardware; latency and cost per million decisions measured | Shown live with Wi-Fi off, compared with a hosted model doing the same job |
| D. Put it to work | 20 | A model only, no workflow | A working tool with a threshold and a review queue | Someone in that job would use it tomorrow; shows what it automated and what it sent to a person |
| E. Make it yours | 10 | An off-the-shelf model with a prompt | One solid change, measured: a fine-tune, distillation, a new head or your own labels | An original idea with a measured gain |
| Total | 100 | | | |

Using the starter problem is fine. For A, tell us who would use your tool and why it should run locally.

Tie-breakers: higher B, then higher C.

## Prize

Build your project with us, with full ecosystem support. The track is also eligible for Best use of Adaption ($1,000 in Adaption credits per team member, open to every track).

## Mentors & Jury

| Role | Who |
|---|---|
| Mentors | The proximata team, on the floor and in the track's Discord channel |
| Jury | The proximata team and guest jurors |

## Submission

Standard submission, see General Rules. In addition:

- A `REPORT.md` at the repo root that starts with the scorecard from [docs/REPORT_TEMPLATE.md](docs/REPORT_TEMPLATE.md).
- One command that reproduces your held-out numbers.
- For data you may not redistribute: a download script or link instead of the files.
