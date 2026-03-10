from datetime import date

from sqlalchemy import BigInteger, Date, String
from sqlalchemy.orm import Mapped, mapped_column

from database.db import Base


class User(Base):
    """
    Модель пользователя Telegram.

    Mapped[type] + mapped_column() — современный синтаксис SQLAlchemy 2.0,
    позволяет использовать аннотации типов вместо Column(String(...)).
    str | None означает что поле может быть NULL в БД.
    """

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    username: Mapped[str | None] = mapped_column(String(64), nullable=True)
    first_name: Mapped[str | None] = mapped_column(String(64), nullable=True)
    zodiac_sign: Mapped[str | None] = mapped_column(String(32), nullable=True)
    birth_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    def __repr__(self) -> str:
        return f"User(id={self.id}, telegram_id={self.telegram_id}, username=@{self.username})"
