"""Tax rates, the quarter a day falls in, and closing one.

A closed quarter is the point of the module: once the return has gone to the tax office,
what it was made of has to stay what it was made of.
"""
from __future__ import annotations

import datetime as dt


def period_of(day: dt.date) -> str:
    """The quarter a day belongs to.

    January to March is the first quarter, and that includes the thirty-first of March.
    Dividing the month number by three put the last day of every quarter into the next
    one, which is only wrong four days a year and is wrong on the four days an accountant
    is looking.
    """
    return "%d-Q%d" % (day.year, (day.month - 1) // 3 + 1)


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


def close_period(ledger: dict, period: str) -> dict:
    """Close a quarter. Closing one that is already closed changes nothing."""
    closed = sorted(set(ledger.get("closed", [])) | {period})
    return {"ok": True, "ledger": {**ledger, "closed": closed}}


def book(ledger: dict, entry: dict) -> dict:
    """Put an entry in the ledger, unless its quarter has gone to the tax office.

    The refusal names the period rather than saying no, because the accountant's next
    move is to date it into the open quarter and they should not have to work out which
    one that is.
    """
    period = period_of(entry["date"])
    if period in ledger.get("closed", []):
        return {"ok": False, "reason": "%s is closed" % period, "period": period,
                "ledger": ledger}
    return {"ok": True, "period": period,
            "ledger": {**ledger, "entries": list(ledger.get("entries", [])) + [entry]}}


def rate_on(rates, day: dt.date) -> float:
    """The tax rate that applied on the day of the invoice.

    A rate that changes in January does not change what was owed in December, and a
    quarter reopened to correct one line must come out at the same total it did before.
    """
    applicable = [(start, percent) for start, percent in rates if start <= day]
    if not applicable:
        raise ValueError("no rate applies on %s" % day)
    return max(applicable)[1]
