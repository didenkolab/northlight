"""The steps the Ledgerline scenarios are written in."""
import datetime as dt

from behave import given, step, then, when

from ledgerline import bankimport, invoices, tax


def _names(text):
    """A list the way a person writes one."""
    return [part.strip() for part in text.replace(" and ", ", ").split(",") if part.strip()]


def _day(text):
    return dt.date.fromisoformat(text)


@given("the ledger has issued no invoices")
def step_no_invoices_yet(context):
    context.sequence = {}
    context.numbers = []
    context.result = None


@step("{count:d} invoices are numbered for {year:d}")
@step("{count:d} invoice is numbered for {year:d}")
def step_number_invoices(context, count, year):
    for _ in range(count):
        made = invoices.next_number(context.sequence, year)
        context.sequence = made["sequence"]
        context.numbers.append(made["number"])


@then("the numbers are {numbers}")
def step_numbers_are(context, numbers):
    assert context.numbers == _names(numbers), context.numbers


@when("two invoices are numbered from one reading of the sequence for {year:d}")
def step_two_from_one_reading(context, year):
    read = context.sequence.get(year, 0)
    first = invoices.next_number(context.sequence, year, expect=read)
    assert first["ok"], first
    context.sequence = first["sequence"]
    context.result = invoices.next_number(context.sequence, year, expect=read)


@then("the second one is refused because {reason}")
def step_second_refused(context, reason):
    assert context.result["ok"] is False, context.result
    assert context.result["reason"] == reason, context.result


def _invoice_lines(table):
    return [invoices.Line(row["description"], int(row["quantity"]), int(row["unit_cents"]),
                          int(row["tax_percent"])) for row in table]


@when("an invoice is composed for {customer}")
def step_compose_invoice(context, customer):
    context.invoice = invoices.compose("2026-0001", customer, _invoice_lines(context.table))


@then("line {index:d} shows {net:d} net, {tax_amount:d} tax and {gross:d} gross")
def step_line_shows(context, index, net, tax_amount, gross):
    line = context.invoice["lines"][index - 1]
    assert line["net_cents"] == net, line
    assert line["tax_cents"] == tax_amount, line
    assert line["gross_cents"] == gross, line


@then("the invoice totals {net:d} net, {tax_amount:d} tax and {gross:d} gross")
def step_invoice_totals(context, net, tax_amount, gross):
    got = invoices.totals(context.invoice)
    assert got["net_cents"] == net, got
    assert got["tax_cents"] == tax_amount, got
    assert got["gross_cents"] == gross, got


@given("an invoice {number} for {customer}")
def step_an_invoice(context, number, customer):
    context.invoice = invoices.compose(number, customer, _invoice_lines(context.table))


@when("{cents:d} cents are credited against it as {number}")
def step_credit_against(context, cents, number):
    context.result = invoices.credit_note(context.invoice, cents, "cancelled", number)


@then("the credit note is made out against {number}")
def step_credit_note_against(context, number):
    assert context.result["ok"], context.result
    assert context.result["note"]["against"] == number, context.result


@step("crediting {cents:d} cents is refused because {reason}")
def step_credit_refused(context, cents, reason):
    refused = invoices.credit_note(context.invoice, cents, "cancelled", "2026-C999")
    assert refused["ok"] is False, refused
    assert refused["reason"] == reason, refused


@given("an invoice fell due on {day}")
def step_fell_due(context, day):
    context.due = _day(day)


@step("it is {day} and nothing has been chased yet")
def step_nothing_chased(context, day):
    context.result = invoices.reminders_due(context.due, _day(day), [])


@step("it is {day} and {count:d} reminder has been sent")
@step("it is {day} and {count:d} reminders have been sent")
def step_some_chased(context, day, count):
    context.result = invoices.reminders_due(context.due, _day(day), ["sent"] * count)


@then("a reminder goes out")
def step_reminder_goes_out(context):
    assert context.result["send"] is True, context.result


@then("no reminder goes out because {reason}")
def step_no_reminder(context, reason):
    assert context.result["send"] is False, context.result
    assert context.result["reason"] == reason, context.result


