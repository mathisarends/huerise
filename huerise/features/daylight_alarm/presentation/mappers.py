from huerise.features.daylight_alarm.presentation.schemas import (
    AfterAlarmConfigurationResponse,
    DaylightAlarmConfigurationResponse,
    NamedResourceResponse,
)
from huerise.platform.configuration import DaylightAlarmConfig, NamedResourceConfig


def to_configuration_response(
    configuration: DaylightAlarmConfig,
) -> DaylightAlarmConfigurationResponse:
    after_alarm = configuration.after_alarm
    return DaylightAlarmConfigurationResponse(
        room=_to_resource_response(configuration.room),
        scene=_to_resource_response(configuration.scene),
        duration_seconds=configuration.duration_seconds,
        after_alarm=(
            AfterAlarmConfigurationResponse(
                room=_to_resource_response(after_alarm.room),
                scene=_to_resource_response(after_alarm.scene),
                delay_seconds=after_alarm.delay_seconds,
            )
            if after_alarm is not None
            else None
        ),
    )


def _to_resource_response(resource: NamedResourceConfig) -> NamedResourceResponse:
    return NamedResourceResponse(id=resource.id, name=resource.name)
