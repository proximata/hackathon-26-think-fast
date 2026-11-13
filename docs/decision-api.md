# Decision API contract

Serve this one endpoint and the evaluation runner (`thinkfast/run_eval.py`)
can score your engine, on the starter problem or on your own. The runner calls
nothing else.

The wire format is the one the open decision-model projects already speak.
[Kev](https://github.com/jaredpalmer/kev) documents it in full in its README and
serves this exact endpoint; it echoes the request's `model` field and ignores
fields it doesn't recognise, so the evaluation runner works against it unchanged
(pass `--model kev-latest` if you like). This track and its starter kit are not
affiliated with TypeSafe or any other vendor.

## `POST /v1/systemone`

The engine listens on `127.0.0.1:8009` unless you document another port.

```json
{
  "model": "local",
  "state": {"channel": "email", "message": "I was charged twice for order #48213."},
  "questions": {
    "team":        {"type": "choice", "instructions": "Which team should handle this ticket?",
                    "criteria": {"billing": "Charges, invoices, payment problems",
                                 "shipping": "Delivery status, delays, lost parcels"}},
    "urgency":     {"type": "score", "instructions": "How urgent is this ticket?",
                    "criteria": ["low", "normal", "high", "critical"]},
    "needs_human": {"type": "noul", "instructions": "Should a person look at this first?"}
  }
}
```

- `state`: a string, object or array. It is the input every question is about.
- `questions`: an object of question ID → question. The ID is yours; the model
  should not need to see it. A request can hold one question or many.
- `type`:
  - `noul`: yes/no. `criteria` is optional: `{"true": "…", "false": "…"}`.
  - `choice`: one of several options. `criteria` maps option name → description (or `null`).
  - `score`: an ordered scale. `criteria` is a list of levels, lowest first.

## Response

```json
{
  "answers": {
    "team":        {"type": "choice", "choice": "billing", "probabilities": {"billing": 0.93, "shipping": 0.07}},
    "urgency":     {"type": "score", "score": 1.8, "probabilities": {"0": 0.05, "1": 0.2, "2": 0.65, "3": 0.1}},
    "needs_human": {"type": "noul", "noul": 0.81}
  }
}
```

What the runner reads:

| Type | Field it scores | Meaning |
|---|---|---|
| `noul` | `noul` | probability of yes |
| `choice` | `probabilities` | probability per option name |
| `score` | `probabilities` | probability per level index, as strings `"0"`, `"1"`, … |

The runner normalises probabilities to sum to 1 and ignores other fields
(`choice`, `score`, `confidence`, `usage`, …), so you can return more.

Any error, timeout (30 s by default) or missing answer counts as a uniform
guess for the questions involved. The engine has to keep serving after a bad
request.

## The runner scores your probabilities

The automation rate, Brier score and calibration error all read your
probabilities, not just the top answer. An engine that always says 0.99 gets
nothing automated once it makes a few confident mistakes. See
[`thinkfast/metrics.py`](../thinkfast/metrics.py) for the exact formulas.
