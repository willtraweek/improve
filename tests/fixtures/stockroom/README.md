# Stockroom

A small in-memory inventory library for a single-process kiosk. Callers use
integer unit counts. Reservations return the remaining stock and must never
increase inventory. This module has no network or persistence boundary.

Run checks without generating bytecode:

```sh
PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s tests -v
```

There is no dependency installation, build, formatter, or typecheck step.
See `docs/decisions.md` for the API choices.
