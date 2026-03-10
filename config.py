from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Конфигурация приложения через pydantic-settings.

    pydantic-settings автоматически читает переменные из файла .env
    и валидирует их типы. Если переменная отсутствует — будет ошибка при старте.
    Это гораздо безопаснее, чем os.getenv() без проверки.
    """

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    BOT_TOKEN: str
    YANDEX_API_KEY: str
    YANDEX_FOLDER_ID: str

    DATABASE_URL: str = "sqlite+aiosqlite:///./astro_bot.db"


# Единственный экземпляр настроек — импортируем его во всех модулях
settings = Settings()
