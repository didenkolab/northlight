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
    note: str = ""


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


def move_crew(board: list, job_id: str, crew: str) -> dict:
    """Hand a job to another crew, if their day has room for it."""
    job = next((j for j in board if j.id == job_id), None)
    if job is None:
        return {"ok": False, "reason": "no such job", "board": board}
    moved = dc.replace(job, crew=crew)
    rest = [j for j in board if j.id != job_id]
    clash = clashes(rest, moved)
    if clash:
        return {"ok": False, "reason": "the crew is already out", "clash": clash[0].id,
                "board": board}
    return {"ok": True, "job": moved, "board": rest + [moved]}


def write_up(board: list, job_id: str, note: str, status: str = "done") -> dict:
    """The crew writes the job up from the van, before it drives off and forgets.

    Written up is finished: the note and the status move together, because a job with a
    note and no status is one the office has to ring the crew about.
    """
    job = next((j for j in board if j.id == job_id), None)
    if job is None:
        return {"ok": False, "reason": "no such job", "board": board}
    if not note.strip():
        return {"ok": False, "reason": "a write-up says something", "board": board}
    done = dc.replace(job, note=note.strip(), status=status)
    return {"ok": True, "job": done,
            "board": [done if j.id == job_id else j for j in board]}


def arrival_window(job: "Job", minutes: int = 120) -> dict:
    """The two hours we promise the customer, around the time we mean to be there.

    The planned minute sits in the middle rather than at the start, so a crew running
    half an hour early is still inside the window they were promised instead of knocking
    on a door nobody is behind yet.
    """
    middle = dt.datetime.combine(job.day, job.start)
    opens = middle - dt.timedelta(minutes=minutes // 2)
    return {"from": opens.time(), "to": (opens + dt.timedelta(minutes=minutes)).time()}


def move_to(board: list, job_id: str, day: dt.date) -> dict:
    """Move a job to another day. It leaves the day it was on.

    Both lists are made from the one board here, so a job cannot be on today and
    tomorrow at once however the phone happens to have cached them.
    """
    job = next((j for j in board if j.id == job_id), None)
    if job is None:
        return {"ok": False, "reason": "no such job", "board": board}
    moved = dc.replace(job, day=day)
    return {"ok": True, "job": moved,
            "board": [moved if j.id == job_id else j for j in board]}
