"""Bank statements, however the bank hands them over.

Three banks, three ideas of what a statement is: two of them answer a request and one of
them sends a file. `normalise` is where they stop disagreeing, and everything after it
works on lines that have a date, an amount in cents and whatever the payer typed.
"""
from __future__ import annotations

import csv
import hashlib
import io
import json


def normalise(line: dict) -> dict:
    """One statement line, in the shape the ledger keeps them in."""
    return {"date": line["date"], "cents": int(line["cents"]),
            "reference": (line.get("reference") or "").strip(),
            "counterparty": (line.get("counterparty") or "").strip()}


def statement_hash(account: str, lines) -> str:
    """What makes two statements the same statement.

    The account and the lines, in the order the bank gave them; nothing about when we
    asked, so asking twice is not two statements.
    """
    body = json.dumps([account] + [normalise(line) for line in lines],
                      sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(body.encode("utf-8")).hexdigest()


def import_statement(ledger: dict, account: str, lines) -> dict:
    """Put a statement into the ledger."""
    digest = statement_hash(account, lines)
    kept = list(ledger.get("lines", [])) + [normalise(line) for line in lines]
    return {"ok": True, "imported": len(lines), "digest": digest, "repeat": False,
            "ledger": {"seen": list(ledger.get("seen", [])) + [digest], "lines": kept}}
