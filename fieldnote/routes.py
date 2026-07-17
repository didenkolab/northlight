"""Putting a crew's stops into an order the day can actually be driven in.

Distances are in minutes, because a crew asks how long it takes and never how far it is.
`roads` holds the pairs we have a real time for; everything else is guessed, and the
guess says out loud that it is one.
"""
from __future__ import annotations

import datetime as dt


def travel_minutes(roads: dict, here: str, there: str):
    """How long the road between two stops takes, or None if we have never driven it."""
    if (here, there) in roads:
        return roads[(here, there)]
    if (there, here) in roads:
        return roads[(there, here)]
    return None


def order_stops(depot: str, stops, roads: dict) -> list:
    """Nearest first, from the depot and then from wherever the crew has got to.

    Not the shortest possible day -- that is a harder problem than the difference is
    worth on eleven stops -- but a day that never sends a van back past where it has
    already been.
    """
    remaining, order, here = list(stops), [], depot
    while remaining:
        remaining.sort()
        nearest = min(remaining, key=lambda stop: (travel_minutes(roads, here, stop) or 999, stop))
        remaining.remove(nearest)
        order.append(nearest)
        here = nearest
    return order
