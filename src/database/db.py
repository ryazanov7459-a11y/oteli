import sqlite3
from sqlite3 import Connection


def get_connection(db_name: str = "hotel.db") -> Connection:
    return sqlite3.connect(db_name)

def create_tables(db_name: str = "hotel.db"):
    conn = get_connection(db_name)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS User (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('receptionist', 'client')),
            client_id INTEGER,
            FOREIGN KEY (client_id) REFERENCES Client(client_id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Room (
            room_id INTEGER PRIMARY KEY AUTOINCREMENT,
            room_number TEXT UNIQUE NOT NULL,
            price_per_day REAL,
            status TEXT DEFAULT 'свободен'
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Client (
            client_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT,
            email TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Booking (
            booking_id INTEGER PRIMARY KEY AUTOINCREMENT,
            room_id INTEGER NOT NULL,
            client_id INTEGER NOT NULL,
            start_date TEXT NOT NULL,
            end_date TEXT NOT NULL,
            FOREIGN KEY (room_id) REFERENCES Room(room_id),
            FOREIGN KEY (client_id) REFERENCES Client(client_id)
        )
    ''')
    conn.commit()
    conn.close()

def insert_sample_data(db_name: str = "hotel.db"):
    conn = get_connection(db_name)
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM User")
    if cursor.fetchone()[0] == 0:
        users = [
            ("admin", "admin123", "receptionist", None),
            ("client1", "client123", "client", 1),
            ("client2", "client123", "client", 2),
            ("client3", "client123", "client", 3)
        ]
        cursor.executemany(
            "INSERT INTO User (username, password, role, client_id) VALUES (?, ?, ?, ?)",
            users
        )

    cursor.execute("SELECT COUNT(*) FROM Room")
    if cursor.fetchone()[0] == 0:
        rooms = [
            ("101", 3500.0, "свободен"),
            ("102", 4000.0, "свободен"),
            ("103", 4500.0, "свободен"),
            ("104", 5000.0, "свободен"),
        ]
        cursor.executemany(
            "INSERT INTO Room (room_number, price_per_day, status) VALUES (?, ?, ?)",
            rooms
        )

    cursor.execute("SELECT COUNT(*) FROM Client")
    if cursor.fetchone()[0] == 0:
        clients = [
            ("Иван Иванов", "+78005553535", "ivan@email.com"),
            ("Анна Некая", "+79999999999", "anna@gmail.com"),
            ("Сергей Какойто", "+79021311313", "sergey@email.com")
        ]
        cursor.executemany(
            "INSERT INTO Client (name, phone, email) VALUES (?, ?, ?)",
            clients
        )

    cursor.execute("SELECT COUNT(*) FROM Booking")
    if cursor.fetchone()[0] == 0:
        bookings = [
            (1, 1, "2025-10-26", "2025-11-11"),
            (2, 2, "2025-10-25", "2025-11-10"),
        ]
        cursor.executemany(
            "INSERT INTO Booking (room_id, client_id, start_date, end_date) VALUES (?, ?, ?, ?)",
            bookings
        )
    conn.commit()
    conn.close()