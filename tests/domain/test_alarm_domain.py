import uuid
from datetime import timezone

import pytest

from huerise.domain.alarm import Alarm
from huerise.domain.exceptions import AlarmAlreadyCancelled, AlarmAlreadyInStatus
from huerise.domain.views import AlarmStatus, AlarmType, Schedule, Weekday


# ---------------------------------------------------------------------------
# Schedule
# ---------------------------------------------------------------------------


class TestScheduleValidation:
    def test_valid_schedule_stores_values(self) -> None:
        s = Schedule(hour=7, minute=30)
        assert s.hour == 7
        assert s.minute == 30

    def test_hour_below_zero_raises(self) -> None:
        with pytest.raises(ValueError, match="Hour must be 0-23"):
            Schedule(hour=-1, minute=0)

    def test_hour_above_23_raises(self) -> None:
        with pytest.raises(ValueError, match="Hour must be 0-23"):
            Schedule(hour=24, minute=0)

    def test_minute_below_zero_raises(self) -> None:
        with pytest.raises(ValueError, match="Minute must be 0-59"):
            Schedule(hour=0, minute=-1)

    def test_minute_above_59_raises(self) -> None:
        with pytest.raises(ValueError, match="Minute must be 0-59"):
            Schedule(hour=0, minute=60)

    def test_boundary_hour_zero_is_valid(self) -> None:
        s = Schedule(hour=0, minute=0)
        assert s.hour == 0

    def test_boundary_hour_23_is_valid(self) -> None:
        s = Schedule(hour=23, minute=59)
        assert s.hour == 23


class TestScheduleIsRecurring:
    def test_no_recurrence_is_not_recurring(self) -> None:
        s = Schedule(hour=8, minute=0)
        assert s.is_recurring() is False

    def test_with_recurrence_is_recurring(self) -> None:
        s = Schedule(hour=8, minute=0, recurrence=frozenset({Weekday.MON}))
        assert s.is_recurring() is True

    def test_empty_frozenset_recurrence_is_recurring(self) -> None:
        s = Schedule(hour=8, minute=0, recurrence=frozenset())
        assert s.is_recurring() is True


# ---------------------------------------------------------------------------
# Alarm factory methods
# ---------------------------------------------------------------------------


class TestCreateOneTime:
    def test_creates_alarm_with_correct_label(self) -> None:
        alarm = Alarm.create_one_time(label="Morning", hour=7, minute=0)
        assert alarm.label == "Morning"

    def test_creates_alarm_with_correct_schedule(self) -> None:
        alarm = Alarm.create_one_time(label="Morning", hour=7, minute=30)
        assert alarm.schedule.hour == 7
        assert alarm.schedule.minute == 30

    def test_creates_alarm_with_active_status(self) -> None:
        alarm = Alarm.create_one_time(label="Morning", hour=7, minute=0)
        assert alarm.status == AlarmStatus.ACTIVE

    def test_creates_alarm_with_one_time_type(self) -> None:
        alarm = Alarm.create_one_time(label="Morning", hour=7, minute=0)
        assert alarm.alarm_type == AlarmType.ONE_TIME

    def test_creates_alarm_with_no_series_id(self) -> None:
        alarm = Alarm.create_one_time(label="Morning", hour=7, minute=0)
        assert alarm.series_id is None

    def test_creates_alarm_with_uuid_id(self) -> None:
        alarm = Alarm.create_one_time(label="Morning", hour=7, minute=0)
        assert isinstance(alarm.id, uuid.UUID)

    def test_each_call_produces_unique_id(self) -> None:
        a1 = Alarm.create_one_time(label="Morning", hour=7, minute=0)
        a2 = Alarm.create_one_time(label="Morning", hour=7, minute=0)
        assert a1.id != a2.id

    def test_created_at_is_utc_aware(self) -> None:
        alarm = Alarm.create_one_time(label="Morning", hour=7, minute=0)
        assert alarm.created_at.tzinfo is not None
        assert alarm.created_at.tzinfo == timezone.utc


