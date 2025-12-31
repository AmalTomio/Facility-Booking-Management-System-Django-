"""
Database models for the booking system
Compatible with MySQL schema using `password` column
"""

from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from database import get_db_connection
import logging

logger = logging.getLogger(__name__)


# =============================================================================
# DB HELPER
# =============================================================================

def execute_query(query, params=None, fetch=False, fetch_one=False):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(query, params or ())

    if fetch:
        result = cursor.fetchall()
    elif fetch_one:
        result = cursor.fetchone()
    else:
        conn.commit()
        result = cursor.rowcount   

    cursor.close()
    conn.close()
    return result



# =============================================================================
# USER MODEL
# =============================================================================

class User(UserMixin):
    def __init__(self, user_id, name, email, password, role, created_at=None):
        self.id = user_id
        self.user_id = user_id
        self.name = name
        self.email = email
        self.password = password
        self.role = role
        self.created_at = created_at

    @staticmethod
    def create(name, email, password, role):
        password_hash = generate_password_hash(password)
        query = """
            INSERT INTO users (name, email, password, role)
            VALUES (%s, %s, %s, %s)
        """
        return execute_query(query, (name, email, password_hash, role))

    @staticmethod
    def get_by_id(user_id):
        row = execute_query(
            "SELECT * FROM users WHERE user_id = %s",
            (user_id,),
            fetch_one=True
        )
        return User(**row) if row else None

    @staticmethod
    def get_by_email(email):
        row = execute_query(
            "SELECT * FROM users WHERE email = %s",
            (email,),
            fetch_one=True
        )
        return User(**row) if row else None

    def verify_password(self, password):
        return check_password_hash(self.password, password)

    def is_admin(self):
        return self.role == "admin"

    def is_staff(self):
        return self.role == "staff"


# =============================================================================
# FACILITY MODEL
# =============================================================================

class Facility:
    def __init__(
        self,
        facility_id,
        name,
        capacity,
        status,
        description=None,
        image=None,
        created_at=None
    ):
        self.facility_id = facility_id
        self.name = name
        self.capacity = capacity
        self.status = status
        self.description = description
        self.image = image
        self.created_at = created_at

    # ==========================
    # CREATE
    # ==========================
    @staticmethod
    def create(name, capacity, description, status, image):
        query = """
            INSERT INTO facilities (name, capacity, description, status, image)
            VALUES (%s, %s, %s, %s, %s)
        """
        return execute_query(query, (name, capacity, description, status, image))

    # ==========================
    # READ
    # ==========================
    @staticmethod
    def get_by_id(facility_id):
        row = execute_query(
            "SELECT * FROM facilities WHERE facility_id = %s",
            (facility_id,),
            fetch_one=True
        )
        return Facility(**row) if row else None

    @staticmethod
    def get_all(include_inactive=False):
        if include_inactive:
            query = "SELECT * FROM facilities ORDER BY name"
        else:
            query = """
                SELECT * FROM facilities
                WHERE status = 'active'
                ORDER BY name
            """
        rows = execute_query(query, fetch=True)
        return [Facility(**row) for row in rows] if rows else []

    @staticmethod
    def get_active_count():
        row = execute_query(
            "SELECT COUNT(*) AS count FROM facilities WHERE status = 'active'",
            fetch_one=True
        )
        return row["count"] if row else 0

    # ==========================
    # UPDATE
    # ==========================
    @staticmethod
    def update(facility_id, name, capacity, description, status, image):
        print(
            "🟢 SQL UPDATE PARAMS:",
            facility_id, name, capacity, description, status, image
        )

        query = """
            UPDATE facilities
            SET name = %s,
                capacity = %s,
                description = %s,
                status = %s,
                image = %s
            WHERE facility_id = %s
        """

        return execute_query(
            query,
            (name, capacity, description, status, image, facility_id)
        )

    # ==========================
    # DELETE
    # ==========================
    @staticmethod
    def delete(facility_id):
        return execute_query(
            "DELETE FROM facilities WHERE facility_id = %s",
            (facility_id,)
        )

    # ==========================
    # SAFETY CHECK
    # ==========================
    @staticmethod
    def has_active_bookings(facility_id):
        row = execute_query(
            """
            SELECT COUNT(*) AS count
            FROM bookings
            WHERE facility_id = %s
              AND status IN ('pending', 'approved')
            """,
            (facility_id,),
            fetch_one=True
        )
        return row["count"] > 0 if row else False



# =============================================================================
# BOOKING MODEL (🔥 COMPLETE)
# =============================================================================

