import random
import string
from flask import g
from flask_hashing import Hashing
import datetime


class InventoryModel:
    def __init__(self):
        self.conn = g.db_conn
        self.hashing = Hashing()

    def generate_inventory_serial_number(self):
        # Get the last sequence number from the inventories table
        sql = "SELECT MAX(inventory_serial_number) FROM inventories"
        
        cur = self.conn.cursor()
        cur.execute(sql)
        last_serial_number = cur.fetchone()[0]

        if last_serial_number is not None:

            numeric_part = last_serial_number[-3:]
            serial_number = int(numeric_part) + 1
        else:
            serial_number = 1

        current_timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        serial_number = f"ivt{current_timestamp}{serial_number:04}"

        return serial_number

    def add_inventory(self, data: dict):
        sql = """
        INSERT INTO inventories 
        (inventory_serial_number, specifications, store_id, type_id, date_of_purchase, quantity, cost, image)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
        """
        inventory_serial_number = self.generate_inventory_serial_number()
        specifications = data.get("specifications")
        store_id = data.get("store_id")
        type_id = data.get("type_id")
        date_of_purchase = data.get("date_of_purchase")
        quantity = data.get("quantity")
        # price = data.get("price") No need to add price when add inventory. Should achieve when update indentory
        cost = data.get("cost")
        image = data.get("image")

        cur = self.conn.cursor()
        cur.execute(sql, (inventory_serial_number, specifications, store_id, type_id, date_of_purchase, quantity, cost, image))
        self.conn.commit()
        cur.close()
        


    def get_all_inventories(self, query=None):
        sql = """
            SELECT 
                inventories.id,
                inventories.inventory_serial_number, 
                stores.name as store_name,
                types.name as type_name,
                categories.name as category_name,
                inventories.date_of_purchase,
                inventories.quantity,
                inventories.specifications,
                inventories.price,
                inventories.cost,
                types.hire_price,
                types.shipping_price,
                inventories.image,
                inventories.is_deleted,
                inventories.created_at,
                inventories.updated_at,
                categories.min_hire_period,
                categories.max_hire_period
            FROM inventories
            LEFT JOIN stores ON inventories.store_id = stores.id
            LEFT JOIN types ON inventories.type_id = types.id
            LEFT JOIN categories ON types.category_id = categories.id;
        """
      
        params = []

        search_columns = ["status", "inventory_serial_number"]

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
    
    def get_inventory_by_id(self, id):
        sql = "SELECT * FROM inventories WHERE id = %s"
        cur = self.conn.cursor()
        cur.execute(sql, (id,))
        inventory_tuple = cur.fetchone()
        if cur.description and inventory_tuple:
            columns = [desc[0] for desc in cur.description]
            inventory = dict(zip(columns, inventory_tuple))
            return inventory
        else:
            return None
    
    def get_inventory_by_field(self, field_name, field_value):
        
        if field_name not in ["inventory_serial_number","id"]:
            raise ValueError("Invalid field name. Allowed fields: 'inventory_serial_number', 'id',")

        sql = f"SELECT * FROM inventories WHERE {field_name} = %s and is_deleted=0"
        with self.conn.cursor() as cur:
            cur.execute(sql, (field_value,))
            inventory_tuple = cur.fetchone()

            if inventory_tuple:
                columns = [desc[0] for desc in cur.description]
                inventory = dict(zip(columns, inventory_tuple))
                return inventory
            else:
                return None
            
    def get_inventory_data_by_id(self, field_name, field_value):
        
        if field_name not in ["type_id","store_id","quantity"]:
            raise ValueError("Invalid field name. Allowed fields: 'type_id', 'store_id','quantity'")

        sql = f"SELECT {field_name} FROM inventories WHERE id = %s and is_deleted=0"
        with self.conn.cursor() as cur:
            cur.execute(sql, (field_value,))
            inventory_tuple = cur.fetchone()

            if inventory_tuple:
                columns = [desc[0] for desc in cur.description]
                inventory = dict(zip(columns, inventory_tuple))
                return inventory
            else:
                return None
            
    def get_store_id_by_inventory_id(self, id):
        sql = "SELECT store_id FROM inventories WHERE id = %s"
        cur = self.conn.cursor()
        cur.execute(sql, (id,))
        store_id = cur.fetchone()
        return store_id
    
    def get_type_id_by_inventory_id(self, id):
        sql = "SELECT type_id FROM inventories WHERE id = %s"
        cur = self.conn.cursor()
        cur.execute(sql, (id,))
        type_id = cur.fetchone()
        return type_id

    def update_inventory(self, id, data):
        valid_keys = {
            "specifications",
            "store_id",
            "type_id",
            "date_of_purchase",
            "quantity",
            "price",
            "cost",
            "image",
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
        UPDATE inventories
        SET {set_clause}
        WHERE id = %s;
        """

        cur = self.conn.cursor()
        cur.execute(sql, tuple(values))
        self.conn.commit()
        cur.close()
