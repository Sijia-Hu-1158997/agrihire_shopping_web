import random
import string
from flask import g
import mysql.connector

class StoreModel:
    def __init__(self):
        self.conn = g.db_conn

    def get_all_stores(self, query=None):
        sql = "SELECT * FROM stores"
        params = []
        
        search_columns = ["name"]

        if query:
            query_conditions = [f"{col} LIKE %s" for col in search_columns]
            sql += " WHERE (" + " OR ".join(query_conditions) + ")"

            params = ["%" + query + "%"] * len(query_conditions)

        with self.conn.cursor() as cur:
            cur.execute(sql, params)
            stores = cur.fetchall() or []
            
            store_dicts = []

            columns = [desc[0] for desc in cur.description]
            for store in stores:
                store_dict = dict(zip(columns, store))
                store_dicts.append(store_dict)

        return store_dicts

    # def get_all_stores(self, query=None):
    #     sql = "SELECT * FROM stores"
    #     params = []

    #     search_columns = ["id", "name", "location"]

    #     if query:
    #         query_conditions = [f"{col} LIKE %s" for col in search_columns]
    #         sql += " WHERE (" + " OR ".join(query_conditions) + ")"

    #         params = ["%" + query + "%"] * len(query_conditions)
    #     try:
    #         with self.conn.cursor() as cur:
    #             cur.execute(sql, params)
    #             stores = cur.fetchall() or []

    #             if cur.description:
    #                 columns = [desc[0] for desc in cur.description]
    #                 stores_dicts = [dict(zip(columns, n)) for n in stores]
    #             else:
    #                 stores_dicts = []
        
    #         return stores_dicts
        
    #     except mysql.connector.errors.InterfaceError as ie:
    #         if ie.msg == 'No result set to fetch from.':
    #             # no problem, we were just at the end of the result set
    #             pass
    #         else:
    #             raise
    #     cur.execute(sql, params)
        



        # with self.conn.cursor() as cur:
        #     cur.execute(sql, params)
        #     stores = cur.fetchall() or []

        #     stores_dicts = []
        #     for store in stores:
        #         store_dict = {
        #             "id": store[0],
        #             "name": store[1],
        #             "address": store[2],
        #             "location": store[3],
        #             "phone": store[4],
        #             "email": store[5],
        #             "manager_id": store[6]
        #         }
        #         stores_dicts.append(store_dict)

        # return stores_dicts
    

    
            
