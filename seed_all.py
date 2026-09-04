
import sqlite3
import hashlib
from datetime import datetime, timedelta

DB_PATH = "repair_erp.db"

                                                                               
          
                                                                               

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def divider(title: str = ""):
    line = "=" * 62
    if title:
        print(f"\n{line}")
        print(f"  {title}")
        print(line)
    else:
        print(line)

                                                                               
                                                                            
                                                                               

def create_tables(c):
    c.executescript("""
        CREATE TABLE IF NOT EXISTS Users (
            user_id       INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            username      TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role          TEXT NOT NULL,
            is_active     BOOLEAN DEFAULT TRUE NOT NULL);

        CREATE TABLE IF NOT EXISTS AuditLogs (
            log_id      INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            user_id     INTEGER,
            action_type TEXT,
            target_id   TEXT,
            timestamp   DATETIME,
            notes       TEXT);

        CREATE TABLE IF NOT EXISTS Customers (
            customer_id  INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name    TEXT,
            phone_number TEXT UNIQUE,
            email        TEXT);

        CREATE TABLE IF NOT EXISTS Devices (
            device_id    INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id  INTEGER,
            imei_serial  TEXT UNIQUE,
            device_brand TEXT,
            device_model TEXT,
            FOREIGN KEY(customer_id) REFERENCES Customers(customer_id));

        CREATE TABLE IF NOT EXISTS Tickets (
            ticket_id         INTEGER PRIMARY KEY AUTOINCREMENT,
            device_id         INTEGER,
            assigned_tech_id  INTEGER,
            issue_description TEXT,
            status            TEXT,
            created_at        DATETIME,
            completed_at      DATETIME,
            service_charge    DECIMAL,
            net_profit        DECIMAL,
            advance_deposit   DECIMAL,
            customer_notified BOOLEAN DEFAULT 0,
            notified_at       DATETIME,
            FOREIGN KEY(device_id)        REFERENCES Devices(device_id),
            FOREIGN KEY(assigned_tech_id) REFERENCES Users(user_id));

        CREATE TABLE IF NOT EXISTS Parts_Inventory (
            part_id            INTEGER PRIMARY KEY AUTOINCREMENT,
            part_name          TEXT,
            brand_compatibility TEXT,
            unit_cost          DECIMAL,
            current_stock      INTEGER);

        CREATE TABLE IF NOT EXISTS Donor_Boards (
            board_id         INTEGER PRIMARY KEY AUTOINCREMENT,
            brand            TEXT,
            model            TEXT,
            serial_number    TEXT,
            status           TEXT,
            acquisition_cost DECIMAL);

        CREATE TABLE IF NOT EXISTS Components (
            component_id  INTEGER PRIMARY KEY AUTOINCREMENT,
            board_id      INTEGER,
            used_ticket_id INTEGER,
            part_name     TEXT,
            condition     TEXT DEFAULT 'Available',
            harvested_date DATETIME,
            FOREIGN KEY(board_id)       REFERENCES Donor_Boards(board_id),
            FOREIGN KEY(used_ticket_id) REFERENCES Tickets(ticket_id));

        CREATE TABLE IF NOT EXISTS Ticket_Parts (
            usage_id              INTEGER PRIMARY KEY AUTOINCREMENT,
            ticket_id             INTEGER,
            part_id               INTEGER,
            donor_component_id    INTEGER,
            quantity_used         INTEGER,
            actual_cost_at_time   DECIMAL,
            allocation_status     TEXT DEFAULT 'Draft',
            FOREIGN KEY(ticket_id)          REFERENCES Tickets(ticket_id),
            FOREIGN KEY(part_id)            REFERENCES Parts_Inventory(part_id),
            FOREIGN KEY(donor_component_id) REFERENCES Components(component_id));

        CREATE TABLE IF NOT EXISTS ModelTemplates (
            template_id     INTEGER PRIMARY KEY AUTOINCREMENT,
            brand           TEXT NOT NULL,
            model           TEXT NOT NULL,
            part_name       TEXT NOT NULL,
            estimated_value DECIMAL DEFAULT 0,
            UNIQUE(model, part_name));
    """)

                                                                               
                                                        
                                                                               

