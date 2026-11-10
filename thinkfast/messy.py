"""Generate a messy product catalogue for the "Put it to work" level.

Writes a CSV merged from three fictional shops, with duplicate listings in
different formats, values in the wrong unit, implausible prices, invalid
codes and gaps. A separate answer key lists every planted problem, so your
tool can report how much it fixed and at what error rate.

    uv run python -m thinkfast.messy --out data/catalogue_messy.csv
"""

from __future__ import annotations

import argparse
import csv
import json
import random
from pathlib import Path

from .suite import CURRENCIES, product, random_date, title

FIELDS = ["row_id", "shop", "title", "brand", "price", "currency", "weight_kg", "in_stock", "updated"]


def clean_row(rng: random.Random, p: dict, shop: str) -> dict[str, str]:
    updated = random_date(rng)
    return {"shop": shop, "title": title(p, rng), "brand": p["brand"],
            "price": f"{p['price'] * rng.uniform(0.92, 1.08):.2f}", "currency": "EUR",
            "weight_kg": f"{p['weight']:g}", "in_stock": rng.choice(["true", "false", "ja", "nein", "1", "0"]),
            "updated": updated.strftime(rng.choice(["%Y-%m-%d", "%d.%m.%Y"]))}


def corrupt(rng: random.Random, row: dict[str, str]) -> str:
    """Plant one problem in the row and return its name."""
    problem = rng.choice(["wrong_unit", "price_outlier", "invalid_currency", "missing_value"])
    if problem == "wrong_unit":
        row["weight_kg"] = f"{float(row['weight_kg']) * 1000:g} g"
    elif problem == "price_outlier":
        row["price"] = rng.choice(["0.01", f"{float(row['price']) * 100:.2f}"])
    elif problem == "invalid_currency":
        row["currency"] = rng.choice(["€", "Euro", "EU", "E"])
    else:
        row[rng.choice(["brand", "price", "title"])] = ""
    return problem


def build(seed: int, products: int) -> tuple[list[dict[str, str]], dict]:
    rng = random.Random(seed)
    rows: list[dict[str, str]] = []
    product_of_row: list[int] = []
    seen: set[tuple[str, str]] = set()
    for pid in range(products):
        p = product(rng)
        while (p["brand"], p["model"]) in seen:  # distinct products must not look like duplicates
            p = product(rng)
        seen.add((p["brand"], p["model"]))
        for shop in rng.sample(["shop A", "shop B", "shop C"], k=rng.choice([1, 1, 2, 3])):
            rows.append(clean_row(rng, p, shop))
            product_of_row.append(pid)
    order = list(range(len(rows)))
    rng.shuffle(order)
    rows = [rows[i] for i in order]
    product_of_row = [product_of_row[i] for i in order]
    problems: dict[str, str] = {}
    for i, row in enumerate(rows):
        row["row_id"] = f"r{i:04d}"
        if rng.random() < 0.15:
            problems[row["row_id"]] = corrupt(rng, row)
    groups: dict[int, list[str]] = {}
    for row, pid in zip(rows, product_of_row):
        groups.setdefault(pid, []).append(row["row_id"])
    key = {"duplicate_groups": [ids for ids in groups.values() if len(ids) > 1], "problems": problems,
           "note": f"valid currencies: {', '.join(CURRENCIES)}"}
    return rows, key


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--out", type=Path, default=Path("data/catalogue_messy.csv"))
    parser.add_argument("--key", type=Path, default=Path("data/catalogue_key.json"))
    parser.add_argument("--seed", type=int, default=13)
    parser.add_argument("--products", type=int, default=300)
    args = parser.parse_args()
    rows, key = build(args.seed, args.products)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    args.key.write_text(json.dumps(key, indent=1, ensure_ascii=False))
    print(f"wrote {len(rows)} rows to {args.out}; {len(key['duplicate_groups'])} duplicate groups and "
          f"{len(key['problems'])} planted problems in {args.key}")


if __name__ == "__main__":
    main()
