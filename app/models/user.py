import random
import string
from flask import g, flash
from flask_hashing import Hashing
import datetime


class UserModel:
    def __init__(self):
        self.conn = g.db_conn
        self.hashing = Hashing()

    def generate_salt(self, length=10):
        characters = string.ascii_letters + string.digits
        random_string = "".join(random.choices(characters, k=length))
        return random_string
    
    def get_all_authors(self):
        sql = """
        SELECT id, first_name, last_name 
        FROM users 
        WHERE role IN ('staff', 'local_manager', 'national_manager', 'admin') 
        AND is_deleted = 0
        """
        with self.conn.cursor() as cur:
            cur.execute(sql)
            users = cur.fetchall()
            return [dict(id=row[0], first_name=row[1], last_name=row[2]) for row in users]
    # Register flow
    # Step 1: fill in account infor, like username(uniq) email(uniq) password, date_of_birth
    # Step 2: get checked if is adult. if yes, continue registration, if not, go to home page;
    #         fill in personal details, like first_name last_name address phone_number etc.;
    #         complete registration, go to home page
    # onboarding = 2 means a users completed registration, otherwise not.

    def register_user(self, data: dict):
        # step 1
        sql = """
        INSERT INTO users
        (username, email, password, date_of_birth, onboarding)
        VALUES (%s, %s, %s, %s, %s);
        """
        username = data.get("username")
        email = data.get("email")
        password = data.get("password")
        date_of_birth = data.get("date_of_birth")
        onboarding = 1

        salt = self.generate_salt()
        hash_password = f"{self.hashing.hash_value(password, salt)}:{salt}"
        cur = self.conn.cursor()
        cur.execute(sql, (username, email, hash_password, date_of_birth, onboarding))
        self.conn.commit()
        cur.close()

    def admin_register_user(self, data: dict):
        sql = """
        INSERT INTO users
        (username, email, password, date_of_birth, role, onboarding, title, first_name, last_name, phone, address)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
        """
        username = data.get("username")
        email = data.get("email")
        password = data.get("password")
        date_of_birth = data.get("date_of_birth")
        role = data.get("role")
        onboarding = 2
        title = data.get("title")
        first_name = data.get("first_name")
        last_name = data.get("last_name")
        phone = data.get("phone")
        address = data.get("address")

        salt = self.generate_salt()
        hash_password = f"{self.hashing.hash_value(password, salt)}:{salt}"

        cur = self.conn.cursor()
        cur.execute(sql, (username, email, hash_password, date_of_birth, role, onboarding, title, first_name, last_name, phone, address))
        self.conn.commit()
        cur.close()

    def update_user_info(self, user_id, data):
        valid_keys = {
            "username",
            "password",
            "role",
            "title",
            "first_name",
            "last_name",
            "phone",
            "address",
            "date_of_birth",
            "profile_image",
            "is_deleted",
            "created_at",
            "updated_at",
            "onboarding",
        }
        data = {
            k: v
            for k, v in data.items()
            if k in valid_keys and v is not None and k not in ["email", "id"]
        }

        # If no valid data to update, return early to avoid executing an empty update
        if not data:
            print("No valid data provided for update.")
            return
        # Build the SQL dynamically based on the data provided
        set_clause = ", ".join([f"{key} = %s" for key in data.keys()])
        values = list(data.values())

        # Include user_id at the end for the WHERE clause
        values.append(user_id)
        print(set_clause, values)
        sql = f"""
        UPDATE users
        SET {set_clause}
        WHERE id = %s;
        """

        cur = self.conn.cursor()
        cur.execute(sql, tuple(values))
        self.conn.commit()
        cur.close()

    def get_user_by_field(self, field_name, field_value):
        """
        Fetch a user by a specific field name and value.

        :param field_name: The name of the field to query (e.g., 'email' or 'username' or 'id').
        :param field_value: The value of the field to query.
        :return: A dictionary of the user's data if found, None otherwise.
        """
        if field_name not in ["email", "username", "id"]:
            raise ValueError("Invalid field name. Allowed fields: 'email', 'username'")

        sql = f"SELECT * FROM users WHERE {field_name} = %s"
        with self.conn.cursor() as cur:
            cur.execute(sql, (field_value,))
            user_tuple = cur.fetchone()

            if user_tuple:
                columns = [desc[0] for desc in cur.description]
                user = dict(zip(columns, user_tuple))
                return user
            else:
                return None

    def get_user_list_by_field(self, field_name, field_value):

        if field_name not in ["role","id"]:
            raise ValueError("Invalid field name. Allowed fields: 'role', 'id',")

        sql = f"SELECT * FROM users WHERE {field_name} = %s"
        with self.conn.cursor() as cur:
            cur.execute(sql, (field_value,))
            items_tuple = cur.fetchall() or []

            if cur.description:
                columns = [desc[0] for desc in cur.description]
                items_dicts = [dict(zip(columns, item)) for item in items_tuple]
            else:
                items_dicts = []
            return items_dicts



    def get_user_by_booking_id(self, id):
        sql = """
        SELECT
            schedules.booking_id,
            bookings.user_id,
            users.title,
            users.first_name,
            users.last_name,
            users.phone,
            users.email,
            users.address,
            users.date_of_birth
            FROM schedules
        LEFT JOIN bookings ON schedules.booking_id = bookings.id
        LEFT JOIN users ON bookings.user_id = users.id
        WHERE booking_id = %s;"""
        with self.conn.cursor() as cur:
            cur.execute(sql, (id,))
            user_tuple = cur.fetchall()

            if user_tuple:
                columns = [desc[0] for desc in cur.description]
                user = dict(zip(columns, user_tuple))
                return user
            else:
                return None


    def check_password(self, username, password):
        sql = "SELECT * FROM users WHERE username = %s"
        cur = self.conn.cursor()
        cur.execute(sql, (username,))
        user_tuple = cur.fetchone()
        if cur.description and user_tuple:
            columns = [desc[0] for desc in cur.description]
            user = dict(zip(columns, user_tuple))
            if user:
                hash_password, salt = user["password"].split(":")
                if self.hashing.check_value(hash_password, password, salt):
                    return user
                else:
                    # add
                    print("Stored password format is incorrect.")
            else:
                # add
                print("User not found.")
        return None

    def validate_oldpassword(self, username, password):
        sql = "SELECT * FROM users WHERE username = %s"
        cur = self.conn.cursor()
        cur.execute(sql, (username,))
        user_tuple = cur.fetchone()
        if cur.description and user_tuple:
            columns = [desc[0] for desc in cur.description]
            user = dict(zip(columns, user_tuple))
            if user:
                hash_password, salt = user["password"].split(":")
                if self.hashing.check_value(hash_password, password, salt):
                    return user
                else:
                    # add
                    flash("old password is incorrect.")
            else:
                # add
                flash("User not found.")
        return None


    def get_users(self, query=None):
        sql = "SELECT * FROM users"
        params = []

        search_columns = ["userid", "first_name", "last_name", "email", "username", "phone"]

        if query:
            query_conditions = [f"{col} LIKE %s" for col in search_columns]
            sql += " WHERE (" + " OR ".join(query_conditions) + ")"

            params = ["%" + query + "%"] * len(query_conditions)

        with self.conn.cursor() as cur:
            cur.execute(sql, params)
            users = cur.fetchall() or []

            if cur.description:
                columns = [desc[0] for desc in cur.description]
                users_dicts = [dict(zip(columns, user)) for user in users]
            else:
                users_dicts = []

        return users_dicts

    def get_customers(self, query=None):
        sql = "SELECT * FROM users WHERE role = 'customer'"
        params = []

        search_columns = ["username", "first_name", "last_name", "email", "phone"]

        if query:
            query_conditions = [f"{col} LIKE %s" for col in search_columns]
            sql += " AND (" + " OR ".join(query_conditions) + ")"

            params = ["%" + query + "%"] * len(query_conditions)

        with self.conn.cursor() as cur:
            cur.execute(sql, params)
            users = cur.fetchall() or []

            if cur.description:
                columns = [desc[0] for desc in cur.description]
                users_dicts = [dict(zip(columns, user)) for user in users]
            else:
                users_dicts = []

        return users_dicts


    def delete_user(self, user_id):
        sql = "DELETE FROM users WHERE id = %s"
        cur = self.conn.cursor()
        cur.execute(sql, (user_id,))
        self.conn.commit()
        cur.close()

    def update_password(self, user_id, password):
        sql = "UPDATE users SET password = %s WHERE id = %s"
        salt = self.generate_salt()
        hash_password = f"{self.hashing.hash_value(password, salt)}:{salt}"
        cur = self.conn.cursor()
        cur.execute(sql, (hash_password, user_id))
        self.conn.commit()
        cur.close()

    def update_profile_img(self,user_id,profile_image):
        sql = "UPDATE users SET profile_image = %s WHERE id = %s"
        cur = self.conn.cursor()
        cur.execute(sql, (profile_image, user_id))
        self.conn.commit()
        cur.close()


    def get_feedback(self, query=None):
        sql = "SELECT * FROM feedback"
        params = []

        search_columns = ["title", "content", "published_at"]

        if query:
            query_conditions = [f"{col} LIKE %s" for col in search_columns]
            sql += " WHERE (" + " OR ".join(query_conditions) + ")"

            params = ["%" + query + "%"] * len(query_conditions)

        with self.conn.cursor() as cur:
            cur.execute(sql, params)
            users = cur.fetchall() or []

            if cur.description:
                columns = [desc[0] for desc in cur.description]
                users_dicts = [dict(zip(columns, user)) for user in users]
            else:
                users_dicts = []

        return users_dicts

    def add_feedback(self, data: dict):
        sql = """
        INSERT INTO feedback (title, content, published_at, feedback_user_id)
        VALUES (%s, %s, %s, %s);
        """
        title = data.get("title")
        content = data.get("content")
        published_at = datetime.datetime.now().date()
        feedback_user_id = data.get("feedback_user_id")

        cur = self.conn.cursor()
        cur.execute(sql, (title, content, published_at,feedback_user_id))
        self.conn.commit()
        cur.close()

