"""Tax rates, the quarter a day falls in, and closing one.

A closed quarter is the point of the module: once the return has gone to the tax office,
what it was made of has to stay what it was made of.
"""
from __future__ import annotations

import datetime as dt


def period_of(day: dt.date) -> str:
    """The quarter a day belongs to."""
    return "%d-Q%d" % (day.year, day.month // 3 + 1)


def rounding(lines, mode: str) -> int:
    """The tax on an invoice, rounded the way the invoice's country rounds it.

    Some countries round the tax on every line and add the results up; some add the lines
    up per rate and round once. The two answers differ by a cent often enough that an
    accountant notices, and which one is right is not ours to choose.
    """
    if mode == "per-line":
        return sum(round(line["net_cents"] * line["tax_percent"] / 100) for line in lines)
    if mode == "per-invoice":
        by_rate = {}
        for line in lines:
            by_rate[line["tax_percent"]] = by_rate.get(line["tax_percent"], 0) + line["net_cents"]
        return sum(round(net * rate / 100) for rate, net in sorted(by_rate.items()))
    raise ValueError("unknown rounding mode %r" % mode)
