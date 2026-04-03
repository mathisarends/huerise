from collections.abc import AsyncIterator

from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from huerise.application import (
    ActivateAlarmCommandHandler,
    CancelAlarmCommandHandler,
    CreateOneTimeAlarmCommandHandler,
    CreateRecurringAlarmCommandHandler,
    DeactivateAlarmCommandHandler,
    DeleteAlarmCommandHandler,
    DeleteSeriesCommandHandler,
    ListAlarmsQueryHandler,
)
from huerise.domain import AlarmRepository
from huerise.infrastructure.persistence import SQLModelAlarmRepository


class DatabaseProvider(Provider):
    def __init__(self, database_url: str) -> None:
        super().__init__()
        engine = create_async_engine(database_url, echo=False)
        self._factory = async_sessionmaker(engine, expire_on_commit=False)

    @provide(scope=Scope.REQUEST)
    async def get_session(self) -> AsyncIterator[AsyncSession]:
        async with self._factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise


class AlarmProvider(Provider):
    scope = Scope.REQUEST

    @provide
    def get_alarm_repository(self, session: AsyncSession) -> AlarmRepository:
        return SQLModelAlarmRepository(session)

    @provide
    def get_list_alarms_handler(self, repo: AlarmRepository) -> ListAlarmsQueryHandler:
        return ListAlarmsQueryHandler(repo)

    @provide
    def get_create_one_time_handler(
        self, repo: AlarmRepository
    ) -> CreateOneTimeAlarmCommandHandler:
        return CreateOneTimeAlarmCommandHandler(repo)

    @provide
    def get_create_recurring_handler(
        self, repo: AlarmRepository
    ) -> CreateRecurringAlarmCommandHandler:
        return CreateRecurringAlarmCommandHandler(repo)

    @provide
    def get_activate_handler(
        self, repo: AlarmRepository
    ) -> ActivateAlarmCommandHandler:
        return ActivateAlarmCommandHandler(repo)

    @provide
    def get_deactivate_handler(
        self, repo: AlarmRepository
    ) -> DeactivateAlarmCommandHandler:
        return DeactivateAlarmCommandHandler(repo)

    @provide
    def get_cancel_handler(self, repo: AlarmRepository) -> CancelAlarmCommandHandler:
        return CancelAlarmCommandHandler(repo)

    @provide
    def get_delete_alarm_handler(
        self, repo: AlarmRepository
    ) -> DeleteAlarmCommandHandler:
        return DeleteAlarmCommandHandler(repo)

    @provide
    def get_delete_series_handler(
        self, repo: AlarmRepository
    ) -> DeleteSeriesCommandHandler:
        return DeleteSeriesCommandHandler(repo)
