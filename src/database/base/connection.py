import mysql.connector
from mysql.connector import errorcode, pooling
import logging
import os
from contextlib import contextmanager
from dotenv import load_dotenv

from .config import get_env_bool, get_external_path


def _get_pool_size():
    try:
        return max(1, min(32, int(os.getenv("DB_POOL_SIZE", "8"))))
    except (TypeError, ValueError):
        return 8

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
            pool_size = _get_pool_size()
            try:
                _DatabaseBase._pool = pooling.MySQLConnectionPool(
                    pool_name="modernlam_pool",
                    pool_size=pool_size,
                    pool_reset_session=True,
                    use_pure=True,
                    auth_plugin='mysql_native_password',
                    **self.db_config
                )
                logging.info(f"Connection pool initialized successfully (Size: {pool_size}).")
            except mysql.connector.Error as e:
                if getattr(e, 'errno', None) == 1040 or "1040" in str(e):
                    logging.warning("1040 Too many connections encountered. Retrying pool initialization with fallback size 3...")
                    try:
                        _DatabaseBase._pool = pooling.MySQLConnectionPool(
                            pool_name="modernlam_pool",
                            pool_size=3,
                            pool_reset_session=True,
                            use_pure=True,
                            auth_plugin='mysql_native_password',
                            **self.db_config
                        )
                        logging.info("Connection pool initialized with fallback size (Size: 3).")
                    except Exception as fallback_err:
                        logging.error(f"❌ Failed to initialize Connection Pool with fallback: {fallback_err}")
                        raise
                else:
                    logging.error(f"❌ Failed to initialize Connection Pool: {e}")
                    raise
            except Exception as e:
                logging.error(f"❌ Failed to initialize Connection Pool: {e}")
                raise

        self.schema_check_on_startup = get_env_bool(
            "DB_SCHEMA_CHECK_ON_STARTUP",
            default=True
        )
        schema_missing = self._schema_missing()
        if schema_missing or (is_local and self.schema_check_on_startup):
            logging.info("Running database schema check / initial setup.")
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
                # Check for key tables that are guaranteed to exist if the schema is fully initialized
                for table in ['Mouvement_Caisse', 'Utilisateurs', 'Audit_Events', 'Roles', 'Schema_Migrations']:
                    cursor.execute(f"SHOW TABLES LIKE '{table}'")
                    if cursor.fetchone() is None:
                        return True
                
                # Check for key columns in Utilisateurs
                cursor.execute("SHOW COLUMNS FROM Utilisateurs LIKE 'is_active'")
                if cursor.fetchone() is None:
                    return True
                cursor.execute("SHOW COLUMNS FROM Utilisateurs LIKE 'role_code'")
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
            logging.warning(f"Could not verify database schema presence (error: {err}), assuming schema update is needed.")
            return True

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
