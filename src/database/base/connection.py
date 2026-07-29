import mysql.connector
from mysql.connector import errorcode, pooling
import logging
import os
from contextlib import contextmanager
from dotenv import load_dotenv

from .config import get_env_bool, get_external_path

class _DatabaseBase:
    _instance = None
    _pool = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(_DatabaseBase, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        if getattr(self, '_initialized', False):
            return

        env_path = get_external_path(".env")
        load_dotenv(env_path, override=True)

        self.db_config = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'user': os.getenv('DB_USER', 'root'),
            'password': os.getenv('DB_PASSWORD', 'root'),
            'database': os.getenv('DB_NAME', 'modernlam'),
            'port': int(os.getenv('DB_PORT', 3306))
        }

        if not all([self.db_config['user'], self.db_config['password'], self.db_config['database']]):
            raise ValueError("Database configuration is missing in .env file.")

        self._ensure_database_exists()

        if _DatabaseBase._pool is None:
            try:
                _DatabaseBase._pool = pooling.MySQLConnectionPool(
                    pool_name="modernlam_pool",
                    pool_size=32,
                    pool_reset_session=True,
                    use_pure=True,
                    auth_plugin='mysql_native_password',
                    **self.db_config
                )
                logging.info("Connection pool initialized successfully (Size: 32).")
            except Exception as e:
                logging.error(f"❌ Failed to initialize Connection Pool: {e}")
                raise

        self.schema_check_on_startup = get_env_bool(
            "DB_SCHEMA_CHECK_ON_STARTUP",
            default=False
        )
        schema_missing = self._schema_missing()
        is_local = self.db_config['host'] in ['127.0.0.1', 'localhost']
        if schema_missing:
            logging.info("Database schema is missing. Running initial schema setup.")
            self._initialize_schema()
        elif is_local and self.schema_check_on_startup:
            self._initialize_schema()
        else:
            logging.info(
                "Schema startup checks skipped. Set DB_SCHEMA_CHECK_ON_STARTUP=true "
                "in .env to run migrations."
            )
        self._initialized = True

    @classmethod
    def reset_connection_state(cls):
        instance = cls._instance
        if instance is not None:
            for attr in ('db_config', 'schema_check_on_startup', '_initialized'):
                if hasattr(instance, attr):
                    try:
                        delattr(instance, attr)
                    except Exception:
                        pass
        cls._pool = None
        cls._instance = None

    def _ensure_database_exists(self):
        try:
            conn_config = self.db_config.copy()
            db_name = conn_config.pop('database')
            conn_config['use_pure'] = True
            conn_config['auth_plugin'] = 'mysql_native_password'

            with mysql.connector.connect(**conn_config) as conn:
                cursor = conn.cursor()
                escaped_db_name = db_name.replace("`", "``")
                cursor.execute(
                    f"CREATE DATABASE IF NOT EXISTS `{escaped_db_name}` "
                    f"CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
                )
        except mysql.connector.Error as err:
            logging.error(f"❌ Could not verify/create database: {err}")
            raise

    def _schema_missing(self):
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor(buffered=True)
                # Check for a table that is guaranteed to exist if the schema is initialized
                cursor.execute("SHOW TABLES LIKE 'Mouvement_Caisse'")
                if cursor.fetchone() is None:
                    return True
                
                # Check if stock mapping columns are missing to trigger migration
                cursor.execute("SHOW COLUMNS FROM Fournisseurs LIKE 'stock_supplier_id'")
                if cursor.fetchone() is None:
                    return True
                cursor.execute("SHOW COLUMNS FROM Partenaires LIKE 'stock_partner_id'")
                if cursor.fetchone() is None:
                    return True
                cursor.execute("SHOW COLUMNS FROM Depenses_Achats LIKE 'stock_br_id'")
                if cursor.fetchone() is None:
                    return True
                cursor.execute("SHOW COLUMNS FROM Operations_Partenaires LIKE 'stock_transfer_id'")
                if cursor.fetchone() is None:
                    return True
                return False
        except mysql.connector.Error as err:
            logging.warning(f"Could not verify database schema presence: {err}")
            return False

    @contextmanager
    def get_db_connection(self):
        conn = None
        try:
            conn = _DatabaseBase._pool.get_connection()
            yield conn
            conn.commit()
        except mysql.connector.Error as err:
            logging.error(f"Database error: {err}")
            if conn:
                conn.rollback()
            raise
        finally:
            if conn and conn.is_connected():
                conn.close()

    def get_raw_connection(self):
        return _DatabaseBase._pool.get_connection()
