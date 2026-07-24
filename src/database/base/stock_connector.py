import os
import json
import logging
import mysql.connector

def load_stock_db_config(settings_path="pdf_settings.json"):
    config = {
        "host": "127.0.0.1",
        "port": 3306,
        "user": "root",
        "password": "root",
        "database": "Lab_Inventory_Enterprise_DB"
    }
    
    # Try to load existing settings first
    if os.path.exists(settings_path):
        try:
            with open(settings_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if "stock_db_host" in data:
                    config["host"] = data["stock_db_host"]
                if "stock_db_port" in data:
                    config["port"] = int(data.get("stock_db_port", 3306))
                if "stock_db_user" in data:
                    config["user"] = data["stock_db_user"]
                if "stock_db_password" in data:
                    config["password"] = data["stock_db_password"]
                if "stock_db_name" in data:
                    config["database"] = data["stock_db_name"]
                return config
        except Exception as e:
            logging.error(f"Error reading stock db config from settings: {e}")

    # Fallback to parsing StockLam .env if exists
    stock_env = "D:\\git\\StockLam\\.env"
    if os.path.exists(stock_env):
        try:
            with open(stock_env, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        k, v = line.split('=', 1)
                        k = k.strip()
                        v = v.strip()
                        if k == 'DB_HOST':
                            config['host'] = v
                        elif k == 'DB_PORT':
                            try:
                                config['port'] = int(v)
                            except ValueError:
                                pass
                        elif k == 'DB_USER':
                            config['user'] = v
                        elif k == 'DB_PASSWORD':
                            config['password'] = v
                        elif k == 'DB_NAME':
                            config['database'] = v
        except Exception as e:
            logging.error(f"Error parsing StockLam .env for config: {e}")
            
    return config

def test_stock_db_connection(config):
    try:
        conn = mysql.connector.connect(
            host=config['host'],
            port=config['port'],
            user=config['user'],
            password=config['password'],
            database=config['database'],
            connect_timeout=3,
            use_pure=True,
            auth_plugin='mysql_native_password'
        )
        conn.close()
        return True, "Connexion réussie."
    except Exception as e:
        return False, str(e)

def get_stock_db_suppliers(config):
    suppliers = []
    try:
        conn = mysql.connector.connect(
            host=config['host'],
            port=config['port'],
            user=config['user'],
            password=config['password'],
            database=config['database'],
            connect_timeout=3,
            use_pure=True,
            auth_plugin='mysql_native_password'
        )
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT Supplier_ID, Supplier_Name FROM Suppliers WHERE Deleted_At IS NULL ORDER BY Supplier_Name")
        suppliers = cursor.fetchall()
        cursor.close()
        conn.close()
    except Exception as e:
        logging.error(f"Error fetching StockLam suppliers: {e}")
    return suppliers

def get_stock_db_partners(config):
    partners = []
    try:
        conn = mysql.connector.connect(
            host=config['host'],
            port=config['port'],
            user=config['user'],
            password=config['password'],
            database=config['database'],
            connect_timeout=3,
            use_pure=True,
            auth_plugin='mysql_native_password'
        )
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT Partner_ID, Partner_Name FROM External_Partners WHERE Deleted_At IS NULL ORDER BY Partner_Name")
        partners = cursor.fetchall()
        cursor.close()
        conn.close()
    except Exception as e:
        logging.error(f"Error fetching StockLam partners: {e}")
    return partners

def get_stock_db_suppliers_full(config):
    suppliers = []
    try:
        conn = mysql.connector.connect(
            host=config['host'],
            port=config['port'],
            user=config['user'],
            password=config['password'],
            database=config['database'],
            connect_timeout=3,
            use_pure=True,
            auth_plugin='mysql_native_password'
        )
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM Suppliers WHERE Deleted_At IS NULL")
        suppliers = cursor.fetchall()
        cursor.close()
        conn.close()
    except Exception as e:
        logging.error(f"Error fetching StockLam suppliers: {e}")
        raise e
    return suppliers

def get_stock_db_partners_full(config):
    partners = []
    try:
        conn = mysql.connector.connect(
            host=config['host'],
            port=config['port'],
            user=config['user'],
            password=config['password'],
            database=config['database'],
            connect_timeout=3,
            use_pure=True,
            auth_plugin='mysql_native_password'
        )
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM External_Partners WHERE Deleted_At IS NULL")
        partners = cursor.fetchall()
        cursor.close()
        conn.close()
    except Exception as e:
        logging.error(f"Error fetching StockLam partners: {e}")
        raise e
    return partners


def sync_stock_data_logic():
    from database import data_manager
    config = load_stock_db_config()
    
    results = {
        "suppliers": {"updated": 0, "imported": 0},
        "partners": {"updated": 0, "imported": 0},
        "receptions": {"updated": 0, "imported": 0},
        "transfers": {"updated": 0, "imported": 0},
        "success": False,
        "error": None
    }
    
    # Check connection first
    connected, conn_msg = test_stock_db_connection(config)
    if not connected:
        results["error"] = f"Connexion echouee: {conn_msg}"
        return results
        
    try:
        # 1. Sync Suppliers
        try:
            stock_suppliers = get_stock_db_suppliers_full(config)
            for s in stock_suppliers:
                stock_id = s['Supplier_ID']
                name = s['Supplier_Name']
                
                existing = data_manager.db.fetch_one("SELECT * FROM Fournisseurs WHERE stock_supplier_id = %s", (stock_id,))
                if not existing:
                    existing = data_manager.db.fetch_one("SELECT * FROM Fournisseurs WHERE nom_fournisseur = %s", (name,))
                
                data = {
                    "nom_fournisseur": name,
                    "stock_supplier_id": stock_id,
                    "contact_person": s.get('Contact_Person'),
                    "phone": s.get('Phone'),
                    "email": s.get('Email'),
                    "website": s.get('Website'),
                    "address_line1": s.get('Address_Line1'),
                    "address_line2": s.get('Address_Line2'),
                    "city": s.get('City'),
                    "postal_code": s.get('Postal_Code'),
                    "tax_id_number": s.get('Tax_ID_Number'),
                    "commercial_reg_no": s.get('Commercial_Reg_No'),
                    "bank_name": s.get('Bank_Name'),
                    "bank_account_iban": s.get('Bank_Account_IBAN')
                }
                
                if existing:
                    success, _ = data_manager.db.update_record("Fournisseurs", "id_fournisseur", existing['id_fournisseur'], data)
                    if success:
                        results["suppliers"]["updated"] += 1
                else:
                    success = data_manager.fournisseurs.add_fournisseur(data)
                    if success:
                        results["suppliers"]["imported"] += 1
        except Exception as e:
            logging.error(f"Error syncing suppliers: {e}")
            results["error"] = f"Erreur Fournisseurs: {e}"

        # 2. Sync Partners
        try:
            stock_partners = get_stock_db_partners_full(config)
            for p in stock_partners:
                stock_id = p['Partner_ID']
                name = p['Partner_Name']
                
                existing = data_manager.db.fetch_one("SELECT * FROM Partenaires WHERE stock_partner_id = %s", (stock_id,))
                if not existing:
                    existing = data_manager.db.fetch_one("SELECT * FROM Partenaires WHERE nom_partenaire = %s", (name,))
                
                data = {
                    "nom_partenaire": name,
                    "stock_partner_id": stock_id,
                    "contact_person": p.get('Contact_Person'),
                    "phone": p.get('Phone'),
                    "email": p.get('Email'),
                    "website": p.get('Website'),
                    "address_line1": p.get('Address_Line1'),
                    "address_line2": p.get('Address_Line2'),
                    "city": p.get('City'),
                    "postal_code": p.get('Postal_Code'),
                    "tax_id_number": p.get('Tax_ID_Number'),
                    "commercial_reg_no": p.get('Commercial_Reg_No'),
                    "bank_name": p.get('Bank_Name'),
                    "bank_account_iban": p.get('Bank_Account_IBAN'),
                    "type_partenaire": "SOUS_TRAITANT"
                }
                
                if existing:
                    data["type_partenaire"] = existing["type_partenaire"]
                    success, _ = data_manager.db.update_record("Partenaires", "id_partenaire", existing['id_partenaire'], data)
                    if success:
                        results["partners"]["updated"] += 1
                else:
                    success = data_manager.partenaires.add_partenaire(data)
                    if success:
                        results["partners"]["imported"] += 1
        except Exception as e:
            logging.error(f"Error syncing partners: {e}")
            results["error"] = f"Erreur Partenaires: {e}"

        # 3. Sync Receipts / Bons de Réception
        try:
            conn = mysql.connector.connect(
                host=config['host'],
                port=config['port'],
                user=config['user'],
                password=config['password'],
                database=config['database'],
                connect_timeout=3,
                use_pure=True,
                auth_plugin='mysql_native_password'
            )
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM reception_log WHERE Status = 'Completed'")
            receptions = cursor.fetchall()
            
            # Get category ID for CONSOMMABLES
            cat_id = data_manager.fournisseurs.ensure_category_exists("CONSOMMABLES")
            
            for r in receptions:
                br_id = r['BR_ID']
                stock_sup_id = r['Supplier_ID']
                reception_date = r['Reception_Date']
                invoice_ref = r.get('Supplier_Invoice_Ref') or ''
                bl_ref = r.get('Supplier_BL_Ref') or ''
                doc_type = r.get('Document_Type') or 'BL'
                
                # Fetch local supplier matching stock_sup_id
                local_sup = data_manager.db.fetch_one("SELECT id_fournisseur FROM Fournisseurs WHERE stock_supplier_id = %s", (stock_sup_id,))
                if not local_sup:
                    continue  # skip if supplier is not found/synced
                    
                id_fournisseur = local_sup['id_fournisseur']
                
                # Determine amount total
                amount = 0.0
                if r.get('Invoice_Total_TTC') is not None and float(r['Invoice_Total_TTC']) > 0:
                    amount = float(r['Invoice_Total_TTC'])
                elif r.get('Invoice_Total_HT') is not None and float(r['Invoice_Total_HT']) > 0:
                    amount = float(r['Invoice_Total_HT'])
                else:
                    # Calculate total from details
                    cursor2 = conn.cursor()
                    cursor2.execute("SELECT SUM(Qty_Received * Unit_Price_Received) FROM reception_details WHERE BR_ID = %s", (br_id,))
                    row_sum = cursor2.fetchone()
                    if row_sum and row_sum[0] is not None:
                        amount = float(row_sum[0])
                    cursor2.close()
                
                # Format type_document
                type_doc = "FACTURE" if doc_type in ("Facture", "Both") else "BL"
                
                # Format date
                date_facture = reception_date.date() if hasattr(reception_date, 'date') else str(reception_date)[:10]
                
                # Format observation
                obs = f"BR #{br_id}"
                if invoice_ref:
                    obs += f" (Facture: {invoice_ref})"
                if bl_ref:
                    obs += f" (BL: {bl_ref})"
                obs += " [StockLam Auto-Sync]"
                
                # Check if receipt already imported
                existing_dep = data_manager.db.fetch_one("SELECT * FROM Depenses_Achats WHERE stock_br_id = %s", (br_id,))
                
                dep_data = {
                    "id_fournisseur": id_fournisseur,
                    "id_categorie": cat_id,
                    "type_document": type_doc,
                    "date_facture": date_facture,
                    "montant_total": amount,
                    "observation": obs,
                    "stock_br_id": br_id
                }
                
                if existing_dep:
                    # Update
                    success, _ = data_manager.db.update_record("Depenses_Achats", "id_depense", existing_dep['id_depense'], dep_data)
                    if success:
                        results["receptions"]["updated"] += 1
                else:
                    # Insert
                    query_ins = "INSERT INTO Depenses_Achats (id_fournisseur, id_categorie, type_document, date_facture, montant_total, observation, stock_br_id) VALUES (%s, %s, %s, %s, %s, %s, %s)"
                    params_ins = (id_fournisseur, cat_id, type_doc, date_facture, amount, obs, br_id)
                    success, _ = data_manager.db.execute(query_ins, params_ins)
                    if success:
                        results["receptions"]["imported"] += 1
            
            cursor.close()
            conn.close()
        except Exception as e:
            logging.error(f"Error syncing receipt notes: {e}")
            results["error"] = f"Erreur BR: {e}"
            
        # 4. Sync External Transfers / Sous Traitant Operations
        try:
            conn = mysql.connector.connect(
                host=config['host'],
                port=config['port'],
                user=config['user'],
                password=config['password'],
                database=config['database'],
                connect_timeout=3,
                use_pure=True,
                auth_plugin='mysql_native_password'
            )
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM external_transfer_log WHERE Status = 'Completed'")
            transfers = cursor.fetchall()
            
            for t in transfers:
                transfer_id = t['Transfer_ID']
                stock_partner_id = t['Partner_ID']
                transfer_date = t['Transaction_Date']
                amount = float(t.get('Total_Amount') or 0.0)
                if amount == 0.0:
                    # Calculate total from details if Total_Amount is not populated
                    cursor2 = conn.cursor()
                    cursor2.execute("SELECT SUM(Qty_Transferred * Unit_Price) FROM external_transfer_details WHERE Transfer_ID = %s", (transfer_id,))
                    row_sum = cursor2.fetchone()
                    if row_sum and row_sum[0] is not None:
                        amount = float(row_sum[0])
                    cursor2.close()
                notes = t.get('Notes') or ''
                
                # Fetch local partner matching stock_partner_id
                local_partner = data_manager.db.fetch_one("SELECT id_partenaire FROM Partenaires WHERE stock_partner_id = %s", (stock_partner_id,))
                if not local_partner:
                    continue  # skip if partner is not found/synced
                    
                id_partenaire = local_partner['id_partenaire']
                
                # Format date
                date_operation = transfer_date.date() if hasattr(transfer_date, 'date') else str(transfer_date)[:10]
                
                # Format observation
                obs = f"Transfert Externe #{transfer_id}"
                if notes:
                    obs += f" - {notes}"
                obs += " [StockLam Auto-Sync]"
                
                # Check if transfer already imported
                existing_op = data_manager.db.fetch_one("SELECT * FROM Operations_Partenaires WHERE stock_transfer_id = %s", (transfer_id,))
                
                op_data = {
                    "id_partenaire": id_partenaire,
                    "type_document": "FACTURE", # default to FACTURE
                    "date_operation": date_operation,
                    "montant_total": amount,
                    "observation": obs,
                    "stock_transfer_id": transfer_id
                }
                
                if existing_op:
                    # Update
                    success, _ = data_manager.db.update_record("Operations_Partenaires", "id_operation", existing_op['id_operation'], op_data)
                    if success:
                        results["transfers"]["updated"] += 1
                else:
                    # Insert
                    query_ins = "INSERT INTO Operations_Partenaires (id_partenaire, type_document, date_operation, montant_total, observation, stock_transfer_id) VALUES (%s, %s, %s, %s, %s, %s)"
                    params_ins = (id_partenaire, op_data["type_document"], date_operation, amount, obs, transfer_id)
                    success, _ = data_manager.db.execute(query_ins, params_ins)
                    if success:
                        results["transfers"]["imported"] += 1
            
            cursor.close()
            conn.close()
        except Exception as e:
            logging.error(f"Error syncing external transfers: {e}")
            if not results["error"]:
                results["error"] = f"Erreur Transferts: {e}"
            
        results["success"] = True
    except Exception as e:
        logging.error(f"Global sync error: {e}")
        results["error"] = str(e)
        
    return results

