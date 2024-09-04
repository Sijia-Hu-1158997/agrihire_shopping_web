import random
import string
from flask import g
from flask_hashing import Hashing
import datetime
import re


class EquipmentModel:
    def __init__(self):
        self.conn = g.db_conn
        self.hashing = Hashing()

    def get_all_equipment(self, query=None):
        sql = """
            SELECT 
                equipments.id,
                equipments.name,
                equipments.cost,
                equipments.image_path,
                equipments.store_id,
                equipments.equipment_serial_number,
                equipments.inventory_id,
                inventories.inventory_serial_number,
                inventories.price,
                inventories.cost as buying_cost,
                inventories.image as inventory_image,
                stores.name as store_name,
                stores.address as store_address,
                stores.phone as store_phone,
                types.name as type_name,
                types.id as type_id,
                types.shipping_price as shipping_price,
                types.hire_price, 
                categories.name as category_name,
                equipments.details,
                equipments.status,
                equipments.image_path,
                equipments.is_deleted,
                equipments.created_at,
                equipments.updated_at,
                categories.min_hire_period,
                categories.max_hire_period
            FROM equipments
            LEFT JOIN stores ON equipments.store_id = stores.id
            LEFT JOIN inventories ON equipments.inventory_id = inventories.id
            LEFT JOIN types ON equipments.type_id = types.id
            LEFT JOIN categories ON types.category_id = categories.id
            LEFT JOIN service_records ON equipments.id = service_records.equipment_id;
        """
        params = []

        search_columns = ["status", "equipment_serial_number"]

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

        # Debug print to check the fetched data
        print("Fetched equipment data:", items_dicts)
        return items_dicts

    def generate_equipment_serial_numbers_by_quantity(self, quantity):
        # Get the last sequence number from the equipment table
        sql = "SELECT MAX(equipment_serial_number) FROM equipments"
        
        cur = self.conn.cursor()
        cur.execute(sql)
        last_serial_number = cur.fetchone()[0]

        next_serial_number = 1
        if last_serial_number:
            # Extract the numeric part of the last serial number using regex to find all digits at the end of the string
            match = re.search(r'(\d+)$', last_serial_number)
            if match:
                next_serial_number = int(match.group(1)) + 1

        current_timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        max_serial_length = 30 - len(current_timestamp) - 2  # 2 for the 'eq' prefix

        serial_numbers = []
        for i in range(quantity):
            next_serial_number = f"{current_timestamp}{i+1:04}"
            truncated_serial_number = f"eq{next_serial_number[-max_serial_length:]}"
            serial_numbers.append(truncated_serial_number)

        # serial_numbers = []
        # for i in range(quantity):
        #     serial_number = f"eq{current_timestamp}{next_serial_number:04}"
        #     serial_numbers.append(serial_number)
        #     next_serial_number += 1

        return serial_numbers
    
    def quick_add_equipment(self, data: dict):
        sql = """
        INSERT INTO equipments 
        (equipment_serial_number, type_id, inventory_id, store_id, status, cost, name)
        VALUES (%s, %s, %s, %s, %s, %s, %s);
        """

        equipment_serial_number = data.get("equipment_serial_number")
        type_id = data.get("type_id")
        inventory_id = data.get("inventory_id")
        store_id = data.get("store_id") 
        status = 'active'
        cost = data.get("cost")
        name = data.get("name")
      
        cur = self.conn.cursor()
        cur.execute(sql, (equipment_serial_number, type_id, inventory_id, store_id, status, cost, name))
        self.conn.commit()
        cur.close()


    def add_equipment(self, data: dict):
        sql = """
        INSERT INTO equipments 
        (equipment_serial_number, type_id, inventory_id, details, store_id, status, name)
        VALUES (%s, %s, %s, %s, %s, %s, %s);
        """
        equipment_serial_number = self.generate_equipment_serial_number()
        type_id = data.get("type_id")
        inventory_id = data.get("inventory_id")
        details = data.get("details")
        store_id = data.get("store_id")
        status = 'active'
        name = data.get("name")

        cur = self.conn.cursor()
        cur.execute(sql, (equipment_serial_number, type_id, inventory_id, details, store_id, status, name))
        self.conn.commit()
        cur.close()

    # def get_all_equipment(self, query=None):
    #     sql = """
    #         SELECT 
    #             equipments.id,
    #             equipments.name,
    #             equipments.cost,
    #             equipments.image_path,
    #             equipments.store_id,
    #             equipments.equipment_serial_number,
    #             equipments.inventory_id,
    #             inventories.inventory_serial_number,
    #             inventories.price,
    #             inventories.cost as buying_cost,
    #             inventories.image as inventory_image,
    #             stores.name as store_name,
    #             stores.address as store_address,
    #             stores.phone as store_phone,
    #             types.name as type_name,
    #             types.id as type_id,
    #             types.shipping_price as shipping_price,
    #             types.hire_price as cost,
    #             categories.name as category_name,
    #             equipments.details,
    #             equipments.status,
    #             equipments.image_path,
    #             equipments.is_deleted,
    #             equipments.created_at,
    #             equipments.updated_at,
    #             categories.min_hire_period,
    #             categories.max_hire_period
    #         FROM equipments
    #         LEFT JOIN stores ON equipments.store_id = stores.id
    #         LEFT JOIN inventories ON equipments.inventory_id = inventories.id
    #         LEFT JOIN types ON equipments.type_id = types.id
    #         LEFT JOIN categories ON types.category_id = categories.id
    #         LEFT JOIN service_records ON equipments.id = service_records.equipment_id;
    #     """
    #     params = []

    #     search_columns = ["status", "equipment_serial_number"]

    #     if query:
    #         query_conditions = [f"{col} LIKE %s" for col in search_columns]
    #         sql += " WHERE (" + " OR ".join(query_conditions) + ")"

    #         params = ["%" + query + "%"] * len(query_conditions)

    #     with self.conn.cursor() as cur:
    #         cur.execute(sql, params)
    #         items = cur.fetchall() or []

    #         if cur.description:
    #             columns = [desc[0] for desc in cur.description]
    #             items_dicts = [dict(zip(columns, item)) for item in items]
    #         else:
    #             items_dicts = []

    #     return items_dicts

    
    def get_all_equipment_by_store_id(self,store_id, query=None):
        sql = """
            SELECT 
                equipments.id,
                equipments.name,
                equipments.cost,
                equipments.image_path,
                equipments.store_id,
                equipments.equipment_serial_number,
                equipments.inventory_id,
                inventories.inventory_serial_number,
                inventories.price,
                inventories.cost,
                inventories.image as inventory_image,
                stores.name as store_name,
                types.name as type_name,
                types.id as type_id,
                types.shipping_price as shipping_price,
                types.hire_price,
                types.specifications as type_specifications,
                categories.name as category_name,
                equipments.details,
                equipments.status,
                equipments.is_deleted,
                equipments.created_at,
                equipments.updated_at
                -- categories.min_hire_period,
                -- categories.max_hire_period
            FROM equipments
            LEFT JOIN stores ON equipments.store_id = stores.id
            LEFT JOIN inventories ON equipments.inventory_id = inventories.id
            LEFT JOIN types ON equipments.type_id = types.id
            LEFT JOIN categories ON types.category_id = categories.id
            where equipments.store_id = %s
        """

        with self.conn.cursor() as cur:
            cur.execute(sql,(store_id,))
            items = cur.fetchall() or []
            if cur.description:
                columns = [desc[0] for desc in cur.description]
                items_dicts = [dict(zip(columns, item)) for item in items]
            else:
                items_dicts = []
        return items_dicts
      
    def get_all_equipment_by_store_type_id(self,store_id,type_id):
        sql = """
            SELECT 
                equipments.id,
                equipments.name,
                equipments.cost,
                equipments.image_path,
                equipments.store_id,
                equipments.equipment_serial_number,
                equipments.inventory_id,
                inventories.inventory_serial_number,
                inventories.price,
                inventories.cost as buying_cost,
                inventories.image as inventory_image,
                stores.name as store_name,
                types.name as type_name,
                types.id as type_id,
                types.shipping_price as shipping_price,
                types.hire_price as cost,
                categories.name as category_name,
                equipments.details,
                equipments.status,
                equipments.is_deleted,
                equipments.created_at,
                equipments.updated_at
                -- categories.min_hire_period,
                -- categories.max_hire_period
            FROM equipments
            LEFT JOIN stores ON equipments.store_id = stores.id
            LEFT JOIN inventories ON equipments.inventory_id = inventories.id
            LEFT JOIN types ON equipments.type_id = types.id
            LEFT JOIN categories ON types.category_id = categories.id
            where equipments.store_id = %s
            and types.id= %s
        """

        with self.conn.cursor() as cur:
            cur.execute(sql,(store_id,type_id))
            items = cur.fetchall() or []
            if cur.description:
                columns = [desc[0] for desc in cur.description]
                items_dicts = [dict(zip(columns, item)) for item in items]
            else:
                items_dicts = []
        return items_dicts

    def get_all_equipment_by_name(self,name, query=None):
        sql = """
            SELECT 
                equipments.id,
                equipments.name,
                equipments.cost,
                equipments.image_path,
                equipments.store_id,
                equipments.equipment_serial_number,
                equipments.inventory_id,
                inventories.inventory_serial_number,
                inventories.price,
                inventories.cost as buying_cost,
                stores.name as store_name,
                stores.address as store_address,
                stores.phone as store_phone,
                -- types.shipping_price,
                types.hire_price as cost,
                categories.name as category_name,
                equipments.details,
                equipments.status,
                equipments.is_deleted,
                equipments.created_at,
                equipments.updated_at
                -- categories.min_hire_period,
                -- categories.max_hire_period
            FROM equipments
            LEFT JOIN stores ON equipments.store_id = stores.id
            LEFT JOIN inventories ON equipments.inventory_id = inventories.id
            LEFT JOIN types ON equipments.type_id = types.id
            LEFT JOIN categories ON types.category_id = categories.id
            where equipments.name = '{name}'
        """.format(name=name)

        cur = self.conn.cursor()
        print("sql:",sql)
        cur.execute(sql)
        items = cur.fetchall() or []
        if cur.description:
            columns = [desc[0] for desc in cur.description]
            items_dicts = [dict(zip(columns, item)) for item in items]
        else:
            items_dicts = []
            
        return items_dicts


    def get_equipment_by_inventory_id(self, id, query=None):
        sql = """
            SELECT 
                equipments.id,
                equipments.name,
                equipments.equipment_serial_number,
                equipments.inventory_id,
                equipments.image_path as equipment_image,
                inventories.inventory_serial_number,
                inventories.price,
                inventories.cost,
                inventories.image as inventory_image,
                stores.name as store_name,
                types.name as type_name,
                types.shipping_price,
                types.hire_price,
                categories.name as category_name,
                equipments.details,
                equipments.status,
                equipments.is_deleted,
                equipments.created_at,
                equipments.updated_at,
                categories.min_hire_period,
                categories.max_hire_period
            FROM equipments
            LEFT JOIN stores ON equipments.store_id = stores.id
            LEFT JOIN inventories ON equipments.inventory_id = inventories.id
            LEFT JOIN types ON equipments.type_id = types.id
            LEFT JOIN categories ON types.category_id = categories.id
            WHERE equipments.inventory_id = %s
        """

        params = []

        search_columns = ["status", "equipment_serial_number"]

        if query:
            query_conditions = [f"{col} LIKE %s" for col in search_columns]
            sql += " WHERE (" + " OR ".join(query_conditions) + ")"

            params = ["%" + query + "%"] * len(query_conditions)

        with self.conn.cursor() as cur:
            cur.execute(sql, (id,), params)
            items = cur.fetchall() or []

            if cur.description:
                columns = [desc[0] for desc in cur.description]
                items_dicts = [dict(zip(columns, item)) for item in items]
            else:
                items_dicts = []

        return items_dicts


    def get_equipment_by_id(self, id):
        sql = """
            SELECT 
            equipments.id,
            equipments.name,
            equipments.equipment_serial_number,
            equipments.type_id,
            equipments.inventory_id,
            equipments.details,
            equipments.image_path,
            equipments.store_id,
            equipments.cost,
            equipments.status,
            equipments.is_deleted,
            equipments.created_at,
            equipments.updated_at,
            types.name as types_name,
            types.hire_price,
            types.specifications as types_specifications,
            categories.name as category_name,
            categories.specifications as categories_specifications
            FROM equipments
            LEFT JOIN types ON equipments.type_id = types.id
            LEFT JOIN categories ON types.category_id = categories.id
            WHERE equipments.id = %s;"""
        cur = self.conn.cursor()
        cur.execute(sql, (id,))
        equipment_tuple = cur.fetchone()
        if cur.description and equipment_tuple:
            columns = [desc[0] for desc in cur.description]
            equipment = dict(zip(columns, equipment_tuple))
            return equipment
        else:
            return None
    

    def get_equipment_by_field(self, field_name, field_value):
        
        if field_name not in ["equipment_serial_number","id"]:
            raise ValueError("Invalid field name. Allowed fields: 'equipment_serial_number', 'id',")

        sql = f"SELECT * FROM equipments WHERE {field_name} = %s and is_deleted=0"
        with self.conn.cursor() as cur:
            cur.execute(sql, (field_value,))
            equipment_tuple = cur.fetchone()

            if equipment_tuple:
                columns = [desc[0] for desc in cur.description]
                equipment = dict(zip(columns, equipment_tuple))
                return equipment
            else:
                return None

    def update_equipment(self, id, data):
        valid_keys = {
            "equipment_serial_number",
            "name",
            "type_id",
            "inventory_id",
            "store_id",
            "status",
            "details",
            "is_deleted",
            "image_path",
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
        UPDATE equipments
        SET {set_clause}
        WHERE id = %s;
        """

        cur = self.conn.cursor()
        cur.execute(sql, tuple(values))
        self.conn.commit()
        cur.close()

