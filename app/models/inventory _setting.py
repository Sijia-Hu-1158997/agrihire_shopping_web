'''
Author: Maggiefyer 109766140@qq.com
Date: 2024-05-15 21:58:43
LastEditors: Maggiefyer 109766140@qq.com
LastEditTime: 2024-05-15 22:03:22
FilePath: \COMP639S1_Project_2_Group_I\app\models\inventory _setting.py
Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
'''
import random
import string
from flask import g
from flask_hashing import Hashing


class CategoryModel:
    def __init__(self):
        self.conn = g.db_conn
        self.hashing = Hashing()

    def add_category(self, data: dict):
        sql = """
        INSERT INTO categories (name, type, description)
        VALUES (%s, %s, %s);
        """
        name = data.get("name")
        type = data.get("type")
        description = data.get("description")

        cur = self.conn.cursor()
        cur.execute(sql, (name, type, description))
        self.conn.commit()
        cur.close()

    def get_all_categories(self, query=None):
        sql = "SELECT * FROM categories"
        params = []

        search_columns = ["name", "type", "description"]

        if query:
            query_conditions = [f"{col} LIKE %s" for col in search_columns]
            sql += " WHERE (" + " OR ".join(query_conditions) + ")"

            params = ["%" + query + "%"] * len(query_conditions)

        with self.conn.cursor() as cur:
            cur.execute(sql, params)
            items = cur.fetchall() or []

            if cur.description:
                columns = [desc[0] for desc in cur.description]
                items_dicts = [dict(zip(columns, item)) for item in items]
            else:
                items_dicts = []

        return items_dicts

    def get_category_by_id(self, id):
        sql = "SELECT * FROM categories WHERE id = %s"
        cur = self.conn.cursor()
        cur.execute(sql, (id,))
        category_tuple = cur.fetchone()
        if cur.description and category_tuple:
            columns = [desc[0] for desc in cur.description]
            category = dict(zip(columns, category_tuple))
            return category
        else:
            return None

    def update_category(self, id, data):
        valid_keys = {
            "name",
            "type",
            "description",
            "is_deleted",
        }
        data = {
            k: v
            for k, v in data.items()
            if k in valid_keys and v is not None and k not in ["id"]
        }

        # If no valid data to update, return early to avoid executing an empty update
        if not data:
            print("No valid data provided for update.")
            return
        # Build the SQL dynamically based on the data provided
        set_clause = ", ".join([f"{key} = %s" for key in data.keys()])
        values = list(data.values())

        # Include user_id at the end for the WHERE clause
        values.append(id)
        print(set_clause, values)
        sql = f"""
        UPDATE categories
        SET {set_clause}
        WHERE id = %s;
        """

        cur = self.conn.cursor()
        cur.execute(sql, tuple(values))
        self.conn.commit()
        cur.close()
