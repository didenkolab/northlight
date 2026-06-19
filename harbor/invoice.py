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


def invoice_for(booking, rates, number: str, issued: dt.date) -> "Invoice":
    """One line, for the nights the boat is here, at the rate on the day it was booked."""
    stayed = booking_module.nights(booking.start, booking.end)
    night_cents = rate_on(rates, booking.start)
    line = Line("Berth %s, %d nights" % (booking.berth, stayed), stayed, night_cents)
    return Invoice(number, booking.ref, (line,), issued)


def rate_on(rates, day: dt.date) -> int:
    """The rate the marina was charging on that day.

    `rates` is a list of (from_date, cents) in any order, and the newest one that had
    already started on `day` is the one that applies. A price change in August is not
    allowed to reprice a booking made in June, which is what happens if the invoice
    reaches for whatever the current rate happens to be.
    """
    applicable = [(start, cents) for start, cents in rates if start <= day]
    if not applicable:
        raise ValueError("no rate applies on %s" % day)
    return max(applicable)[1]
