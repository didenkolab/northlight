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