def seed_users(c, conn):
    print("\n[1/9] Seeding Users ...")
    rows = [
        ("admin",  hash_password("admin"),  "admin",      True),
        ("admin1", hash_password("admin1"), "admin",      True),
        ("tec",    hash_password("tec"),    "technician", True),
        ("tec1",   hash_password("tec1"),   "technician", True),
        ("help",   hash_password("help"),   "helpdesk",   True),
        ("help1",  hash_password("help1"),  "helpdesk",   True),
    ]
    for u in rows:
        try:
            c.execute(
                "INSERT INTO Users (username, password_hash, role, is_active) VALUES (?,?,?,?)", u
            )
            print(f"  + User '{u[0]}' ({u[2]}) created.")
        except sqlite3.IntegrityError:
            print(f"  ~ User '{u[0]}' already exists — skipped.")
    conn.commit()

                                                                               
                                      
                                                                               

def seed_customers(c, conn):
    print("\n[2/9] Seeding Customers ...")
    customers = [
        ("Amal Perera",       "0711234567", "amal.perera@email.com"),
        ("Nimal Silva",       "0722345678", "nimal.silva@email.com"),
        ("Kamani Fernando",   "0733456789", "kamani.f@email.com"),
        ("Ruwan Jayasena",    "0744567890", "ruwan.j@email.com"),
        ("Dilini Wickrama",   "0755678901", "dilini.w@email.com"),
        ("Kasun Bandara",     "0766789012", "kasun.b@email.com"),
        ("Thilini Rajapaksa", "0777890123", "thilini.r@email.com"),
        ("Saman Kumara",      "0788901234", "saman.k@email.com"),
        ("Malini Dissanayake","0799012345", "malini.d@email.com"),
        ("Pradeep Herath",    "0700123456", "pradeep.h@email.com"),
    ]
    customer_ids = []
    for cust in customers:
        try:
            c.execute(
                "INSERT INTO Customers (full_name, phone_number, email) VALUES (?,?,?)", cust
            )
            customer_ids.append(c.lastrowid)
            print(f"  + Customer '{cust[0]}' inserted.")
        except sqlite3.IntegrityError:
            c.execute("SELECT customer_id FROM Customers WHERE phone_number=?", (cust[1],))
            existing_id = c.fetchone()[0]
            customer_ids.append(existing_id)
            print(f"  ~ Customer '{cust[0]}' already exists — using ID {existing_id}.")
    conn.commit()
    return customer_ids

                                                                               
                                                       
                                                                               

def seed_devices(c, conn, customer_ids):
    print("\n[3/9] Seeding Devices ...")
    devices_data = [
        (customer_ids[0], "352099001234560", "Samsung", "Galaxy A54"),
        (customer_ids[1], "357839002345671", "Apple",   "iPhone 13"),
        (customer_ids[2], "860123003456782", "Xiaomi",  "Redmi Note 12"),
        (customer_ids[3], "490154004567893", "Oppo",    "Reno 8"),
        (customer_ids[4], "356789005678904", "Samsung", "Galaxy S22"),
        (customer_ids[5], "012345006789015", "Apple",   "iPhone 12"),
        (customer_ids[6], "867543007890126", "Xiaomi",  "POCO X5"),
        (customer_ids[7], "354321008901237", "Vivo",    "V25"),
        (customer_ids[8], "861234009012348", "Realme",  "C35"),
        (customer_ids[9], "359876000123459", "Samsung", "Galaxy A14"),
    ]
    device_ids = []
    for dev in devices_data:
        try:
            c.execute(
                "INSERT INTO Devices (customer_id, imei_serial, device_brand, device_model)"
                " VALUES (?,?,?,?)", dev
            )
            device_ids.append(c.lastrowid)
            print(f"  + Device '{dev[3]}' (IMEI {dev[1]}) inserted.")
        except sqlite3.IntegrityError:
            c.execute("SELECT device_id FROM Devices WHERE imei_serial=?", (dev[1],))
            existing_id = c.fetchone()[0]
            device_ids.append(existing_id)
            print(f"  ~ Device '{dev[1]}' already exists — using ID {existing_id}.")
    conn.commit()
    return device_ids

                                                                               
                                                                      
                                                                               

