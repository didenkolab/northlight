"""What a stay costs, and the invoice that says so.

Money is in whole cents, everywhere, because a marina that prices a season in fractions
of a cent is a marina with a rounding argument to have with an accountant.
"""
from __future__ import annotations

import dataclasses as dc
import datetime as dt

from harbor import booking as booking_module


@dc.dataclass(frozen=True)
class Line:
    """One line of an invoice: what it is for, how many, and what one costs."""

    description: str
    quantity: int
    unit_cents: int


@dc.dataclass(frozen=True)
class Invoice:
    """An invoice as the guest gets it."""

    number: str
    booking_ref: str
    lines: tuple
    issued: dt.date
    currency: str = "EUR"


def line_cents(line: "Line") -> int:
    return line.quantity * line.unit_cents


def total_cents(invoice: "Invoice") -> int:
    return sum(line_cents(line) for line in invoice.lines)


def invoice_for(booking, night_cents: int, number: str, issued: dt.date) -> "Invoice":
    """One line, for the nights the boat is here."""
    stayed = booking_module.nights(booking.start, booking.end)
    line = Line("Berth %s, %d nights" % (booking.berth, stayed), stayed, night_cents)
    return Invoice(number, booking.ref, (line,), issued)
