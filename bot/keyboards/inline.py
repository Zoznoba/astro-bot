from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.services.astrology_service import ZODIAC_SIGNS


def zodiac_keyboard() -> InlineKeyboardMarkup:
    """
    Создаёт inline-клавиатуру с 12 знаками зодиака (3 кнопки в ряд).
    callback_data в формате "zodiac:{sign}" — обрабатывается в handlers/horoscope.py
    """
    builder = InlineKeyboardBuilder()
    for sign, emoji in ZODIAC_SIGNS.items():
        builder.button(text=f"{emoji} {sign}", callback_data=f"zodiac:{sign}")
    builder.adjust(3)  # 3 кнопки в каждой строке
    return builder.as_markup()


def compatibility_keyboard(selected_sign: str | None = None) -> InlineKeyboardMarkup:
    """
    Клавиатура выбора знака для совместимости.
    Если знак уже выбран — отмечает его галочкой ✅
    callback_data в формате "compat:{sign}"
    """
    builder = InlineKeyboardBuilder()
    for sign, emoji in ZODIAC_SIGNS.items():
        if sign == selected_sign:
            text = f"✅ {emoji} {sign}"
        else:
            text = f"{emoji} {sign}"
        builder.button(text=text, callback_data=f"compat:{sign}")
    builder.adjust(3)
    return builder.as_markup()
