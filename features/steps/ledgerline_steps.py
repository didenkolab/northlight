"""The steps the Ledgerline scenarios are written in."""
import datetime as dt

from behave import given, step, then, when

from ledgerline import invoices


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