class TestCreateRecurring:
    def test_creates_alarm_with_correct_label(self) -> None:
        series = uuid.uuid4()
        alarm = Alarm.create_recurring(
            label="Weekdays",
            hour=6,
            minute=30,
            days={Weekday.MON, Weekday.FRI},
            series_id=series,
        )
        assert alarm.label == "Weekdays"

    def test_creates_alarm_with_recurring_type(self) -> None:
        series = uuid.uuid4()
        alarm = Alarm.create_recurring(
            label="Weekdays", hour=6, minute=30, days={Weekday.MON}, series_id=series
        )
        assert alarm.alarm_type == AlarmType.RECURRING

    def test_creates_alarm_with_active_status(self) -> None:
        series = uuid.uuid4()
        alarm = Alarm.create_recurring(
            label="Weekdays", hour=6, minute=30, days={Weekday.MON}, series_id=series
        )
        assert alarm.status == AlarmStatus.ACTIVE

    def test_stores_series_id(self) -> None:
        series = uuid.uuid4()
        alarm = Alarm.create_recurring(
            label="Weekdays", hour=6, minute=30, days={Weekday.MON}, series_id=series
        )
        assert alarm.series_id == series

    def test_stores_days_as_frozenset_in_schedule(self) -> None:
        series = uuid.uuid4()
        days = {Weekday.MON, Weekday.WED, Weekday.FRI}
        alarm = Alarm.create_recurring(
            label="MWF", hour=7, minute=0, days=days, series_id=series
        )
        assert alarm.schedule.recurrence == frozenset(days)

    def test_schedule_is_recurring(self) -> None:
        series = uuid.uuid4()
        alarm = Alarm.create_recurring(
            label="Daily", hour=7, minute=0, days={Weekday.MON}, series_id=series
        )
        assert alarm.schedule.is_recurring() is True


# ---------------------------------------------------------------------------
# Alarm.deactivate
# ---------------------------------------------------------------------------


class TestAlarmDeactivate:
    def _active_alarm(self) -> Alarm:
        return Alarm.create_one_time(label="Test", hour=8, minute=0)

    def test_active_alarm_becomes_inactive(self) -> None:
        alarm = self._active_alarm()
        alarm.deactivate()
        assert alarm.status == AlarmStatus.INACTIVE

    def test_deactivating_inactive_alarm_raises(self) -> None:
        alarm = self._active_alarm()
        alarm.deactivate()
        with pytest.raises(AlarmAlreadyInStatus, match="inactive"):
            alarm.deactivate()

    def test_deactivating_cancelled_alarm_raises(self) -> None:
        alarm = self._active_alarm()
        alarm.cancel()
        with pytest.raises(AlarmAlreadyCancelled):
            alarm.deactivate()


# ---------------------------------------------------------------------------
# Alarm.activate
# ---------------------------------------------------------------------------


class TestAlarmActivate:
    def _inactive_alarm(self) -> Alarm:
        alarm = Alarm.create_one_time(label="Test", hour=8, minute=0)
        alarm.deactivate()
        return alarm

    def test_inactive_alarm_becomes_active(self) -> None:
        alarm = self._inactive_alarm()
        alarm.activate()
        assert alarm.status == AlarmStatus.ACTIVE

    def test_activating_active_alarm_raises(self) -> None:
        alarm = Alarm.create_one_time(label="Test", hour=8, minute=0)
        with pytest.raises(AlarmAlreadyInStatus, match="active"):
            alarm.activate()

    def test_activating_cancelled_alarm_raises(self) -> None:
        alarm = Alarm.create_one_time(label="Test", hour=8, minute=0)
        alarm.cancel()
        with pytest.raises(AlarmAlreadyCancelled):
            alarm.activate()


# ---------------------------------------------------------------------------
# Alarm.cancel
# ---------------------------------------------------------------------------


class TestAlarmCancel:
    def test_active_alarm_becomes_cancelled(self) -> None:
        alarm = Alarm.create_one_time(label="Test", hour=8, minute=0)
        alarm.cancel()
        assert alarm.status == AlarmStatus.CANCELLED

    def test_inactive_alarm_becomes_cancelled(self) -> None:
        alarm = Alarm.create_one_time(label="Test", hour=8, minute=0)
        alarm.deactivate()
        alarm.cancel()
        assert alarm.status == AlarmStatus.CANCELLED

    def test_cancelling_already_cancelled_alarm_raises(self) -> None:
        alarm = Alarm.create_one_time(label="Test", hour=8, minute=0)
        alarm.cancel()
        with pytest.raises(AlarmAlreadyCancelled):
            alarm.cancel()
