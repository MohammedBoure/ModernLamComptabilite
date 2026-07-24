import os
import sys
import logging

# Ensure src is in sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.database.base.database import Database

def init_database():
    """
    Initializes the database using the python-based SchemaInitializerMixin
    rather than an external database.sql file.
    """
    print("Starting database initialization using schema_initializer...")
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    
    try:
        # Re-initialize the connection state just in case it's already loaded
        Database.reset_connection_state()
        
        # Instantiating Database ensures the DB exists (creates if missing)
        db = Database()
        
        # Explicitly call _initialize_schema to ensure tables, views, and migrations run
        db._initialize_schema()
        
        print("Database initialized successfully from schema_initializer.py.")
        return True
    except Exception as e:
        print(f"Error initializing database: {e}")
        return False

if __name__ == "__main__":
    init_database()