def seed_tickets(c, conn, device_ids):
    print("\n[4/9] Seeding Tickets ...")
    issues = [
        "Screen cracked and touch unresponsive",
        "Battery drains within 2 hours of full charge",
        "Charging port not working — phone won't charge",
        "Speaker producing no sound during calls",
        "Camera app crashes immediately on launch",
        "Phone randomly restarts multiple times a day",
        "Back glass shattered after drop damage",
        "Microphone not picking up voice during calls",
        "Wi-Fi disconnects frequently and won't reconnect",
        "Home button / fingerprint sensor not responding",
    ]
    deposits  = [2000, 1500, 1000, 500, 2500, 1800, 3000, 1200, 800, 2200]
    base_date = datetime(2026, 5, 10)
    ticket_ids = []
    for i, dev_id in enumerate(device_ids):
        created_at = (base_date + timedelta(days=i)).strftime("%Y-%m-%d %H:%M:%S")
        c.execute(
            """INSERT INTO Tickets
               (device_id, assigned_tech_id, issue_description,
                status, created_at, service_charge, net_profit,
                advance_deposit, customer_notified)
               VALUES (?,?,?,?,?,?,?,?,?)""",
            (dev_id, None, issues[i], "Intake", created_at,
             None, None, deposits[i], 0)
        )
        tid = c.lastrowid
        ticket_ids.append(tid)
        print(f"  + Ticket TKT-{tid:04d} for device_id={dev_id} created (Intake).")
    conn.commit()
    return ticket_ids

                                                                               
                                                                         
                                                                               

def seed_parts(c, conn):
    print("\n[5/9] Seeding Parts_Inventory ...")

                                                                              
    normal_parts = [
        ("OLED Display Assembly",      "Samsung",  3500.00, 8),
        ("iPhone 13 LCD Screen",       "Apple",    4200.00, 5),
        ("Samsung A54 Battery",        "Samsung",   950.00, 15),
        ("iPhone 12 Battery",          "Apple",    1100.00, 12),
        ("USB-C Charging Port Flex",   "Generic",   350.00, 20),
        ("Lightning Connector Module", "Apple",     750.00, 10),
        ("Rear Camera Module 64MP",    "Xiaomi",   1800.00, 6),
        ("Front Camera 12MP Assembly", "Samsung",  1200.00, 7),
        ("Loudspeaker Unit",           "Generic",   280.00, 25),
        ("Fingerprint Sensor Module",  "Oppo",      650.00, 9),
    ]

                                                                              
    low_stock_parts = [
                          
        ("iPhone 14 OLED Display",         "Apple",    5800.00, 0),
        ("Samsung Galaxy S23 Battery",     "Samsung",  1250.00, 0),
                              
        ("USB-C Fast Charge Port Module",  "Xiaomi",    420.00, 1),
        ("Oppo A57 Fingerprint Flex",      "Oppo",      580.00, 1),
        ("Vivo Y33 Charging Dock",         "Vivo",      390.00, 2),
        ("Realme 9 Pro Speaker Unit",      "Realme",    310.00, 2),
                   
        ("iPhone 12 Pro Front Camera",     "Apple",    2100.00, 3),
        ("Samsung A73 Rear Camera 108MP",  "Samsung",  2800.00, 3),
        ("Xiaomi 12 Vibration Motor",      "Xiaomi",    180.00, 4),
        ("Generic Proximity Sensor Flex",  "Generic",   140.00, 4),
    ]

    part_ids = []
    for p in normal_parts + low_stock_parts:
        c.execute(
            "SELECT part_id FROM Parts_Inventory"
            " WHERE part_name=? AND brand_compatibility=?", (p[0], p[1])
        )
        existing = c.fetchone()
        if existing:
            part_ids.append(existing[0])
            print(f"  ~ Part '{p[0]}' already exists — skipped.")
        else:
            c.execute(
                "INSERT INTO Parts_Inventory"
                " (part_name, brand_compatibility, unit_cost, current_stock)"
                " VALUES (?,?,?,?)", p
            )
            part_ids.append(c.lastrowid)
            stock_label = "OUT OF STOCK" if p[3] == 0 else f"stock={p[3]}"
            print(f"  + Part '{p[0]}' ({p[1]}) — {stock_label}")
    conn.commit()
    return part_ids

                                                                               
                                        
                                                                               

