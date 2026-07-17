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
    return {"date": line["date"], "cents": signed_cents(line),
            "reference": (line.get("reference") or "").strip(),
            "counterparty": (line.get("counterparty") or "").strip()}


def signed_cents(line: dict) -> int:
    """Money leaving the account is negative, whichever way the bank writes it.

    Two of our three put the direction in a column of its own and leave the amount
    positive, so a refund sent to a customer read as a payment received and the day's
    takings came out at twice what the practice had actually taken.
    """
    cents = int(line["cents"])
    direction = (line.get("direction") or "").strip().lower()
    if direction in ("debit", "out", "d"):
        return -abs(cents)
    if direction in ("credit", "in", "c"):
        return abs(cents)
    return cents


def statement_hash(account: str, lines) -> str:
    """What makes two statements the same statement.

    The account and the lines, in the order the bank gave them; nothing about when we
    asked, so asking twice is not two statements.
    """
    body = json.dumps([account] + [normalise(line) for line in lines],
                      sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(body.encode("utf-8")).hexdigest()


def import_statement(ledger: dict, account: str, lines) -> dict:
    """Put a statement into the ledger, once.

    Importing the same statement twice is something people do -- the connection dropped,
    the page was refreshed, the accountant was not sure it had worked -- and until this
    it produced two of everything and a reconciliation nobody could finish. The digest is
    of the statement itself, so the second import is recognised rather than merely
    tolerated.
    """
    digest = statement_hash(account, lines)
    if digest in ledger.get("seen", []):
        return {"ok": True, "imported": 0, "digest": digest, "repeat": True, "ledger": ledger}
    kept = list(ledger.get("lines", [])) + [normalise(line) for line in lines]
    return {"ok": True, "imported": len(lines), "digest": digest, "repeat": False,
            "ledger": {"seen": list(ledger.get("seen", [])) + [digest], "lines": kept}}


def lines_from_csv(text: str, columns: dict) -> list:
    """A statement that arrives as a file rather than through a door.

    `columns` says which of the file's own headings holds the date, the amount and the
    reference, because no two of them agree and the third bank changes its mind about
    the order every spring.
    """
    rows = csv.DictReader(io.StringIO(text))
    lines = []
    for row in rows:
        amount = row[columns["cents"]].strip().replace(" ", "").replace(",", ".")
        lines.append({"date": row[columns["date"]].strip(),
                      "cents": int(round(float(amount) * 100)),
                      "reference": row.get(columns.get("reference", ""), "") or "",
                      "counterparty": row.get(columns.get("counterparty", ""), "") or "",
                      "direction": row.get(columns.get("direction", ""), "") or ""})
    return lines
