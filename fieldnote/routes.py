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


def straight_minutes(places: dict, here: str, there: str) -> int:
    """A number for a road we have no time for.

    The straight line, and then a third again, because no road is the line -- least of
    all round a fjord, where the line is water. It is a guess and the plan is allowed to
    say so; what it must not do is call it nothing.
    """
    (here_x, here_y), (there_x, there_y) = places[here], places[there]
    line = ((here_x - there_x) ** 2 + (here_y - there_y) ** 2) ** 0.5
    return int(round(line * 1.3))


def leg_minutes(roads: dict, places: dict, here: str, there: str) -> int:
    """The road if we know it, the guess if we do not."""
    known = travel_minutes(roads, here, there)
    return known if known is not None else straight_minutes(places, here, there)


def order_stops(depot: str, stops, roads: dict, places: dict) -> list:
    """Nearest first, from the depot and then from wherever the crew has got to.

    Not the shortest possible day -- that is a harder problem than the difference is
    worth on eleven stops -- but a day that never sends a van back past where it has
    already been.
    """
    remaining, order, here = sorted(stops), [], depot
    while remaining:
        nearest = min(remaining, key=lambda stop: (leg_minutes(roads, places, here, stop), stop))
        remaining.remove(nearest)
        order.append(nearest)
        here = nearest
    return order


def plan_day(depot: str, stops, roads: dict, places: dict) -> list:
    """The whole day, depot to depot.

    The van starts at the depot and has to get back to it, and a plan that stops at the
    last customer hides an hour of driving from the crew who has to do it.
    """
    return [depot] + order_stops(depot, stops, roads, places) + [depot]


def reflow(times, from_stop: str, overrun_minutes: int) -> list:
    """A job has overrun. Move the rest of the day rather than breaking it.

    Everything after the stop that ran over shifts by the same amount, which is what the
    crew is going to experience anyway; replanning the order from where they are standing
    sends them back past two customers who are already expecting them.
    """
    shifted, moving = [], False
    for entry in times:
        if moving:
            entry = {**entry, "at": entry["at"] + dt.timedelta(minutes=overrun_minutes)}
        shifted.append(entry)
        if entry["stop"] == from_stop:
            moving = True
    return shifted


def ferry_breaks(times, ferries: dict) -> list:
    """The crossings the crew would reach after the last boat of the day.

    A plan that puts a stop on the far side at five past six is not a plan, it is a night
    in a car park, so the legs that cannot be made are handed back and the day is replanned
    on one side of the water.
    """
    missed = []
    for entry in times:
        last = ferries.get(entry["stop"])
        if last is not None and entry["at"].time() > last:
            missed.append({"stop": entry["stop"], "at": entry["at"], "last_crossing": last})
    return missed
