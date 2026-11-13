# REPORT: [project name]

<!--
Copy this file to REPORT.md at the root of your repo and fill it in.
Keep the scorecard first: the jury reads it during your demo slot.
Every number must come from a command in your repo. "Not measured" is a fine answer; a guess is not.
-->

## Scorecard

| | |
|---|---|
| Problem, in one line | |
| Who makes these calls today, how often, and what it costs them | |
| Why it should run locally | |
| Data: source, licence, size, link | |
| Test set: how it was held out (by time, by customer, by site…) | |
| Metric, and why it fits the problem | |
| Simple baseline on the test set | |
| Your model on the test set | |
| Optional: bootstrap 95% range on the gain over the baseline | |
| Optional: weakest slice (rarest answers, a segment): baseline vs yours | |
| Big-model reference on the test set (optional) | |
| Threshold: share decided automatically, and the error rate there | |
| Calibration: Brier score or calibration error, before → after | |
| Model: name, size, licence | |
| What you trained, tuned or built yourself | |
| Hardware and latency (p50 / p95 per decision) | |
| Cost per million decisions: yours vs a hosted model | |
| Runs with Wi-Fi off? | yes / no, shown in the video at m:ss |
| Command that reproduces the test-set numbers | |
| Demo video | |
| Known limits | |
| Optional: what you'd ship, and when you'd still pick the big model | |

## Is it a good problem?

Tick what holds and say why in a line each. The first four are Airbnb's tests for when a small tuned model pays off; the last three keep your test honest, as in Dataset Factory's task contracts.

- [ ] Volume is high: how many calls a day?
- [ ] Latency is tight: does someone or something wait for the answer?
- [ ] You need a threshold, not a verdict: what does a wrong yes cost, and a wrong no?
- [ ] You have labelled data, or a way to make it
- [ ] Inputs are only what is known at decision time: nothing from after the decision leaks in
- [ ] The test set is split by time, or by customer or site, if your data allows it
- [ ] A simple baseline is measured on the same test set

## The problem

Who has it, what they do today, and what a good answer saves them.

## Data

Where it comes from, its licence, how you cleaned and labelled it, and how you split it. If you may not redistribute it, say how to download it.

## Method

The model, what you changed and why, and how you chose the threshold.

## Results

The test-set numbers next to the baseline, with the command that produced them. One table is enough. Point estimates aren't claims: resample the test set (a bootstrap) to show the range of each difference, and check the slice where your model is weakest, such as the rarest labels.

Cost per million decisions, roughly:

- **On your own hardware:** what the machine costs per hour (rental price, or purchase price spread over its life), divided by decisions per hour, times 1,000,000.
- **Hosted model:** input and output tokens per decision times the list price, times 1,000,000.

## Recommendation

What would you ship for this problem, under which constraints (quality, latency, cost, privacy)? When would the big hosted model still be worth its price?

## Limits and next steps

Where it fails, what you didn't measure, and what you'd do with another week.