def seed_donor_boards(c, conn):
    print("\n[6/9] Seeding Donor_Boards ...")
    donor_boards = [
        ("Samsung", "Galaxy A32", "SN-DB-001", "Active",   1500.00),
        ("Apple",   "iPhone 11",  "SN-DB-002", "Active",   3500.00),
        ("Xiaomi",  "Redmi 10",   "SN-DB-003", "Active",    800.00),
        ("Oppo",    "A57",        "SN-DB-004", "Active",    700.00),
        ("Samsung", "Galaxy A22", "SN-DB-005", "Active",   1200.00),
        ("Apple",   "iPhone XR",  "SN-DB-006", "Depleted", 2000.00),
        ("Vivo",    "Y21",        "SN-DB-007", "Active",    600.00),
        ("Realme",  "C25",        "SN-DB-008", "Active",    550.00),
        ("Xiaomi",  "POCO M3",    "SN-DB-009", "Active",    900.00),
        ("Samsung", "Galaxy M32", "SN-DB-010", "Active",   1300.00),
    ]
    board_ids = []
    for b in donor_boards:
        c.execute("SELECT board_id FROM Donor_Boards WHERE serial_number=?", (b[2],))
        existing = c.fetchone()
        if existing:
            board_ids.append(existing[0])
            print(f"  ~ Donor Board '{b[1]}' ({b[2]}) already exists — skipped.")
        else:
            c.execute(
                "INSERT INTO Donor_Boards"
                " (brand, model, serial_number, status, acquisition_cost)"
                " VALUES (?,?,?,?,?)", b
            )
            board_ids.append(c.lastrowid)
            print(f"  + Donor Board '{b[1]}' ({b[2]}) inserted.")
    conn.commit()
    return board_ids

                                                                               
                         
                                                                  
                                                                        
                                                                               

def seed_components(c, conn, board_ids, tech_id):
    print("\n[7/9] Seeding Components ...")

                                                                              
    normal_components = [
        "Display Assembly",
        "Battery",
        "Charging Port Flex",
        "Rear Camera",
        "Front Camera",
        "Loudspeaker",
        "Fingerprint Sensor",
        "Mainboard",
        "Back Cover Glass",
        "Power Button Flex",
    ]
    harvested_base = datetime(2026, 5, 1)
    for i, board_id in enumerate(board_ids):
        part_name     = normal_components[i]
        harvested_date = (harvested_base + timedelta(days=i * 3)).strftime("%Y-%m-%d %H:%M:%S")
        c.execute(
            "SELECT component_id FROM Components"
            " WHERE board_id=? AND part_name=? AND condition='Available'",
            (board_id, part_name)
        )
        if c.fetchone():
            print(f"  ~ Component '{part_name}' on board {board_id} already exists — skipped.")
        else:
            c.execute(
                "INSERT INTO Components"
                " (board_id, used_ticket_id, part_name, condition, harvested_date)"
                " VALUES (?,?,?,?,?)",
                (board_id, None, part_name, "Available", harvested_date)
            )
            print(f"  + Component '{part_name}' harvested from board_id={board_id}.")

                                                                              
    flagged_components = [
                                                        
        ("Display Assembly",    "Screen has multiple dead pixels on the top-left corner. Touch response also seems faulty after harvest.",          1, 0),
        ("Battery",             "Swollen battery — noticeably puffy. Likely unsafe to use. Flagging for write-off.",                               2, 1),
        ("Rear Camera Module",  "Camera captures blurry images even after cleaning the lens. Optical stabilisation appears broken.",               3, 2),
        ("Charging Port Flex",  "Port flex is partially torn near the connector. Charging is intermittent and unreliable.",                        4, 3),
        ("Front Camera",        "Front camera produces green tint on all photos. Sensor issue suspected.",                                         5, 4),
        ("Loudspeaker Unit",    "Loud crackling noise at mid volume. Cone may be damaged internally.",                                             6, 5),
        ("Mainboard",           "Board shows corrosion marks near SIM slot area. Possible liquid damage. Needs expert inspection.",                2, 0),
        ("Fingerprint Sensor",  "Fingerprint sensor consistently fails to register. Even after multiple reseating attempts, not functional.",       3, 1),
    ]
    now = datetime.now()
    for part_name, notes, days_ago, board_idx in flagged_components:
        board_id = board_ids[board_idx % len(board_ids)]
        c.execute(
            "SELECT component_id FROM Components"
            " WHERE board_id=? AND part_name=? AND condition='Flagged_Review'",
            (board_id, part_name)
        )
        if c.fetchone():
            print(f"  ~ Flagged component '{part_name}' on board {board_id} already exists — skipped.")
            continue
        harvested_date = (now - timedelta(days=days_ago + 2)).strftime("%Y-%m-%d %H:%M:%S")
        c.execute(
            "INSERT INTO Components"
            " (board_id, used_ticket_id, part_name, condition, harvested_date)"
            " VALUES (?,NULL,?,'Flagged_Review',?)",
            (board_id, part_name, harvested_date)
        )
        comp_id    = c.lastrowid
        flagged_at = (now - timedelta(days=days_ago)).strftime("%Y-%m-%d %H:%M:%S")
        c.execute(
            "INSERT INTO AuditLogs"
            " (user_id, action_type, target_id, timestamp, notes)"
            " VALUES (?, 'Part Flagged Damaged', ?, ?, ?)",
            (tech_id, comp_id, flagged_at, notes)
        )
        print(f"  + Flagged '{part_name}' from board_id={board_id} — by tech_id={tech_id}.")
    conn.commit()

                                                                               
                                                                      
                                                                               

