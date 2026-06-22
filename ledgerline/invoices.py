"""Invoice numbers, the lines under them and the tax on each line.

An invoice number is the one thing in this product that cannot be reissued, reused or
guessed at: a tax office reads the sequence and a gap in it is a question.
"""
from __future__ import annotations

import dataclasses as dc


def next_number(sequence: dict, year: int) -> dict:
    """The next invoice number, and the sequence to keep for the one after it.

    The caller stores what it is given back rather than counting for itself, because two
    people counting is how a sequence grows a gap.
    """
    used = sequence.get("last", 0) + 1
    return {"number": "%d-%04d" % (year, used), "sequence": {"last": used}}
