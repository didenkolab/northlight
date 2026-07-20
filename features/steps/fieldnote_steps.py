"""The steps the Fieldnote scenarios are written in."""
import datetime as dt

from behave import given, step, then, when

from fieldnote import jobs, routes


def _names(text):
    """A list the way a person writes one."""
    return [part.strip() for part in text.replace(" and ", ", ").split(",") if part.strip()]


def _day(text):
    return dt.date.fromisoformat(text)


def _time(text):
    hour, minute = (int(part) for part in text.split(":"))
    return dt.time(hour, minute)


def _clock(text):
    return dt.datetime.combine(dt.date(2026, 7, 16), _time(text))


@given("an empty board")
def step_empty_board(context):
    context.board = []
    context.result = None


@given("these jobs are on the board")
def step_jobs_on_board(context):
    context.board = [jobs.Job(row["id"], row["crew"], _day(row["day"]), _time(row["start"]),
                              int(row["minutes"]), row["address"]) for row in context.table]


@when("the {crew} crew's day for {day} is read")
def step_read_crew_day(context, crew, day):
    context.day = jobs.day_list(context.board, crew, _day(day))


@then("the day is {ids}")
def step_day_is(context, ids):
    assert [job.id for job in context.day] == _names(ids), context.day


@when("{job_id} is put on the {crew} crew for {day} at {start} for {minutes:d} minutes")
def step_put_on_crew(context, job_id, crew, day, start, minutes):
    context.result = jobs.assign(context.board,
                                 jobs.Job(job_id, crew, _day(day), _time(start), minutes,
                                          "Somewhere 1"))
    context.board = context.result["board"]


@then("the job is taken")
def step_job_taken(context):
    assert context.result["ok"] is True, context.result


@then("the job is refused because {reason}")
def step_job_refused(context, reason):
    assert context.result["ok"] is False, context.result
    assert context.result["reason"] == reason, context.result


@then("the job in the way is {job_id}")
def step_job_in_the_way(context, job_id):
    assert context.result["clash"] == job_id, context.result


@given("the roads we know")
def step_roads_we_know(context):
    context.roads = {(row["from"], row["to"]): int(row["minutes"]) for row in context.table}
    context.places = {}


@when("the stops {stops} are ordered from {depot}")
def step_order_stops(context, stops, depot):
    context.order = routes.order_stops(depot, _names(stops), context.roads, context.places)


@then("the order is {stops}")
def step_order_is(context, stops):
    assert context.order == _names(stops), context.order


@given("where the stops are")
def step_where_stops_are(context):
    context.places = {row["stop"]: (float(row["x"]), float(row["y"])) for row in context.table}


@when("the leg from {here} to {there} is worked out")
def step_leg_worked_out(context, here, there):
    context.leg = routes.leg_minutes(context.roads, context.places, here, there)


@then("the leg is {minutes:d} minutes")
def step_leg_is(context, minutes):
    assert context.leg == minutes, context.leg
