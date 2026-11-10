"""Generate decision suites: data-work questions with known answers.

Each item is one request to the decision API plus the labels for its
questions. All data is synthetic product, order and support data (fictional
brands, no people), so you can generate as much training data as you like with
other seeds. The hidden suite used for grading draws these families with a
secret seed and adds task families that are not in this file.

    uv run python -m thinkfast.suite --out data/dev.jsonl
"""

from __future__ import annotations

import argparse
import json
import random
from collections.abc import Callable
from datetime import date, timedelta
from pathlib import Path
from typing import Any

DEV_SEED = 2026
Item = dict[str, Any]
Family = Callable[[random.Random], tuple[Any, dict[str, Any], dict[str, Any]]]

BRANDS = ["Nordwind", "Alpenglas", "Donaukraft", "Kessler", "Vela", "Brightline", "Ostara", "Tiefgrund"]
PLACES = [("Wien", "1030"), ("Graz", "8010"), ("Linz", "4020"), ("Salzburg", "5020"), ("Innsbruck", "6020"),
          ("Budapest", "1051"), ("Bratislava", "81101"), ("München", "80331")]
COUNTRY_NAMES = ["Austria", "Österreich", "Germany", "Deutschland", "Hungary", "Slovakia", "Czechia", "Italy"]
ISO2 = ["AT", "DE", "HU", "SK", "CZ", "IT", "SI", "PL"]
CURRENCIES = ["EUR", "HUF", "CZK", "PLN", "CHF", "USD"]

# category -> (series prefix, attribute name, attribute values, unit, typical price range EUR, weight kg)
CATEGORIES = {
    "cordless drill": ("BS", "voltage", [12, 18, 24], "V", (49, 229), 1.6),
    "electric kettle": ("WK", "capacity", [1.0, 1.5, 1.7], "l", (19, 89), 1.1),
    "monitor": ("MN", "screen size", [24, 27, 32], "inch", (129, 599), 5.4),
    "LED bulb": ("LB", "power", [5, 8, 12], "W", (3, 19), 0.05),
    "office chair": ("OC", "max load", [110, 130, 150], "kg", (89, 449), 14.0),
}


def product(rng: random.Random, category: str | None = None) -> dict[str, Any]:
    category = category or rng.choice(list(CATEGORIES))
    prefix, attr, values, unit, (lo, hi), weight = CATEGORIES[category]
    value = rng.choice(values)
    brand = rng.choice(BRANDS)
    model = f"{prefix}-{rng.randint(10, 99)}{rng.choice('ABCX')}"
    return {"brand": brand, "model": model, "category": category, "attribute": attr, "value": value,
            "unit": unit, "price": round(rng.uniform(lo, hi), 2), "weight": weight}


def number(value: float, decimal_comma: bool) -> str:
    text = f"{value:g}"
    return text.replace(".", ",") if decimal_comma else text


def title(p: dict[str, Any], rng: random.Random) -> str:
    comma = rng.random() < 0.5
    spec = f"{number(p['value'], comma)}{rng.choice(['', ' '])}{p['unit']}"
    return rng.choice([
        f"{p['brand']} {p['category']} {p['model']} {spec}",
        f"{p['brand']} {p['model']} - {p['category'].title()}, {spec}",
        f"{p['category'].title()} {spec} {p['brand']} ({p['model']})",
        f"{p['brand'].upper()} {p['model'].replace('-', '')} {p['category']} {spec}",
    ])


def random_date(rng: random.Random, start: date = date(2025, 1, 1), days: int = 700) -> date:
    return start + timedelta(days=rng.randint(0, days))


# --- column_type: what kind of data is in this column? -----------------------

def pick(options: list, style: float):
    """Choose one format per column, so every value in a column looks alike."""
    return options[int(style * len(options))]


def date_text(rng: random.Random, style: float) -> str:
    return random_date(rng).strftime(pick(["%Y-%m-%d", "%d.%m.%Y", "%m/%d/%Y", "%d %b %Y"], style))


