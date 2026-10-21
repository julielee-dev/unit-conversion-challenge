# unit-conversion-challenge


Grades a student's unit-conversion answer as **correct**, **incorrect**, or **invalid**.

    pip install .
    unitconv 98.6 fahrenheit celsius 37     # -> CORRECT
    unitconv                                # friendly interactive prompts
    docker run --rm ghcr.io/<org>/unitconv 1 gallons liters 3.8

Exit codes: 0 correct, 1 incorrect, 2 invalid.
Results are displayed in a table with the conversion, student answer,
expected value when available, verdict, and any validation details.

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
    pip install -e ".[web,dev]" && ruff check . && pytest

## JSON API
Install the optional web dependencies and start the API:

    pip install -e ".[web]"
    uvicorn unitconv_api:app --reload

Send a JSON request to `POST /api/grade`:

    curl -X POST http://127.0.0.1:8000/api/grade \
      -H "Content-Type: application/json" \
      -d '{"value":"98.6","from_unit":"fahrenheit","to_unit":"celsius","response":"37"}'

The response includes a `verdict` (`correct`, `incorrect`, or `invalid`),
the expected value as a decimal string when available, and an optional
validation `reason`. Send numeric values as strings to preserve decimal
precision. The existing `unitconv` command syntax and exit codes are unchanged.

- Pull requests: lint, tests (Python 3.10 and 3.12), and a Docker build smoke test.
- Merge to `main`: tests pass, then the image is pushed to GHCR as `latest` and the commit SHA.
- Repo settings to enable: branch protection on `main` requiring one approving
  review and the `test` check, and no direct pushes.
