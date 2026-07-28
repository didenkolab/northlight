"""Checking a guest in from the pontoon, which is where the signal is not.

Nothing here talks to a server. A check-in made on the pontoon is put on a queue, and the
queue is handed to `flush` by whatever finds itself with a connection.
"""
from __future__ import annotations

import dataclasses as dc
import datetime as dt


@dc.dataclass(frozen=True)
class CheckIn:
    """A guest, on their boat, at a moment the phone believed in."""

    booking_ref: str
    at: dt.datetime
    by: str
    source: str = "pontoon"


def queue(pending: list, entry: "CheckIn") -> list:
    """Keep a check-in on the phone until there is something to send it to."""
    return pending + [entry]


def flush(pending: list, arrived) -> dict:
    """Send the queue. A guest the office already has is not checked in twice."""
    seen = list(arrived)
    applied = []
    for entry in pending:
        if entry.booking_ref in seen:
            continue
        seen.append(entry.booking_ref)
        applied.append(entry)
    return {"ok": True, "applied": applied, "arrived": seen, "pending": []}