def seed_audit_logs(c, conn, help_user_id, ticket_ids, device_ids):
    print("\n[8/9] Seeding AuditLogs ...")
    base_date = datetime(2026, 5, 10)
    for i, ticket_id in enumerate(ticket_ids):
        ts = (base_date + timedelta(days=i)).strftime("%Y-%m-%d %H:%M:%S")
        c.execute(
            "INSERT INTO AuditLogs"
            " (user_id, action_type, target_id, timestamp, notes)"
            " VALUES (?,?,?,?,?)",
            (help_user_id, "Create Ticket",
             f"TKT-{ticket_id:04d}", ts,
             f"Helpdesk 'help' created ticket TKT-{ticket_id:04d}"
             f" for device_id={device_ids[i]}")
        )
        print(f"  + AuditLog: 'help' created TKT-{ticket_id:04d}.")
    conn.commit()

                                                                               
                                             
                                                                               

def seed_model_templates(c, conn):
    print("\n[9/9] Seeding ModelTemplates ...")
    templates = [
        ("Samsung", "Galaxy A54",    "Display Assembly",   3500.00),
        ("Samsung", "Galaxy A54",    "Battery",             950.00),
        ("Apple",   "iPhone 13",     "Display Assembly",   4500.00),
        ("Apple",   "iPhone 13",     "Battery",            1100.00),
        ("Xiaomi",  "Redmi Note 12", "Display Assembly",   2200.00),
        ("Xiaomi",  "Redmi Note 12", "Charging Port Flex",  350.00),
        ("Oppo",    "Reno 8",        "Rear Camera",        1800.00),
        ("Apple",   "iPhone 12",     "Battery",            1050.00),
        ("Samsung", "Galaxy S22",    "Display Assembly",   5500.00),
        ("Vivo",    "V25",           "Front Camera",        900.00),
    ]
    for t in templates:
        try:
            c.execute(
                "INSERT INTO ModelTemplates"
                " (brand, model, part_name, estimated_value) VALUES (?,?,?,?)", t
            )
            print(f"  + Template: {t[0]} {t[1]} — {t[2]}.")
        except sqlite3.IntegrityError:
            print(f"  ~ Template '{t[1]} / {t[2]}' already exists — skipped.")
    conn.commit()

                                                                               
                                                    
                                                                               

