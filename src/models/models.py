class User:
    """
    Модель для таблицы User
    Поля:
    - user_id: уникальный идентификатор пользователя (PK)
    - username: логин
    - password: пароль
    - role: роль
    - client_id: клиент
    """
    def __init__(self, user_id, username, password, role, client_id=None):
        self.user_id = user_id
        self.username = username
        self.password = password
        self.role = role
        self.client_id = client_id
class Room:
    """
    Модель для таблицы Room
    Поля:
    - room_id: уникальный идентификатор номера (PK)
    - room_number: номер комнаты
    - price_per_day: стоимость проживания за сутки
    - status: статус номера
    """
    def __init__(self, room_id, room_number, price_per_day, status):
        self.room_id = room_id
        self.room_number = room_number
        self.price_per_day = price_per_day
        self.status = status
class Client:
    """
    Модель для таблицы Client
    Поля:
    - client_id: уникальный идентификатор клиента (PK)
    - name: имя клиента
    - phone: номер телефона
    - email: адрес электронной почты
    """
    def __init__(self, client_id, name, phone, email):
        self.client_id = client_id
        self.name = name
        self.phone = phone
        self.email = email
class Booking:
    """
    Модель для таблицы Booking
    Поля:
    - booking_id: уникальный идентификатор бронирования (PK)
    - room_id: идентификатор номера (FK -> Room.room_id)
    - client_id: идентификатор клиента (FK -> Client.client_id)
    - start_date: дата начала бронирования
    - end_date: дата окончания бронирования
    """
    def __init__(self, booking_id, room_id, client_id, start_date, end_date):
        self.booking_id = booking_id
        self.room_id = room_id
        self.client_id = client_id
        self.start_date = start_date
        self.end_date = end_date