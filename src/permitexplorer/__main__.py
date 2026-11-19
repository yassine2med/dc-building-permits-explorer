"""Command line entry: python -m permitexplorer <command> <csv> [filters]."""
from __future__ import annotations

import argparse
import sys

from .core import bar_chart, cost_by, count_by, filter_records, load


def main(argv: list[str] | None = None) -> int:
    """Run the CLI. Exit code 0 on success, 2 on bad input."""
    parser = argparse.ArgumentParser(prog="permitexplorer", description="Explore building permit data.")
    parser.add_argument("command", choices=["summary", "count", "cost"])
    parser.add_argument("csv")
    parser.add_argument("--by", default="kind", help="count: kind, ward, status, month. cost: kind, ward")
    parser.add_argument("--kind")
    parser.add_argument("--ward")
    parser.add_argument("--year", type=int)
    args = parser.parse_args(argv)
    try:
        rows = filter_records(load(args.csv), args.kind, args.ward, args.year)
        if args.command == "summary":
            print(f"Permits: {len(rows)}")
            total = sum(r.cost for r in rows)
            print(f"Declared cost: {total:,.0f}")
            print("By type:")
            print(bar_chart(count_by(rows, "kind")))
        elif args.command == "count":
            print(bar_chart(count_by(rows, args.by)))
        else:
            print(bar_chart(cost_by(rows, args.by)))
    except (ValueError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
