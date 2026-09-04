from datetime import datetime
import sqlite3
import re

class HelpdeskAPI:
    def __init__(self, db_path: str):
        self.db_path = db_path
        
    def get_tickets(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        query = '''
                SELECT 
                    t.ticket_id, c.full_name, c.phone_number, d.device_brand, d.device_model, 
                    t.status, t.created_at, u.username, t.customer_notified
                FROM Tickets t
                JOIN Devices d ON t.device_id = d.device_id
                JOIN Customers c ON d.customer_id = c.customer_id
                LEFT JOIN Users u ON t.assigned_tech_id = u.user_id
                ORDER BY t.ticket_id DESC
            '''
        c.execute(query)
        rows = c.fetchall()
        conn.close()
        
        tickets = []
        for r in rows:
            tickets.append({
                'id': f"TKT-{r[0]:04d}",
                'raw_id': r[0],
                'customer': r[1],
                'phone': r[2],
                'device': f"{r[3]} {r[4]}",
                'status': r[5],
                'created': r[6],
                'tech': r[7] if r[7] else "Unassigned",
                'notified': bool(r[8])
            })
        return {'status': 'success', 'data': tickets}

    def get_customers(self):
            
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            
            query = '''
                SELECT 
                    c.customer_id, 
                    c.full_name, 
                    c.phone_number, 
                    c.email,
                    t.ticket_id, 
                    d.device_brand || ' ' || d.device_model as device_name, 
                    t.status, 
                    t.created_at,
                    t.issue_description
                FROM Customers c
                LEFT JOIN Devices d ON c.customer_id = d.customer_id
                LEFT JOIN Tickets t ON d.device_id = t.device_id
                ORDER BY c.full_name ASC, t.ticket_id DESC
            '''
            c.execute(query)
            rows = c.fetchall()
            conn.close()
            
                                                                                  
                                                                           
            customer_map = {}
            for r in rows:
                cust_id = r[0]
                if cust_id not in customer_map:
                    customer_map[cust_id] = {
                        'customer_id': cust_id,
                        'name': r[1],
                        'phone': r[2],
                        'email': r[3] if r[3] else "No email",
                        'tickets': []
                    }
                
                                                                              
                if r[4] is not None:
                    customer_map[cust_id]['tickets'].append({
                        'id': f"TKT-{r[4]:04d}",
                        'device': r[5],
                        'status': r[6],
                        'created': r[7].split(' ')[0],                
                        'issue': r[8]
                    })

                                               
            customers = list(customer_map.values())
            return {'status': 'success', 'data': customers}

    def create_ticket(self, user_id, phone, name, email, brand, model, imei, issue, deposit):

                                                                             
                                  
        if not re.fullmatch(r"\d{10}", str(phone)):
            return {'status': 'error',
                    'message': 'Phone must be exactly 10 digits (e.g. 9876543210).'}

                                                              
        if email and not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", str(email)):
            return {'status': 'error',
                    'message': 'Email must be a valid address (e.g. user@example.com).'}

                                      
        raw_deposit = str(deposit) if deposit else ""
        if raw_deposit:
            try:
                if float(raw_deposit) < 0:
                    raise ValueError
            except ValueError:
                return {'status': 'error',
                        'message': 'Advance Deposit must be a valid non-negative number.'}

        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        try:
            c.execute("SELECT customer_id FROM Customers WHERE phone_number=?", (phone,))
            cust = c.fetchone()
            if cust: customer_id = cust[0]
            else:
                c.execute("INSERT INTO Customers (full_name, phone_number, email) VALUES (?, ?, ?)", (name, phone, email))
                customer_id = c.lastrowid

            c.execute("SELECT device_id FROM Devices WHERE imei_serial=?", (imei,))
            dev = c.fetchone()
            if dev: device_id = dev[0]
            else:
                c.execute("INSERT INTO Devices (customer_id, imei_serial, device_brand, device_model) VALUES (?, ?, ?, ?)", 
                          (customer_id, imei, brand, model))
                device_id = c.lastrowid

            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            deposit_val = float(deposit) if deposit else 0.0
            
            c.execute('''INSERT INTO Tickets (device_id, issue_description, status, created_at, advance_deposit, customer_notified) 
                         VALUES (?, ?, ?, ?, ?, ?)''', (device_id, issue, 'Intake', now, deposit_val, False))
            new_ticket_id = c.lastrowid

            c.execute("INSERT INTO AuditLogs (user_id, action_type, target_id, timestamp) VALUES (?, ?, ?, ?)",
                      (user_id, 'Ticket Created', f"TKT-{new_ticket_id}", now))
            conn.commit()
            return {'status': 'success', 'ticket_id': f"TKT-{new_ticket_id:04d}"}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
        finally:
            conn.close()

    def notify_customer(self, user_id, ticket_id):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        try:
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            c.execute("UPDATE Tickets SET customer_notified = 1, notified_at = ? WHERE ticket_id = ?", (now, ticket_id))
            c.execute("INSERT INTO AuditLogs (user_id, action_type, target_id, timestamp) VALUES (?, ?, ?, ?)",
                      (user_id, 'Customer Notified', f"TKT-{ticket_id}", now))
            conn.commit()
            return {'status': 'success'}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
        finally:
            conn.close()

