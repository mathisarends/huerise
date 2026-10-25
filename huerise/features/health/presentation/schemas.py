from typing import Literal

from pydantic import BaseModel


class DoctorCheckResponse(BaseModel):
    name: str
    status: Literal["ok"]


class DoctorResponse(BaseModel):
    status: Literal["ok"]
    checks: list[DoctorCheckResponse]
