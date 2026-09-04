from datetime import datetime
import sqlite3

class TechAPI:
    def __init__(self, db_path: str):
        self.db_path = db_path
        
        
    def get_intake_pool(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        query = '''
            SELECT 
                t.ticket_id, d.device_brand || ' ' || d.device_model, 
                t.issue_description, t.created_at
            FROM Tickets t
            JOIN Devices d ON t.device_id = d.device_id
            WHERE t.assigned_tech_id IS NULL AND t.status = 'Intake'
            ORDER BY t.ticket_id ASC
        '''
        c.execute(query)
        rows = c.fetchall()
        conn.close()
        
        tickets = []
        for r in rows:
            tickets.append({
                'raw_id': r[0],
                'id': f"TKT-{r[0]:04d}",
                'device': r[1],
                'issue': r[2],
                'created': r[3]
            })
        return {'status': 'success', 'data': tickets}
    
    
    def accept_ticket(self, tech_id, ticket_raw_id):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        try:
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            c.execute("UPDATE Tickets SET assigned_tech_id = ? WHERE ticket_id = ?", (tech_id, ticket_raw_id))
            
            c.execute("INSERT INTO AuditLogs (user_id, action_type, target_id, timestamp, notes) VALUES (?, ?, ?, ?, ?)",
                      (tech_id, 'Ticket Accepted', f"TKT-{ticket_raw_id}", now, "Technician accepted ticket from Intake Pool"))
            conn.commit()
            return {'status': 'success'}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
        finally:
            conn.close()        
            
            
    def get_my_tickets(self, tech_id):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
                                                                
        query = '''
            SELECT 
                t.ticket_id, d.device_brand || ' ' || d.device_model, 
                t.status, t.created_at, t.issue_description
            FROM Tickets t
            JOIN Devices d ON t.device_id = d.device_id
            WHERE t.assigned_tech_id = ?
            ORDER BY t.ticket_id DESC
        '''
        c.execute(query, (tech_id,))
        rows = c.fetchall()
        conn.close()
        
        tickets = []
        for r in rows:
            tickets.append({
                'raw_id': r[0],
                'id': f"TKT-{r[0]:04d}",
                'device': r[1],
                'status': r[2],
                'created': r[3],
                'issue': r[4]                                    
            })
        return {'status': 'success', 'data': tickets}
              
    def search_new_inventory(self, search_term=""):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
                                                                                                  
        query = '''
            SELECT 
                p.part_id, p.part_name, p.brand_compatibility, p.unit_cost,
                (p.current_stock - COALESCE((
                    SELECT SUM(quantity_used) FROM Ticket_Parts tp 
                    WHERE tp.part_id = p.part_id AND tp.allocation_status IN ('Draft', 'Installed')
                ), 0)) as effective_stock
            FROM Parts_Inventory p
            WHERE effective_stock > 0
        '''
        params = ()
        
        if search_term:
            query += " AND (p.part_name LIKE ? OR p.brand_compatibility LIKE ?)"
            term = f"%{search_term}%"
            params = (term, term)
            
        c.execute(query, params)
        rows = c.fetchall()
        conn.close()
        
        parts = []
        for r in rows:
            parts.append({
                'id': r[0],
                'name': r[1],
                'compatibility': r[2],
                'cost': float(r[3]),
                'stock': r[4]                                  
            })
        return {'status': 'success', 'data': parts}

    def search_donor_inventory(self, search_term=""):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
                                                                           
        query = '''
            SELECT 
                c.component_id, c.part_name, b.brand, b.model, b.serial_number
            FROM Components c
            JOIN Donor_Boards b ON c.board_id = b.board_id
            WHERE c.condition = 'Available'
        '''
        params = ()
        
        if search_term:
            query += " AND (c.part_name LIKE ? OR b.brand LIKE ? OR b.model LIKE ?)"
            term = f"%{search_term}%"
            params = (term, term, term)
            
        c.execute(query, params)
        rows = c.fetchall()
        conn.close()
        
        parts = []
        for r in rows:
            parts.append({
                'id': r[0],
                'name': r[1],
                'source_brand': r[2],
                'source_model': r[3],
                'source_serial': r[4]
            })
        return {'status': 'success', 'data': parts}

    def allocate_draft_parts(self, tech_id, ticket_raw_id, parts_data):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        try:
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            for part in parts_data:
                if part['type'] == 'new':
                                                                             
                    c.execute('''
                        SELECT (current_stock - COALESCE((
                            SELECT SUM(quantity_used) FROM Ticket_Parts 
                            WHERE part_id = ? AND allocation_status IN ('Draft', 'Installed')
                        ), 0))
                        FROM Parts_Inventory WHERE part_id = ?
                    ''', (part['id'], part['id']))
                    
                    effective_stock = c.fetchone()[0]
                    
                    if effective_stock < 1:
                        conn.close()
                        return {'status': 'error', 'message': 'Part is out of stock (remaining units are drafted to other tickets).'}

                                                     
                    c.execute("SELECT unit_cost FROM Parts_Inventory WHERE part_id=?", (part['id'],))
                    cost = c.fetchone()[0]
                    
                    c.execute('''INSERT INTO Ticket_Parts (ticket_id, part_id, quantity_used, actual_cost_at_time, allocation_status) 
                                 VALUES (?, ?, 1, ?, 'Draft')''', (ticket_raw_id, part['id'], cost))
                    
                elif part['type'] == 'donor':
                                                                 
                    c.execute("SELECT condition FROM Components WHERE component_id=?", (part['id'],))
                    comp_row = c.fetchone()
                    if not comp_row or comp_row[0] != 'Available':
                        conn.close()
                        return {'status': 'error', 'message': 'This donor part is no longer available.'}

                                                                        
                    c.execute('''INSERT INTO Ticket_Parts (ticket_id, donor_component_id, quantity_used, actual_cost_at_time, allocation_status) 
                                 VALUES (?, ?, 1, 0.0, 'Draft')''', (ticket_raw_id, part['id']))
                    
                                                                                                     
                    c.execute('''UPDATE Components SET condition='Drafted', used_ticket_id=?, harvested_date=? 
                                 WHERE component_id=?''', (ticket_raw_id, now, part['id']))
                                                  
                                                                                  
            c.execute("UPDATE Tickets SET status = 'In-Progress' WHERE ticket_id = ?", (ticket_raw_id,))
            
                            
            c.execute("INSERT INTO AuditLogs (user_id, action_type, target_id, timestamp, notes) VALUES (?, ?, ?, ?, ?)",
                      (tech_id, 'Parts Allocated', f"TKT-{ticket_raw_id}", now, "Draft parts allocated. Ticket moved to In-Progress."))
            
            conn.commit()
            return {'status': 'success'}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
        finally:
            conn.close()

    
    def get_ticket_parts(self, ticket_raw_id):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
                        
        c.execute('''
            SELECT tp.usage_id, 'new', p.part_name, tp.actual_cost_at_time, tp.allocation_status 
            FROM Ticket_Parts tp
            JOIN Parts_Inventory p ON tp.part_id = p.part_id
            WHERE tp.ticket_id = ?
        ''', (ticket_raw_id,))
        new_parts = c.fetchall()
        
                          
        c.execute('''
            SELECT tp.usage_id, 'donor', comp.part_name, tp.actual_cost_at_time, tp.allocation_status 
            FROM Ticket_Parts tp
            JOIN Components comp ON tp.donor_component_id = comp.component_id
            WHERE tp.ticket_id = ?
        ''', (ticket_raw_id,))
        donor_parts = c.fetchall()
        conn.close()
        
        parts = []
        for r in new_parts + donor_parts:
            parts.append({
                'usage_id': r[0],
                'type': r[1],
                'name': r[2],
                'cost': float(r[3]),
                'status': r[4]
            })
            
        return {'status': 'success', 'data': parts}

    def remove_ticket_part(self, user_id, usage_id):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        try:
            c.execute("SELECT ticket_id, donor_component_id FROM Ticket_Parts WHERE usage_id=?", (usage_id,))
            row = c.fetchone()
            if not row: 
                return {'status': 'error', 'message': 'Part not found'}
            
            ticket_id, donor_id = row
            
                                                                           
            if donor_id:
                c.execute("UPDATE Components SET condition='Available', used_ticket_id=NULL, harvested_date=NULL WHERE component_id=?", (donor_id,))
                
            c.execute("DELETE FROM Ticket_Parts WHERE usage_id=?", (usage_id,))
            
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            c.execute("INSERT INTO AuditLogs (user_id, action_type, target_id, timestamp, notes) VALUES (?, ?, ?, ?, ?)",
                      (user_id, 'Draft Removed', f"TKT-{ticket_id}", now, "Removed part from ticket"))
            conn.commit()
            return {'status': 'success'}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
        finally:
            conn.close()        
            
            
    def flag_donor_part(self, tech_id, component_id, notes):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        try:
                                                                             
            c.execute(
                "SELECT component_id, condition FROM Components WHERE component_id = ?",
                (component_id,)
            )
            component = c.fetchone()

                                                                             
            if not component:
                return {'status': 'error', 'message': 'Error: Component not found on this board.'}

            comp_id, current_condition = component

                                                                             
            if current_condition != 'Available':
                return {
                    'status': 'error',
                    'message': (
                        f'Error: Part condition is "{current_condition}". '
                        'Only Available parts can be flagged.'
                    )
                }

                                                                             
            c.execute(
                "UPDATE Components SET condition = 'Flagged_Review' WHERE component_id = ?",
                (comp_id,)
            )

                                                                             
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            c.execute(
                "INSERT INTO AuditLogs "
                "(user_id, action_type, target_id, timestamp, notes) "
                "VALUES (?, ?, ?, ?, ?)",
                (tech_id, 'Part Flagged Damaged', f"COMP-{comp_id}", now, notes)
            )
            conn.commit()

                                                                             
            return {
                'status': 'success',
                'message': 'Alert Sent: Part flagged for Admin review. Please return the board to the Admin desk.'
            }
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
        finally:
            conn.close()

    def mark_part_installed(self, tech_id, usage_id):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        try:
            c.execute("UPDATE Ticket_Parts SET allocation_status = 'Installed' WHERE usage_id = ?", (usage_id,))
            
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            c.execute("INSERT INTO AuditLogs (user_id, action_type, target_id, timestamp, notes) VALUES (?, ?, ?, ?, ?)",
                      (tech_id, 'Part Installed', f"USAGE-{usage_id}", now, "Part permanently consumed/soldered to device"))
            conn.commit()
            return {'status': 'success'}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
        finally:
            conn.close()
    
    def complete_ticket(self, tech_id, ticket_raw_id, service_charge):
        conn = sqlite3.connect('repair_erp.db')
        c = conn.cursor()
        try:
                                                                                        
            c.execute("SELECT usage_id, part_id, donor_component_id, actual_cost_at_time FROM Ticket_Parts WHERE ticket_id = ? AND allocation_status IN ('Draft', 'Installed')", (ticket_raw_id,))
            parts = c.fetchall()
            
            
            total_parts_cost = 0.00
            
            for part in parts:
                usage_id, new_part_id, donor_id, cost = part
                total_parts_cost += float(cost)
                
                                                                            
                if new_part_id:
                    c.execute("UPDATE Parts_Inventory SET current_stock = current_stock - 1 WHERE part_id = ?", (new_part_id,))
                
                                                   
                c.execute("UPDATE Ticket_Parts SET allocation_status = 'Confirmed' WHERE usage_id = ?", (usage_id,))

                                                                         
                if donor_id:
                    c.execute("SELECT board_id FROM Components WHERE component_id = ?", (donor_id,))
                    board_row = c.fetchone()
                    if board_row:
                        board_id = board_row[0]
                                                                                           
                        c.execute("SELECT COUNT(*) FROM Components WHERE board_id = ? AND condition = 'Available'", (board_id,))
                        available_count = c.fetchone()[0]
                        if available_count == 0:
                                                                                   
                            c.execute("UPDATE Donor_Boards SET status = 'Depleted' WHERE board_id = ?", (board_id,))

                                                       
            net_profit = float(service_charge) - total_parts_cost
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            c.execute('''UPDATE Tickets 
                         SET status = 'Completed', service_charge = ?, net_profit = ?, completed_at = ? 
                         WHERE ticket_id = ?''', (service_charge, net_profit, now, ticket_raw_id))
            
            c.execute("INSERT INTO AuditLogs (user_id, action_type, target_id, timestamp, notes) VALUES (?, ?, ?, ?, ?)",
                      (tech_id, 'Ticket Completed', f"TKT-{ticket_raw_id}", now, f"Repair finalized. Profit: Rs.{net_profit}"))
            conn.commit()
            return {'status': 'success'}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
        finally:
            conn.close()
