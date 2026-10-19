# unit-conversion-challenge


Grades a student's unit-conversion answer as **correct**, **incorrect**, or **invalid**.

    pip install .
    unitconv 98.6 fahrenheit celsius 37     # -> CORRECT
    unitconv                                # interactive prompts
    docker run --rm ghcr.io/<org>/unitconv 1 gallons liters 3.8

Exit codes: 0 correct, 1 incorrect, 2 invalid.

Units: kelvin, celsius, fahrenheit, rankine (temperature); liters, tablespoons,
cubic-inches, cups, cubic-feet, gallons (volume, US customary). Short forms
(`F`, `tbsp`, `gal`, `in3`, `ft3`) and singular/case variants are accepted.

## Design decisions
- `Decimal` arithmetic with exact conversion constants, so rounding to tenths
  (round-half-up) is never skewed by float error.
- Temperatures route through Kelvin, volumes through liters: N units need N
  formulas, not N^2.
- **Invalid** = unknown unit, mixing temperature and volume, non-numeric or
  non-finite input/response (`abc`, blank, `NaN`, `inf`), below absolute zero,
  or negative volume.
- Gallon/cup/tablespoon are US customary.

## Development / CI-CD
    pip install -e ".[dev]" && ruff check . && pytest

- Pull requests: lint, tests (Python 3.10 and 3.12), and a Docker build smoke test.
- Merge to `main`: tests pass, then the image is pushed to GHCR as `latest` and the commit SHA.
- Repo settings to enable: branch protection on `main` requiring one approving
  review and the `test` check, and no direct pushes.
