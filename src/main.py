from src.database.db import create_tables, insert_sample_data
from src.repository.repository import Repository
import os

DB_FILE = "hotel.db"

def main():
    # Если базы нет, создаем таблицы и вставляем тестовые данные
    if not os.path.exists(DB_FILE):
        create_tables(DB_FILE)
        insert_sample_data(DB_FILE)

    repo = Repository(DB_FILE)

    # --- Основной цикл программы ---
    while True:
        print("\n=== Система управления отелем ===")
        print("1 - Показать все комнаты")
        print("2 - Показать свободные комнаты")
        print("3 - Показать всех клиентов")
        print("4 - Создать бронирование")
        print("5 - Показать все бронирования")
        print("6 - Отменить бронирование")
        print("0 - Выход")
        choice = input("Ваш выбор: ")

        if choice == "1":
            rooms = repo.get_all_rooms()
            print("\nСписок всех комнат:")
            for room in rooms:
                print(f"{room.room_id}: №{room.room_number} - {room.price_per_day} руб./день - {room.status}")

        elif choice == "2":
            rooms = repo.get_available_rooms()
            print("\nСвободные комнаты:")
            for room in rooms:
                print(f"{room.room_id}: №{room.room_number} - {room.price_per_day} руб./день")

        elif choice == "3":
            clients = repo.get_all_clients()
            print("\nСписок всех клиентов:")
            for client in clients:
                print(f"{client.client_id}: {client.name} - {client.phone} - {client.email}")

        elif choice == "4":
            print("\nСоздание нового бронирования:")

            # Показываем свободные комнаты
            available_rooms = repo.get_available_rooms()
            if not available_rooms:
                print("Нет свободных комнат для бронирования")
                continue

            print("Доступные комнаты:")
            for room in available_rooms:
                print(f"{room.room_id}: №{room.room_number} - {room.price_per_day} руб./день")

            room_id = int(input("Выберите ID комнаты: "))

            clients = repo.get_all_clients()
            print("\nСуществующие клиенты:")
            for client in clients:
                print(f"{client.client_id}: {client.name}")

            client_choice = input("Использовать существующего клиента (введите ID) или создать нового (введите 'new'): ")

            if client_choice.lower() == 'new':
                name = input("Имя клиента: ")
                phone = input("Телефон: ")
                email = input("Email: ")
                client_id = repo.add_client(name, phone, email)
                print(f"Создан новый клиент с ID: {client_id}")
            else:
                client_id = int(client_choice)

            start_date = input("Дата заезда (ГГГГ-ММ-ДД): ")
            end_date = input("Дата выезда (ГГГГ-ММ-ДД): ")

            try:
                booking_id = repo.create_booking(room_id, client_id, start_date, end_date)
                print(f"Бронирование создано успешно! ID бронирования: {booking_id}")
            except Exception as e:
                print(f"Ошибка при создании бронирования: {e}")

        elif choice == "5":
            bookings = repo.get_all_bookings()
            print("\nВсе бронирования:")
            for booking in bookings:
                room = repo.get_room_by_id(booking.room_id)
                client = repo.get_client_by_id(booking.client_id)
                print(f"Бронирование {booking.booking_id}: Комната №{room.room_number}, "
                      f"Клиент: {client.name}, с {booking.start_date} по {booking.end_date}")

        elif choice == "6":
            bookings = repo.get_all_bookings()
            print("\nТекущие бронирования:")
            for booking in bookings:
                room = repo.get_room_by_id(booking.room_id)
                client = repo.get_client_by_id(booking.client_id)
                print(f"{booking.booking_id}: Комната №{room.room_number}, "
                      f"Клиент: {client.name}, с {booking.start_date} по {booking.end_date}")

            booking_id = int(input("Введите ID бронирования для отмены: "))
            if repo.delete_booking(booking_id):
                print("Бронирование успешно отменено")
            else:
                print("Бронирование не найдено")

        elif choice == "0":
            print("Выход из программы...")
            break
        else:
            print("Неверный выбор. Попробуйте снова.")

    repo.close()

if __name__ == "__main__":
    main()