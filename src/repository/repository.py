import sqlite3
from src.models.models import Room, Client, Booking, User

class Repository:
    def __init__(self, db_file: str = "hotel.db"):
        self.conn = sqlite3.connect(db_file)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()

    # --- Методы аутентификации ---
    def authenticate_user(self, username: str, password: str):
        self.cursor.execute(
            "SELECT user_id, username, role, client_id FROM User WHERE username = ? AND password = ?",
            (username, password)
        )
        row = self.cursor.fetchone()
        if row:
            return User(
                user_id=row["user_id"],
                username=row["username"],
                password="",
                role=row["role"],
                client_id=row["client_id"]
            )
        return None

    def register_client(self, username: str, password: str, name: str, phone: str = None, email: str = None):
        try:
            self.cursor.execute(
                "INSERT INTO Client (name, phone, email) VALUES (?, ?, ?)",
                (name, phone, email)
            )
            client_id = self.cursor.lastrowid

            self.cursor.execute(
                "INSERT INTO User (username, password, role, client_id) VALUES (?, ?, 'client', ?)",
                (username, password, client_id)
            )
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            self.conn.rollback()
            return False

    def get_all_rooms(self):
        self.cursor.execute("SELECT room_id, room_number, price_per_day, status FROM Room")
        rows = self.cursor.fetchall()
        return [Room(room_id=row["room_id"], room_number=row["room_number"],
                     price_per_day=row["price_per_day"], status=row["status"]) for row in rows]

    def get_available_rooms(self):
        self.cursor.execute("SELECT room_id, room_number, price_per_day, status FROM Room WHERE status = 'свободен'")
        rows = self.cursor.fetchall()
        return [Room(room_id=row["room_id"], room_number=row["room_number"],
                     price_per_day=row["price_per_day"], status=row["status"]) for row in rows]

    def get_room_by_id(self, room_id: int):
        self.cursor.execute("SELECT room_id, room_number, price_per_day, status FROM Room WHERE room_id = ?", (room_id,))
        row = self.cursor.fetchone()
        if row:
            return Room(room_id=row["room_id"], room_number=row["room_number"],
                        price_per_day=row["price_per_day"], status=row["status"])
        return None

    def add_room(self, room_number: str, price_per_day: float):
        try:
            self.cursor.execute(
                "INSERT INTO Room (room_number, price_per_day) VALUES (?, ?)",
                (room_number, price_per_day)
            )
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def update_room(self, room_id: int, room_number: str, price_per_day: float):
        self.cursor.execute(
            "UPDATE Room SET room_number = ?, price_per_day = ? WHERE room_id = ?",
            (room_number, price_per_day, room_id)
        )
        self.conn.commit()
        return self.cursor.rowcount > 0

    def delete_room(self, room_id: int):
        self.cursor.execute("DELETE FROM Room WHERE room_id = ?", (room_id,))
        self.conn.commit()
        return self.cursor.rowcount > 0

    def update_room_status(self, room_id: int, status: str):
        self.cursor.execute("UPDATE Room SET status = ? WHERE room_id = ?", (status, room_id))
        self.conn.commit()

    def get_all_clients(self):
        self.cursor.execute("SELECT client_id, name, phone, email FROM Client")
        rows = self.cursor.fetchall()
        return [Client(client_id=row["client_id"], name=row["name"],
                       phone=row["phone"], email=row["email"]) for row in rows]

    def get_client_by_id(self, client_id: int):
        self.cursor.execute("SELECT client_id, name, phone, email FROM Client WHERE client_id = ?", (client_id,))
        row = self.cursor.fetchone()
        if row:
            return Client(client_id=row["client_id"], name=row["name"],
                          phone=row["phone"], email=row["email"])
        return None

    def add_client(self, name: str, phone: str = None, email: str = None):
        self.cursor.execute("INSERT INTO Client (name, phone, email) VALUES (?, ?, ?)",
                            (name, phone, email))
        self.conn.commit()
        return self.cursor.lastrowid

    def get_all_bookings(self):
        self.cursor.execute("SELECT booking_id, room_id, client_id, start_date, end_date FROM Booking")
        rows = self.cursor.fetchall()
        return [Booking(booking_id=row["booking_id"], room_id=row["room_id"],
                        client_id=row["client_id"], start_date=row["start_date"],
                        end_date=row["end_date"]) for row in rows]

    def get_bookings_by_client(self, client_id: int):
        self.cursor.execute("SELECT booking_id, room_id, client_id, start_date, end_date FROM Booking WHERE client_id = ?",
                            (client_id,))
        rows = self.cursor.fetchall()
        return [Booking(booking_id=row["booking_id"], room_id=row["room_id"],
                        client_id=row["client_id"], start_date=row["start_date"],
                        end_date=row["end_date"]) for row in rows]

    def create_booking(self, room_id: int, client_id: int, start_date: str, end_date: str):
        self.cursor.execute("SELECT status FROM Room WHERE room_id = ?", (room_id,))
        room = self.cursor.fetchone()

        if not room or room["status"] != "свободен":
            return None

        self.cursor.execute(
            "INSERT INTO Booking (room_id, client_id, start_date, end_date) VALUES (?, ?, ?, ?)",
            (room_id, client_id, start_date, end_date)
        )
        booking_id = self.cursor.lastrowid

        self.update_room_status(room_id, "занят")
        self.conn.commit()

        return booking_id

    def cancel_booking(self, booking_id: int):
        self.cursor.execute("SELECT room_id FROM Booking WHERE booking_id = ?", (booking_id,))
        row = self.cursor.fetchone()

        if row:
            room_id = row["room_id"]
            self.cursor.execute("DELETE FROM Booking WHERE booking_id = ?", (booking_id,))
            self.conn.commit()
            self.update_room_status(room_id, "свободен")
            return True
        return False

    def close(self):
        self.conn.close()