"""Консольное приложение «Трекер курсов валют»."""
import sys
from app.exceptions import AppError
from app.providers import CbrXmlProvider, StaticRateProvider
from app.services import CurrencyTracker


def print_header(title: str) -> None:
    print(f"\n{'=' * 40}")
    print(f"  {title}")
    print(f"{'=' * 40}")


def main() -> None:
    # Проверяем аргументы командной строки: если есть --offline, берем демо-данные
    provider = StaticRateProvider.demo() if "--offline" in sys.argv else CbrXmlProvider()
    tracker = CurrencyTracker(provider)

    print("Добро пожаловать в Трекер курсов валют ЦБ РФ!")
    if "--offline" in sys.argv:
        print("Режим: ОФЛАЙН (демонстрационные данные)")

    current_user_id = None

    while True:
        print_header("ГЛАВНОЕ МЕНЮ")
        print("1. Зарегистрироваться")
        print("2. Загрузить валюты с сервера")
        print("3. Показать все валюты")
        print("4. Подписаться на валюту")
        print("5. Мои подписки и курсы")
        print("0. Выход")

        if current_user_id:
            print(f"\n[Вы вошли как: {tracker.get_user(current_user_id).username}]")
        else:
            print("\n[Вы не авторизованы]")

        choice = input("\nВыберите действие: ").strip()

        try:
            if choice == "1":
                username = input("Введите имя пользователя: ")
                email = input("Введите email: ")
                user = tracker.register_user(username, email)
                current_user_id = user.id
                print(f"Успешно! Вы зарегистрированы как {user.username}.")

            elif choice == "2":
                print("Загрузка данных...")
                added = tracker.load_currencies()
                print(f"Успешно загружено! Новых валют: {added}")

            elif choice == "3":
                currencies = tracker.list_currencies()
                if not currencies:
                    print("Справочник пуст. Сначала загрузите валюты (пункт 2).")
                else:
                    print("\nДоступные валюты:")
                    for curr in currencies:
                        print(f"  [{curr.code}] {curr.name}")

            elif choice == "4":
                if not current_user_id:
                    print("Сначала зарегистрируйтесь (пункт 1).")
                    continue
                code = input("Введите код валюты для подписки (например, USD): ")
                sub = tracker.subscribe(current_user_id, code)
                print(f"Вы подписались на {sub.currency.name}.")

            elif choice == "5":
                if not current_user_id:
                    print("Сначала зарегистрируйтесь (пункт 1).")
                    continue
                rates = tracker.get_user_rates(current_user_id)
                if not rates:
                    print("У вас нет подписок или данные о курсах не загружены.")
                else:
                    print("\nАктуальные курсы по вашим подпискам:")
                    for code, rate_info in rates.items():
                        print(f"  {code}: {rate_info}")

            elif choice == "0":
                print("До свидания!")
                break
            else:
                print("Неверный пункт меню. Попробуйте еще раз.")

        except AppError as exc:
            # Ловим все наши кастомные ошибки (ValidationError, DuplicateError и т.д.)
            print(f"\nОшибка: {exc}")
        except KeyboardInterrupt:
            print("\nВыход...")
            break
        except Exception as exc:
            print(f"\nНепредвиденная ошибка: {exc}")

        input("\nНажмите Enter, чтобы продолжить...")


if __name__ == "__main__":
    main()