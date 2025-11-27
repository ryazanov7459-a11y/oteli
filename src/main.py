from src.database.db import create_tables, insert_sample_data
from src.repository.repository import Repository
import os

DB_FILE = "hotel.db"

class HotelSystem:
    def __init__(self):
        if not os.path.exists(DB_FILE):
            create_tables(DB_FILE)
            insert_sample_data(DB_FILE)
        self.repo = Repository(DB_FILE)
        self.current_user = None

    def authenticate(self):
        print("\n=== Аутентификация ===")
        while True:
            print("1 - Вход")
            print("2 - Регистрация (для клиентов)")
            print("0 - Выход")
            choice = input("Ваш выбор: ")

            if choice == "1":
                username = input("Логин: ")
                password = input("Пароль: ")
                user = self.repo.authenticate_user(username, password)
                if user:
                    self.current_user = user
                    print(f"Добро пожаловать, {user.username} ({user.role})!")
                    return True
                else:
                    print("Неверный логин или пароль!")

            elif choice == "2":
                self.register_client()

            elif choice == "0":
                return False
            else:
                print("Неверный выбор!")

    def register_client(self):
        print("\n Регистрация ")
        username = input("Логин: ")
        password = input("Пароль: ")
        name = input("ФИО: ")
        phone = input("Телефон: ")
        email = input("Email: ")

        if self.repo.register_client(username, password, name, phone, email):
            print("Регистрация успешна! Теперь вы можете войти.")
        else:
            print("Неправильно, прпроьуйте ещё раз.")

    def receptionist_menu(self):
        while True:
            print("\n портье ")
            print("1 - Просмотреть все номера")
            print("2 - Просмотреть свободные номера")
            print("3 - Показать всех клиентов")
            print("4 - Оформить бронирование")
            print("5 - Показать все бронирования")
            print("6 - Отменить бронирование")
            print("7 - Добавить номер")
            print("8 - Редактировать номер")
            print("9 - Удалить номер")
            print("0 - Выход")
            choice = input("Ваш выбор: ")

            if choice == "1":
                self.show_all_rooms()
            elif choice == "2":
                self.show_available_rooms()
            elif choice == "3":
                self.show_all_clients()
            elif choice == "4":
                self.create_booking_receptionist()
            elif choice == "5":
                self.show_all_bookings()
            elif choice == "6":
                self.cancel_booking()
            elif choice == "7":
                self.add_room()
            elif choice == "8":
                self.edit_room()
            elif choice == "9":
                self.delete_room()
            elif choice == "0":
                break
            else:
                print("Неправильно, прпроьуйте ещё раз.")

    def client_menu(self):
        while True:
            print("\n клиент ")
            print("1 - Просмотреть все номера")
            print("2 - Просмотреть свободные номера")
            print("3 - Забронировать номер")
            print("4 - Мои бронирования")
            print("5 - Отменить бронирование")
            print("0 - Выход")
            choice = input("Ваш выбор: ")

            if choice == "1":
                self.show_all_rooms()
            elif choice == "2":
                self.show_available_rooms()
            elif choice == "3":
                self.create_booking_client()
            elif choice == "4":
                self.show_my_bookings()
            elif choice == "5":
                self.cancel_my_booking()
            elif choice == "0":
                break
            else:
                print("Неправильно, прпроьуйте ещё раз.")

    def show_all_rooms(self):
        rooms = self.repo.get_all_rooms()
        print("\nВсе номера:")
        for room in rooms:
            print(f"{room.room_id}: №{room.room_number} - {room.price_per_day} руб./день - {room.status}")

    def show_available_rooms(self):
        rooms = self.repo.get_available_rooms()
        print("\nСвободные номера:")
        for room in rooms:
            print(f"{room.room_id}: №{room.room_number} - {room.price_per_day} руб./день")

    def show_all_clients(self):
        if self.current_user.role != 'receptionist':
            print("Доступ запрещен!")
            return

        clients = self.repo.get_all_clients()
        print("\nВсе клиенты:")
        for client in clients:
            print(f"{client.client_id}: {client.name} - {client.phone} - {client.email}")

    def show_all_bookings(self):
        if self.current_user.role != 'receptionist':
            print("Доступ запрещен!")
            return

        bookings = self.repo.get_all_bookings()
        print("\nВсе бронирования:")
        for booking in bookings:
            room = self.repo.get_room_by_id(booking.room_id)
            client = self.repo.get_client_by_id(booking.client_id)
            print(f"Бронирование {booking.booking_id}: Комната №{room.room_number}, "
                  f"Клиент: {client.name}, с {booking.start_date} по {booking.end_date}")

    def show_my_bookings(self):
        if not self.current_user.client_id:
            print("клиент не найден(((")
            return

        bookings = self.repo.get_bookings_by_client(self.current_user.client_id)
        print("\nМои бронирования:")
        for booking in bookings:
            room = self.repo.get_room_by_id(booking.room_id)
            print(f"Бронирование {booking.booking_id}: Комната №{room.room_number}, "
                  f"с {booking.start_date} по {booking.end_date}")

    def create_booking_receptionist(self):
        print("\n=== Оформление бронирования ===")

        available_rooms = self.repo.get_available_rooms()
        if not available_rooms:
            print("Нет свободных комнат для бронирования")
            return

        print("Доступные комнаты:")
        for room in available_rooms:
            print(f"{room.room_id}: №{room.room_number} - {room.price_per_day} руб./день")

        try:
            room_id = int(input("Выберите ID комнаты: "))

            clients = self.repo.get_all_clients()
            print("\nКлиенты:")
            for client in clients:
                print(f"{client.client_id}: {client.name}")

            client_choice = input("Выберите ID клиента или введите 'new' для нового клиента: ")

            if client_choice.lower() == 'new':
                name = input("ФИО клиента: ")
                phone = input("Телефон: ")
                email = input("Email: ")
                client_id = self.repo.add_client(name, phone, email)
                print(f"Создан новый клиент с ID: {client_id}")
            else:
                client_id = int(client_choice)

            start_date = input("Дата заезда (ГГГГ-ММ-ДД): ")
            end_date = input("Дата выезда (ГГГГ-ММ-ДД): ")

            booking_id = self.repo.create_booking(room_id, client_id, start_date, end_date)
            if booking_id:
                print(f"Бронирование создано успешно! ID бронирования: {booking_id}")
            else:
                print("Ошибка: комната недоступна для бронирования")

        except ValueError:
            print("Ошибка ввода данных!")
        except Exception as e:
            print(f"Ошибка при создании бронирования: {e}")

    def create_booking_client(self):
        print("\n Бронирование номера ")

        available_rooms = self.repo.get_available_rooms()
        if not available_rooms:
            print("Нет свободных комнат")
            return

        print("Доступные комнаты:")
        for room in available_rooms:
            print(f"{room.room_id}: №{room.room_number} - {room.price_per_day} руб./день")

        try:
            room_id = int(input("Выберите ID комнаты: "))
            start_date = input("Дата заезда (ГГГГ-ММ-ДД): ")
            end_date = input("Дата выезда (ГГГГ-ММ-ДД): ")

            client_id = self.current_user.client_id
            booking_id = self.repo.create_booking(room_id, client_id, start_date, end_date)

            if booking_id:
                print(f"Бронирование создано успешно! ID бронирования: {booking_id}")
            else:
                print("Ошибка: комната недоступна для бронирования")

        except ValueError:
            print("Ошибка ввода данных!")
        except Exception as e:
            print(f"Ошибка при создании бронирования: {e}")

    def cancel_booking(self):
        bookings = self.repo.get_all_bookings()
        print("\nТекущие бронирования:")
        for booking in bookings:
            room = self.repo.get_room_by_id(booking.room_id)
            client = self.repo.get_client_by_id(booking.client_id)
            print(f"{booking.booking_id}: Комната №{room.room_number}, "
                  f"Клиент: {client.name}, с {booking.start_date} по {booking.end_date}")

        try:
            booking_id = int(input("Введите ID бронирования для отмены: "))
            if self.repo.cancel_booking(booking_id):
                print("Бронирование успешно отменено")
            else:
                print("Бронирование не найдено")
        except ValueError:
            print("Ошибка ввода!")

    def cancel_my_booking(self):
        if not self.current_user.client_id:
            print("клиент не найден(((")
            return

        bookings = self.repo.get_bookings_by_client(self.current_user.client_id)
        print("\nМои бронирования:")
        for booking in bookings:
            room = self.repo.get_room_by_id(booking.room_id)
            print(f"{booking.booking_id}: Комната №{room.room_number}, "
                  f"с {booking.start_date} по {booking.end_date}")

        try:
            booking_id = int(input("Введите ID бронирования для отмены: "))
            target_booking = None
            for booking in bookings:
                if booking.booking_id == booking_id:
                    target_booking = booking
                    break

            if target_booking and self.repo.cancel_booking(booking_id):
                print("Бронирование успешно отменено")
            else:
                print("Бронирование не найдено или у вас нет прав для его отмены")
        except ValueError:
            print("Ошибка ввода!")

    def add_room(self):
        if self.current_user.role != 'receptionist':
            print("Доступ запрещен!")
            return

        print("\n=== Добавление номера ===")
        room_number = input("Номер комнаты: ")
        try:
            price = float(input("Цена за сутки: "))
            if self.repo.add_room(room_number, price):
                print("Номер успешно добавлен")
            else:
                print("Ошибка: номер с таким номером уже существует")
        except ValueError:
            print("Ошибка ввода цены!")

    def edit_room(self):
        if self.current_user.role != 'receptionist':
            print("Доступ запрещен!")
            return

        rooms = self.repo.get_all_rooms()
        print("\nВсе номера:")
        for room in rooms:
            print(f"{room.room_id}: №{room.room_number} - {room.price_per_day} руб./день - {room.status}")

        try:
            room_id = int(input("Введите ID номера для редактирования: "))
            room_number = input("Новый номер комнаты: ")
            price = float(input("Новая цена за сутки: "))

            if self.repo.update_room(room_id, room_number, price):
                print("Номер успешно обновлен")
            else:
                print("Номер не найден")
        except ValueError:
            print("Ошибка ввода!")

    def delete_room(self):
        if self.current_user.role != 'receptionist':
            print("Доступ запрещен!")
            return

        rooms = self.repo.get_all_rooms()
        print("\nВсе номера:")
        for room in rooms:
            print(f"{room.room_id}: №{room.room_number} - {room.price_per_day} руб./день - {room.status}")

        try:
            room_id = int(input("Введите ID номера для удаления: "))
            if self.repo.delete_room(room_id):
                print("Номер успешно удален")
            else:
                print("Номер не найден")
        except ValueError:
            print("Ошибка ввода!")

    def run(self):
        print(" Система управления отелем ")

        while True:
            if not self.current_user:
                if not self.authenticate():
                    break
            else:
                if self.current_user.role == 'receptionist':
                    self.receptionist_menu()
                    self.current_user = None
                elif self.current_user.role == 'client':
                    self.client_menu()
                    self.current_user = None

        self.repo.close()
        print("До свидания!")

def main():
    system = HotelSystem()
    system.run()

if __name__ == "__main__":
    main()