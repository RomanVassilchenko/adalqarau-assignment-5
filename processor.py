"""Summarize synthetic procurement records by year for reproducible research."""

import argparse
import csv
import re
from collections import defaultdict
from datetime import date
from pathlib import Path

FIELDS = ("contract_id", "contract_date", "amount_kzt")
OUTPUT_FIELDS = ("year", "record_count", "amount_total_kzt")


def summarize(source):
    reader = csv.DictReader(source)
    if reader.fieldnames != list(FIELDS):
        raise ValueError(f"CSV header must be: {','.join(FIELDS)}")
    totals = defaultdict(lambda: [0, 0])
    seen = set()
    for line, row in enumerate(reader, 2):
        identifier = (row["contract_id"] or "").strip()
        if not identifier or identifier in seen:
            raise ValueError(f"line {line}: contract_id must be nonempty and unique")
        seen.add(identifier)
        if None in row or any(value is None for value in row.values()):
            raise ValueError(f"line {line}: expected exactly three CSV fields")
        try:
            if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", row["contract_date"]):
                raise ValueError
            year = date.fromisoformat(row["contract_date"]).year
            amount = int(row["amount_kzt"])
        except (TypeError, ValueError) as exc:
            raise ValueError(f"line {line}: invalid date or amount") from exc
        if amount < 0 or str(amount) != row["amount_kzt"]:
            raise ValueError(f"line {line}: amount_kzt must be a nonnegative integer")
        totals[year][0] += 1
        totals[year][1] += amount
    return [(year, *totals[year]) for year in sorted(totals)]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    if args.input.resolve() == args.output.resolve() or (
        args.output.exists() and args.input.samefile(args.output)
    ):
        parser.error("input and output must be different files")
    with args.input.open(newline="", encoding="utf-8") as source:
        try:
            rows = summarize(source)
        except ValueError as exc:
            parser.error(str(exc))
    with args.output.open("w", newline="", encoding="utf-8") as target:
        writer = csv.writer(target, lineterminator="\n")
        writer.writerow(OUTPUT_FIELDS)
        writer.writerows(rows)


if __name__ == "__main__":
    main()
