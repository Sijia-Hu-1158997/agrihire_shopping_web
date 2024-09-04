import random
import string
from flask import g
from flask_hashing import Hashing
import datetime
from datetime import datetime, timedelta


class ReminderModel:
    def __init__(self):
        self.conn = g.db_conn
        self.hashing = Hashing()

    def get_pending_bookings(self, user_id):
        """
        Retrieve pending bookings for a given user.
        """
        sql = "SELECT * FROM bookings WHERE user_id = %s AND status = 'pending'"
        with self.conn.cursor() as cursor:
            cursor.execute(sql, (user_id,))
            bookings = cursor.fetchall()
        return bookings
    

    def get_booking_items_by_user_id(self, user_id, query=None):
        sql = """
            SELECT 
                booking_items.id,
                booking_items.booking_id,
                booking_items.equipment_id,
                booking_items.hire_start,
                booking_items.hire_end,
                bookings.user_id,
                bookings.store_id,
                bookings.status
            FROM booking_items
            LEFT JOIN bookings ON booking_items.booking_id = bookings.id
            WHERE user_id = %s and status = 'active'
            """

        with self.conn.cursor() as cur:
            cur.execute(sql, (user_id,))
            items = cur.fetchall() or []

            if cur.description:
                columns = [desc[0] for desc in cur.description]
                items_dicts = [dict(zip(columns, item)) for item in items]
            else:
                items_dicts = []

        booking_data = {}
        for item in items_dicts:
            booking_id = item['booking_id']
            if booking_id not in booking_data:
                booking_data[booking_id] = []
            booking_data[booking_id].append({
                'hire_start': item['hire_start'],
                'hire_end': item['hire_end']
            })

        return booking_data