class Booking:
    def __init__(
        self,
        booking_id,
        user_id,
        facility_id,
        booking_date,
        start_time,
        end_time,
        status,
        purpose=None,
        created_at=None,
        user_name=None,
        facility_name=None
    ):
        self.booking_id = booking_id
        self.user_id = user_id
        self.facility_id = facility_id
        self.booking_date = booking_date
        self.start_time = self._format_time(start_time)
        self.end_time = self._format_time(end_time)
        self.status = status
        self.purpose = purpose
        self.created_at = created_at
        self.user_name = user_name
        self.facility_name = facility_name

    def _format_time(self, value):
        if hasattr(value, "seconds"):
            h = value.seconds // 3600
            m = (value.seconds % 3600) // 60
            return f"{h:02d}:{m:02d}"
        return value.strftime("%H:%M")

    # ==========================
    # CREATE
    # ==========================
    @staticmethod
    def create(user_id, facility_id, booking_date, start_time, end_time, purpose):
        query = """
            INSERT INTO bookings
            (user_id, facility_id, booking_date, start_time, end_time, purpose, status)
            VALUES (%s, %s, %s, %s, %s, %s, 'pending')
        """
        return execute_query(
            query,
            (user_id, facility_id, booking_date, start_time, end_time, purpose)
        )

    # ==========================
    # READ
    # ==========================
    @staticmethod
    def get_by_user(user_id):
        query = """
            SELECT b.*, f.name AS facility_name
            FROM bookings b
            JOIN facilities f ON f.facility_id = b.facility_id
            WHERE b.user_id = %s
            ORDER BY b.created_at DESC
        """
        rows = execute_query(query, (user_id,), fetch=True)
        return [Booking(**row) for row in rows] if rows else []

    @staticmethod
    def get_all(status=None):
        query = """
            SELECT b.*, u.name AS user_name, f.name AS facility_name
            FROM bookings b
            JOIN users u ON u.user_id = b.user_id
            JOIN facilities f ON f.facility_id = b.facility_id
        """
        params = []

        if status:
            query += " WHERE b.status = %s"
            params.append(status)

        query += " ORDER BY b.created_at DESC"
        rows = execute_query(query, tuple(params) if params else None, fetch=True)
        return [Booking(**row) for row in rows] if rows else []


    @staticmethod
    def get_recent(limit=10):
        query = """
            SELECT b.*, u.name AS user_name, f.name AS facility_name
            FROM bookings b
            JOIN users u ON u.user_id = b.user_id
            JOIN facilities f ON f.facility_id = b.facility_id
            ORDER BY b.created_at DESC
            LIMIT %s
        """
        rows = execute_query(query, (limit,), fetch=True)
        return [Booking(**row) for row in rows] if rows else []

    # ==========================
    # UPDATE
    # ==========================
    @staticmethod
    def update_status(booking_id, status):
        query = "UPDATE bookings SET status = %s WHERE booking_id = %s"
        return execute_query(query, (status, booking_id))

    @staticmethod
    def cancel(booking_id, user_id):
        query = """
            UPDATE bookings
            SET status = 'cancelled'
            WHERE booking_id = %s
              AND user_id = %s
              AND status = 'pending'
        """
        return execute_query(query, (booking_id, user_id))

    # ==========================
    # ADMIN STATS
    # ==========================
    @staticmethod
    def get_total_count():
        row = execute_query(
            "SELECT COUNT(*) AS count FROM bookings",
            fetch_one=True
        )
        return row["count"] if row else 0

    @staticmethod
    def get_pending_count():
        row = execute_query(
            "SELECT COUNT(*) AS count FROM bookings WHERE status = 'pending'",
            fetch_one=True
        )
        return row["count"] if row else 0

    @staticmethod
    def get_approved_count():
        row = execute_query(
            "SELECT COUNT(*) AS count FROM bookings WHERE status = 'approved'",
            fetch_one=True
        )
        return row["count"] if row else 0

    @staticmethod
    def get_rejected_count():
        row = execute_query(
            "SELECT COUNT(*) AS count FROM bookings WHERE status = 'rejected'",
            fetch_one=True
        )
        return row["count"] if row else 0

    @staticmethod
    def get_user_stats(user_id):
        query = """
            SELECT
                COUNT(*) AS total,
                SUM(status='pending') AS pending,
                SUM(status='approved') AS approved
            FROM bookings
            WHERE user_id = %s
        """
        row = execute_query(query, (user_id,), fetch_one=True)
        return {
            "total": row["total"] or 0,
            "pending": row["pending"] or 0,
            "approved": row["approved"] or 0,
        }

    @staticmethod
    def get_upcoming_by_user(user_id, limit=5):
        query = """
            SELECT b.*, f.name AS facility_name
            FROM bookings b
            JOIN facilities f ON f.facility_id = b.facility_id
            WHERE b.user_id = %s
              AND b.booking_date >= CURDATE()
              AND b.status IN ('pending', 'approved')
            ORDER BY b.booking_date ASC, b.start_time ASC
            LIMIT %s
        """
        rows = execute_query(query, (user_id, limit), fetch=True)
        return [Booking(**row) for row in rows] if rows else []
