from decimal import Decimal

import pytest

from unitconv import Verdict, grade, main

C, I, V = Verdict.CORRECT, Verdict.INCORRECT, Verdict.INVALID


@pytest.mark.parametrize("value,src,dst,resp,verdict", [
    ("98.6", "fahrenheit", "celsius", "37", C),
    ("98.6", "fahrenheit", "celsius", "37.04", C),      # both round to 37.0
    ("98.6", "fahrenheit", "celsius", "37.1", I),
    ("0", "kelvin", "fahrenheit", "-459.7", C),          # -459.67 -> -459.7
    ("0", "celsius", "rankine", "491.7", C),             # 491.67
    ("100", "celsius", "kelvin", "373.2", C),            # 373.15 -> 373.2 (half up)
    ("100", "celsius", "kelvin", "373.1", I),
    ("100", "celsius", "kelvin", "373.15", C),
    ("-40", "celsius", "fahrenheit", "-40", C),
    ("1", "gallons", "liters", "3.8", C),
    ("1", "cups", "tablespoons", "16", C),
    ("1", "cubic-feet", "cubic-inches", "1728", C),
    ("1", "cubic-feet", "gallons", "7.5", C),            # 7.4805
    ("2", "liters", "cups", "8.5", C),                   # 8.4535 -> 8.5
    ("2", "liters", "cups", "8.4", I),
])
def test_grading(value, src, dst, resp, verdict):
    assert grade(value, src, dst, resp).verdict is verdict


def test_boundary_rounding_is_half_up_not_float_artifacts():
    # 0.05 C -> 273.2 K exactly at the tie; floats would often give 273.1
    assert grade("0.05", "celsius", "kelvin", "273.2").verdict is C


@pytest.mark.parametrize("value,src,dst,resp", [
    ("98.6", "fahrenheit", "celsius", "abc"),
    ("98.6", "fahrenheit", "celsius", ""),
    ("98.6", "fahrenheit", "celsius", "NaN"),
    ("98.6", "fahrenheit", "celsius", "inf"),
    ("98.6", "fahrenheit", "celsius", "1_0"),
    ("98.6", "fahrenheit", "celsius", "1e99999"),
    ("abc", "fahrenheit", "celsius", "37"),
    ("98.6", "fahrenheit", "liters", "37"),              # dimension mismatch
    ("98.6", "furlongs", "celsius", "37"),
    ("-1", "kelvin", "celsius", "-274.2"),               # below absolute zero
    ("-1", "liters", "cups", "-4"),                      # negative volume
])
def test_invalid(value, src, dst, resp):
    assert grade(value, src, dst, resp).verdict is V


def test_unit_aliases_and_case():
    assert grade("1", "Gallon", "L", "3.8").verdict is C
    assert grade("1", "cubic feet", "cubic_inches", "1728").verdict is C


def test_expected_reported_on_incorrect():
    assert grade("1", "gallons", "liters", "4").expected == Decimal("3.8")


def test_cli_exit_codes(capsys):
    assert main(["98.6", "F", "C", "37"]) == 0
    output = capsys.readouterr().out
    assert "Conversion" in output
    assert "98.6 F -> C" in output
    assert "CORRECT" in output

    assert main(["98.6", "F", "C", "40"]) == 1
    output = capsys.readouterr().out
    assert "Expected" in output
    assert "37.0" in output
    assert "INCORRECT" in output

    assert main(["98.6", "F", "C", "x"]) == 2
    output = capsys.readouterr().out
    assert "INVALID" in output
    assert "response is not a number" in output

    assert main(["-40", "C", "F", "-40"]) == 0            # negative numbers OK
    capsys.readouterr()
    assert main(["1"]) == 2


def test_cli_interactive_prompts_and_renders_result(monkeypatch, capsys):
    answers = iter(["98.6", "fahrenheit", "celsius", "37", ""])
    monkeypatch.setattr("builtins.input", lambda prompt: next(answers))

    assert main([]) == 0
    output = capsys.readouterr().out
    assert "Unit Conversion Grader" in output
    assert "Press Enter at the first prompt to quit" in output
    assert "CORRECT" in output


def test_cli_table_shows_invalid_input_details(capsys):
    assert main(["abc", "fahrenheit", "celsius", "37"]) == 2

    output = capsys.readouterr().out
    assert "+-" in output
    assert "Expected" in output
    assert "Not available" in output
    assert "input value is not a number" in output