# type -> (description, typical headers, value maker taking (rng, column style))
COLUMN_TYPES: dict[str, tuple[str, list[str], Callable[[random.Random, float], str]]] = {
    "date": ("Calendar dates", ["order_date", "datum", "created_on"], date_text),
    "timestamp": ("Date and time of day", ["created_at", "ts", "zeitstempel"],
                  lambda r, s: f"{random_date(r).isoformat()}T{r.randint(0, 23):02d}:{r.randint(0, 59):02d}:00Z"),
    "money": ("Monetary amounts", ["price", "betrag", "total_eur"],
              lambda r, s: pick(["€ {:.2f}", "{:.2f} EUR", "EUR {:.2f}", "{:.2f}"], s).format(r.uniform(1, 900))),
    "percentage": ("Percentages or rates", ["discount", "rabatt_pct", "vat_rate"],
                   lambda r, s: pick(["{:.0f}%", "{:.1f} %", "{:.0f} pct"], s).format(r.uniform(0, 60))),
    "quantity": ("Counts of items", ["qty", "menge", "units"], lambda r, s: str(r.randint(1, 250))),
    "postal_code": ("Postal codes", ["plz", "zip", "postcode"], lambda r, s: r.choice(PLACES)[1]),
    "country": ("Country names or codes", ["country", "land", "ship_to_country"],
                lambda r, s: r.choice(ISO2 if s < 0.5 else COUNTRY_NAMES)),
    "city": ("City names", ["city", "ort", "stadt"], lambda r, s: r.choice(PLACES)[0]),
    "url": ("Web addresses", ["url", "link", "product_page"],
            lambda r, s: f"https://shop.example/{pick(['p', 'item', 'artikel'], s)}/{r.randint(1000, 99999)}"),
    "product_code": ("Product or article codes", ["sku", "artikelnr", "model"], lambda r, s: product(r)["model"]),
    "boolean": ("Yes/no flags", ["in_stock", "aktiv", "is_returned"],
                lambda r, s: r.choice(pick([["true", "false"], ["ja", "nein"], ["Y", "N"]], s))),
    "currency_code": ("ISO currency codes", ["currency", "waehrung", "ccy"], lambda r, s: r.choice(CURRENCIES)),
    "measurement": ("Physical measurements with a unit", ["weight", "gewicht", "size"],
                    lambda r, s: pick(["{:.1f} kg", "{:.0f} g", "{:.0f} cm", "{:.1f} l"], s).format(r.uniform(0.1, 90))),
    "free_text": ("Free-form text comments", ["comment", "notiz", "remarks"],
                  lambda r, s: r.choice(["deliver to back entrance", "box slightly dented", "reorder in spring",
                                         "Kunde wünscht Rückruf", "gift wrap please", "second delivery attempt"])),
}


def column_type(rng: random.Random):
    label = rng.choice(list(COLUMN_TYPES))
    _, names, make = COLUMN_TYPES[label]
    roll = rng.random()
    if roll < 0.45:
        name = rng.choice(names)
    elif roll < 0.9:
        name = rng.choice([f"col_{rng.randint(1, 40)}", f"field{rng.randint(1, 40)}", f"Unnamed: {rng.randint(1, 40)}"])
    else:  # a misleading header: the values decide
        name = rng.choice(COLUMN_TYPES[rng.choice([t for t in COLUMN_TYPES if t != label])][1])
    style = rng.random()
    values = [make(rng, style) for _ in range(6)]
    if rng.random() < 0.15:
        values[rng.randrange(len(values))] = rng.choice(["", "n/a", "NULL"])
    state = {"column_header": name, "sample_values": values}
    questions = {"type": {
        "type": "choice",
        "instructions": "What kind of data does this column hold? Judge by the values; headers can be wrong.",
        "criteria": {t: desc for t, (desc, _, _) in COLUMN_TYPES.items()},
    }}
    return state, questions, {"type": label}


# --- product_match: are two listings the same product? -----------------------

def listing(p: dict[str, Any], rng: random.Random) -> dict[str, Any]:
    return {"title": title(p, rng), "brand": p["brand"] if rng.random() < 0.8 else "",
            "price_eur": round(p["price"] * rng.uniform(0.9, 1.1), 2), "shop": rng.choice(["shop A", "shop B", "shop C"])}


def product_match(rng: random.Random):
    a = product(rng)
    same = rng.random() < 0.5
    if same:
        b = dict(a)
    else:
        b = dict(a)
        kind = rng.random()
        if kind < 0.4:  # same series, different spec and model number
            b["value"] = rng.choice([v for v in CATEGORIES[a["category"]][2] if v != a["value"]])
            b["model"] = f"{a['model'][:-1]}{rng.choice([c for c in 'ABCX' if c != a['model'][-1]])}"
        elif kind < 0.7:  # same model number pattern, different brand
            b["brand"] = rng.choice([x for x in BRANDS if x != a["brand"]])
        else:  # same brand and category, unrelated model
            b = product(rng, a["category"])
            b["brand"] = a["brand"]
            if b["model"] == a["model"]:
                b["model"] = b["model"][:-1] + ("A" if b["model"][-1] != "A" else "B")
    state = {"listing_a": listing(a, rng), "listing_b": listing(b, rng)}
    questions = {"same_product": {
        "type": "noul",
        "instructions": "Do these two shop listings sell the same product (same brand, model and specification)? "
                        "Formatting, word order, abbreviations and small price differences don't matter.",
    }}
    return state, questions, {"same_product": same}


