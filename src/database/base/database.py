import logging
from mysql.connector import Error

from .connection import _DatabaseBase
from .schema_initializer import SchemaInitializerMixin

class Database(SchemaInitializerMixin, _DatabaseBase):
    """
    Main Database class.

    Assembled from focused mixins:
      - connection.py         → connection pool, get_db_connection, get_raw_connection
      - schema_initializer.py → _initialize_schema (CREATE TABLE, migrations, indexes)
    
    Includes backward compatibility methods (fetch_all, fetch_one, execute)
    so existing managers do not need to be rewritten immediately.
    """
    
    def fetch_all(self, query, params=None):
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor(dictionary=True)
                cursor.execute(query, params or ())
                result = cursor.fetchall()
                cursor.close()
                return result
        except Error as e:
            logging.error(f"Error fetching data: {e}")
            return []

    def fetch_one(self, query, params=None):
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor(dictionary=True)
                cursor.execute(query, params or ())
                result = cursor.fetchone()
                cursor.close()
                return result
        except Error as e:
            logging.error(f"Error fetching data: {e}")
            return None

    def execute(self, query, params=None):
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params or ())
                conn.commit()
                rowcount = cursor.rowcount
                lastrowid = cursor.lastrowid
                cursor.close()
                return True, lastrowid
        except Error as e:
            logging.error(f"Error executing query: {e}")
            return False, 0

    def update_record(self, table_name, pk_col, pk_val, data_dict):
        cols = list(data_dict.keys())
        set_clause = ", ".join(f"{col} = %s" for col in cols)
        query = f"UPDATE {table_name} SET {set_clause} WHERE {pk_col} = %s"
        params = list(data_dict.values()) + [pk_val]
        return self.execute(query, params)

    def delete_record(self, table_name, pk_col, pk_val):
        query = f"DELETE FROM {table_name} WHERE {pk_col} = %s"
        return self.execute(query, (pk_val,))
