from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from sqlalchemy import select

from bot.models.user import User
from database.db import AsyncSessionFactory

# ---------------------------------------------------------------------------
# ASYNC УРОК #5: Хендлеры aiogram — это корутины
# ---------------------------------------------------------------------------
#
# Router — это "мини-диспетчер" для группы хендлеров.
# Каждый модуль создаёт свой Router и регистрирует его в main.py
#
# @router.message(CommandStart()) — декоратор-фильтр.
# Когда приходит сообщение "/start", aiogram вызывает cmd_start.
#
# async def cmd_start(message: Message):
#   Это корутина. aiogram 'await'-ит её через event loop.
#   Внутри можно использовать await для любых async операций:
#   - await message.answer(...)   — отправить сообщение
#   - await session.execute(...)  — запрос к БД
#   - await ask_yandex_gpt(...)   — запрос к AI
# ---------------------------------------------------------------------------

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    """
    Обрабатывает команду /start.
    Сохраняет нового пользователя в БД или приветствует существующего.
    """
    async with AsyncSessionFactory() as session:
        # Ищем пользователя по telegram_id
        result = await session.execute(
            select(User).where(User.telegram_id == message.from_user.id)
        )
        user = result.scalar_one_or_none()

        if not user:
            # Новый пользователь — создаём запись
            user = User(
                telegram_id=message.from_user.id,
                username=message.from_user.username,
                first_name=message.from_user.first_name,
            )
            session.add(user)
            await session.commit()

    name = message.from_user.first_name or "друг"
    await message.answer(
        f"✨ <b>Привет, {name}!</b>\n\n"
        f"Я — AstroBot, твой личный астрологический помощник 🔮\n\n"
        f"Что я умею:\n"
        f"🌟 /horoscope — гороскоп на сегодня\n"
        f"🌙 /natal — натальный анализ по дате рождения\n"
        f"💞 /compatibility — совместимость двух знаков\n"
        f"❓ /help — все команды\n\n"
        f"Выбери команду и начнём! ⭐"
    )
