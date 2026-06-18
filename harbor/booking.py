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
