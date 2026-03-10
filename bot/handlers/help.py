from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

router = Router()


@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    """Показывает список всех доступных команд."""
    await message.answer(
        "🔮 <b>AstroBot — список команд</b>\n\n"
        "🌟 /horoscope — гороскоп на сегодня по знаку зодиака\n"
        "🌙 /natal — натальный анализ по дате рождения\n"
        "💞 /compatibility — совместимость двух знаков зодиака\n"
        "❓ /help — это сообщение\n\n"
        "<i>Powered by YandexGPT ✨</i>"
    )
