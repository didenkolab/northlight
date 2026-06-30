"""Charging a card for a booking, and giving the money back.

The ledger is a list of Charge, oldest first, and a refund is a charge with a negative
amount rather than a second kind of thing: whatever is in the list for a booking always
adds up to what the guest is really out of pocket.
"""
from __future__ import annotations

import dataclasses as dc


@dc.dataclass(frozen=True)
class Charge:
    """One movement of money for one booking."""

    reference: str
    booking_ref: str
    amount_cents: int


def capture(ledger: list, booking_ref: str, amount_cents: int, reference: str) -> dict:
    """Charge the card when the booking is confirmed."""
    if amount_cents <= 0:
        return {"ok": False, "reason": "nothing to charge", "ledger": ledger}
    charge = Charge(reference, booking_ref, amount_cents)
    return {"ok": True, "charge": charge, "ledger": ledger + [charge]}


def charged_cents(ledger: list, booking_ref: str) -> int:
    """What the guest is out of pocket for a booking, refunds included."""
    return sum(c.amount_cents for c in ledger if c.booking_ref == booking_ref)


def charges_for(ledger: list, booking_ref: str) -> list:
    """Every movement of money for a booking, oldest first."""
    return [c for c in ledger if c.booking_ref == booking_ref]


def start(pending: dict, booking_ref: str, token: str) -> dict:
    """The guest leaves for the bank's own page. `token` is what will come back."""
    return {"ok": True, "pending": {**pending, token: booking_ref}}


def resume(pending: dict, token: str) -> dict:
    """Hand the guest back to the booking they went away to pay for.

    The bank's page returns them to us with nothing but the token, and a guest who comes
    back to the wrong booking -- or to a list -- has to work out for themselves whether
    they paid.
    """
    if token not in pending:
        return {"ok": False, "reason": "unknown token"}
    return {"ok": True, "booking_ref": pending[token]}