# --- value_check: is this value valid for the column? ------------------------

def value_check(rng: random.Random):
    column, description, valid, invalid = rng.choice(VALUE_RULES)
    ok = rng.random() < 0.5
    value = valid(rng) if ok else invalid(rng)
    state = {"column": column, "rule": description, "value": value}
    questions = {"valid": {"type": "noul", "instructions": "Does the value satisfy the column's rule?"}}
    return state, questions, {"valid": ok}


def bad_date(rng: random.Random) -> str:
    d = random_date(rng)
    return rng.choice([f"{d.year}-02-30", f"{d.year}-13-{d.day:02d}", d.strftime("%d.%m.%Y"), d.strftime("%Y/%m/%d")])


VALUE_RULES = [
    ("quantity", "Whole number of units ordered, at least 1",
     lambda r: str(r.randint(1, 500)), lambda r: r.choice(["0", "-3", "2.5", "zwei", "1e3x"])),
    ("discount_pct", "Discount in percent, between 0 and 100",
     lambda r: f"{r.uniform(0, 100):.1f}", lambda r: r.choice(["130", "-5", "250.0", "half"])),
    ("order_date", "A real calendar date written as YYYY-MM-DD",
     lambda r: random_date(r).isoformat(), bad_date),
    ("country", "Two-letter ISO 3166-1 country code",
     lambda r: r.choice(ISO2), lambda r: r.choice(["Austria", "AUT", "XX", "A", "Deutschland"])),
    ("currency", "Three-letter ISO 4217 currency code",
     lambda r: r.choice(CURRENCIES), lambda r: r.choice(["Euro", "€", "EU", "DOLLAR", "FT"])),
    ("unit_price_eur", "Positive price in euros with at most two decimals",
     lambda r: f"{r.uniform(0.5, 900):.2f}", lambda r: r.choice(["-3.50", "0", "12.999", "1.2.3"])),
    ("postal_code_at", "Austrian postal code: exactly four digits",
     lambda r: str(r.choice([1010, 1030, 1100, 4020, 5020, 6020, 8010, 9020])),
     lambda r: r.choice(["10115", "103", "A-1O30", "80331"])),
    ("weight_kg", "Shipping weight in kilograms, a number between 0 and 1000",
     lambda r: f"{r.uniform(0.05, 900):.2f}", lambda r: r.choice(["-1", "1700 g", "heavy", "1500"])),
]


# --- row_issue: what, if anything, is wrong with this order row? -------------

ROW_ISSUES = {
    "ok": "Nothing is wrong with the row",
    "missing_value": "A required field is empty",
    "wrong_unit": "A value is given in a different unit than the column expects",
    "swapped_fields": "Two fields hold each other's values",
    "outlier": "A value is technically valid but implausible for this product",
    "inconsistent": "Fields contradict each other",
}


def order_row(rng: random.Random) -> dict[str, Any]:
    p = product(rng)
    qty = rng.randint(1, 12)
    ordered = random_date(rng)
    city, plz = rng.choice(PLACES)
    return {"product": f"{p['brand']} {p['category']} {p['model']}", "quantity": qty,
            "unit_price_eur": p["price"], "total_eur": round(qty * p["price"], 2), "weight_kg": p["weight"],
            "order_date": ordered.isoformat(),
            "delivery_date": (ordered + timedelta(days=rng.randint(1, 14))).isoformat(),
            "city": city, "postal_code": plz}


def row_issue(rng: random.Random):
    row = order_row(rng)
    label = rng.choice(list(ROW_ISSUES))
    if label == "missing_value":
        row[rng.choice(["product", "quantity", "unit_price_eur", "order_date"])] = ""
    elif label == "wrong_unit":
        row["weight_kg"] = f"{row['weight_kg'] * 1000:g} g"
    elif label == "swapped_fields":
        row["city"], row["postal_code"] = row["postal_code"], row["city"]
    elif label == "outlier":
        if rng.random() < 0.5:
            row["quantity"] = rng.randint(50_000, 900_000)
        else:
            row["unit_price_eur"] = 0.01
        row["total_eur"] = round(row["quantity"] * row["unit_price_eur"], 2)
    elif label == "inconsistent":
        if rng.random() < 0.5:
            row["delivery_date"] = (date.fromisoformat(row["order_date"]) - timedelta(days=rng.randint(3, 30))).isoformat()
        else:
            row["total_eur"] = round(row["total_eur"] * rng.choice([0.5, 2, 3]), 2)
    state = {"table": "order lines of a home-and-office web shop",
             "expected": "total_eur = quantity × unit_price_eur; delivery after order; weight_kg in kilograms",
             "row": row}
    questions = {"issue": {"type": "choice", "instructions": "What is wrong with this row, if anything?",
                           "criteria": ROW_ISSUES}}
    return state, questions, {"issue": label}


