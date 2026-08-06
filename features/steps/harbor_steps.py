"""The steps the Harbor scenarios are written in.

Every one of them calls the package and looks at what came back. Nothing here stands in
for a module or reaches inside one, so a scenario that passes is the code doing the work.
"""
import datetime as dt

from behave import given, step, then, when

from harbor import booking, checkin, invoice, payments


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
    context.rates = []
    context.ledger = []
    context.tokens = {}
    context.queue = []
    context.arrived = []
    context.codes = {}
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


@when("the office asks which berths are free from {start} to {end}")
def step_asks_free(context, start, end):
    context.free = booking.free_berths(context.calendar, context.berths, _day(start), _day(end))


@then("the free berths are {names}")
def step_free_berths_are(context, names):
    assert context.free == _names(names), context.free


SPREADSHEET = [{"berth": " A1 ", "length": "9,5", "note2": "16A"},
               {"berth": "A2", "length": "12,0", "note2": ""},
               {"berth": "B7", "length": "7,25", "note2": " 10A "}]


@when("the marina's berth spreadsheet is imported")
def step_import_spreadsheet(context):
    context.read_berths = booking.berths_from_rows(SPREADSHEET)


@then("the berths read are {names}")
def step_berths_read(context, names):
    assert [b["berth"] for b in context.read_berths] == _names(names), context.read_berths


@then("berth {berth} has shore power")
def step_has_power(context, berth):
    found = next(b for b in context.read_berths if b["berth"] == berth)
    assert found["power"] is True, found


@then("berth {berth} has no shore power")
def step_has_no_power(context, berth):
    found = next(b for b in context.read_berths if b["berth"] == berth)
    assert found["power"] is False, found


@step("{boat} holds berth {berth} from {start} to {end} as {ref} at {clock}")
def step_holds_berth(context, boat, berth, start, end, ref, clock):
    context.result = booking.hold(context.calendar, context.holds, ref, berth,
                                  _day(start), _day(end), _clock(clock))
    context.holds = context.result["holds"]


@then("the hold is taken")
def step_hold_taken(context):
    assert context.result["ok"] is True, context.result


@then("the hold runs out at {clock}")
def step_hold_runs_out(context, clock):
    assert context.result["hold"].until == _clock(clock), context.result


@then("the hold is refused because {reason}")
def step_hold_refused(context, reason):
    assert context.result["ok"] is False, context.result
    assert context.result["reason"] == reason, context.result


@when("booking {ref} is cancelled")
def step_cancel_booking(context, ref):
    context.result = booking.cancel(context.calendar, ref)
    assert context.result["ok"], context.result
    context.calendar = context.result["calendar"]


@then("the free berths from {start} to {end} are {names}")
def step_free_between(context, start, end, names):
    free = booking.free_berths(context.calendar, context.berths, _day(start), _day(end))
    assert free == _names(names), free


@then("the cancellation says it gave back berth {berth}")
def step_cancellation_freed(context, berth):
    assert context.result["freed"]["berth"] == berth, context.result


@given("the marina charges {cents:d} cents a night from {day}")
def step_night_rate(context, cents, day):
    context.rates = context.rates + [(_day(day), cents)]


@when("the invoice for {ref} is made out as {number}")
def step_invoice_for(context, ref, number):
    made = next(b for b in context.calendar if b.ref == ref)
    context.invoice = invoice.invoice_for(made, context.rates, number, _day("2026-07-06"))


@then("the invoice totals {cents:d} cents")
def step_invoice_totals(context, cents):
    assert invoice.total_cents(context.invoice) == cents, context.invoice


@then("the invoice is numbered {number}")
def step_invoice_numbered(context, number):
    assert context.invoice.number == number, context.invoice


@step("{ref} is confirmed for {cents:d} cents")
def step_confirmed(context, ref, cents):
    context.result = payments.capture(context.ledger, ref, cents,
                                      "ch-%d" % (len(context.ledger) + 1), ref)
    context.ledger = context.result["ledger"]


@then("the card has been charged {cents:d} cents for {ref}")
def step_card_charged(context, cents, ref):
    assert payments.charged_cents(context.ledger, ref) == cents, context.ledger


@step("{ref} is confirmed for {cents:d} cents with intent {intent}")
def step_confirmed_with_intent(context, ref, cents, intent):
    context.result = payments.capture(context.ledger, ref, cents,
                                      "ch-%d" % (len(context.ledger) + 1), intent)
    context.ledger = context.result["ledger"]


@then("the ledger holds {count:d} charges")
def step_ledger_holds(context, count):
    assert len(context.ledger) == count, context.ledger


@given("{ref} sends the guest away to pay with token {token}")
def step_sends_away(context, ref, token):
    context.tokens = payments.start(context.tokens, ref, token)["pending"]


@when("the guest comes back with token {token}")
def step_comes_back(context, token):
    context.result = payments.resume(context.tokens, token)


@then("they are put back on booking {ref}")
def step_put_back_on(context, ref):
    assert context.result["ok"], context.result
    assert context.result["booking_ref"] == ref, context.result


@given("the phone has no signal")
def step_no_signal(context):
    context.queue = []
    context.arrived = []


@step("{who} checks {ref} in at {clock}")
def step_checks_in(context, who, ref, clock):
    context.queue = checkin.queue(context.queue, checkin.CheckIn(ref, _clock(clock), who))


@then("the phone is holding {refs}")
def step_phone_holding(context, refs):
    assert [entry.booking_ref for entry in context.queue] == _names(refs), context.queue


@step("the phone finds a signal")
def step_finds_signal(context):
    context.result = checkin.flush(context.queue, context.arrived)
    context.arrived = context.result["arrived"]
    context.queue = context.result["pending"]


@then("the office has {refs} as arrived")
def step_office_has(context, refs):
    assert context.arrived == _names(refs), context.arrived
