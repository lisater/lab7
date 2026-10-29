"""Модели предметной области."""


class User:
    """Пользователь приложения."""

    def __init__(self, username: str, email: str) -> None:
        self.username = username
        self.email = email

    def info(self) -> str:
        return f"{self.username} <{self.email}>"