# --- ticket_triage: three questions about one support ticket -----------------

TEAMS = {
    "billing": "Charges, invoices, payment problems",
    "shipping": "Delivery status, delays, lost parcels",
    "returns": "Exchanges, refunds, damaged or wrong items",
    "technical": "App, website or API errors",
    "account": "Login, account settings, data requests",
}
URGENCY = ["low", "normal", "high", "critical"]

# (team, text, base urgency index, needs a human by itself)
TICKETS = [
    ("billing", "I was charged twice for order #{n}.", 2, False),
    ("billing", "Could you send me a copy of invoice {n}?", 0, False),
    ("billing", "The invoice for order #{n} shows the wrong company address.", 1, False),
    ("shipping", "Parcel {n} says delivered but nothing arrived.", 2, False),
    ("shipping", "When will order #{n} ship?", 0, False),
    ("shipping", "Can I change the delivery address for order #{n}?", 1, False),
    ("returns", "The {item} from order #{n} arrived broken, I want a refund.", 2, False),
    ("returns", "How do I exchange the {item} for another model?", 0, False),
    ("returns", "You sent me the wrong {item} (order #{n}).", 1, False),
    ("technical", "The app crashes every time I open my order history.", 1, False),
    ("technical", "Your API returns 500 for every order upload since {time}.", 2, False),
    ("technical", "The checkout page doesn't load in my browser.", 2, False),
    ("account", "Please delete my account and all data you hold about me.", 1, True),
    ("account", "The password reset email never arrives.", 1, False),
    ("account", "How do I add a colleague to our business account?", 0, False),
]
CALM = ["No rush, ", "Whenever you get a chance: ", "Just a quick question. "]
URGENT = [" Our whole warehouse team is blocked by this.", " This is the third time I'm writing, I'll go to "
          "consumer protection if this isn't fixed today.", " URGENT - we have a customer event tomorrow."]


def ticket_triage(rng: random.Random):
    team, text, urgency, human = rng.choice(TICKETS)
    body = text.format(n=rng.randint(10000, 99999), item=rng.choice(list(CATEGORIES)),
                       time=f"{rng.randint(6, 11)}:{rng.choice(['00', '15', '30'])}")
    mood = rng.random()
    if mood < 0.2:
        first = body if body.startswith("I ") else body[0].lower() + body[1:]
        body, urgency = rng.choice(CALM) + first, 0
    elif mood < 0.4:
        body, urgency = body + rng.choice(URGENT), 3
    state = {"channel": rng.choice(["email", "web form", "chat"]), "message": body}
    questions = {
        "team": {"type": "choice", "instructions": "Which team should handle this ticket?", "criteria": TEAMS},
        "urgency": {"type": "score", "instructions": "How urgent is this ticket?", "criteria": URGENCY},
        "needs_human": {"type": "noul",
                        "instructions": "Should a person look at this ticket before any automated reply? "
                                        "Yes for urgent tickets, complaints that threaten escalation, and "
                                        "requests to delete personal data."},
    }
    labels = {"team": team, "urgency": urgency, "needs_human": human or urgency >= 2}
    return state, questions, labels


FAMILIES: dict[str, Family] = {
    "column_type": column_type,
    "product_match": product_match,
    "value_check": value_check,
    "row_issue": row_issue,
    "ticket_triage": ticket_triage,
}


def build_suite(seed: int = DEV_SEED, per_family: int = 200,
                families: dict[str, Family] | None = None) -> list[Item]:
    rng = random.Random(seed)
    items: list[Item] = []
    for name, make in (families or FAMILIES).items():
        for i in range(per_family):
            state, questions, labels = make(rng)
            items.append({"id": f"{name}-{i:04d}", "family": name,
                          "request": {"state": state, "questions": questions}, "labels": labels})
    rng.shuffle(items)
    return items


def label_key(question: dict[str, Any], label: Any) -> str:
    """Labels as option keys: "true"/"false" for yes/no, the level index for scores."""
    if question["type"] == "noul":
        return "true" if label else "false"
    return str(label)


def write_jsonl(items: list[Item], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for item in items:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")


def read_jsonl(path: Path) -> list[Item]:
    with path.open(encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--out", type=Path, default=Path("data/dev.jsonl"))
    parser.add_argument("--seed", type=int, default=DEV_SEED, help="change it to generate training data")
    parser.add_argument("--per-family", type=int, default=200)
    args = parser.parse_args()
    items = build_suite(args.seed, args.per_family)
    write_jsonl(items, args.out)
    questions = sum(len(i["request"]["questions"]) for i in items)
    print(f"wrote {len(items)} requests ({questions} questions) to {args.out}")


if __name__ == "__main__":
    main()