def verify(c):
    divider("VERIFICATION REPORT")

                                                                               
    c.execute("SELECT COUNT(*) FROM Users")
    total = c.fetchone()[0]
    print(f"\n  Users ({total} rows):")
    c.execute("SELECT username, role, is_active FROM Users ORDER BY role, username")
    for r in c.fetchall():
        status = "active" if r[2] else "inactive"
        print(f"    [{status:>8}]  {r[1]:<12} {r[0]}")

                                                                               
    c.execute("SELECT COUNT(*) FROM Customers")
    print(f"\n  Customers: {c.fetchone()[0]} rows")

                                                                               
    c.execute("SELECT COUNT(*) FROM Devices")
    print(f"  Devices:   {c.fetchone()[0]} rows")

                                                                               
    c.execute("SELECT COUNT(*) FROM Tickets")
    total = c.fetchone()[0]
    c.execute("SELECT status, COUNT(*) FROM Tickets GROUP BY status ORDER BY status")
    breakdown = ", ".join(f"{r[1]} {r[0]}" for r in c.fetchall())
    print(f"  Tickets:   {total} rows  ({breakdown})")

                                                                               
    c.execute("SELECT COUNT(*) FROM Parts_Inventory")
    total = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM Parts_Inventory WHERE current_stock = 0")
    out  = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM Parts_Inventory WHERE current_stock > 0 AND current_stock < 5")
    low  = c.fetchone()[0]
    print(f"  Parts_Inventory: {total} rows  ({out} out-of-stock, {low} low-stock)")

    print("\n    Low-stock / out-of-stock items:")
    c.execute(
        "SELECT part_name, brand_compatibility, current_stock"
        " FROM Parts_Inventory WHERE current_stock < 5 ORDER BY current_stock, part_name"
    )
    for r in c.fetchall():
        label = "OUT OF STOCK" if r[2] == 0 else f"{r[2]:>2} units"
        print(f"    [{label:>12}]  {r[1]:<10} {r[0]}")

                                                                               
    c.execute("SELECT COUNT(*) FROM Donor_Boards")
    total = c.fetchone()[0]
    c.execute("SELECT status, COUNT(*) FROM Donor_Boards GROUP BY status")
    breakdown = ", ".join(f"{r[1]} {r[0]}" for r in c.fetchall())
    print(f"\n  Donor_Boards: {total} rows  ({breakdown})")

                                                                               
    c.execute("SELECT COUNT(*) FROM Components")
    total = c.fetchone()[0]
    c.execute("SELECT condition, COUNT(*) FROM Components GROUP BY condition ORDER BY condition")
    breakdown = ", ".join(f"{r[1]} {r[0]}" for r in c.fetchall())
    print(f"  Components: {total} rows  ({breakdown})")

    print("\n    Flagged components (Flagged_Review):")
    c.execute("""
        SELECT comp.part_name, db.brand, db.model
        FROM   Components comp
        JOIN   Donor_Boards db ON comp.board_id = db.board_id
        WHERE  comp.condition = 'Flagged_Review'
        ORDER  BY comp.component_id
    """)
    for r in c.fetchall():
        print(f"    [FLAGGED]  {r[0]:<26} <-- {r[1]} {r[2]}")

                                                                               
    c.execute("SELECT COUNT(*) FROM Ticket_Parts")
    print(f"\n  Ticket_Parts: {c.fetchone()[0]} rows")

                                                                               
    c.execute("SELECT COUNT(*) FROM AuditLogs")
    total = c.fetchone()[0]
    c.execute("SELECT action_type, COUNT(*) FROM AuditLogs GROUP BY action_type ORDER BY COUNT(*) DESC")
    breakdown = " | ".join(f"{r[1]}x {r[0]}" for r in c.fetchall())
    print(f"  AuditLogs: {total} rows  ({breakdown})")

                                                                               
    c.execute("SELECT COUNT(*) FROM ModelTemplates")
    print(f"  ModelTemplates: {c.fetchone()[0]} rows")

    divider()
    print("  All tables verified. Database is ready.")
    divider()

                                                                               
       
                                                                               

def run():
    conn = sqlite3.connect(DB_PATH)
    c    = conn.cursor()

    divider("RepairERP — Full Seed Script")
    print(f"  Database : {DB_PATH}")
    print(f"  Started  : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

                                                                               
    create_tables(c)
    conn.commit()

                                                                               
    seed_users(c, conn)

                                          
    c.execute("SELECT user_id FROM Users WHERE username='help'")
    help_user_id = c.fetchone()[0]

    c.execute("SELECT user_id FROM Users WHERE role='technician' LIMIT 1")
    tech_row = c.fetchone()
    if not tech_row:
        print("\nERROR: No technician user found after seeding — aborting.")
        conn.close()
        return
    tech_id = tech_row[0]

    customer_ids = seed_customers(c, conn)
    device_ids   = seed_devices(c, conn, customer_ids)
    ticket_ids   = seed_tickets(c, conn, device_ids)
    seed_parts(c, conn)
    board_ids    = seed_donor_boards(c, conn)
    seed_components(c, conn, board_ids, tech_id)
    seed_audit_logs(c, conn, help_user_id, ticket_ids, device_ids)
    seed_model_templates(c, conn)

                                                                               
    verify(c)

    conn.close()

if __name__ == "__main__":
    run()
