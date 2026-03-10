from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from bot.keyboards.inline import zodiac_keyboard
from bot.services.ai_service import ask_yandex_gpt
from bot.services.astrology_service import (
    ASTROLOGY_SYSTEM_PROMPT,
    build_horoscope_prompt,
    get_zodiac_emoji,
)

router = Router()


@router.message(Command("horoscope"))
async def cmd_horoscope(message: Message) -> None:
    """Показывает inline-клавиатуру с выбором знака зодиака."""
    await message.answer(
        "🌟 <b>Выбери свой знак зодиака:</b>",
        reply_markup=zodiac_keyboard(),
    )


@router.callback_query(F.data.startswith("zodiac:"))
async def process_zodiac_selection(callback: CallbackQuery) -> None:
    """
    Обрабатывает нажатие на знак зодиака и возвращает гороскоп.

    CallbackQuery — тип обновления при нажатии inline-кнопки.
    F.data.startswith("zodiac:") — фильтр Magic Filter aiogram 3.x,
    аналог lambda: callback.data.startswith("zodiac:")
    """
    sign = callback.data.split(":")[1]
    emoji = get_zodiac_emoji(sign)

    # Отвечаем на callback чтобы убрать "часики" у кнопки в Telegram
    await callback.answer()

    # Сообщение-заглушка пока AI генерирует ответ
    await callback.message.answer(f"{emoji} <b>Составляю гороскоп для {sign}...</b>")

    # await приостанавливает корутину до ответа YandexGPT
    # event loop в это время обрабатывает других пользователей
    prompt = build_horoscope_prompt(sign)
    response = await ask_yandex_gpt(prompt, system_prompt=ASTROLOGY_SYSTEM_PROMPT)

    await callback.message.answer(
        f"{emoji} <b>Гороскоп для знака {sign}</b>\n\n{response}"
    )
