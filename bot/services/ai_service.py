import logging

import httpx

from config import settings

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# ASYNC УРОК #3: Асинхронные HTTP-запросы с httpx
# ---------------------------------------------------------------------------
#
# requests (синхронная библиотека) блокирует поток на время HTTP-запроса.
# В async-боте это означает что пока один пользователь ждёт ответа от AI,
# остальные пользователи не получат ответа вообще.
#
# httpx.AsyncClient решает это:
#
#   СИНХРОННО (плохо):                   АСИНХРОННО (правильно):
#   resp = requests.post(url, ...)  →    resp = await client.post(url, ...)
#   [все 50 пользователей ждут]          [event loop обрабатывает других пока ждём]
#
# async with httpx.AsyncClient() as client:
#   - создаёт клиент при входе в блок
#   - автоматически закрывает соединение при выходе (даже при исключении)
#   - аналог: with open("file") as f: — только async
# ---------------------------------------------------------------------------

YANDEX_GPT_URL = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"


async def ask_yandex_gpt(prompt: str, system_prompt: str = "") -> str:
    """
    Отправляет запрос к YandexGPT и возвращает текстовый ответ.

    Args:
        prompt: Основной запрос пользователя / промпт для генерации
        system_prompt: Системная инструкция (роль и стиль ответа модели)

    Returns:
        Текстовый ответ от модели YandexGPT
    """
    # Формат modelUri: "gpt://{folder_id}/{model_name}"
    model_uri = f"gpt://{settings.YANDEX_FOLDER_ID}/yandexgpt-lite"

    headers = {
        "Authorization": f"Api-Key {settings.YANDEX_API_KEY}",
        "x-folder-id": settings.YANDEX_FOLDER_ID,
        "Content-Type": "application/json",
    }

    messages = []
    if system_prompt:
        messages.append({"role": "system", "text": system_prompt})
    messages.append({"role": "user", "text": prompt})

    payload = {
        "modelUri": model_uri,
        "completionOptions": {
            "stream": False,
            "temperature": 0.7,
            "maxTokens": "1500",
        },
        "messages": messages,
    }

    # async with создаёт новый HTTP-клиент на время запроса
    # timeout=30.0 — если YandexGPT не отвечает 30 сек, выбрасываем ошибку
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.post(YANDEX_GPT_URL, headers=headers, json=payload)
            response.raise_for_status()  # Бросает исключение при HTTP 4xx/5xx

            data = response.json()
            return data["result"]["alternatives"][0]["message"]["text"]

        except httpx.TimeoutException:
            logger.error("YandexGPT API timeout")
            return "⏳ Сервис временно недоступен. Попробуй чуть позже."
        except httpx.HTTPStatusError as e:
            logger.error(f"YandexGPT HTTP error: {e.response.status_code} — {e.response.text}")
            return "❌ Ошибка при обращении к AI. Проверь API-ключ и Folder ID."
        except (KeyError, IndexError) as e:
            logger.error(f"Unexpected YandexGPT response format: {e}")
            return "❌ Неожиданный формат ответа от AI."
