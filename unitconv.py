"""Grade student unit-conversion answers (temperature and volume)."""
from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation, localcontext
from enum import Enum

PRECISION = 60
TENTH = Decimal("0.1")
_NUMBER = re.compile(r"^[+-]?(\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?$")


class Verdict(str, Enum):
    CORRECT = "correct"
    INCORRECT = "incorrect"
    INVALID = "invalid"


@dataclass(frozen=True)
class Result:
    verdict: Verdict
    expected: Decimal | None = None  # authoritative answer, rounded to tenths
    reason: str = ""


# ---- temperature: everything goes through Kelvin ---------------------------
_TO_K = {
    "kelvin": lambda x: x,
    "celsius": lambda x: x + Decimal("273.15"),
    "fahrenheit": lambda x: (x - 32) * 5 / 9 + Decimal("273.15"),
    "rankine": lambda x: x * 5 / 9,
}
_FROM_K = {
    "kelvin": lambda k: k,
    "celsius": lambda k: k - Decimal("273.15"),
    "fahrenheit": lambda k: (k - Decimal("273.15")) * 9 / 5 + 32,
    "rankine": lambda k: k * 9 / 5,
}

# ---- volume: everything goes through liters (US customary, exact) ----------
_LITERS_PER = {
    "liters": Decimal(1),
    "tablespoons": Decimal("0.01478676478125"),
    "cubic-inches": Decimal("0.016387064"),
    "cups": Decimal("0.2365882365"),
    "cubic-feet": Decimal("28.316846592"),
    "gallons": Decimal("3.785411784"),
}

_ALIASES = {
    "kelvin": "kelvin", "k": "kelvin",
    "celsius": "celsius", "c": "celsius",
    "fahrenheit": "fahrenheit", "f": "fahrenheit",
    "rankine": "rankine", "r": "rankine",
    "liters": "liters", "liter": "liters", "litres": "liters", "litre": "liters", "l": "liters",
    "tablespoons": "tablespoons", "tablespoon": "tablespoons", "tbsp": "tablespoons",
    "cubic-inches": "cubic-inches", "cubic-inch": "cubic-inches", "in3": "cubic-inches",
    "cups": "cups", "cup": "cups",
    "cubic-feet": "cubic-feet", "cubic-foot": "cubic-feet", "ft3": "cubic-feet",
    "gallons": "gallons", "gallon": "gallons", "gal": "gallons",
}


def normalize_unit(name: str) -> str | None:
    key = re.sub(r"[\s_]+", "-", name.strip().lower())
    return _ALIASES.get(key)


def parse_number(text: str) -> Decimal | None:
    """Parse a plain decimal number; reject NaN, Infinity, '1_000', '', etc."""
    text = text.strip()
    if not _NUMBER.match(text):
        return None
    return Decimal(text)


def round_tenths(x: Decimal) -> Decimal:
    with localcontext() as ctx:
        ctx.prec = PRECISION
        return x.quantize(TENTH, rounding=ROUND_HALF_UP)


def convert(value: Decimal, src: str, dst: str) -> Decimal:
    """Convert between canonical units. Raises ValueError on bad input."""
    with localcontext() as ctx:
        ctx.prec = PRECISION
        if src in _TO_K and dst in _FROM_K:
            kelvin = _TO_K[src](value)
            if kelvin < 0:
                raise ValueError("temperature is below absolute zero")
            return _FROM_K[dst](kelvin)
        if src in _LITERS_PER and dst in _LITERS_PER:
            if value < 0:
                raise ValueError("volume cannot be negative")
            return value * _LITERS_PER[src] / _LITERS_PER[dst]
    raise ValueError(f"cannot convert {src} to {dst}")


def grade(value: str, from_unit: str, to_unit: str, response: str) -> Result:
    """Return CORRECT / INCORRECT / INVALID for one worksheet question."""
    src, dst = normalize_unit(from_unit), normalize_unit(to_unit)
    if src is None:
        return Result(Verdict.INVALID, reason=f"unknown input unit: {from_unit!r}")
    if dst is None:
        return Result(Verdict.INVALID, reason=f"unknown target unit: {to_unit!r}")
    number = parse_number(value)
    if number is None:
        return Result(Verdict.INVALID, reason=f"input value is not a number: {value!r}")
    try:
        expected = round_tenths(convert(number, src, dst))
    except (ValueError, InvalidOperation) as exc:
        return Result(Verdict.INVALID, reason=str(exc))

    answer = parse_number(response)
    if answer is None:
        return Result(Verdict.INVALID, expected, f"response is not a number: {response!r}")
    try:
        answer = round_tenths(answer)
    except InvalidOperation:
        return Result(Verdict.INVALID, expected, "response is out of range")
    verdict = Verdict.CORRECT if answer == expected else Verdict.INCORRECT
    return Result(verdict, expected)


# ---- command line -----------------------------------------------------------
_EXIT = {Verdict.CORRECT: 0, Verdict.INCORRECT: 1, Verdict.INVALID: 2}
_USAGE = """usage: unitconv VALUE FROM_UNIT TO_UNIT RESPONSE
       unitconv            (no arguments: prompts for each field)

units: kelvin celsius fahrenheit rankine | liters tablespoons cubic-inches cups cubic-feet gallons
exit code: 0 correct, 1 incorrect, 2 invalid"""


def _report(res: Result) -> None:
    line = res.verdict.value.upper()
    if res.reason:
        line += f" ({res.reason})"
    print(line)
    if res.verdict is Verdict.INCORRECT:
        print(f"expected: {res.expected}")


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    if args in (["-h"], ["--help"]):
        print(_USAGE)
        return 0
    if len(args) == 4:
        res = grade(*args)
        _report(res)
        return _EXIT[res.verdict]
    if args:
        print(_USAGE, file=sys.stderr)
        return 2
    try:  # interactive mode: one question after another until blank/Ctrl-D
        while True:
            value = input("Input value (blank to quit): ")
            if not value.strip():
                return 0
            fields = [value, input("Input unit: "), input("Target unit: "), input("Student response: ")]
            _report(grade(*fields))
            print()
    except EOFError:
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
