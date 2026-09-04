from datetime import datetime
import sqlite3
import hashlib
class AdminAPI:
    def __init__(self, db_path: str):
        self.db_path = db_path
    
    def hash_password(self, password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()
    
    def create_user(self, creator_id, name, role, username, password):
        
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        try:
            hashed_pw = self.hash_password(password)
            c.execute("INSERT INTO Users (username, password_hash, role, is_active) VALUES (?, ?, ?, ?)",
                      (username, hashed_pw, role, True))
            new_user_id = c.lastrowid
            
                                               
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            c.execute("INSERT INTO AuditLogs (user_id, action_type, target_id, timestamp, notes) VALUES (?, ?, ?, ?, ?)",
                      (creator_id, 'User Created', f"USR-{new_user_id}", now, f"Created {role} account for {username} ({name})"))
            conn.commit()
            return {'status': 'success'}
        except sqlite3.IntegrityError:
                                                            
            return {'status': 'error', 'message': 'Username already exists in the system.'}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
        finally:
            conn.close()

    def get_all_users(self) -> dict:
        
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        try:
            c.execute("""
                SELECT user_id, username, role, is_active
                FROM Users
                WHERE role != 'master'
                ORDER BY role ASC, username ASC
            """)
            rows = c.fetchall()
            users = []
            for r in rows:
                users.append({
                    'user_id':   r[0],
                    'username':  r[1],
                    'role':      r[2],
                    'is_active': bool(r[3]),
                })
            return {'status': 'success', 'data': users}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
        finally:
            conn.close()

    def toggle_user_active(self, admin_id: int, target_user_id: int, new_state: bool) -> dict:
        
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        try:
                                                                   
            c.execute("SELECT role, username FROM Users WHERE user_id = ?", (target_user_id,))
            row = c.fetchone()
            if not row:
                return {'status': 'error', 'message': 'User not found.'}
            if row[0] == 'master':
                return {'status': 'error', 'message': 'Cannot modify the master account.'}

            c.execute("UPDATE Users SET is_active = ? WHERE user_id = ?",
                      (1 if new_state else 0, target_user_id))

            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            action = "User Activated" if new_state else "User Deactivated"
            c.execute(
                "INSERT INTO AuditLogs (user_id, action_type, target_id, timestamp, notes) "
                "VALUES (?, ?, ?, ?, ?)",
                (admin_id, action, f"USR-{target_user_id}", now,
                 f"{action}: {row[1]} ({row[0]})")
            )
            conn.commit()
            return {'status': 'success'}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
        finally:
            conn.close()
            
    def get_all_tickets_admin(self, search_term: str = "") -> dict:
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        try:
            base_query = '''
                SELECT
                    t.ticket_id,
                    c.full_name,
                    c.phone_number,
                    d.device_brand,
                    d.device_model,
                    t.status,
                    t.created_at,
                    t.completed_at,
                    u.username         AS tech_username,
                    t.service_charge,
                    t.net_profit,
                    t.advance_deposit,
                    t.customer_notified,
                    t.notified_at,
                    t.issue_description,
                    d.imei_serial
                FROM Tickets t
                JOIN Devices d ON t.device_id = d.device_id
                JOIN Customers c ON d.customer_id = c.customer_id
                LEFT JOIN Users u ON t.assigned_tech_id = u.user_id
            '''

            if search_term:
                term = f"%{search_term}%"
                base_query += '''
                    WHERE
                        CAST(t.ticket_id AS TEXT) LIKE ?
                        OR c.full_name       LIKE ?
                        OR c.phone_number    LIKE ?
                        OR d.device_brand    LIKE ?
                        OR d.device_model    LIKE ?
                        OR t.status          LIKE ?
                        OR u.username        LIKE ?
                        OR t.issue_description LIKE ?
                '''
                base_query += " ORDER BY t.ticket_id DESC"
                params = (term, term, term, term, term, term, term, term)
                c.execute(base_query, params)
            else:
                base_query += " ORDER BY t.ticket_id DESC"
                c.execute(base_query)

            rows = c.fetchall()
            tickets = []
            for r in rows:
                tickets.append({
                    'raw_id':     r[0],
                    'id':         f"TKT-{r[0]:04d}",
                    'customer':   r[1],
                    'phone':      r[2],
                    'device':     f"{r[3]} {r[4]}",
                    'status':     r[5],
                    'created':    r[6] or "—",
                    'completed':  r[7] or "—",
                    'tech':       r[8] if r[8] else "Unassigned",
                    'charge':     float(r[9]) if r[9] else 0.0,
                    'profit':     float(r[10]) if r[10] else 0.0,
                    'deposit':    float(r[11]) if r[11] else 0.0,
                    'notified':   bool(r[12]),
                    'notified_at': r[13] or "—",
                    'issue':      r[14] or "No description",
                    'imei':       r[15] or "—",
                })
            return {'status': 'success', 'data': tickets}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
        finally:
            conn.close()

    def get_ticket_detail(self, ticket_raw_id: int) -> dict:
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        try:
                                                                             
            c.execute('''
                SELECT
                    t.ticket_id, t.issue_description, t.status,
                    t.created_at, t.completed_at,
                    t.service_charge, t.net_profit, t.advance_deposit,
                    t.customer_notified, t.notified_at,
                    c.full_name, c.phone_number, c.email,
                    d.device_brand, d.device_model, d.imei_serial,
                    u.user_id, u.username
                FROM Tickets t
                JOIN Devices d ON t.device_id = d.device_id
                JOIN Customers c ON d.customer_id = c.customer_id
                LEFT JOIN Users u ON t.assigned_tech_id = u.user_id
                WHERE t.ticket_id = ?
            ''', (ticket_raw_id,))
            row = c.fetchone()

            if not row:
                return {'status': 'error', 'message': f'Ticket {ticket_raw_id} not found.'}

            detail = {
                'raw_id':          row[0],
                'id':              f"TKT-{row[0]:04d}",
                'issue':           row[1] or "No description",
                'status':          row[2],
                'created':         row[3] or "—",
                'completed':       row[4] or "—",
                'charge':          float(row[5]) if row[5] else 0.0,
                'profit':          float(row[6]) if row[6] else 0.0,
                'deposit':         float(row[7]) if row[7] else 0.0,
                'notified':        bool(row[8]),
                'notified_at':     row[9] or "—",
                'customer_name':   row[10],
                'customer_phone':  row[11],
                'customer_email':  row[12] or "—",
                'device_brand':    row[13],
                'device_model':    row[14],
                'imei':            row[15] or "—",
                'tech_id':         row[16],
                'tech_username':   row[17] if row[17] else "Unassigned",
            }

                                                                             
            c.execute('''
                SELECT p.part_name, tp.actual_cost_at_time, tp.allocation_status, 'New Part'
                FROM Ticket_Parts tp
                JOIN Parts_Inventory p ON tp.part_id = p.part_id
                WHERE tp.ticket_id = ?
            ''', (ticket_raw_id,))
            new_parts = c.fetchall()

                                                                             
            c.execute('''
                SELECT comp.part_name, tp.actual_cost_at_time, tp.allocation_status,
                       'Donor (' || db.brand || ' ' || db.model || ')'
                FROM Ticket_Parts tp
                JOIN Components comp ON tp.donor_component_id = comp.component_id
                JOIN Donor_Boards db ON comp.board_id = db.board_id
                WHERE tp.ticket_id = ?
            ''', (ticket_raw_id,))
            donor_parts = c.fetchall()

            parts = []
            for r in new_parts + donor_parts:
                parts.append({
                    'name':   r[0],
                    'cost':   float(r[1]) if r[1] else 0.0,
                    'status': r[2],
                    'source': r[3],
                })
            detail['parts'] = parts
            
                                                                             
            c.execute('''
                SELECT al.timestamp, al.action_type, u.username, al.notes
                FROM AuditLogs al
                LEFT JOIN Users u ON al.user_id = u.user_id
                WHERE al.target_id = ?
                ORDER BY al.log_id DESC
                LIMIT 15
            ''', (f"TKT-{ticket_raw_id}",))
            logs = []
            for r in c.fetchall():
                logs.append({
                    'timestamp':   r[0] or "—",
                    'action':      r[1],
                    'performed_by': r[2] if r[2] else "System",
                    'notes':       r[3] or "—",
                })
            detail['audit_log'] = logs

            return {'status': 'success', 'data': detail}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
        finally:
            conn.close()

    def cancel_ticket(self, admin_id: int, ticket_raw_id: int) -> dict:
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        try:
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                                                                            
            c.execute(
                "SELECT ticket_id, status FROM Tickets WHERE ticket_id = ?",
                (ticket_raw_id,)
            )
            ticket_row = c.fetchone()
            if not ticket_row:
                return {'status': 'error', 'message': f'Ticket {ticket_raw_id} not found.'}

                                                                            
            c.execute(
                """SELECT tp.usage_id, p.part_name, tp.actual_cost_at_time, tp.quantity_used
                   FROM Ticket_Parts tp
                   JOIN Parts_Inventory p ON tp.part_id = p.part_id
                   WHERE tp.ticket_id = ? AND tp.allocation_status = 'Installed'""",
                (ticket_raw_id,)
            )
            installed_rows = c.fetchall()
            installed_loss = sum(
                float(r[2] or 0) * int(r[3] or 1) for r in installed_rows
            )

                                                                            
            c.execute(
                """SELECT usage_id, part_id, donor_component_id, quantity_used
                   FROM Ticket_Parts
                   WHERE ticket_id = ? AND allocation_status = 'Draft'""",
                (ticket_raw_id,)
            )
            draft_rows = c.fetchall()
            draft_released = len(draft_rows)

            for usage_id, part_id, donor_component_id, qty in draft_rows:
                if part_id is not None:
                    c.execute(
                        "UPDATE Parts_Inventory SET current_stock = current_stock + ? "
                        "WHERE part_id = ?",
                        (qty, part_id)
                    )
                    c.execute(
                        "SELECT part_name FROM Parts_Inventory WHERE part_id = ?", (part_id,)
                    )
                    prow = c.fetchone()
                    part_name = prow[0] if prow else f"Part #{part_id}"

                    c.execute(
                        "INSERT INTO AuditLogs "
                        "(user_id, action_type, target_id, timestamp, notes) "
                        "VALUES (?, ?, ?, ?, ?)",
                        (
                            admin_id,
                            'Draft Released',
                            f"TKT-{ticket_raw_id:04d}",
                            now,
                            f"Draft part '{part_name}' (usage #{usage_id}) returned to "
                            f"inventory (+{qty} unit(s)) on ticket cancellation.",
                        )
                    )
                elif donor_component_id is not None:
                    c.execute(
                        "UPDATE Components SET condition = 'Available', used_ticket_id = NULL "
                        "WHERE component_id = ?",
                        (donor_component_id,)
                    )
                    c.execute(
                        "SELECT part_name FROM Components WHERE component_id = ?", (donor_component_id,)
                    )
                    prow = c.fetchone()
                    part_name = prow[0] if prow else f"Part #{donor_component_id}"

                    c.execute(
                        "INSERT INTO AuditLogs "
                        "(user_id, action_type, target_id, timestamp, notes) "
                        "VALUES (?, ?, ?, ?, ?)",
                        (
                            admin_id,
                            'Draft Released',
                            f"TKT-{ticket_raw_id:04d}",
                            now,
                            f"Draft donor component '{part_name}' (usage #{usage_id}) returned to "
                            f"donor board on ticket cancellation.",
                        )
                    )

                                                                            
            if installed_rows:
                loss_detail = ", ".join(
                    f"{r[1]} (Rs.{float(r[2] or 0):.2f} x{int(r[3] or 1)})"
                    for r in installed_rows
                )
                c.execute(
                    "INSERT INTO AuditLogs "
                    "(user_id, action_type, target_id, timestamp, notes) "
                    "VALUES (?, ?, ?, ?, ?)",
                    (
                        admin_id,
                        'Installed Parts Loss',
                        f"TKT-{ticket_raw_id:04d}",
                        now,
                        f"Ticket cancelled with {len(installed_rows)} installed part(s) "
                        f"written off as loss. Net loss: -Rs.{installed_loss:.2f}. "
                        f"Parts: {loss_detail}",
                    )
                )

           
            c.execute(
                "UPDATE Tickets SET status = 'Cancelled' WHERE ticket_id = ?",
                (ticket_raw_id,)
            )
            
            c.execute("UPDATE Tickets SET assigned_tech_id = NULL WHERE ticket_id = ?",
                (ticket_raw_id,))

                                                                            
            parts_note = ""
            if draft_released:
                parts_note += f" {draft_released} draft part(s) returned to inventory."
            if installed_rows:
                parts_note += (
                    f" {len(installed_rows)} installed part(s) written off "
                    f"(loss: -Rs.{installed_loss:.2f})."
                )
            if not parts_note:
                parts_note = " No parts were allocated."

            c.execute(
                "INSERT INTO AuditLogs "
                "(user_id, action_type, target_id, timestamp, notes) "
                "VALUES (?, ?, ?, ?, ?)",
                (
                    admin_id,
                    'Ticket Cancelled',
                    f"TKT-{ticket_raw_id:04d}",
                    now,
                    f"Admin cancelled ticket TKT-{ticket_raw_id:04d}.{parts_note}",
                )
            )

            conn.commit()
            return {
                'status':          'success',
                'draft_released':  draft_released,
                'installed_loss':  installed_loss,
                'message': (
                    f"Ticket TKT-{ticket_raw_id:04d} has been Cancelled.{parts_note}"
                ),
            }

        except Exception as e:
            conn.rollback()
            return {'status': 'error', 'message': str(e)}
        finally:
            conn.close()

                                                
                                  
                                                

    def get_all_inventory(self, search_term: str = "", stock_filter: str = "all") -> dict:
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        try:
            query = '''
                SELECT
                    p.part_id,
                    p.part_name,
                    p.brand_compatibility,
                    p.unit_cost,
                    p.current_stock,
                    (p.current_stock - COALESCE((
                        SELECT SUM(tp.quantity_used) FROM Ticket_Parts tp
                        WHERE tp.part_id = p.part_id
                          AND tp.allocation_status IN ('Draft', 'Installed')
                    ), 0)) AS effective_stock
                FROM Parts_Inventory p
                WHERE 1=1
            '''
            params = []

            if search_term:
                query += " AND (p.part_name LIKE ? OR p.brand_compatibility LIKE ?)"
                term = f"%{search_term}%"
                params.extend([term, term])

            query += " ORDER BY effective_stock ASC, p.part_name ASC"

            c.execute(query, params)
            rows = c.fetchall()

            parts = []
            for r in rows:
                effective = r[5]
                                                                                      
                if stock_filter == "low" and effective >= 5:
                    continue
                if stock_filter == "out" and effective != 0:
                    continue

                parts.append({
                    'part_id':         r[0],
                    'part_name':       r[1],
                    'brand':           r[2] or "—",
                    'unit_cost':       float(r[3]) if r[3] else 0.0,
                    'current_stock':   r[4],
                    'effective_stock': effective,
                })
            return {'status': 'success', 'data': parts}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
        finally:
            conn.close()

    def add_new_part_type(self, admin_id: int, name: str, brand: str,
                          cost: float, initial_stock: int) -> dict:
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        try:
            c.execute(
                "INSERT INTO Parts_Inventory (part_name, brand_compatibility, unit_cost, current_stock) "
                "VALUES (?, ?, ?, ?)",
                (name.strip(), brand.strip(), cost, initial_stock)
            )
            new_id = c.lastrowid

            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            c.execute(
                "INSERT INTO AuditLogs (user_id, action_type, target_id, timestamp, notes) "
                "VALUES (?, ?, ?, ?, ?)",
                (admin_id, 'Inventory: New Part Added', new_id, now,
                 f"Admin added new part type: {name.strip()} with stock {initial_stock}")
            )
            conn.commit()
            return {'status': 'success', 'part_id': new_id}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
        finally:
            conn.close()

    def restock_existing_part(self, admin_id: int, part_id: int,
                              added_quantity: int, new_cost: float = None) -> dict:
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        try:
                                
            c.execute("SELECT part_name, current_stock, unit_cost FROM Parts_Inventory WHERE part_id = ?",
                      (part_id,))
            row = c.fetchone()
            if not row:
                return {'status': 'error', 'message': 'Part not found in inventory.'}

            part_name, old_stock, old_cost = row

                          
            c.execute(
                "UPDATE Parts_Inventory SET current_stock = current_stock + ? WHERE part_id = ?",
                (added_quantity, part_id)
            )

                                    
            cost_note = ""
            if new_cost is not None:
                c.execute(
                    "UPDATE Parts_Inventory SET unit_cost = ? WHERE part_id = ?",
                    (new_cost, part_id)
                )
                cost_note = f" | Unit cost updated: Rs.{old_cost:.2f} → Rs.{new_cost:.2f}"

            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            c.execute(
                "INSERT INTO AuditLogs (user_id, action_type, target_id, timestamp, notes) "
                "VALUES (?, ?, ?, ?, ?)",
                (admin_id, 'Inventory: Restocked', part_id, now,
                 f"Restocked '{part_name}': +{added_quantity} units (was {old_stock}){cost_note}")
            )
            conn.commit()
            return {'status': 'success'}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
        finally:
            conn.close()

                                                
                                    
                                                

    def get_alert_counts(self) -> dict:
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        try:
            c.execute("SELECT COUNT(*) FROM Parts_Inventory WHERE current_stock < 5")
            low_stock = c.fetchone()[0]

            c.execute("SELECT COUNT(*) FROM Components WHERE condition = 'Flagged_Review'")
            flagged = c.fetchone()[0]

            return {'status': 'success', 'low_stock': low_stock, 'flagged': flagged}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
        finally:
            conn.close()

    def get_low_stock_alerts(self) -> dict:
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        try:
            c.execute('''
                SELECT part_id, part_name, brand_compatibility, unit_cost, current_stock
                FROM Parts_Inventory
                WHERE current_stock < 5
                ORDER BY current_stock ASC, part_name ASC
            ''')
            rows = c.fetchall()

            parts = []
            for r in rows:
                parts.append({
                    'part_id':       r[0],
                    'part_name':     r[1],
                    'brand':         r[2] or "—",
                    'unit_cost':     float(r[3]) if r[3] else 0.0,
                    'current_stock': r[4],
                })
            return {'status': 'success', 'data': parts}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
        finally:
            conn.close()

    def get_flagged_components(self) -> dict:
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        try:
                                                    
            c.execute('''
                SELECT
                    comp.component_id,
                    comp.part_name,
                    db.brand,
                    db.model,
                    db.board_id
                FROM Components comp
                JOIN Donor_Boards db ON comp.board_id = db.board_id
                WHERE comp.condition = 'Flagged_Review'
                ORDER BY comp.component_id DESC
            ''')
            rows = c.fetchall()

            items = []
            for r in rows:
                comp_id = r[0]

                                                                                            
                c.execute('''
                    SELECT u.username, al.notes, al.timestamp
                    FROM AuditLogs al
                    LEFT JOIN Users u ON al.user_id = u.user_id
                    WHERE al.target_id = ? AND al.action_type = 'Part Flagged Damaged'
                    ORDER BY al.log_id DESC
                    LIMIT 1
                ''', (comp_id,))
                log = c.fetchone()

                items.append({
                    'component_id': comp_id,
                    'part_name':    r[1],
                    'board_brand':  r[2],
                    'board_model':  r[3],
                    'board_id':     r[4],
                    'flagged_by':   log[0] if log else "Unknown",
                    'tech_notes':   log[1] if log else "No notes",
                    'flagged_at':   log[2] if log else "—",
                })
            return {'status': 'success', 'data': items}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
        finally:
            conn.close()

    def resolve_flagged_component(self, admin_id: int, component_id: int,
                                   decision: str) -> dict:
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        try:
                                                            
            c.execute(
                "SELECT component_id, condition FROM Components WHERE component_id = ?",
                (component_id,)
            )
            row = c.fetchone()

            if not row:
                return {'status': 'error', 'message': 'Component not found.'}

            if row[1] != 'Flagged_Review':
                return {
                    'status': 'error',
                    'message': f'Component is not in Flagged_Review state (current: {row[1]}).'
                }

            if decision not in ('Damaged', 'Available'):
                return {'status': 'error', 'message': 'Invalid decision. Must be "Damaged" or "Available".'}

                                      
            c.execute(
                "UPDATE Components SET condition = ? WHERE component_id = ?",
                (decision, component_id)
            )

                               
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            if decision == 'Damaged':
                notes = f"Admin confirmed damage — component C-{component_id} permanently written off."
            else:
                notes = f"Admin restored component C-{component_id} to Available stock (false alarm)."

            c.execute(
                "INSERT INTO AuditLogs (user_id, action_type, target_id, timestamp, notes) "
                "VALUES (?, ?, ?, ?, ?)",
                (admin_id, 'Flag Resolved', component_id, now, notes)
            )
            conn.commit()

                                    
            if decision == 'Damaged':
                msg = 'Component confirmed as Damaged. Permanently locked from inventory.'
            else:
                msg = 'False alarm resolved. Component returned to Available stock.'

            return {'status': 'success', 'message': msg}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
        finally:
            conn.close()

                                                
                                           
                                                

    def get_model_template(self, brand: str, model: str) -> dict:
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        try:
            c.execute(
                "SELECT part_name, estimated_value FROM ModelTemplates "
                "WHERE LOWER(model) = LOWER(?) "
                "ORDER BY template_id ASC",
                (model.strip(),)
            )
            rows = c.fetchall()
            parts = [
                {'part_name': r[0],
                 'estimated_value': float(r[1]) if r[1] else 0.0,
                 'source': 'Template'}
                for r in rows
            ]
            return {'status': 'success', 'data': parts}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
        finally:
            conn.close()

    def add_part_to_template(self, brand: str, model: str,
                             part_name: str, estimated_value: float) -> dict:
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        try:
            c.execute(
                "INSERT OR IGNORE INTO ModelTemplates "
                "(brand, model, part_name, estimated_value) VALUES (?, ?, ?, ?)",
                (brand.strip(), model.strip(), part_name.strip(), estimated_value)
            )
            conn.commit()
            return {'status': 'success'}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
        finally:
            conn.close()

    def create_model_template(self, brand: str, model: str,
                              parts: list[dict]) -> dict:
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        try:
            added = 0
            for p in parts:
                c.execute(
                    "INSERT OR IGNORE INTO ModelTemplates "
                    "(brand, model, part_name, estimated_value) VALUES (?, ?, ?, ?)",
                    (brand.strip(), model.strip(),
                     p['part_name'].strip(), float(p.get('estimated_value', 0)))
                )
                added += c.rowcount
            conn.commit()
            return {'status': 'success', 'rows_added': added}
        except Exception as e:
            conn.rollback()
            return {'status': 'error', 'message': str(e)}
        finally:
            conn.close()

    def register_donor_board(self, admin_id: int, brand: str, model: str,
                             serial_number: str, acquisition_cost: float,
                             selected_components: list[dict]) -> dict:
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        try:
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                                                                         
            c.execute(
                """INSERT INTO Donor_Boards
                       (brand, model, serial_number, status, acquisition_cost)
                   VALUES (?, ?, ?, 'Active', ?)""",
                (brand.strip(), model.strip(), serial_number.strip(), acquisition_cost)
            )
            board_id = c.lastrowid

                                                                          
            for comp in selected_components:
                c.execute(
                    """INSERT INTO Components
                           (board_id, part_name, condition, harvested_date)
                       VALUES (?, ?, 'Available', ?)""",
                    (board_id, comp['part_name'].strip(), now)
                )

            comp_count = len(selected_components)

                                                                           
            c.execute(
                "INSERT INTO AuditLogs "
                "(user_id, action_type, target_id, timestamp, notes) "
                "VALUES (?, ?, ?, ?, ?)",
                (
                    admin_id,
                    'Donor Board Registered',
                    board_id,
                    now,
                    (
                        f"Registered donor board DB-{board_id:04d}: "
                        f"{brand} {model} (S/N: {serial_number}), "
                        f"cost Rs.{acquisition_cost:.2f}, "
                        f"{comp_count} component(s) added."
                    )
                )
            )

                                                                           
            conn.commit()
            return {
                'status': 'success',
                'board_id': board_id,
                'components_added': comp_count,
            }

        except Exception as e:
            conn.rollback()
            return {'status': 'error', 'message': str(e)}
        finally:
            conn.close()

                                                
                                 
                                                

    def get_financial_summary(self, start_date: str, end_date: str) -> dict:
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        try:
                                                                    
            c.execute('''
                SELECT
                    t.ticket_id,
                    c.full_name,
                    d.device_brand || ' ' || d.device_model AS device,
                    t.completed_at,
                    COALESCE(t.service_charge, 0.0)   AS service_charge,
                    COALESCE(t.advance_deposit, 0.0)  AS deposit,
                    COALESCE(t.net_profit, 0.0)       AS net_profit,
                    COALESCE((
                        SELECT SUM(tp.actual_cost_at_time)
                        FROM Ticket_Parts tp
                        WHERE tp.ticket_id = t.ticket_id
                          AND tp.allocation_status = 'Confirmed'
                    ), 0.0) AS parts_cost
                FROM Tickets t
                JOIN Devices d   ON t.device_id   = d.device_id
                JOIN Customers c ON d.customer_id = c.customer_id
                WHERE t.status = 'Completed'
                  AND DATE(t.completed_at) >= DATE(?)
                  AND DATE(t.completed_at) <= DATE(?)
                ORDER BY t.completed_at DESC
            ''', (start_date, end_date))
            rows = c.fetchall()

            result_rows = []
            total_revenue   = 0.0
            total_parts     = 0.0
            total_profit    = 0.0
            total_deposits  = 0.0

            for r in rows:
                service_charge = float(r[4])
                deposit        = float(r[5])
                net_profit     = float(r[6])
                parts_cost     = float(r[7])

                total_revenue  += service_charge
                total_parts    += parts_cost
                total_profit   += net_profit
                total_deposits += deposit

                result_rows.append({
                    'ticket_id':     f"TKT-{r[0]:04d}",
                    'customer':      r[1],
                    'device':        r[2],
                    'completed_at':  r[3][:10] if r[3] else '—',
                    'service_charge': service_charge,
                    'parts_cost':    parts_cost,
                    'net_profit':    net_profit,
                    'deposit':       deposit,
                })

            return {
                'status': 'success',
                'summary': {
                    'total_revenue':  total_revenue,
                    'total_parts':    total_parts,
                    'total_profit':   total_profit,
                    'total_deposits': total_deposits,
                    'ticket_count':   len(result_rows),
                },
                'rows': result_rows,
            }
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
        finally:
            conn.close()

    def get_donor_board_roi(self) -> dict:
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        try:
            c.execute('''
                SELECT
                    db.board_id,
                    db.brand,
                    db.model,
                    db.serial_number,
                    db.status,
                    COALESCE(db.acquisition_cost, 0.0) AS acq_cost,
                    -- Sum estimated_value from ModelTemplates for each component condition
                    COALESCE((
                        SELECT SUM(mt.estimated_value)
                        FROM Components comp
                        JOIN ModelTemplates mt
                          ON LOWER(mt.model)     = LOWER(db.model)
                         AND LOWER(mt.part_name) = LOWER(comp.part_name)
                        WHERE comp.board_id  = db.board_id
                          AND comp.condition = 'Available'
                    ), 0.0) AS val_available,
                    COALESCE((
                        SELECT SUM(mt.estimated_value)
                        FROM Components comp
                        JOIN ModelTemplates mt
                          ON LOWER(mt.model)     = LOWER(db.model)
                         AND LOWER(mt.part_name) = LOWER(comp.part_name)
                        WHERE comp.board_id  = db.board_id
                          AND comp.condition IN ('Harvested', 'Confirmed')
                    ), 0.0) AS val_used,
                    COALESCE((
                        SELECT COUNT(*)
                        FROM Components comp
                        WHERE comp.board_id  = db.board_id
                          AND comp.condition = 'Damaged'
                    ), 0) AS damaged_count,
                    db.brand || ' ' || db.model AS display_name
                FROM Donor_Boards db
                ORDER BY db.board_id DESC
            ''')
            rows = c.fetchall()

            result = []
            total_invested  = 0.0
            total_recovered = 0.0

            for r in rows:
                acq      = float(r[5])
                avail    = float(r[6])
                used     = float(r[7])
                dmg      = int(r[8])
                total_sv = avail + used
                roi      = ((total_sv - acq) / acq * 100) if acq > 0 else 0.0

                total_invested  += acq
                total_recovered += total_sv

                result.append({
                    'board_id':    f"DB-{r[0]:04d}",
                    'brand':       r[1],
                    'model':       r[2],
                    'serial':      r[3],
                    'board_status': r[4],
                    'acq_cost':    acq,
                    'val_available': avail,
                    'val_used':    used,
                    'total_sv':    total_sv,
                    'damaged_count': dmg,
                    'roi_percent': roi,
                })

            overall_roi = ((total_recovered - total_invested) / total_invested * 100)\
                          if total_invested > 0 else 0.0

            return {
                'status': 'success',
                'rows': result,
                'summary': {
                    'total_invested':  total_invested,
                    'total_recovered': total_recovered,
                    'overall_roi':     overall_roi,
                    'board_count':     len(result),
                }
            }
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
        finally:
            conn.close()

    def get_low_stock_report(self, threshold: int = 5) -> dict:
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        try:
            c.execute('''
                SELECT part_id, part_name, brand_compatibility, unit_cost, current_stock
                FROM Parts_Inventory
                WHERE current_stock <= ?
                ORDER BY current_stock ASC, part_name ASC
            ''', (threshold,))
            rows = c.fetchall()

            parts = []
            total_restock_cost = 0.0
            for r in rows:
                suggested_qty = max(10 - r[4], 1)
                restock_cost  = suggested_qty * float(r[3])
                total_restock_cost += restock_cost
                parts.append({
                    'part_id':      f"P-{r[0]:04d}",
                    'part_name':    r[1],
                    'brand':        r[2] or '—',
                    'unit_cost':    float(r[3]),
                    'current_stock': r[4],
                    'suggested_qty': suggested_qty,
                    'restock_cost':  restock_cost,
                })
            return {
                'status': 'success',
                'rows': parts,
                'summary': {
                    'part_count':        len(parts),
                    'total_restock_cost': total_restock_cost,
                    'threshold':         threshold,
                }
            }
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
        finally:
            conn.close()

    def get_inventory_valuation(self) -> dict:
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        try:
                       
            c.execute('''
                SELECT part_id, part_name, brand_compatibility,
                       unit_cost, current_stock,
                       (unit_cost * current_stock) AS line_value
                FROM Parts_Inventory
                ORDER BY line_value DESC
            ''')
            new_parts = c.fetchall()

            new_rows  = []
            new_total = 0.0
            for r in new_parts:
                lv = float(r[5])
                new_total += lv
                new_rows.append({
                    'part_id':   f"P-{r[0]:04d}",
                    'name':      r[1],
                    'brand':     r[2] or '—',
                    'unit_cost': float(r[3]),
                    'stock':     r[4],
                    'value':     lv,
                })

                                                                     
            c.execute('''
                SELECT
                    comp.component_id,
                    comp.part_name,
                    db.brand,
                    db.model,
                    COALESCE(mt.estimated_value, 0.0) AS est_val
                FROM Components comp
                JOIN Donor_Boards db ON comp.board_id = db.board_id
                LEFT JOIN ModelTemplates mt
                  ON LOWER(mt.model)     = LOWER(db.model)
                 AND LOWER(mt.part_name) = LOWER(comp.part_name)
                WHERE comp.condition = 'Available'
                ORDER BY est_val DESC
            ''')
            donor_parts = c.fetchall()

            donor_rows  = []
            donor_total = 0.0
            for r in donor_parts:
                ev = float(r[4])
                donor_total += ev
                donor_rows.append({
                    'component_id': f"C-{r[0]:04d}",
                    'name':         r[1],
                    'brand':        r[2],
                    'model':        r[3],
                    'est_value':    ev,
                })

            return {
                'status': 'success',
                'new_parts': {
                    'rows':  new_rows,
                    'total': new_total,
                    'count': len(new_rows),
                },
                'donor_parts': {
                    'rows':  donor_rows,
                    'total': donor_total,
                    'count': len(donor_rows),
                },
                'grand_total': new_total + donor_total,
            }
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
        finally:
            conn.close()

    def get_quality_control_report(self) -> dict:
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        try:
            c.execute('''
                SELECT
                    comp.component_id,
                    comp.part_name,
                    db.brand,
                    db.model,
                    COALESCE(mt.estimated_value, 0.0) AS est_val,
                    -- Who flagged it
                    (SELECT u.username FROM AuditLogs al JOIN Users u ON al.user_id = u.user_id
                     WHERE al.target_id = comp.component_id AND al.action_type = 'Part Flagged Damaged'
                     ORDER BY al.log_id DESC LIMIT 1) AS flagged_by,
                    -- Who resolved it
                    (SELECT u.username FROM AuditLogs al JOIN Users u ON al.user_id = u.user_id
                     WHERE al.target_id = comp.component_id AND al.action_type = 'Flag Resolved'
                     ORDER BY al.log_id DESC LIMIT 1) AS resolved_by,
                    -- When it was resolved
                    (SELECT al.timestamp FROM AuditLogs al
                     WHERE al.target_id = comp.component_id AND al.action_type = 'Flag Resolved'
                     ORDER BY al.log_id DESC LIMIT 1) AS resolved_at
                FROM Components comp
                JOIN Donor_Boards db ON comp.board_id = db.board_id
                LEFT JOIN ModelTemplates mt
                  ON LOWER(mt.model)     = LOWER(db.model)
                 AND LOWER(mt.part_name) = LOWER(comp.part_name)
                WHERE comp.condition = 'Damaged'
                ORDER BY comp.component_id DESC
            ''')
            rows = c.fetchall()

            result  = []
            total_loss = 0.0
            for r in rows:
                ev = float(r[4])
                total_loss += ev
                result.append({
                    'component_id': f"C-{r[0]:04d}",
                    'part_name':    r[1],
                    'brand':        r[2],
                    'model':        r[3],
                    'est_value':    ev,
                    'flagged_by':   r[5] or 'Unknown',
                    'resolved_by':  r[6] or 'Unknown',
                    'resolved_at':  (r[7] or '—')[:10],
                })

            return {
                'status': 'success',
                'rows': result,
                'summary': {
                    'damaged_count': len(result),
                    'total_loss':    total_loss,
                }
            }
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
        finally:
            conn.close()

    def get_technician_performance(self, start_date: str, end_date: str) -> dict:
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        try:
            c.execute('''
                SELECT
                    u.user_id,
                    u.username,
                    COUNT(DISTINCT t.ticket_id)                              AS assigned,
                    COUNT(DISTINCT CASE WHEN t.status = 'Completed'
                                        AND DATE(t.completed_at) BETWEEN DATE(?) AND DATE(?)
                                   THEN t.ticket_id END)                     AS completed,
                    COALESCE(AVG(
                        CASE WHEN t.status = 'Completed'
                              AND DATE(t.completed_at) BETWEEN DATE(?) AND DATE(?)
                        THEN (JULIANDAY(t.completed_at) - JULIANDAY(t.created_at)) * 24
                        END
                    ), 0.0) AS avg_hrs,
                    COALESCE(SUM(
                        CASE WHEN t.status = 'Completed'
                              AND DATE(t.completed_at) BETWEEN DATE(?) AND DATE(?)
                        THEN t.service_charge ELSE 0 END
                    ), 0.0) AS revenue
                FROM Users u
                LEFT JOIN Tickets t ON t.assigned_tech_id = u.user_id
                WHERE u.role = 'technician'
                GROUP BY u.user_id, u.username
                ORDER BY completed DESC
            ''', (start_date, end_date,
                  start_date, end_date,
                  start_date, end_date))
            rows = c.fetchall()

            result = []
            for r in rows:
                result.append({
                    'user_id':   r[0],
                    'username':  r[1],
                    'assigned':  r[2],
                    'completed': r[3],
                    'avg_hrs':   round(float(r[4]), 1),
                    'revenue':   float(r[5]),
                })

            return {'status': 'success', 'rows': result}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
        finally:
            conn.close()

    def get_ticket_pipeline(self) -> dict:
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        try:
            c.execute('''
                SELECT status, COUNT(*) AS cnt
                FROM Tickets
                WHERE status != 'Completed'
                GROUP BY status
            ''')
            rows = c.fetchall()
            pipeline = {r[0]: r[1] for r in rows}

                                                      
            c.execute('''
                SELECT COUNT(*) FROM Tickets
                WHERE status = 'Completed' AND customer_notified = 0
            ''')
            awaiting_pickup = c.fetchone()[0]

                                          
            c.execute("SELECT COUNT(*) FROM Tickets WHERE status != 'Completed'")
            total_active = c.fetchone()[0]

            c.execute("SELECT COUNT(*) FROM Tickets WHERE status = 'Completed'")
            total_completed = c.fetchone()[0]

            return {
                'status': 'success',
                'pipeline': pipeline,
                'awaiting_pickup': awaiting_pickup,
                'total_active': total_active,
                'total_completed': total_completed,
            }
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
        finally:
            conn.close()

    def get_device_trends(self, months: int = 6) -> dict:
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        try:
            cutoff = f"date('now', '-{months} months')"

                               
            c.execute(f'''
                SELECT d.device_brand || ' ' || d.device_model AS device, COUNT(*) AS cnt
                FROM Tickets t
                JOIN Devices d ON t.device_id = d.device_id
                WHERE DATE(t.created_at) >= {cutoff}
                GROUP BY device
                ORDER BY cnt DESC
                LIMIT 10
            ''')
            device_rows = [{'device': r[0], 'count': r[1]} for r in c.fetchall()]

                                                           
            c.execute(f'''
                SELECT p.part_name, COUNT(*) AS cnt
                FROM Ticket_Parts tp
                JOIN Parts_Inventory p ON tp.part_id = p.part_id
                JOIN Tickets t ON tp.ticket_id = t.ticket_id
                WHERE tp.allocation_status = 'Confirmed'
                  AND DATE(t.completed_at) >= {cutoff}
                GROUP BY p.part_name
                ORDER BY cnt DESC
                LIMIT 10
            ''')
            parts_rows = [{'part': r[0], 'count': r[1]} for r in c.fetchall()]

                                   
            c.execute(f'''
                SELECT comp.part_name, COUNT(*) AS cnt
                FROM Ticket_Parts tp
                JOIN Components comp ON tp.donor_component_id = comp.component_id
                JOIN Tickets t ON tp.ticket_id = t.ticket_id
                WHERE tp.allocation_status = 'Confirmed'
                  AND DATE(t.completed_at) >= {cutoff}
                GROUP BY comp.part_name
                ORDER BY cnt DESC
                LIMIT 10
            ''')
            donor_used = [{'part': r[0], 'count': r[1]} for r in c.fetchall()]

            return {
                'status': 'success',
                'device_trends': device_rows,
                'top_parts': parts_rows,
                'top_donor_parts': donor_used,
                'months': months,
            }
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
        finally:
            conn.close()        