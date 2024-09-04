import random
import string
from flask import g
from flask_hashing import Hashing
import datetime

class ServiceModel:
    def __init__(self):
        self.conn = g.db_conn
        self.hashing = Hashing()

    
    # def add_service(self, data: dict):
    #     sql = """
    #     INSERT INTO inventories 
    #     (inventory_serial_number, specifications, store_id, type_id, date_of_purchase, quantity, cost, status, image)
    #     VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
    #     """
    #     inventory_serial_number = self.generate_inventory_serial_number()
    #     specifications = data.get("specifications")
    #     store_id = data.get("store_id")
    #     type_id = data.get("type_id")
    #     date_of_purchase = data.get("date_of_purchase")
    #     quantity = data.get("quantity")
    #     # price = data.get("price") No need to add price when add inventory. Should achieve when update indentory
    #     cost = data.get("cost")
    #     status = 'in_stock'
    #     image = data.get("image")

    #     cur = self.conn.cursor()
    #     cur.execute(sql, (inventory_serial_number, specifications, store_id, type_id, date_of_purchase, quantity, cost, status, image))
    #     self.conn.commit()
    #     cur.close()
        


    def get_service(self, query=None):
        sql = "SELECT * FROM services"
      
        params = []

        search_columns = ["name"]

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
    
    def get_service_by_id(self, id):
        sql = "SELECT * FROM services WHERE id = %s"
        cur = self.conn.cursor()
        cur.execute(sql, (id,))
        inventory_tuple = cur.fetchone()
        if cur.description and inventory_tuple:
            columns = [desc[0] for desc in cur.description]
            inventory = dict(zip(columns, inventory_tuple))
            return inventory
        else:
            return None
        
    def get_all_service_by_service_id(self, id, query=None):
        sql = """
                SELECT
                    services.id as service_id,
                    service_records.id as service_record_id,
                    service_records.equipment_id,
                    service_records.service_start,
                    service_records.service_end,
                    service_records.details,
                    service_records.created_at,
                    service_records.updated_at,
                    service_records.is_deleted,
                    equipments.equipment_serial_number,
                    types.name as type_name,
                    categories.name as category_name,
                    stores.name as store_name
                FROM
                    services
                    LEFT JOIN service_records ON services.id = service_records.service_id
                    LEFT JOIN equipments ON service_records.equipment_id = equipments.id
                    LEFT JOIN types ON equipments.type_id = types.id
                    LEFT JOIN categories ON types.category_id = categories.id
                    LEFT JOIN stores ON equipments.store_id = stores.id
                WHERE 
                    services.id = %s;
        """
      
        params = []

        search_columns = ["equipment_serial_number"]

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
    


    def add_service_record(self, data: dict):
        sql = """
        INSERT INTO service_records 
        (equipment_id, service_id, service_end, details)
        VALUES (%s, %s, %s, %s);
        """

        equipment_id = data.get("equipment_id")
        service_id = data.get("service_id")
        service_end = data.get("service_end")
        details = data.get("details")

        cur = self.conn.cursor()
        cur.execute(sql, (equipment_id, service_id, service_end, details))
        self.conn.commit()
        cur.close()

    def update_service_record(self, id, data):
        valid_keys = {
            "equipment_id",
            "service_id",
            # "service_start",
            "service_end",
            "details",
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
        UPDATE service_records
        SET {set_clause}
        WHERE id = %s;
        """

        cur = self.conn.cursor()
        cur.execute(sql, tuple(values))
        self.conn.commit()
        cur.close()



    def get_service_record_by_field(self, field_name, field_value):
        
        if field_name not in ["equipment_id","service_id", "id"]:
            raise ValueError("Invalid field name. Allowed fields: 'equipment_id', 'service_id', 'id")

        sql = f"SELECT * FROM service_records WHERE {field_name} = %s and is_deleted=0"
        with self.conn.cursor() as cur:
            cur.execute(sql, (field_value,))
            service_record_tuple = cur.fetchone()

            if service_record_tuple:
                columns = [desc[0] for desc in cur.description]
                service_record = dict(zip(columns, service_record_tuple))
                return service_record
            else:
                return None
            


    def get_service_record_by_equipment_id(self, id, query=None):
        sql = """
                SELECT 
                    service_records.id,
                    service_records.equipment_id,
                    service_records.service_id,
                    service_records.service_start,
                    service_records.service_end,
                    service_records.details,
                    service_records.is_deleted,
                    services.name,
                    services.price
                FROM service_records 
                LEFT JOIN services ON service_records.service_id = services.id
                WHERE equipment_id = %s;
        """
       
        params = []

        search_columns = ["equipment_id"]

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
    

    def get_latest_service_record_by_equipment_id(self, id):
        sql = "SELECT * FROM service_records WHERE equipment_id = %s AND is_deleted = 0 ORDER BY service_end DESC LIMIT 1"
        with self.conn.cursor() as cur:
            cur.execute(sql, (id,))
            service_record_tuple = cur.fetchone()
            if service_record_tuple:
                columns = [desc[0] for desc in cur.description]
                service_record = dict(zip(columns, service_record_tuple))
                return service_record
            else:
                return None