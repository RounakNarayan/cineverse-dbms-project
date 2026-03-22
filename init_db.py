# ============================================================
#  CineVerse — Cinema Management System
#  File: init_db.py
#  Description: Database initialization script.
#               Creates all 9 SQL tables and seeds sample data.
#
#  Run ONCE before starting the app:
#      python init_db.py
#
#  Tables created:
#    users, managers, halls, movies, screens,
#    bookings, snack_menu, snack_orders, payments
# ============================================================

import sqlite3
import os
import hashlib

# Path to the SQLite database file
DB_PATH = os.path.join(os.path.dirname(__file__), 'instance', 'cinema.db')
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)


def hash_password(p):
    """Hash password with SHA-256."""
    return hashlib.sha256(p.encode()).hexdigest()


# ── SQL Schema ─────────────────────────────────────────────────────────────────

SCHEMA = """

-- Table 1: users — registered customer accounts
CREATE TABLE IF NOT EXISTS users (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    name       TEXT    NOT NULL,
    phone      TEXT    UNIQUE NOT NULL,
    password   TEXT    NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table 2: managers — manager credentials (city-wise)
CREATE TABLE IF NOT EXISTS managers (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    name         TEXT NOT NULL,
    manager_code TEXT UNIQUE NOT NULL,
    password     TEXT NOT NULL,
    city         TEXT NOT NULL
);

-- Table 3: halls — physical cinema buildings
CREATE TABLE IF NOT EXISTS halls (
    id      INTEGER PRIMARY KEY AUTOINCREMENT,
    name    TEXT NOT NULL,
    city    TEXT NOT NULL,
    address TEXT
);

-- Table 4: movies — movie catalogue
CREATE TABLE IF NOT EXISTS movies (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    title         TEXT    NOT NULL,
    genre         TEXT,
    duration_mins INTEGER,
    language      TEXT DEFAULT 'English',
    rating        TEXT
);

-- Table 5: screens — auditoriums within a hall
CREATE TABLE IF NOT EXISTS screens (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    hall_id      INTEGER NOT NULL,
    name         TEXT    NOT NULL,
    movie_id     INTEGER,
    show_time    TEXT,
    total_seats  INTEGER DEFAULT 100,
    ticket_price REAL    DEFAULT 250.0,
    FOREIGN KEY (hall_id)  REFERENCES halls(id),
    FOREIGN KEY (movie_id) REFERENCES movies(id)
);

-- Table 6: bookings — customer ticket bookings
CREATE TABLE IF NOT EXISTS bookings (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id      INTEGER NOT NULL,
    screen_id    INTEGER NOT NULL,
    booking_date TEXT    NOT NULL,
    seats_booked INTEGER NOT NULL,
    status       TEXT    DEFAULT 'confirmed',
    created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id)   REFERENCES users(id),
    FOREIGN KEY (screen_id) REFERENCES screens(id)
);

-- Table 7: snack_menu — available food and drinks
CREATE TABLE IF NOT EXISTS snack_menu (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT NOT NULL,
    category    TEXT,
    price       REAL NOT NULL,
    description TEXT
);

-- Table 8: snack_orders — multiple snacks per booking
CREATE TABLE IF NOT EXISTS snack_orders (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    booking_id INTEGER NOT NULL,
    snack_id   INTEGER NOT NULL,
    quantity   INTEGER DEFAULT 1,
    person_num INTEGER DEFAULT 1,
    FOREIGN KEY (booking_id) REFERENCES bookings(id),
    FOREIGN KEY (snack_id)   REFERENCES snack_menu(id)
);

-- Table 9: payments — payment record for each booking
CREATE TABLE IF NOT EXISTS payments (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    booking_id INTEGER NOT NULL,
    amount     REAL    NOT NULL,
    method     TEXT    DEFAULT 'card',
    paid_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (booking_id) REFERENCES bookings(id)
);
"""


# ── Sample Data ────────────────────────────────────────────────────────────────

