import sqlite3
import hashlib
from datetime import datetime

from api.helpdesk_api import HelpdeskAPI
from api.admin_api import AdminAPI
from api.tec_api import TechAPI

class Api:

    def __init__(self):
                                                                 
                                                    
        self.init_db()
                                                           
        self.purge_old_records()
        self.helpdesk_api = HelpdeskAPI(db_path='repair_erp.db')
        self.admin_api = AdminAPI(db_path='repair_erp.db')
        self.tec_api = TechAPI(db_path='repair_erp.db')
        
    def hash_password(self, password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()

    def init_db(self):
        conn = sqlite3.connect('repair_erp.db')
        c = conn.cursor()

                              
        c.execute('''CREATE TABLE IF NOT EXISTS Users (
                        user_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                        username TEXT UNIQUE NOT NULL,
                        password_hash TEXT NOT NULL,
                        role TEXT NOT NULL,
                        is_active BOOLEAN DEFAULT TRUE NOT NULL)''')

        c.execute('''CREATE TABLE IF NOT EXISTS AuditLogs (
                        log_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                        user_id INTEGER,
                        action_type TEXT,
                        target_id TEXT,
                        timestamp DATETIME,
                        notes TEXT)''')

                              
        c.execute('''CREATE TABLE IF NOT EXISTS Customers (
                        customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        full_name TEXT,
                        phone_number TEXT UNIQUE,
                        email TEXT)''')

                            
        c.execute('''CREATE TABLE IF NOT EXISTS Devices (
                        device_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        customer_id INTEGER,
                        imei_serial TEXT UNIQUE,
                        device_brand TEXT,
                        device_model TEXT,
                        FOREIGN KEY(customer_id) REFERENCES Customers(customer_id))''')

                            
        c.execute('''CREATE TABLE IF NOT EXISTS Tickets (
                        ticket_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        device_id INTEGER,
                        assigned_tech_id INTEGER,
                        issue_description TEXT,
                        status TEXT,
                        created_at DATETIME,
                        completed_at DATETIME,
                        service_charge DECIMAL,
                        net_profit DECIMAL,
                        advance_deposit DECIMAL,
                        customer_notified BOOLEAN DEFAULT 0,
                        notified_at DATETIME,
                        FOREIGN KEY(device_id) REFERENCES Devices(device_id),
                        FOREIGN KEY(assigned_tech_id) REFERENCES Users(user_id))''')

                                                       
        c.execute('''CREATE TABLE IF NOT EXISTS Parts_Inventory (
                        part_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        part_name TEXT,
                        brand_compatibility TEXT,
                        unit_cost DECIMAL,
                        current_stock INTEGER)''')

                                 
        c.execute('''CREATE TABLE IF NOT EXISTS Donor_Boards (
                        board_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        brand TEXT,
                        model TEXT,
                        serial_number TEXT,
                        status TEXT,
                        acquisition_cost DECIMAL)''')

                                                 
        c.execute('''CREATE TABLE IF NOT EXISTS Components (
                        component_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        board_id INTEGER,
                        used_ticket_id INTEGER,
                        part_name TEXT,
                        condition TEXT DEFAULT 'Available',
                        harvested_date DATETIME,
                        FOREIGN KEY(board_id) REFERENCES Donor_Boards(board_id),
                        FOREIGN KEY(used_ticket_id) REFERENCES Tickets(ticket_id))''')

                                                    
        c.execute('''CREATE TABLE IF NOT EXISTS Ticket_Parts (
                        usage_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        ticket_id INTEGER,
                        part_id INTEGER,
                        donor_component_id INTEGER,
                        quantity_used INTEGER,
                        actual_cost_at_time DECIMAL,
                        allocation_status TEXT DEFAULT 'Draft',
                        FOREIGN KEY(ticket_id) REFERENCES Tickets(ticket_id),
                        FOREIGN KEY(part_id) REFERENCES Parts_Inventory(part_id),
                        FOREIGN KEY(donor_component_id) REFERENCES Components(component_id))''')

                                                                            
        c.execute('''CREATE TABLE IF NOT EXISTS ModelTemplates (
                        template_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        brand TEXT NOT NULL,
                        model TEXT NOT NULL,
                        part_name TEXT NOT NULL,
                        estimated_value DECIMAL DEFAULT 0,
                        UNIQUE(model, part_name))''')

                                  
        c.execute ("SELECT * FROM Users WHERE username='master'")
        if not c.fetchone():
            master_hash = self.hash_password('master')
            c.execute("INSERT INTO Users (username, password_hash, role, is_active) VALUES (?, ?, ?, ?)",
                      ('master', master_hash, 'master', True))
            print("System Initialized. Hidden Master account created.")

        conn.commit()
        conn.close()

    def purge_old_records(self) -> dict:
        conn = sqlite3.connect('repair_erp.db')
        c    = conn.cursor()
        try:
            cutoff = datetime.now().replace(year=datetime.now().year - 1).strftime("%Y-%m-%d %H:%M:%S")

                                                                            
            c.execute(
                """
                SELECT ticket_id
                FROM   Tickets
                WHERE  status IN ('Completed', 'Cancelled')
                  AND  created_at < ?
                """,
                (cutoff,)
            )
            old_ticket_ids = [r[0] for r in c.fetchall()]

            if not old_ticket_ids:
                conn.close()
                print("[Purge] No records older than 1 year found. Nothing to clean.")
                return {
                    'status': 'success',
                    'tickets_purged': 0,
                    'devices_purged': 0,
                    'customers_purged': 0,
                    'message': 'No old records to purge.'
                }

                                                         
            placeholders = ",".join("?" * len(old_ticket_ids))
            ids          = tuple(old_ticket_ids)

                                                                            
                                                                    
            ticket_id_strings = tuple(f"TKT-{tid}" for tid in old_ticket_ids)
            audit_placeholders = ",".join("?" * len(ticket_id_strings))
            c.execute(
                f"DELETE FROM AuditLogs WHERE target_id IN ({audit_placeholders})",
                ticket_id_strings
            )
            audit_deleted = c.rowcount

                                                                            
            c.execute(
                f"DELETE FROM Ticket_Parts WHERE ticket_id IN ({placeholders})",
                ids
            )
            parts_deleted = c.rowcount

                                                                            
                                                                            
                                                                        
                                                                
            c.execute(
                f"DELETE FROM Components WHERE used_ticket_id IN ({placeholders})",
                ids
            )
            components_deleted = c.rowcount

                                                                            
            c.execute(
                f"SELECT DISTINCT device_id FROM Tickets WHERE ticket_id IN ({placeholders})",
                ids
            )
            candidate_device_ids = [r[0] for r in c.fetchall()]

                                                                            
            c.execute(
                f"DELETE FROM Tickets WHERE ticket_id IN ({placeholders})",
                ids
            )
            tickets_purged = c.rowcount

                                                                            
                                                                                
            devices_purged    = 0
            orphan_device_ids = []
            for dev_id in candidate_device_ids:
                c.execute(
                    "SELECT COUNT(*) FROM Tickets WHERE device_id = ?",
                    (dev_id,)
                )
                if c.fetchone()[0] == 0:
                    orphan_device_ids.append(dev_id)

            if orphan_device_ids:
                dev_placeholders = ",".join("?" * len(orphan_device_ids))
                dev_ids          = tuple(orphan_device_ids)

                                                                     
                c.execute(
                    f"SELECT DISTINCT customer_id FROM Devices WHERE device_id IN ({dev_placeholders})",
                    dev_ids
                )
                candidate_customer_ids = [r[0] for r in c.fetchall()]

                c.execute(
                    f"DELETE FROM Devices WHERE device_id IN ({dev_placeholders})",
                    dev_ids
                )
                devices_purged = c.rowcount
            else:
                candidate_customer_ids = []

                                                                            
                                                                         
            customers_purged    = 0
            orphan_customer_ids = []
            for cust_id in candidate_customer_ids:
                c.execute(
                    "SELECT COUNT(*) FROM Devices WHERE customer_id = ?",
                    (cust_id,)
                )
                if c.fetchone()[0] == 0:
                    orphan_customer_ids.append(cust_id)

            if orphan_customer_ids:
                cust_placeholders = ",".join("?" * len(orphan_customer_ids))
                c.execute(
                    f"DELETE FROM Customers WHERE customer_id IN ({cust_placeholders})",
                    tuple(orphan_customer_ids)
                )
                customers_purged = c.rowcount

            conn.commit()

            msg = (
                f"[Purge] Startup cleanup complete — "
                f"{tickets_purged} ticket(s), "
                f"{devices_purged} device(s), "
                f"{customers_purged} customer(s) removed. "
                f"({parts_deleted} part allocation(s), "
                f"{components_deleted} donor component(s), and "
                f"{audit_deleted} audit log(s) also cleared.)"
            )
            print(msg)
            return {
                'status':           'success',
                'tickets_purged':   tickets_purged,
                'devices_purged':   devices_purged,
                'customers_purged': customers_purged,
                'message':          msg,
            }

        except Exception as e:
            conn.rollback()
            print(f"[Purge] ERROR during startup cleanup: {e}")
            return {'status': 'error', 'message': str(e)}
        finally:
            conn.close()

    def login(self, username: str, password: str) -> dict:
        conn = sqlite3.connect('repair_erp.db')
        c = conn.cursor()
        hashed_pw = self.hash_password(password)                                
        
                                         
        c.execute("SELECT user_id, username, role FROM Users WHERE username=? AND password_hash=? AND is_active=1", 
                  (username, hashed_pw))
        user = c.fetchone()

        if user:
            user_id, uname, role = user
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                                                  
            c.execute("INSERT INTO AuditLogs (user_id, action_type, target_id, timestamp, notes) VALUES (?, ?, ?, ?, ?)",
                      (user_id, 'Login', f"USR-{user_id}", now, 'User logged into desktop app'))
            conn.commit()
            conn.close()
            return {'status': 'success', 'user': {'id': user_id, 'username': uname, 'role': role}}
        else:
            conn.close()
            return {'status': 'error', 'message': 'Invalid credentials or inactive account'}

                               

    def get_tickets(self):
        return self.helpdesk_api.get_tickets()
    def get_customers(self):
        return self.helpdesk_api.get_customers()
    def create_ticket(self, user_id, phone, name, email, brand, model, imei, issue, deposit):
        return self.helpdesk_api.create_ticket(user_id, phone, name, email, brand, model, imei, issue, deposit)
    def notify_customer(self, user_id, ticket_id):
        return self.helpdesk_api.notify_customer(user_id, ticket_id)
    

                                    

    def create_user(self, creator_id, name, role, username, password):
        return self.admin_api.create_user(creator_id, name, role, username, password)
    def get_all_users(self):
        return self.admin_api.get_all_users() 
    def toggle_user_active(self, admin_id, target_user_id, new_state):
        return self.admin_api.toggle_user_active(admin_id, target_user_id, new_state)   
    def get_all_tickets_admin(self, search_term=""):
        return self.admin_api.get_all_tickets_admin(search_term)
    def get_ticket_detail(self, ticket_raw_id):
        return self.admin_api.get_ticket_detail(ticket_raw_id)
    def cancel_ticket(self, admin_id, ticket_raw_id):
        return self.admin_api.cancel_ticket(admin_id, ticket_raw_id)
    
    
                                       

    def get_all_inventory(self, search_term="",stock_filter="all"):
        return self.admin_api.get_all_inventory(search_term, stock_filter)
    def add_new_part_type(self, admin_id, name, brand, cost, initial_stock):
        return self.admin_api.add_new_part_type(admin_id, name, brand, cost, initial_stock)
    def restock_existing_part(self, admin_id, part_id, added_quantity, new_cost):
        return self.admin_api.restock_existing_part(admin_id, part_id, added_quantity, new_cost)
    
    
                                        

    def get_alert_counts(self):
        return self.admin_api.get_alert_counts()
    def get_low_stock_alerts(self):
        return self.admin_api.get_low_stock_alerts()
    def get_flagged_components(self):
        return self.admin_api.get_flagged_components()
    def resolve_flagged_component(self, admin_id, component_id, decision):
        return self.admin_api.resolve_flagged_component(admin_id, component_id, decision)
    
    
                                              
   
    def get_model_template(self, brand, model):
        return self.admin_api.get_model_template(brand, model)
    def add_part_to_template(self, brand, model, part_name, estimated_value):
        return self.admin_api.add_part_to_template(brand, model, part_name, estimated_value)
    def create_model_template(self, brand, model, parts):
        return self.admin_api.create_model_template(brand, model, parts)
    def register_donor_board(self, admin_id, brand, model, serial_number, acquisition_cost, selected_components):
        return self.admin_api.register_donor_board(admin_id, brand, model, serial_number, acquisition_cost, selected_components)
    
    
                                       
 
    def get_financial_summary(self, start_date, end_date):
        return self.admin_api.get_financial_summary(start_date, end_date) 
    def get_inventory_valuation(self):
        return self.admin_api.get_inventory_valuation()
    def get_ticket_pipeline(self):
        return self.admin_api.get_ticket_pipeline()
    def get_device_trends(self, months):
        return self.admin_api.get_device_trends(months)
    
    
    

                                

    def get_intake_pool(self):
        return self.tec_api.get_intake_pool()
    
    def accept_ticket(self, tech_id, ticket_raw_id):
        return self.tec_api.accept_ticket(tech_id, ticket_raw_id)
    
    def get_my_tickets(self, tech_id):
        return self.tec_api.get_my_tickets(tech_id)
    
    def search_new_inventory(self, search_term=""):
        return self.tec_api.search_new_inventory(search_term)
    
    def search_donor_inventory(self, search_term=""):
        return self.tec_api.search_donor_inventory(search_term)
    
    def allocate_draft_parts(self, tech_id, ticket_raw_id, parts_data):
        return self.tec_api.allocate_draft_parts(tech_id, ticket_raw_id, parts_data)
    
    def get_ticket_parts(self, ticket_raw_id):
        return self.tec_api.get_ticket_parts(ticket_raw_id)
    
    def remove_ticket_part(self, user_id, usage_id):
        return self.tec_api.remove_ticket_part(user_id, usage_id)
    
    def flag_donor_part(self, tech_id, component_id, notes):
        return self.tec_api.flag_donor_part(tech_id, component_id, notes)
    
    def mark_part_installed(self, tech_id, usage_id):
        return self.tec_api.mark_part_installed(tech_id, usage_id)
    
    def complete_ticket(self, tech_id, ticket_raw_id, service_charge):
        return self.tec_api.complete_ticket(tech_id, ticket_raw_id, service_charge)
    
 

