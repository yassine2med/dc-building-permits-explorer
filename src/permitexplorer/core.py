"""Load building permit records from CSV and summarize them."""
from __future__ import annotations

import csv
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import date
from pathlib import Path

REQUIRED = ("permit_id", "type", "ward", "status", "issued", "cost")


@dataclass(frozen=True)
class PermitRecord:
    permit_id: str
    kind: str
    ward: str
    status: str
    issued: date
    cost: float


def load(path: str | Path) -> list[PermitRecord]:
    """Read permits from CSV. Raises ValueError with the line number on a bad row."""
    with open(path, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        missing = [c for c in REQUIRED if c not in (reader.fieldnames or [])]
        if missing:
            raise ValueError(f"missing columns: {', '.join(missing)}")
        rows = []
        for line, row in enumerate(reader, start=2):
            try:
                rows.append(PermitRecord(row["permit_id"].strip(), row["type"].strip(), row["ward"].strip(),
                                         row["status"].strip(), date.fromisoformat(row["issued"]),
                                         float(row["cost"] or 0)))
            except ValueError as exc:
                raise ValueError(f"line {line}: {exc}") from exc
    return rows


def filter_records(rows: list[PermitRecord], kind: str | None = None, ward: str | None = None,
                   year: int | None = None) -> list[PermitRecord]:
    """Keep rows matching every given filter (case-insensitive for text)."""
    out = rows
    if kind:
        out = [r for r in out if r.kind.lower() == kind.lower()]
    if ward:
        out = [r for r in out if r.ward.lower() == ward.lower()]
    if year:
        out = [r for r in out if r.issued.year == year]
    return out


def count_by(rows: list[PermitRecord], field: str) -> list[tuple[str, int]]:
    """Count rows by 'kind', 'ward', 'status' or 'month' (YYYY-MM). Sorted by count, then name."""
    if field == "month":
        keys = [r.issued.strftime("%Y-%m") for r in rows]
    elif field in {"kind", "ward", "status"}:
        keys = [getattr(r, field) for r in rows]
    else:
        raise ValueError(f"cannot group by '{field}'")
    items = Counter(keys).items()
    if field == "month":
        return sorted(items)
    return sorted(items, key=lambda kv: (-kv[1], kv[0]))


def cost_by(rows: list[PermitRecord], field: str) -> list[tuple[str, float]]:
    """Total declared cost by 'kind' or 'ward', largest first."""
    if field not in {"kind", "ward"}:
        raise ValueError(f"cannot group cost by '{field}'")
    totals: dict[str, float] = defaultdict(float)
    for r in rows:
        totals[getattr(r, field)] += r.cost
    return sorted(totals.items(), key=lambda kv: (-kv[1], kv[0]))


def bar_chart(pairs: list[tuple[str, float]], width: int = 30) -> str:
    """Text bar chart, scaled so the largest value fills `width`."""
    if not pairs:
        return "(no data)"
    top = max(v for _, v in pairs)
    label_w = max(len(k) for k, _ in pairs)
    lines = []
    for k, v in pairs:
        bar = "#" * (round(v / top * width) if top else 0)
        shown = f"{v:,.0f}"
        lines.append(f"{k:<{label_w}}  {bar:<{width}}  {shown}")
    return "\n".join(lines)
