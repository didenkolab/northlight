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

## What is in here

    harbor/       berths, what a stay costs, and taking the money for it
    ledgerline/   invoice numbers, bank statements and tax periods
    fieldnote/    a crew's day, the order they drive it in, and a phone with no signal
    features/     the same three, as behave scenarios

Every module is pure: a function is handed the state it needs and gives back a new one.
Nothing here opens a socket, reads a file it was not given, or asks what time it is.

## License

MIT. See [LICENSE](LICENSE).
