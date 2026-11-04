"""Сервисный слой: бизнес-логика приложения."""
from __future__ import annotations
from app.exceptions import DuplicateError, NotFoundError
from app.models import User, Currency, Subscription
from app.providers import RateProvider


class CurrencyTracker:
    """Сервис для управления пользователями, валютами и подписками."""

    def __init__(self, provider: RateProvider) -> None:
        self._provider = provider
        self._users: dict[int, User] = {}
        self._currencies: dict[int, Currency] = {}
        self._subscriptions: set[Subscription] = set()

    # --- Пользователи ---
    def register_user(self, username: str, email: str) -> User:
        """Зарегистрировать нового пользователя."""
        for user in self._users.values():
            if user.username.lower() == username.lower():
                raise DuplicateError(f"Пользователь с именем {username} уже существует")
            if user.email.lower() == email.lower():
                raise DuplicateError(f"Пользователь с email {email} уже существует")

        new_user = User(username, email)
        self._users[new_user.id] = new_user
        return new_user

    def get_user(self, user_id: int) -> User:
        if user_id not in self._users:
            raise NotFoundError(f"Пользователь с id={user_id} не найден")
        return self._users[user_id]

    # --- Валюты ---
    def load_currencies(self) -> int:
        """Загрузить справочник валют из провайдера. Возвращает число новых валют."""
        rates = self._provider.get_rates()
        added_count = 0

        existing_codes = {c.code for c in self._currencies.values()}

        for code, rate in rates.items():
            if code not in existing_codes:
                new_currency = Currency(code, rate.name)
                self._currencies[new_currency.id] = new_currency
                added_count += 1

        return added_count

    def list_currencies(self) -> list[Currency]:
        return list(self._currencies.values())

    def get_currency(self, currency_id: int) -> Currency:
        if currency_id not in self._currencies:
            raise NotFoundError(f"Валюта с id={currency_id} не найдена")
        return self._currencies[currency_id]

    def get_currency_by_code(self, code: str) -> Currency:
        code = code.upper()
        for curr in self._currencies.values():
            if curr.code == code:
                return curr
        raise NotFoundError(f"Валюта {code} не найдена")

    # --- Подписки ---
    def subscribe(self, user_id: int, currency_code: str) -> Subscription:
        user = self.get_user(user_id)
        currency = self.get_currency_by_code(currency_code)

        new_sub = Subscription(user, currency)
        if new_sub in self._subscriptions:
            raise DuplicateError(f"Вы уже подписаны на {currency.code}")

        self._subscriptions.add(new_sub)
        return new_sub

    def unsubscribe(self, user_id: int, currency_code: str) -> None:
        user = self.get_user(user_id)
        currency = self.get_currency_by_code(currency_code)

        sub = Subscription(user, currency)
        if sub not in self._subscriptions:
            raise NotFoundError(f"Подписка на {currency.code} не найдена")

        self._subscriptions.remove(sub)

    def get_user_subscriptions(self, user_id: int) -> list[Currency]:
        """Вернуть список валют, на которые подписан пользователь."""
        self.get_user(user_id)  # проверяем, что юзер существует
        return [sub.currency for sub in self._subscriptions if sub.user_id == user_id]

    # --- Курсы ---
    def get_user_rates(self, user_id: int) -> dict[str, str]:
        """Получить актуальные курсы валют по подпискам пользователя."""
        currencies = self.get_user_subscriptions(user_id)
        rates = self._provider.get_rates()

        result = {}
        for curr in currencies:
            if curr.code in rates:
                rate = rates[curr.code]
                result[curr.code] = f"{rate.value} RUB за {rate.nominal} {rate.code}"
        return result
