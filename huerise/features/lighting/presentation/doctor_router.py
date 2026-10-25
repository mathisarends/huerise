from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi_canon import CanonRouter

from huerise.features.lighting.application import Doctor
from huerise.features.lighting.presentation.errors import doctor_errors, lighting_errors
from huerise.features.lighting.presentation.mappers import to_doctor_response
from huerise.features.lighting.presentation.schemas import DoctorResponse
from huerise.platform.api.errors import AUTHENTICATION_REQUIRED

doctor_router = CanonRouter(
    tags=["doctor"],
    route_class=DishkaRoute,
    error_registry=lighting_errors,
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
