"""Berths, and which boat has one for which nights.

Every function is handed the calendar it should look at and gives back a new one; nothing
here edits what it was passed. A calendar is a plain list of Booking, oldest first, and a
stay runs from the first night to the morning the boat leaves -- so the day in `end` is
somebody else's night, not this boat's.
"""
from __future__ import annotations

import dataclasses as dc
import datetime as dt


@dc.dataclass(frozen=True)
class Booking:
    """A boat, a berth, and the nights between two dates."""

    ref: str
    berth: str
    boat: str
    start: dt.date
    end: dt.date
    status: str = "confirmed"


def nights(start: dt.date, end: dt.date) -> int:
    """How many nights a boat is charged for. Arriving and leaving on the same day is
    nought nights, not one day."""
    return (end - start).days


def overlaps(taken: "Booking", start: dt.date, end: dt.date) -> bool:
    """True when a stay from start to end wants a night the booking already has.

    Both ranges end on the morning the boat leaves, and that morning is not a night, so
    a stay beginning on the day another one ends is not a clash. Comparing the dates as
    if they were inclusive kept a berth off the market for a night nobody was in it.
    """
    return taken.start < end and start < taken.end


def reserve(calendar: list, booking: "Booking") -> dict:
    """Put a booking on the calendar, or say which booking is in the way."""
    if nights(booking.start, booking.end) < 1:
        return {"ok": False, "reason": "a stay is at least one night", "calendar": calendar}
    for taken in calendar:
        if taken.berth == booking.berth and overlaps(taken, booking.start, booking.end):
            return {"ok": False, "reason": "berth taken", "clash": taken.ref, "calendar": calendar}
    return {"ok": True, "booking": booking, "calendar": calendar + [booking]}


def free_berths(calendar: list, berths, start: dt.date, end: dt.date) -> list:
    """The berths with nothing in them for the whole of a stay."""
    taken = {b.berth for b in calendar if overlaps(b, start, end)}
    return [berth for berth in berths if berth not in taken]


def berths_from_rows(rows) -> list:
    """The marina's own spreadsheet, as berths.

    Their file writes lengths with a comma for a decimal point and keeps shore power in
    a column called `note2`, which is a column name and not a mistake: an empty cell
    means the berth has no power on it.
    """
    berths = []
    for row in rows:
        berths.append({
            "berth": row["berth"].strip(),
            "metres": float(row["length"].strip().replace(",", ".")),
            "power": bool(row.get("note2", "").strip()),
        })
    return berths


@dc.dataclass(frozen=True)
class Hold:
    """A berth kept back for a guest who is typing a card number."""

    ref: str
    berth: str
    start: dt.date
    end: dt.date
    until: dt.datetime


def hold(calendar: list, holds: list, hold_ref: str, berth: str, start: dt.date,
         end: dt.date, at: dt.datetime, minutes: int = 20) -> dict:
    """Keep a berth for twenty minutes while the guest pays for it.

    A hold that has run out is not a hold, so the ones that expired before `at` are
    dropped rather than swept up later by something that has to be remembered.

    A berth somebody else is holding is as unavailable as a berth somebody else has
    booked. Looking only at the calendar meant two guests who clicked within the same
    minute were both told to go and pay, and one of them was going to be turned away at
    the pontoon.
    """
    live = [h for h in holds if h.until > at]
    for taken in calendar:
        if taken.berth == berth and overlaps(taken, start, end):
            return {"ok": False, "reason": "berth taken", "clash": taken.ref, "holds": live}
    for other in live:
        if other.berth == berth and other.start < end and start < other.end:
            return {"ok": False, "reason": "berth held", "clash": other.ref, "holds": live}
    kept = Hold(hold_ref, berth, start, end, at + dt.timedelta(minutes=minutes))
    return {"ok": True, "hold": kept, "holds": live + [kept]}


def cancel(calendar: list, ref: str) -> dict:
    """Take a booking off the calendar. Cancelling twice is not cancelling twice as
    hard; the second time is a refusal, because somebody may have taken the nights."""
    kept = [b for b in calendar if b.ref != ref]
    if len(kept) == len(calendar):
        return {"ok": False, "reason": "no such booking", "calendar": calendar}
    return {"ok": True, "calendar": kept}
