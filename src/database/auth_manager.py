import json
import hashlib
import logging
from database import data_manager

class AuthManager:
    @staticmethod
    def hash_password(password):
        """Return the password as plain text without hashing, as requested."""
        return password

    @staticmethod
    def check_password(hashed_password, user_password):
        """Check a plain text password (variable name kept for compatibility)."""
        return hashed_password == user_password

    @staticmethod
    def initialize_default_admin():
        """Create a default admin user if no users exist."""
        try:
            result = data_manager.db.fetch_one("SELECT COUNT(*) as count FROM Utilisateurs")
            
            if result and result['count'] == 0:
                admin_pass = 'admin123'
                admin_permissions = json.dumps({
                    "sections": ["Dashboard", "HR", "Caisse", "Cloture", "Fournisseurs", "Partenaires", "Banque", "Settings"],
                    "tabs": {}
                })
                
                query = """
                INSERT INTO Utilisateurs (username, password_hash, nom_complet, permissions) 
                VALUES (%s, %s, %s, %s)
                """
                data_manager.db.execute(query, ('admin', admin_pass, 'Administrateur', admin_permissions))
                logging.info("Default admin user created.")
                
        except Exception as err:
            logging.error(f"Error initializing default admin: {err}")

    @staticmethod
    def authenticate(username, password):
        """Authenticate a user by username and password. Returns user dict on success, None on failure."""
        try:
            query = "SELECT * FROM Utilisateurs WHERE username = %s"
            user = data_manager.db.fetch_one(query, (username,))
            
            if user and AuthManager.check_password(user['password_hash'], password):
                # Parse permissions JSON
                try:
                    user['permissions'] = json.loads(user['permissions'])
                except json.JSONDecodeError:
                    user['permissions'] = {"sections": [], "tabs": {}}
                return user
            
            return None
        except Exception as err:
            logging.error(f"Error during authentication: {err}")
            return None

    @staticmethod
    def get_user_by_username(username):
        """Get a user by username without checking password. Returns user dict on success, None on failure."""
        try:
            query = "SELECT * FROM Utilisateurs WHERE username = %s"
            user = data_manager.db.fetch_one(query, (username,))
            
            if user:
                # Parse permissions JSON
                try:
                    user['permissions'] = json.loads(user['permissions'])
                except json.JSONDecodeError:
                    user['permissions'] = {"sections": [], "tabs": {}}
                return user
            
            return None
        except Exception as err:
            logging.error(f"Error getting user by username: {err}")
            return None
