from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.keyboards.inline import compatibility_keyboard
from bot.services.ai_service import ask_yandex_gpt
from bot.services.astrology_service import (
    ASTROLOGY_SYSTEM_PROMPT,
    build_compatibility_prompt,
    get_zodiac_emoji,
)
from bot.states.forms import CompatibilityForm

router = Router()


@router.message(Command("compatibility"))
async def cmd_compatibility(message: Message, state: FSMContext) -> None:
    """Начинает FSM: просим выбрать первый знак зодиака."""
    await state.set_state(CompatibilityForm.waiting_for_first_sign)
    await message.answer(
        "💞 <b>Совместимость знаков</b>\n\n"
        "Выбери <b>первый</b> знак зодиака:",
        reply_markup=compatibility_keyboard(),
    )


@router.callback_query(CompatibilityForm.waiting_for_first_sign, F.data.startswith("compat:"))
async def process_first_sign(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Сохраняем первый знак в FSM-данных и просим выбрать второй.

    state.update_data() — сохраняет произвольные данные в FSM-сессии пользователя.
    Эти данные доступны на следующих шагах через state.get_data().
    """
    sign1 = callback.data.split(":")[1]

    await state.update_data(sign1=sign1)
    await state.set_state(CompatibilityForm.waiting_for_second_sign)

    await callback.answer()
    await callback.message.edit_text(
        f"💞 <b>Совместимость знаков</b>\n\n"
        f"Первый знак: <b>{get_zodiac_emoji(sign1)} {sign1}</b>\n\n"
        f"Теперь выбери <b>второй</b> знак:",
        reply_markup=compatibility_keyboard(selected_sign=sign1),
    )


@router.callback_query(CompatibilityForm.waiting_for_second_sign, F.data.startswith("compat:"))
async def process_second_sign(callback: CallbackQuery, state: FSMContext) -> None:
    """Получаем второй знак и запускаем анализ совместимости."""
    sign2 = callback.data.split(":")[1]

    # Извлекаем первый знак из FSM-данных
    data = await state.get_data()
    sign1 = data["sign1"]

    await state.clear()
    await callback.answer()

    emoji1 = get_zodiac_emoji(sign1)
    emoji2 = get_zodiac_emoji(sign2)

    # Редактируем сообщение с клавиатурой — убираем кнопки, показываем прогресс
    await callback.message.edit_text(
        f"💞 {emoji1} <b>{sign1}</b> и {emoji2} <b>{sign2}</b>\n\n"
        f"🔍 <i>Анализирую совместимость...</i>"
    )

    prompt = build_compatibility_prompt(sign1, sign2)
    response = await ask_yandex_gpt(prompt, system_prompt=ASTROLOGY_SYSTEM_PROMPT)

    await callback.message.answer(
        f"💞 <b>Совместимость: {emoji1} {sign1} и {emoji2} {sign2}</b>\n\n"
        f"{response}"
    )
