"""Invoice numbers, the lines under them and the tax on each line.

An invoice number is the one thing in this product that cannot be reissued, reused or
guessed at: a tax office reads the sequence and a gap in it is a question.
"""
from __future__ import annotations

import dataclasses as dc


def next_number(sequence: dict, year: int, expect=None) -> dict:
    """The next invoice number for a business year, and the sequence to keep.

    Each business year has its own unbroken run: 2026-0001 up, and then 2027-0001, not
    2027-0349.

    `expect` is the last number the caller believes was handed out. Two invoices raised
    in the same minute both read the sequence, both saw 41, and both wrote 42; passing
    back what was read turns the second one into a refusal it can retry rather than a
    duplicate nobody notices until the quarter is filed.
    """
    used = sequence.get(year, 0)
    if expect is not None and expect != used:
        return {"ok": False, "reason": "the sequence has moved on", "sequence": sequence}
    return {"ok": True, "number": "%d-%04d" % (year, used + 1),
            "sequence": {**sequence, year: used + 1}}


@dc.dataclass(frozen=True)
class Line:
    """One line of an invoice, with the tax rate that line is charged at."""

    description: str
    quantity: int
    unit_cents: int
    tax_percent: int


def net_cents(line: "Line") -> int:
    return line.quantity * line.unit_cents


def tax_cents(line: "Line") -> int:
    return round(net_cents(line) * line.tax_percent / 100)


def gross_cents(line: "Line") -> int:
    return net_cents(line) + tax_cents(line)


def compose(number: str, customer: str, lines) -> dict:
    """An invoice laid out the way an accountant reads one: a table you can read down,
    with the tax shown against every line rather than gathered up at the bottom."""
    return {
        "number": number,
        "customer": customer,
        "lines": [{"description": line.description, "quantity": line.quantity,
                   "unit_cents": line.unit_cents, "tax_percent": line.tax_percent,
                   "net_cents": net_cents(line), "tax_cents": tax_cents(line),
                   "gross_cents": gross_cents(line)} for line in lines],
    }


def totals(invoice: dict) -> dict:
    """The three numbers under the table, each of them the sum of the column above it."""
    return {
        "net_cents": sum(line["net_cents"] for line in invoice["lines"]),
        "tax_cents": sum(line["tax_cents"] for line in invoice["lines"]),
        "gross_cents": sum(line["gross_cents"] for line in invoice["lines"]),
    }
