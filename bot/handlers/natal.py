from datetime import datetime

from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from sqlalchemy import select

from bot.models.user import User
from bot.services.ai_service import ask_yandex_gpt
from bot.services.astrology_service import (
    ASTROLOGY_SYSTEM_PROMPT,
    build_natal_prompt,
    get_zodiac_emoji,
    get_zodiac_sign,
)
from bot.states.forms import NatalForm
from database.db import AsyncSessionFactory

router = Router()


@router.message(Command("natal"))
async def cmd_natal(message: Message, state: FSMContext) -> None:
    """
    Начинает FSM-сценарий натального анализа.

    state: FSMContext — объект для управления состоянием пользователя.
    После set_state() следующее сообщение от этого юзера попадёт
    в хендлер с фильтром NatalForm.waiting_for_birth_date.
    """
    await state.set_state(NatalForm.waiting_for_birth_date)
    await message.answer(
        "🌙 <b>Натальный анализ</b>\n\n"
        "Введи дату рождения в формате <code>ДД.ММ.ГГГГ</code>\n"
        "Например: <code>15.03.1990</code>"
    )


@router.message(NatalForm.waiting_for_birth_date)
async def process_birth_date(message: Message, state: FSMContext) -> None:
    """
    Обрабатывает введённую дату рождения.
    Срабатывает только когда пользователь находится в состоянии waiting_for_birth_date.
    """
    try:
        birth_date = datetime.strptime(message.text.strip(), "%d.%m.%Y").date()
    except ValueError:
        await message.answer(
            "❌ Неверный формат даты. Попробуй ещё раз:\n"
            "Например: <code>15.03.1990</code>"
        )
        return  # Остаёмся в том же состоянии — ждём правильный ввод

    # Сбрасываем состояние FSM — диалог завершён
    await state.clear()

    sign = get_zodiac_sign(birth_date)
    emoji = get_zodiac_emoji(sign)

    # Сохраняем знак и дату рождения в профиле пользователя
    async with AsyncSessionFactory() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == message.from_user.id)
        )
        user = result.scalar_one_or_none()
        if user:
            user.zodiac_sign = sign
            user.birth_date = birth_date
            await session.commit()

    await message.answer(
        f"{emoji} Твой знак зодиака: <b>{sign}</b>\n\n"
        f"🔍 <i>Составляю натальный анализ...</i>"
    )

    prompt = build_natal_prompt(sign, birth_date)
    response = await ask_yandex_gpt(prompt, system_prompt=ASTROLOGY_SYSTEM_PROMPT)

    await message.answer(
        f"{emoji} <b>Натальный анализ</b>\n"
        f"<i>Дата рождения: {birth_date.strftime('%d.%m.%Y')}</i>\n\n"
        f"{response}"
    )
