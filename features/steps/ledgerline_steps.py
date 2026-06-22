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
