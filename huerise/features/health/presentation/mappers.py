from huerise.features.health.application import DoctorReport
from huerise.features.health.presentation.schemas import (
    DoctorCheckResponse,
    DoctorResponse,
)


def to_doctor_response(report: DoctorReport) -> DoctorResponse:
    return DoctorResponse(
        status=report.status,
        checks=[
            DoctorCheckResponse(name=check.name, status=check.status)
            for check in report.checks
        ],
    )
