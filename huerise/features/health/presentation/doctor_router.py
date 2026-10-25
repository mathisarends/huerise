from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi_canon import CanonRouter

from huerise.features.health.application import Doctor
from huerise.features.health.presentation.errors import doctor_errors, health_errors
from huerise.features.health.presentation.mappers import to_doctor_response
from huerise.features.health.presentation.schemas import DoctorResponse
from huerise.platform.api.errors import AUTHENTICATION_REQUIRED

doctor_router = CanonRouter(
    tags=["doctor"],
    route_class=DishkaRoute,
    error_registry=health_errors,
    raises=[AUTHENTICATION_REQUIRED],
)


@doctor_router.get(
    "/doctor",
    status_code=200,
    response_model=DoctorResponse,
    operation_id="doctor",
    raises=doctor_errors,
)
async def doctor(
    doctor: FromDishka[Doctor],
) -> DoctorResponse:
    report = await doctor.check()
    return to_doctor_response(report)
