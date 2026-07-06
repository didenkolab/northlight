"""Invoice numbers, the lines under them and the tax on each line.

An invoice number is the one thing in this product that cannot be reissued, reused or
guessed at: a tax office reads the sequence and a gap in it is a question.
"""
from __future__ import annotations

import dataclasses as dc


def next_number(sequence: dict, year: int) -> dict:
    """The next invoice number for a business year, and the sequence to keep.

    Each business year has its own unbroken run: 2026-0001 up, and then 2027-0001, not
    2027-0349. The caller stores what it is given back rather than counting for itself,
    because two people counting is how a sequence grows a gap.
    """
    used = sequence.get(year, 0) + 1
    return {"number": "%d-%04d" % (year, used), "sequence": {**sequence, year: used}}


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
