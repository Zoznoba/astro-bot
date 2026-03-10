import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from config import settings
from database.db import init_db
from bot.handlers import start, help, horoscope, natal, compatibility

# ---------------------------------------------------------------------------
# Настройка логирования
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# ASYNC УРОК #1: Точка входа и Event Loop
# ---------------------------------------------------------------------------
#
# Python выполняет код последовательно (синхронно).
# Async позволяет "переключаться" между задачами пока одна из них ждёт I/O
# (сеть, диск, БД), не блокируя весь процесс.
#
# asyncio.run(main()) создаёт Event Loop — "диспетчер", который:
#   1. Принимает корутины (async def функции)
#   2. Запускает их, переключается между ними когда они "ждут" (await)
#   3. Завершает работу когда все корутины выполнены
#
# Аналог из жизни: официант в кафе. Он не стоит и не ждёт пока готовится
# один заказ — он берёт следующий, потом возвращается за готовым.
# ---------------------------------------------------------------------------


async def main() -> None:
    # Bot — объект для отправки запросов к Telegram API
    # DefaultBotProperties задаёт параметры по умолчанию для всех сообщений
    bot = Bot(
        token=settings.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )

    # Dispatcher — "маршрутизатор" обновлений.
    # Он получает обновления от Telegram и передаёт их нужному хендлеру.
    dp = Dispatcher()

    # Регистрируем роутеры каждого модуля хендлеров
    dp.include_router(start.router)
    dp.include_router(help.router)
    dp.include_router(horoscope.router)
    dp.include_router(natal.router)
    dp.include_router(compatibility.router)

    # Создаём таблицы в БД если они ещё не существуют
    await init_db()

    logger.info("Бот запущен! Нажми Ctrl+C для остановки.")

    # start_polling — запускает бесконечный цикл опроса Telegram API.
    # await здесь означает: "передай управление event loop-у пока бот работает"
    await dp.start_polling(bot)


if __name__ == "__main__":
    # asyncio.run() — создаёт event loop, запускает main(), закрывает loop после завершения
    asyncio.run(main())
