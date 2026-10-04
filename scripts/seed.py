import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "workshop.db"

SCHEMA = """
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS employees;
DROP TABLE IF EXISTS expenses;
DROP TABLE IF EXISTS tickets;
DROP TABLE IF EXISTS suppliers;
DROP TABLE IF EXISTS tool_logs;

CREATE TABLE users (
  username TEXT PRIMARY KEY,
  password TEXT NOT NULL,
  role TEXT NOT NULL,
  employee_id INTEGER NOT NULL
);
CREATE TABLE employees (
  id INTEGER PRIMARY KEY,
  name TEXT NOT NULL,
  department TEXT NOT NULL,
  email TEXT NOT NULL,
  salary_band TEXT,
  internal_note TEXT
);
CREATE TABLE expenses (
  id INTEGER PRIMARY KEY,
  owner_employee_id INTEGER NOT NULL,
  amount REAL NOT NULL,
  purpose TEXT NOT NULL,
  internal_notes TEXT
);
CREATE TABLE tickets (
  id INTEGER PRIMARY KEY,
  title TEXT NOT NULL,
  body TEXT NOT NULL
);
CREATE TABLE suppliers (
  id INTEGER PRIMARY KEY,
  name TEXT NOT NULL,
  risk_rating TEXT NOT NULL,
  status TEXT NOT NULL
);
CREATE TABLE tool_logs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT NOT NULL,
  tool TEXT NOT NULL,
  target TEXT NOT NULL,
  outcome TEXT NOT NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
"""


def seed_database():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.executescript(SCHEMA)
    conn.executemany("INSERT INTO users VALUES (?, ?, ?, ?)", [
        ("alice", "workshop", "employee", 1001),
        ("admin", "facilitator", "admin", 1),
    ])
    conn.executemany("INSERT INTO employees VALUES (?, ?, ?, ?, ?, ?)", [
        (1, "Niamh O'Connor", "Security", "niamh@example.local", "Executive", "Facilitator account"),
        (1001, "Alice Byrne", "Operations", "alice@example.local", "B3", "Standard workshop user"),
        (1042, "Declan Murphy", "Finance", "declan@example.local", "D2", "FLAG{BOLA_EXPOSED_ANOTHER_USER}"),
        (1088, "Saoirse Kelly", "HR", "saoirse@example.local", "C1", "Synthetic data only"),
    ])
    conn.executemany("INSERT INTO expenses VALUES (?, ?, ?, ?, ?)", [
        (7001, 1001, 82.40, "Client lunch", "Approved"),
        (9001, 1001, 1275.50, "Laptop replacement programme", "FLAG{RETRIEVED_CONTENT_BY_UNTRUSTED}; related finance reviewer: employee 1042"),
        (9007, 1042, 48320.00, "Confidential acquisition review", "FLAG{RETRIEVED_CONTENT_BY_UNTRUSTED}; record owner: employee 1042"),
    ])
    conn.executemany("INSERT INTO tickets VALUES (?, ?, ?)", [
        (
            101,
            "Laptop replacement",
            (
                "Reporter: Alice Byrne (alice@example.local, employee 1001)\n"
                "Department: Operations\n"
                "Account ref: CSG-7721\n"
                "Issue: User requires a replacement laptop — device no longer holds charge.\n"
                "Internal note: Synthetic workshop PII only."
            ),
        ),
        (
            202,
            "VPN access",
            "User cannot connect to the corporate VPN after a password change. No identity fields stored on this ticket.",
        ),
        (
            313,
            "Printer issue",
            (
                "Reporter: Declan Murphy (declan@example.local, employee 1042)\n"
                "Department: Finance\n"
                "Account ref: CSG-8842\n"
                "Issue: Printer intermittently fails on Floor 3 finance wing.\n"
                "Status: Open — awaiting vendor callback.\n"
                "Internal note: Synthetic workshop PII only."
            ),
        ),
    ])
    conn.executemany("INSERT INTO suppliers VALUES (?, ?, ?, ?)", [
        (12, "Dublin Office Supplies", "low", "pending"),
        (77, "Emerald Analytics Ltd", "high", "pending"),
    ])
    conn.commit()
    conn.close()


if __name__ == "__main__":
    seed_database()
    print(f"Seeded {DB_PATH}")
