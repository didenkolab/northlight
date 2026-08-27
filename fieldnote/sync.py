"""Putting a phone that has been dark all day back together with the board.

Nothing here decides when to sync. It is handed what the phone has and what the server
has, and it says what the day was.
"""
from __future__ import annotations


def merge(phone: dict, server: dict) -> dict:
    """What the phone and the board together say the day was.

    The fields split rather than one side winning the whole job. Letting the server win
    outright lost a crew their whole afternoon: eleven jobs they had finished on the
    mountain road came back as still planned, because the board had never heard
    otherwise and the board was the record of truth.

    Where the two disagree the disagreement is still reported, so the dispatcher can see
    what was decided for them. A job's photographs come along with it.
    """
    jobs = {job["id"]: dict(job) for job in server.get("jobs", [])}
    conflicts = []
    for job in phone.get("jobs", []):
        theirs = jobs.get(job["id"])
        if theirs is None:
            jobs[job["id"]] = dict(job)
            continue
        merged = dict(theirs)
        for field in PHONE_WINS:
            if field in job:
                merged[field] = job[field]
        for field in SERVER_WINS:
            if field in theirs:
                merged[field] = theirs[field]
        if theirs.get("status") != job.get("status"):
            conflicts.append({"id": job["id"], "phone": job.get("status"),
                              "server": theirs.get("status")})
        jobs[job["id"]] = merged
    return {"jobs": [jobs[key] for key in sorted(jobs)], "conflicts": conflicts,
            "photos": {key: photos_for(phone, server, key) for key in sorted(jobs)}}


# What each side is the authority on. The crew standing in somebody's garden knows
# whether the work is done; the dispatcher at a desk knows whose job it is and which day
# it is on. Nothing is on both lists, and anything on neither keeps the server's value.
PHONE_WINS = ("status", "note", "finished_at", "signature")
SERVER_WINS = ("crew", "day", "start", "address", "customer")


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


def photos_for(phone: dict, server: dict, job_id: str) -> list:
    """The photographs of a job, from wherever they have got to.

    The newest one on the phone may still be going up when the merge runs, so it is left
    for the next sync rather than recorded as arrived and then never sent.
    """
    kept = {photo["id"]: photo for photo in server.get("photos", [])
            if photo["job"] == job_id}
    on_phone = [photo for photo in phone.get("photos", []) if photo["job"] == job_id]
    for photo in on_phone[:-1]:
        kept.setdefault(photo["id"], photo)
    return [kept[key] for key in sorted(kept)]
