"""The steps the Harbor scenarios are written in.

Every one of them calls the package and looks at what came back. Nothing here stands in
for a module or reaches inside one, so a scenario that passes is the code doing the work.
"""
import datetime as dt

from behave import given, step, then, when

from harbor import booking


def _names(text):
    """A list the way a person writes one: "A1, A2 and B7"."""
    return [part.strip() for part in text.replace(" and ", ", ").split(",") if part.strip()]


def _day(text):
    return dt.date.fromisoformat(text)


def _clock(text):
    """A time of day, on the one day the scenarios all happen to be about."""
    hour, minute = (int(part) for part in text.split(":"))
    return dt.datetime(2026, 7, 16, hour, minute)


@given("the marina has berths {names}")
def step_marina_has_berths(context, names):
    context.berths = _names(names)
    context.calendar = []
    context.holds = []
    context.result = None


@given("{boat} has berth {berth} from {start} to {end} as {ref}")
def step_has_berth(context, boat, berth, start, end, ref):
    made = booking.reserve(context.calendar,
                           booking.Booking(ref, berth, boat, _day(start), _day(end)))
    assert made["ok"], made
    context.calendar = made["calendar"]


@when("{boat} books berth {berth} from {start} to {end} as {ref}")
def step_books_berth(context, boat, berth, start, end, ref):
    context.result = booking.reserve(context.calendar,
                                     booking.Booking(ref, berth, boat, _day(start), _day(end)))
    context.calendar = context.result["calendar"]


@then("the booking is taken")
def step_booking_taken(context):
    assert context.result["ok"] is True, context.result


@then("the booking is refused because {reason}")
def step_booking_refused(context, reason):
    assert context.result["ok"] is False, context.result
    assert context.result["reason"] == reason, context.result


@then("the refusal names {ref}")
def step_refusal_names(context, ref):
    assert context.result["clash"] == ref, context.result


@then("the calendar holds {refs}")
def step_calendar_holds(context, refs):
    assert [b.ref for b in context.calendar] == _names(refs), context.calendar
