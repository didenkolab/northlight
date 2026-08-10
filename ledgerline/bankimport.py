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


def match(lines, invoices) -> dict:
    """Pair the bank's lines with the invoices they pay.

    The amount has to be right, and then the reference the payer typed has to name the
    invoice. Anything that needs more cleverness than that is left unmatched on purpose:
    a wrong pairing costs a person an hour to find and a right one saves them a minute.
    """
    left = list(invoices)
    matched, unmatched = [], []
    for index, line in enumerate(lines):
        found = None
        for invoice in left:
            if invoice["cents"] != line["cents"]:
                continue
            if invoice["number"] not in (line.get("reference") or ""):
                continue
            found = invoice
            break
        if found is None:
            unmatched.append(index)
        else:
            left.remove(found)
            matched.append({"line": index, "invoice": found["number"]})
    return {"matched": matched, "unmatched": unmatched}


def match_by_hand(result: dict, line_index: int, invoice_number: str) -> dict:
    """A pairing a person made, which the importer would not have guessed.

    Half a practice's payments arrive with the wrong reference or none at all, and the
    person who knows it is Bergstrom paying three invoices at once should be able to say
    so once rather than argue with a matcher.
    """
    if line_index not in result["unmatched"]:
        return {"ok": False, "reason": "that line is already matched", **result}
    return {"ok": True,
            "matched": result["matched"] + [{"line": line_index, "invoice": invoice_number,
                                             "by_hand": True}],
            "unmatched": [i for i in result["unmatched"] if i != line_index]}
