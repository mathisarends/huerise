import uuid
from huerise.domain.views import AlarmStatus


class AlarmAlreadyCancelled(Exception):
    def __init__(self, alarm_id: uuid.UUID) -> None:
        super().__init__(f"Alarm {alarm_id} is already cancelled")


class AlarmAlreadyInStatus(Exception):
    def __init__(self, alarm_id: uuid.UUID, status: AlarmStatus) -> None:
        super().__init__(f"Alarm {alarm_id} is already {status}")
