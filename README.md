# Northlight

Harbor, Ledgerline and Fieldnote: three small products belonging to a company that does
not exist. This repository is the code; the vault beside it is the same team's issue
tracker.

## None of this is real

Northlight is invented. The company, the three products, the six people in the commit
log, the marinas, the accountants and the field crews are all made up for a demonstration
of an issue tracker that keeps its issues in Markdown. Nothing here has ever charged a
card or imported a bank statement, and no real company, product or person is meant by any
name in it.

## Quick start

    git clone https://github.com/didenkolab/northlight.git
    cd northlight
    python3 -m venv .venv && .venv/bin/pip install behave
    .venv/bin/behave features

Sixty scenarios run, and two of them fail on purpose:

  * `HARBOR-PAY-004`, *A refund larger than the invoice it credits is refused* — it is
    not refused. Twenty-five thousand cents go back against a charge of eighteen.
  * *A job finished offline keeps its photographs* — it comes back one photograph short.
    Nobody tagged that scenario, so it is known by the id derived from its own name,
    `FIELD-GEN-04E49B`.

Both are bugs, and both are written up in the vault next door. Everything else passes.

## Requirements

| | |
|---|---|
| Python 3.11 or newer | `pyproject.toml` asks for it, and nothing here needs anything newer |
| behave | The one dependency, and only for the scenarios. The three packages import nothing but the standard library |

## Install

Nothing to install. Clone the repository and the packages are importable from the
checkout; the virtualenv above exists for `behave` and for nothing else.

## Usage

One product's suite at a time:

    .venv/bin/behave features/harbor

The Cucumber JSON the vault imports, which is how a run gets onto the board:

    .venv/bin/behave features/harbor -q --no-summary -f json -o reports/harbor.json

One feature file, the way the board's own button runs it — the second argument says
where to leave the JUnit XML:

    ./run-tests features/harbor/booking.feature reports/junit.xml

## Configuration

None. No environment variable and no file outside this checkout changes what the
scenarios do; the virtualenv is the whole of the setup.

## How it works

    harbor/       berths, what a stay costs, and taking the money for it
    ledgerline/   invoice numbers, bank statements and tax periods
    fieldnote/    a crew's day, the order they drive it in, and a phone with no signal
    features/     the same three, as behave scenarios, three files per product

Every module is pure: a function is handed the state it needs and gives back a new one.
Nothing here opens a socket, reads a file it was not given, or asks what time it is,
which is why a suite can be run against a checkout from three months ago and mean
something.

Some scenarios carry a case id — `@HARBOR-PAY-004` — and some carry nothing. A tagged one
keeps its identity when somebody rewords it. An untagged one is identified by its feature
file's name and its own, hashed into `FIELD-GEN-04E49B` and the like. Both kinds are
imported; an untagged scenario is not second class.

Results reach the board from the vault, not from here. Somebody runs a suite and hands
the JSON to `hooks/import-cucumber.sh` in `docket-showcase`, which writes one execution
and one run per scenario, each attached to its test by that same id. Those ids and the
task key every commit message here opens with are the only things joining the two
repositories — the key is how the vault blames a scenario's lines back to a ticket.

## Where things are

  * [docket-showcase](https://github.com/didenkolab/docket-showcase) — the vault: the
    same team's board, backlog, wiki, and the test results these scenarios produce.
  * [docket](https://github.com/didenkolab/docket) — the tracker the vault is kept in.

## Contributing

Put a scenario in the feature file for the area it belongs to. Tag it with a case id if
it settles a case somebody wrote down, and leave it untagged if it does not.

Do not rename a feature file, and do not rename a scenario that has runs against it. An
untagged scenario's id is derived from those two names, so a rename starts a new test and
leaves the old one holding the history. Once a scenario is tagged, reword it freely.

There is no other test suite. Run it before you push:

    .venv/bin/behave features

## License

MIT. See [LICENSE](LICENSE).
