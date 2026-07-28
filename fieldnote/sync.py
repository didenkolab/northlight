"""Putting a phone that has been dark all day back together with the board.

Nothing here decides when to sync. It is handed what the phone has and what the server
has, and it says what the day was.
"""
from __future__ import annotations


def merge(phone: dict, server: dict) -> dict:
    """What the phone and the board together say the day was.

    A job comes from the board, so the board's version of one it knows about is the one
    that is kept, and anything the phone made while it was dark is added to it.
    """
    jobs = {job["id"]: dict(job) for job in server.get("jobs", [])}
    for job in phone.get("jobs", []):
        jobs.setdefault(job["id"], dict(job))
    return {"jobs": [jobs[key] for key in sorted(jobs)], "conflicts": []}


def queue_edit(pending: list, edit: dict) -> list:
    """An edit the crew made while the phone was dark, kept in the order they made it."""
    return list(pending) + [dict(edit)]


def apply_edits(day, pending) -> list:
    """Replay a phone's queue onto the day, oldest first.

    The order is the whole point. A job set to 'on the way' and then to 'done' is done,
    and replaying the two the other way round sends a crew back to a job they finished
    an hour ago.
    """
    by_id = {job["id"]: dict(job) for job in day}
    for edit in pending:
        job = by_id.get(edit["id"])
        if job is not None:
            job[edit["field"]] = edit["value"]
    return [by_id[key] for key in sorted(by_id)]
