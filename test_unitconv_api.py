from fastapi.testclient import TestClient

from unitconv_api import app

client = TestClient(app)


def test_grade_endpoint_returns_json_result():
    response = client.post(
        "/api/grade",
        json={
            "value": "98.6",
            "from_unit": "fahrenheit",
            "to_unit": "celsius",
            "response": "37",
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "verdict": "correct",
        "expected": "37.0",
        "reason": None,
    }


def test_grade_endpoint_reports_incorrect_answer():
    response = client.post(
        "/api/grade",
        json={
            "value": "1",
            "from_unit": "gallons",
            "to_unit": "liters",
            "response": "4",
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "verdict": "incorrect",
        "expected": "3.8",
        "reason": None,
    }


def test_grade_endpoint_reports_invalid_answer():
    response = client.post(
        "/api/grade",
        json={
            "value": "1",
            "from_unit": "gallons",
            "to_unit": "liters",
            "response": "not a number",
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "verdict": "invalid",
        "expected": "3.8",
        "reason": "response is not a number: 'not a number'",
    }


def test_grade_endpoint_rejects_extra_fields():
    response = client.post(
        "/api/grade",
        json={
            "value": "1",
            "from_unit": "gallons",
            "to_unit": "liters",
            "response": "3.8",
            "unexpected": True,
        },
    )

    assert response.status_code == 422


def test_grade_endpoint_rejects_missing_fields():
    response = client.post(
        "/api/grade",
        json={"value": "1", "from_unit": "gallons", "to_unit": "liters"},
    )

    assert response.status_code == 422


def test_grade_endpoint_rejects_numeric_values():
    response = client.post(
        "/api/grade",
        json={
            "value": 98.6,
            "from_unit": "fahrenheit",
            "to_unit": "celsius",
            "response": "37",
        },
    )

    assert response.status_code == 422
