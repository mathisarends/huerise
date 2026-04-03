import importlib.util

if importlib.util.find_spec("fastmcp") is None:
    raise ImportError(
        "MCP support requires 'fastmcp'. Install with: pip install huerise[mcp]"
    )

from fastmcp import Context

from uuid import UUID

from huerise.application.commands import (
    ActivateAlarmCommand,
    ActivateAlarmCommandHandler,
    CancelAlarmCommand,
    CancelAlarmCommandHandler,
    CreateOneTimeAlarmCommand,
    CreateOneTimeAlarmCommandHandler,
    CreateRecurringAlarmCommand,
    CreateRecurringAlarmCommandHandler,
    DeactivateAlarmCommand,
    DeactivateAlarmCommandHandler,
    DeleteAlarmCommand,
    DeleteAlarmCommandHandler,
    DeleteSeriesCommand,
    DeleteSeriesCommandHandler,
    SnoozeAlarmCommand,
    SnoozeAlarmCommandHandler,
)
from huerise.application.queries import ListAlarmsQuery, ListAlarmsQueryHandler
from huerise.domain.views import Weekday
from huerise.presentation.api.schemas import AlarmOut
from huerise.presentation.mapper import to_alarm_out
from huerise.presentation.mcp.server import mcp


@mcp.tool()
async def list_alarms(ctx: Context) -> list[AlarmOut]:
    async with ctx.lifespan_context["container"]() as scope:
        handler = await scope.get(ListAlarmsQueryHandler)
        alarms = await handler.execute(ListAlarmsQuery())
        return [to_alarm_out(a) for a in alarms]


@mcp.tool()
async def create_one_time_alarm(
    label: str,
    hour: int,
    minute: int,
    room_name: str,
    ctx: Context,
    intro_audio_file: str = "wake-up-bowls.mp3",
    ringtone_audio_file: str = "get-up-aurora.mp3",
) -> AlarmOut:
    """Create a one-time alarm that fires on the next occurrence of the given time."""
    async with ctx.lifespan_context["container"]() as scope:
        handler = await scope.get(CreateOneTimeAlarmCommandHandler)
        command = CreateOneTimeAlarmCommand(
            label=label,
            hour=hour,
            minute=minute,
            room_name=room_name,
            intro_audio_file=intro_audio_file,
            ringtone_audio_file=ringtone_audio_file,
        )
        alarm = await handler.execute(command)
        return to_alarm_out(alarm)


@mcp.tool()
async def create_recurring_alarm(
    label: str,
    hour: int,
    minute: int,
    days: list[Weekday],
    room_name: str,
    ctx: Context,
    intro_audio_file: str = "wake-up-bowls.mp3",
    ringtone_audio_file: str = "get-up-aurora.mp3",
) -> AlarmOut:
    async with ctx.lifespan_context["container"]() as scope:
        handler = await scope.get(CreateRecurringAlarmCommandHandler)
        command = CreateRecurringAlarmCommand(
            label=label,
            hour=hour,
            minute=minute,
            days=frozenset(days),
            room_name=room_name,
            intro_audio_file=intro_audio_file,
            ringtone_audio_file=ringtone_audio_file,
        )
        alarm = await handler.execute(command)
        return to_alarm_out(alarm)


@mcp.tool()
async def activate_alarm(alarm_id: UUID, ctx: Context) -> AlarmOut:
    async with ctx.lifespan_context["container"]() as scope:
        handler = await scope.get(ActivateAlarmCommandHandler)
        alarm = await handler.execute(ActivateAlarmCommand(alarm_id=alarm_id))
        return to_alarm_out(alarm)


@mcp.tool()
async def deactivate_alarm(alarm_id: UUID, ctx: Context) -> AlarmOut:
    async with ctx.lifespan_context["container"]() as scope:
        handler = await scope.get(DeactivateAlarmCommandHandler)
        alarm = await handler.execute(DeactivateAlarmCommand(alarm_id=alarm_id))
        return to_alarm_out(alarm)


@mcp.tool()
async def cancel_alarm(alarm_id: UUID, ctx: Context) -> AlarmOut:
    async with ctx.lifespan_context["container"]() as scope:
        handler = await scope.get(CancelAlarmCommandHandler)
        alarm = await handler.execute(CancelAlarmCommand(alarm_id=alarm_id))
        return to_alarm_out(alarm)


@mcp.tool()
async def snooze_alarm(alarm_id: UUID, ctx: Context, minutes: int = 10) -> AlarmOut:
    async with ctx.lifespan_context["container"]() as scope:
        handler = await scope.get(SnoozeAlarmCommandHandler)
        alarm = await handler.execute(
            SnoozeAlarmCommand(alarm_id=alarm_id, minutes=minutes)
        )
        return to_alarm_out(alarm)


@mcp.tool()
async def delete_alarm(alarm_id: UUID, ctx: Context) -> None:
    async with ctx.lifespan_context["container"]() as scope:
        handler = await scope.get(DeleteAlarmCommandHandler)
        await handler.execute(DeleteAlarmCommand(alarm_id=alarm_id))


@mcp.tool()
async def delete_series(series_id: UUID, ctx: Context) -> None:
    async with ctx.lifespan_context["container"]() as scope:
        handler = await scope.get(DeleteSeriesCommandHandler)
        await handler.execute(DeleteSeriesCommand(series_id=series_id))
