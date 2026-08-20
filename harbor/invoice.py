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


def invoice_for(booking, rates, number: str, issued: dt.date, month_rates=()) -> "Invoice":
    """The nights the boat is here, at the rates that applied on the day it was booked.

    A stay of four weeks or more is a season, and a season is sold by the month: the
    marina's month rate is cheaper than thirty nights of the nightly one, which is the
    whole point of taking a season berth. Whatever is left over after the whole months
    is charged by the night.
    """
    stayed = booking_module.nights(booking.start, booking.end)
    night_cents = rate_on(rates, booking.start)
    if stayed >= SEASON_NIGHTS and month_rates:
        months, rest = divmod(stayed, MONTH_NIGHTS)
        lines = [Line("Berth %s, %d months" % (booking.berth, months), months,
                      rate_on(month_rates, booking.start))]
        if rest:
            lines.append(Line("Berth %s, %d nights" % (booking.berth, rest), rest, night_cents))
        return Invoice(number, booking.ref, tuple(lines), issued)
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


SEASON_NIGHTS = 28          # from here up, a stay is a season and is priced by the month
MONTH_NIGHTS = 30
