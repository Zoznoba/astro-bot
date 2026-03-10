from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from config import settings

# ---------------------------------------------------------------------------
# ASYNC УРОК #2: Асинхронная работа с базой данных
# ---------------------------------------------------------------------------
#
# Обычный SQLAlchemy (синхронный) блокирует поток пока выполняется запрос к БД.
# Для async-приложений это неприемлемо — пока один запрос ждёт ответа от БД,
# event loop не может обрабатывать другие сообщения от пользователей.
#
# Решение — SQLAlchemy Async + aiosqlite (async-драйвер для SQLite):
#
#   СИНХРОННО (плохо для бота):              АСИНХРОННО (правильно):
#   result = session.execute(query)  →       result = await session.execute(query)
#   [весь бот заморожен на это время]        [event loop может обрабатывать другие]
#
# create_async_engine использует "sqlite+aiosqlite://" вместо "sqlite://"
# ---------------------------------------------------------------------------


class Base(DeclarativeBase):
    """Базовый класс для всех SQLAlchemy моделей."""
    pass


# Async engine — управляет пулом соединений к БД
# echo=False: не выводить SQL-запросы в консоль (поставь True для отладки)
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
)

# async_sessionmaker — фабрика для создания сессий.
# expire_on_commit=False: объекты остаются доступны после commit() без перезагрузки
AsyncSessionFactory = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def init_db() -> None:
    """Создаёт все таблицы при первом запуске бота."""
    # Импортируем модели здесь чтобы они зарегистрировались в Base.metadata
    from bot.models import user  # noqa: F401

    async with engine.begin() as conn:
        # run_sync запускает синхронную функцию в async контексте
        await conn.run_sync(Base.metadata.create_all)
