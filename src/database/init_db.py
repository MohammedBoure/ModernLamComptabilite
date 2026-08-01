import os
import sys
import logging

# Ensure src is in sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_root = os.path.dirname(current_dir)
project_root = os.path.dirname(os.path.dirname(current_dir))
for path in (src_root, project_root):
    if path not in sys.path:
        sys.path.insert(0, path)

try:
    from database import data_manager
except ModuleNotFoundError:
    from src.database import data_manager

def init_database():
    """
    Initializes the database using the python-based SchemaInitializerMixin
    rather than an external database.sql file.
    """
    print("Starting database initialization using schema_initializer...")
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    
    try:
        # Reuse the application's singleton so initialization does not create
        # a second connection pool or invalidate data_manager.db.
        db = data_manager.db
        if not getattr(db, "_schema_initialized", False):
            db._initialize_schema()
            db._schema_initialized = True
        
        print("Database initialized successfully from schema_initializer.py.")
        return True
    except Exception as e:
        print(f"Error initializing database: {e}")
        return False

if __name__ == "__main__":
    init_database()