SEED_DATA = [

    # ── Users (customers) ──────────────────────────────────────────
    ("INSERT OR IGNORE INTO users (name, phone, password) VALUES (?,?,?)", [
        ("Arjun Sharma",  "9876543210", hash_password("password123")),
        ("Priya Patel",   "9123456780", hash_password("priya456")),
        ("Rahul Mehta",   "9988776655", hash_password("rahul789")),
    ]),

    # ── Managers (one per city) ────────────────────────────────────
    ("INSERT OR IGNORE INTO managers (name, manager_code, password, city) VALUES (?,?,?,?)", [
        ("Vikram Singh",   "MGR-MUM", hash_password("mgr@mumbai"),    "Mumbai"),
        ("Neha Kapoor",    "MGR-DEL", hash_password("mgr@delhi"),     "Delhi"),
        ("Suresh Reddy",   "MGR-BLR", hash_password("mgr@bangalore"), "Bangalore"),
        ("Priya Nair",     "MGR-CHN", hash_password("mgr@chennai"),   "Chennai"),
    ]),

    # ── Movies ─────────────────────────────────────────────────────
    ("INSERT OR IGNORE INTO movies (title, genre, duration_mins, language, rating) VALUES (?,?,?,?,?)", [
        ("Kalki 2898 AD", "Sci-Fi/Action",    181, "Telugu",  "U/A"),
        ("Fighter",       "Action/Thriller",  166, "Hindi",   "UA"),
        ("Animal",        "Action/Drama",     201, "Hindi",   "A"),
        ("Dunki",         "Drama/Comedy",     161, "Hindi",   "U/A"),
        ("Salaar",        "Action",           173, "Telugu",  "A"),
        ("Sam Bahadur",   "Biographical",     156, "Hindi",   "U/A"),
        ("Oppenheimer",   "Historical Drama", 180, "English", "UA"),
        ("Dune Part 2",   "Sci-Fi",           166, "English", "UA"),
    ]),

    # ── Cinema Halls ───────────────────────────────────────────────
    ("INSERT OR IGNORE INTO halls (name, city, address) VALUES (?,?,?)", [
        ("PVR Cinemas",        "Mumbai",    "Phoenix Mall, Lower Parel"),
        ("INOX Grand",         "Mumbai",    "R-City Mall, Ghatkopar"),
        ("Cinepolis Gold",     "Delhi",     "DLF Mall of India, Noida"),
        ("PVR Director's Cut", "Delhi",     "Ambience Mall, Vasant Kunj"),
        ("INOX Lido",          "Bangalore", "MG Road, Bangalore"),
        ("Cinepolis VIP",      "Bangalore", "Orion Mall, Malleswaram"),
        ("PVR Luxe",           "Chennai",   "Express Avenue, Royapettah"),
        ("AGS Cinemas",        "Chennai",   "Grand Square Mall, Anna Nagar"),
    ]),

    # ── Screens ────────────────────────────────────────────────────
    ("INSERT OR IGNORE INTO screens (hall_id, name, movie_id, show_time, total_seats, ticket_price) VALUES (?,?,?,?,?,?)", [
        (1, "Screen 1 - IMAX",     1, "10:00 AM", 150, 450),
        (1, "Screen 2 - 4DX",      2, "01:30 PM", 100, 550),
        (1, "Screen 3 - Standard", 3, "06:00 PM", 200, 280),
        (1, "Screen 4 - Premium",  4, "09:30 PM", 120, 380),
        (2, "Screen A - Gold",     5, "11:00 AM",  80, 500),
        (2, "Screen B - Standard", 6, "03:00 PM", 180, 300),
        (2, "Screen C - Dolby",    7, "07:00 PM", 130, 420),
        (3, "Screen 1 - IMAX",     8, "10:30 AM", 160, 480),
        (3, "Screen 2 - 4DX",      1, "02:00 PM", 110, 560),
        (3, "Screen 3 - Standard", 2, "05:30 PM", 190, 270),
        (4, "Auditorium 1",        3, "11:30 AM", 200, 350),
        (4, "Auditorium 2",        4, "04:00 PM", 180, 350),
        (5, "Screen 1 - Luxe",     5, "09:00 AM",  90, 520),
        (5, "Screen 2 - Standard", 6, "12:30 PM", 170, 290),
        (5, "Screen 3 - Dolby",    7, "06:30 PM", 140, 440),
        (6, "VIP Screen 1",        8, "10:00 AM",  60, 700),
        (6, "VIP Screen 2",        1, "02:30 PM",  60, 700),
        (7, "Screen 1 - IMAX",     2, "10:00 AM", 145, 460),
        (7, "Screen 2 - Standard", 3, "01:00 PM", 185, 280),
        (8, "Screen A",            4, "11:00 AM", 160, 320),
        (8, "Screen B - 4K",       5, "03:30 PM", 120, 400),
    ]),

    # ── Snack Menu ─────────────────────────────────────────────────
    ("INSERT OR IGNORE INTO snack_menu (name, category, price, description) VALUES (?,?,?,?)", [
        ("Classic Popcorn (Large)", "Snacks",    180, "Buttery salted popcorn"),
        ("Cheese Popcorn (Large)",  "Snacks",    220, "Loaded with cheddar cheese"),
        ("Caramel Popcorn",         "Snacks",    200, "Sweet caramel coated popcorn"),
        ("Nachos with Salsa",       "Snacks",    250, "Crispy nachos with spicy salsa dip"),
        ("Cheese Nachos",           "Snacks",    290, "Nachos with melted cheese sauce"),
        ("Veg Burger Combo",        "Meals",     380, "Burger + Fries + Drink"),
        ("Chicken Burger Combo",    "Meals",     450, "Chicken burger + Fries + Drink"),
        ("Hot Dog",                 "Snacks",    220, "Classic American hot dog"),
        ("Cold Coffee",             "Beverages", 150, "Chilled blended coffee"),
        ("Soft Drink (Large)",      "Beverages", 120, "Pepsi / 7Up / Mountain Dew"),
        ("Fresh Lime Soda",         "Beverages", 100, "Sweet or salty lime soda"),
        ("Combo Meal A",            "Combos",    490, "Popcorn + Nachos + 2 Drinks"),
        ("Combo Meal B",            "Combos",    580, "Burger + Popcorn + 2 Drinks"),
        ("Ice Cream Tub",           "Desserts",  180, "Vanilla / Chocolate / Strawberry"),
    ]),
]


# ── Main Function ──────────────────────────────────────────────────────────────

def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.executescript(SCHEMA)
    conn.commit()
    for query, rows in SEED_DATA:
        for row in rows:
            conn.execute(query, row)
    conn.commit()
    conn.close()

    print("✅ Database initialized successfully!")
    print(f"📁 Location: {DB_PATH}")
    print("\n🔑 Demo Login Credentials:")
    print("   Customer    → Phone: 9876543210   | Password: password123")
    print("   Mumbai Mgr  → ID: MGR-MUM          | Password: mgr@mumbai")
    print("   Delhi Mgr   → ID: MGR-DEL          | Password: mgr@delhi")
    print("   Blr Mgr     → ID: MGR-BLR          | Password: mgr@bangalore")
    print("   Chennai Mgr → ID: MGR-CHN          | Password: mgr@chennai")


if __name__ == '__main__':
    init_db()
