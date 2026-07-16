"""What a crew is going to today, and in what order.

A board is a list of Job. Everything here takes one and gives back another; the
dispatcher's screen is somewhere else's problem.
"""
from __future__ import annotations

import dataclasses as dc
import datetime as dt


@dc.dataclass(frozen=True)
class Job:
    """One visit: whose it is, which day, when it starts and how long it is meant to take."""

    id: str
    crew: str
    day: dt.date
    start: dt.time
    minutes: int
    address: str
    status: str = "planned"


def ends(job: "Job") -> dt.time:
    """When the crew is meant to be back in the van."""
    return (dt.datetime.combine(job.day, job.start) + dt.timedelta(minutes=job.minutes)).time()


def day_list(board: list, crew: str, day: dt.date) -> list:
    """One crew's day, in the order it is meant to happen.

    Sorted by the clock and then by job id, so two jobs planned for the same minute come
    out in the same order every time the crew opens the phone.
    """
    theirs = [job for job in board if job.crew == crew and job.day == day]
    return sorted(theirs, key=lambda job: (job.start, job.id))


def clashes(board: list, job: "Job") -> list:
    """The jobs already on this crew's day that want the same minutes.

    A job that finishes exactly as the next one starts is not a clash; it is a tight day.
    """
    same_day = [other for other in board
                if other.crew == job.crew and other.day == job.day and other.id != job.id]
    return [other for other in same_day
            if other.start < ends(job) and job.start < ends(other)]


def assign(board: list, job: "Job") -> dict:
    """Put a job on a crew. Two o'clock belongs to one job, not two.

    The dispatcher gets the job that is in the way rather than a refusal, because their
    next question is always which one.
    """
    clash = clashes(board, job)
    if clash:
        return {"ok": False, "reason": "the crew is already out", "clash": clash[0].id,
                "board": board}
    return {"ok": True, "job": job, "board": board + [job]}