@given("these things happened to our messages")
def step_message_events(context):
    context.events = [row.as_dict() for row in context.table]


@when("we ask what became of {message_id}")
def step_ask_what_became(context, message_id):
    context.result = invoices.delivery(message_id, context.events)


@then("what became of it is {state}")
def step_what_became(context, state):
    assert context.result["state"] == state, context.result


@given("an empty ledger")
def step_empty_ledger(context):
    context.ledger = {}
    context.result = None


@step("the statement for account {account} is imported")
def step_import_statement(context, account):
    lines = [row.as_dict() for row in context.table]
    context.result = bankimport.import_statement(context.ledger, account, lines)
    context.ledger = context.result["ledger"]


@then("the ledger holds lines dated {days}")
def step_ledger_dated(context, days):
    assert [line["date"] for line in context.ledger["lines"]] == _names(days), context.ledger


@then("the import is recognised as one we already have")
def step_import_repeat(context):
    assert context.result["repeat"] is True, context.result


FILE_COLUMNS = {"date": "date", "cents": "amount", "reference": "message"}


@when("this file is read as a statement")
def step_read_file(context):
    context.lines = bankimport.lines_from_csv(context.text, FILE_COLUMNS)


@then("the file gives lines dated {days}")
def step_file_dated(context, days):
    assert [line["date"] for line in context.lines] == _names(days), context.lines


@then("the first line of the file is {cents:d} cents")
def step_file_first_line(context, cents):
    assert context.lines[0]["cents"] == cents, context.lines[0]


@then("the ledger's amounts are {amounts}")
def step_ledger_amounts(context, amounts):
    want = [int(part) for part in _names(amounts)]
    assert [line["cents"] for line in context.ledger["lines"]] == want, context.ledger


@given("the ledger is owed")
def step_ledger_owed(context):
    context.invoices = [{"number": row["number"], "cents": int(row["cents"])}
                        for row in context.table]


@when("these lines are matched")
def step_lines_matched(context):
    lines = [{"date": row["date"], "cents": int(row["cents"]), "reference": row["reference"]}
             for row in context.table]
    context.result = bankimport.match(lines, context.invoices)


@then("the lines are matched to {numbers}")
def step_matched_to(context, numbers):
    got = [pair["invoice"] for pair in context.result["matched"]]
    assert got == _names(numbers), context.result


@then("line {index:d} is left unmatched")
def step_line_unmatched(context, index):
    assert index in context.result["unmatched"], context.result


@when("a person matches line {index:d} to {number}")
def step_person_matches(context, index, number):
    context.result = bankimport.match_by_hand(context.result, index, number)


@then("line {index:d} is matched to {number} by hand")
def step_matched_by_hand(context, index, number):
    made = [pair for pair in context.result["matched"] if pair["line"] == index]
    assert made, context.result
    assert made[0]["invoice"] == number, made
    assert made[0].get("by_hand") is True, made


@when("the bank's bytes are decoded as {charset}")
def step_decode_bytes(context, charset):
    context.decoded = bankimport.decode(b"S\xf8rensen", charset)


@then("the name reads {name}")
def step_name_reads(context, name):
    assert context.decoded == name, context.decoded


@when("the tax on these lines is worked out {mode}")
def step_tax_rounding(context, mode):
    lines = [{"net_cents": int(row["net_cents"]), "tax_percent": int(row["tax_percent"])}
             for row in context.table]
    context.tax = tax.rounding(lines, mode)


@then("the tax comes to {cents:d} cents")
def step_tax_comes_to(context, cents):
    assert context.tax == cents, context.tax


@given("the quarter {period} is closed")
def step_quarter_closed(context, period):
    context.ledger = tax.close_period(context.ledger, period)["ledger"]


@when("an entry dated {day} is booked")
def step_entry_booked(context, day):
    context.result = tax.book(context.ledger, {"date": _day(day), "cents": 1000})
    context.ledger = context.result["ledger"]


@then("the entry is refused because {reason}")
def step_entry_refused(context, reason):
    assert context.result["ok"] is False, context.result
    assert context.result["reason"] == reason, context.result
