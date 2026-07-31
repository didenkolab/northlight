"""The steps the Fieldnote scenarios are written in."""
import datetime as dt

from behave import given, step, then, when

from fieldnote import jobs, routes, sync


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


@when("{job_id} is handed to the {crew} crew")
def step_handed_to_crew(context, job_id, crew):
    context.result = jobs.move_crew(context.board, job_id, crew)
    context.board = context.result["board"]


@then("the {crew} crew's day for {day} is {ids}")
def step_crew_day_is(context, crew, day, ids):
    got = jobs.day_list(context.board, crew, _day(day))
    assert [job.id for job in got] == _names(ids), got


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


@when("the day through {stops} is planned from {depot}")
def step_plan_day(context, stops, depot):
    context.plan = routes.plan_day(depot, _names(stops), context.roads, context.places)


@then("the plan is {stops}")
def step_plan_is(context, stops):
    assert context.plan == _names(stops), context.plan


@given("nothing on the phone and nothing on the board")
def step_nothing_anywhere(context):
    context.phone = {"jobs": [], "photos": []}
    context.server = {"jobs": [], "photos": []}
    context.edits = []


@given("the board has these jobs")
def step_board_jobs(context):
    context.server = {**context.server, "jobs": [row.as_dict() for row in context.table]}


@given("the phone has these jobs")
def step_phone_jobs(context):
    context.phone = {**context.phone, "jobs": [row.as_dict() for row in context.table]}


@when("the phone and the board are merged")
def step_merged(context):
    context.merged = sync.merge(context.phone, context.server)


@then("{job_id} comes back as {status}")
def step_comes_back_as(context, job_id, status):
    job = next(j for j in context.merged["jobs"] if j["id"] == job_id)
    assert job["status"] == status, job


@then("the merged day is {ids}")
def step_merged_day(context, ids):
    assert [job["id"] for job in context.merged["jobs"]] == _names(ids), context.merged


@given("the phone queued these edits")
def step_queued_edits(context):
    for row in context.table:
        context.edits = sync.queue_edit(context.edits, row.as_dict())


@when("the queued edits are replayed onto the board")
def step_replay_edits(context):
    context.merged = {"jobs": sync.apply_edits(context.server["jobs"], context.edits),
                      "conflicts": []}


@then("the merge reports {job_id} as {phone_status} on the phone and {board_status} on the board")
def step_merge_reports(context, job_id, phone_status, board_status):
    found = [row for row in context.merged["conflicts"] if row["id"] == job_id]
    assert found, context.merged
    assert found[0]["phone"] == phone_status, found
    assert found[0]["server"] == board_status, found
