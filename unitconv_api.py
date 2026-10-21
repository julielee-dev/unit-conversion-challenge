"""JSON API for grading unit-conversion answers."""
from __future__ import annotations

from fastapi import FastAPI
from pydantic import BaseModel, ConfigDict

from unitconv import Verdict, grade


class GradeRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    value: str
    from_unit: str
    to_unit: str
    response: str


class GradeResponse(BaseModel):
    verdict: Verdict
    expected: str | None
    reason: str | None


app = FastAPI(title="Unit Conversion Grader")


@app.post("/api/grade", response_model=GradeResponse)
def grade_request(request: GradeRequest) -> GradeResponse:
    result = grade(request.value, request.from_unit, request.to_unit, request.response)
    return GradeResponse(
        verdict=result.verdict,
        expected=str(result.expected) if result.expected is not None else None,
        reason=result.reason or None,
    )
