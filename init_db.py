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
#
#  Cities: A–Z (26 Indian cities, alphabetical)
#  Halls:  3–4 halls per city
#  Snacks: 35+ items across 6 categories
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

-- Table 2: managers — manager credentials (separate from users)
CREATE TABLE IF NOT EXISTS managers (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    name         TEXT NOT NULL,
    manager_code TEXT UNIQUE NOT NULL,
    password     TEXT NOT NULL
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

-- Table 8: snack_orders — pre-ordered snacks per booking
CREATE TABLE IF NOT EXISTS snack_orders (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    booking_id INTEGER NOT NULL,
    snack_id   INTEGER NOT NULL,
    quantity   INTEGER DEFAULT 1,
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

    # ── Managers ───────────────────────────────────────────────────
    ("INSERT OR IGNORE INTO managers (name, manager_code, password) VALUES (?,?,?)", [
        ("Vikram Singh",  "MGR001", hash_password("mgr@001")),
        ("Neha Kapoor",   "MGR002", hash_password("mgr@002")),
        ("Aditya Rao",    "MGR003", hash_password("mgr@003")),
        ("Sunita Joshi",  "MGR004", hash_password("mgr@004")),
    ]),

    # ── Movies ─────────────────────────────────────────────────────
    ("INSERT OR IGNORE INTO movies (title, genre, duration_mins, language, rating) VALUES (?,?,?,?,?)", [
        ("Kalki 2898 AD",    "Sci-Fi/Action",    181, "Telugu",  "U/A"),
        ("Fighter",          "Action/Thriller",  166, "Hindi",   "UA"),
        ("Animal",           "Action/Drama",     201, "Hindi",   "A"),
        ("Dunki",            "Drama/Comedy",     161, "Hindi",   "U/A"),
        ("Salaar",           "Action",           173, "Telugu",  "A"),
        ("Sam Bahadur",      "Biographical",     156, "Hindi",   "U/A"),
        ("Oppenheimer",      "Historical Drama", 180, "English", "UA"),
        ("Dune Part 2",      "Sci-Fi",           166, "English", "UA"),
        ("Stree 2",          "Horror/Comedy",    140, "Hindi",   "U/A"),
        ("Pushpa 2",         "Action/Drama",     190, "Telugu",  "A"),
        ("Devara",           "Action/Thriller",  175, "Telugu",  "UA"),
        ("Singham Returns",  "Action",           155, "Hindi",   "UA"),
    ]),

    # ── Cinema Halls — A to Z (26 Indian cities) ───────────────────
    # City IDs after insert: Agra=1..4, Ahmedabad=5..8, ... Varanasi=97..100
    ("INSERT OR IGNORE INTO halls (name, city, address) VALUES (?,?,?)", [
        # A — Agra
        ("PVR Agra Central",     "Agra",        "Sadar Bazaar, Agra"),
        ("INOX Fun Republic",    "Agra",        "Raja Ki Mandi, Agra"),
        ("Cinepolis Agra Mall",  "Agra",        "Taj Nagri, Agra"),

        # B — Ahmedabad
        ("PVR Palladium",        "Ahmedabad",   "Palladium Mall, Prahlad Nagar"),
        ("INOX Himalaya",        "Ahmedabad",   "Himalaya Mall, Drive-In Road"),
        ("Cinepolis Ahmedabad",  "Ahmedabad",   "Alpha One Mall, Vastrapur"),
        ("Wide Angle Cinemas",   "Ahmedabad",   "Shyamal Cross Roads"),

        # C — Bangalore
        ("PVR Forum Mall",       "Bangalore",   "Forum Mall, Koramangala"),
        ("INOX Lido",            "Bangalore",   "MG Road, Bangalore"),
        ("Cinepolis VIP",        "Bangalore",   "Orion Mall, Malleswaram"),
        ("Urvashi Theatre",      "Bangalore",   "Lalbagh Road, Bangalore"),

        # D — Bhopal
        ("PVR DB City",          "Bhopal",      "DB City Mall, Arera Hills"),
        ("INOX Bhopal",          "Bhopal",      "Aashima Mall, Hoshangabad Road"),
        ("Cinepolis Bhopal",     "Bhopal",      "Ismart Bhopal, Kolar Road"),

        # E — Chandigarh
        ("PVR Elante",           "Chandigarh",  "Elante Mall, Industrial Area"),
        ("INOX Centra",          "Chandigarh",  "Centra Mall, Sector 17"),
        ("Cinepolis Chandigarh", "Chandigarh",  "Bestech Square, Mohali"),
        ("Wave Cinemas",         "Chandigarh",  "Wave Estate, Mohali"),

        # F — Chennai
        ("PVR Luxe",             "Chennai",     "Express Avenue, Royapettah"),
        ("AGS Cinemas",          "Chennai",     "Grand Square Mall, Anna Nagar"),
        ("INOX Palladium",       "Chennai",     "Palladium Mall, OMR"),
        ("Rohini Silver Screens","Chennai",     "Kasi Theatre Complex, Ashok Nagar"),

        # G — Coimbatore
        ("PVR Coimbatore",       "Coimbatore",  "Brookefields Mall, Kuniyamuthur"),
        ("INOX Sree Annamalai",  "Coimbatore",  "DB Road, Coimbatore"),
        ("Cinepolis Fun Cinemas","Coimbatore",  "Fun Republic Mall, Peelamedu"),

        # H — Delhi
        ("PVR Director's Cut",   "Delhi",       "Ambience Mall, Vasant Kunj"),
        ("INOX Nehru Place",     "Delhi",       "Saket District Centre, Saket"),
        ("Cinepolis DLF",        "Delhi",       "DLF Mall of India, Noida"),
        ("Odeon Cinemas",        "Delhi",       "South Extension, New Delhi"),

        # I — Goa
        ("INOX Panaji",          "Goa",         "Old GMC Complex, Panaji"),
        ("PVR Goa",              "Goa",         "Caculo Mall, St. Inez"),
        ("Cinepolis Goa",        "Goa",         "EDC Mall, Patto, Panaji"),

        # J — Guwahati
        ("PVR Guwahati",         "Guwahati",    "Birubari, Guwahati"),
        ("INOX G Plus",          "Guwahati",    "GS Road, Guwahati"),
        ("Cinepolis Guwahati",   "Guwahati",    "Baruah Plaza, Chandmari"),

        # K — Hyderabad
        ("PVR IMAX Hyderabad",   "Hyderabad",   "Inorbit Mall, Madhapur"),
        ("INOX GVK One",         "Hyderabad",   "GVK One Mall, Banjara Hills"),
        ("Cinepolis Hyderabad",  "Hyderabad",   "Cinepolis, Kukatpally"),
        ("Asian Cinemas",        "Hyderabad",   "Attapur, Hyderabad"),

        # L — Indore
        ("PVR C21 Mall",         "Indore",      "C21 Mall, A B Road"),
        ("INOX Treasure Island", "Indore",      "Treasure Island Mall, MG Road"),
        ("Cinepolis Indore",     "Indore",      "Orbit Mall, A B Road"),

        # M — Jaipur
        ("PVR Jaipur",           "Jaipur",      "World Trade Park, Malviya Nagar"),
        ("INOX Raj Mandir",      "Jaipur",      "Bhagwan Das Road, C-Scheme"),
        ("Cinepolis Jaipur",     "Jaipur",      "Pink Square Mall, Mansarovar"),
        ("Movietime Jaipur",     "Jaipur",      "Vaishali Nagar, Jaipur"),

        # N — Kanpur
        ("PVR Z Square",         "Kanpur",      "Z Square Mall, Kanpur"),
        ("INOX Kanpur",          "Kanpur",      "Rave Moti, GT Road"),
        ("Cinepolis Kanpur",     "Kanpur",      "Pacific Mall, Kanpur"),

        # O — Kochi
        ("PVR LuLu Kochi",       "Kochi",       "LuLu Mall, Edapally"),
        ("INOX Gold Souk",       "Kochi",       "Gold Souk Grande, Edapally"),
        ("Cinepolis Kochi",      "Kochi",       "Centre Square Mall, MG Road"),
        ("Srikumar Cinemas",     "Kochi",       "Ernakulam North, Kochi"),

        # P — Kolkata
        ("PVR Acropolis",        "Kolkata",     "Acropolis Mall, Kasba"),
        ("INOX South City",      "Kolkata",     "South City Mall, Prince Anwar Shah Road"),
        ("Cinepolis Quest",      "Kolkata",     "Quest Mall, Park Street"),
        ("Priya Cinema",         "Kolkata",     "Rashbehari Avenue, Kolkata"),

        # Q — Lucknow
        ("PVR Phoenix",          "Lucknow",     "Phoenix Palassio, Gomti Nagar"),
        ("INOX Lucknow",         "Lucknow",     "Sahara Ganj Mall, Hazratganj"),
        ("Cinepolis Fun Republic","Lucknow",    "Fun Republic Mall, Gomti Nagar"),
        ("Wave Cinemas Lucknow", "Lucknow",     "Wave Mall, Gomti Nagar"),

        # R — Mumbai
        ("PVR Cinemas",          "Mumbai",      "Phoenix Mall, Lower Parel"),
        ("INOX Grand",           "Mumbai",      "R-City Mall, Ghatkopar"),
        ("Cinepolis Andheri",    "Mumbai",      "Infiniti Mall, Andheri"),
        ("Regal Cinema",         "Mumbai",      "Colaba, Mumbai"),

        # S — Nagpur
        ("PVR Eternity",         "Nagpur",      "Eternity Mall, Sitabuldi"),
        ("INOX Nagpur",          "Nagpur",      "Poonam Chambers, Dharampeth"),
        ("Cinepolis Nagpur",     "Nagpur",      "South Avenue Mall, Nagpur"),

        # T — Patna
        ("PVR Patna",            "Patna",       "Patna One Mall, Dak Bungalow Road"),
        ("INOX Patna",           "Patna",       "P&M Mall, Frazer Road"),
        ("Cinepolis Patna",      "Patna",       "Maurya Lok Complex, Patna"),

        # U — Pune
        ("PVR Amanora",          "Pune",        "Amanora Town Centre, Hadapsar"),
        ("INOX Bund Garden",     "Pune",        "Bund Garden Road, Pune"),
        ("Cinepolis Pune",       "Pune",        "Seasons Mall, Magarpatta"),
        ("E-Square Cinemas",     "Pune",        "University Road, Pune"),

        # V — Ranchi
        ("PVR Nucleus Mall",     "Ranchi",      "Nucleus Mall, Main Road"),
        ("INOX Ranchi",          "Ranchi",      "Lalpur, Ranchi"),
        ("Cinepolis Ranchi",     "Ranchi",      "Orion Mall, HEC Colony"),

        # W — Surat
        ("PVR VR Mall",          "Surat",       "VR Mall, Surat"),
        ("INOX Rahul Raj",       "Surat",       "Rahul Raj Mall, Adajan"),
        ("Cinepolis Surat",      "Surat",       "Dreams Mall, Surat"),
        ("Fun Republic Surat",   "Surat",       "Ring Road, Surat"),

        # X — Thiruvananthapuram
        ("PVR Kerala",           "Thiruvananthapuram", "LuLu Mall, Thiruvananthapuram"),
        ("INOX Trivandrum",      "Thiruvananthapuram", "Bhavani Complex, MG Road"),
        ("Cinepolis Trivandrum", "Thiruvananthapuram", "Oberon Mall, Edapally Road"),

        # Y — Varanasi
        ("PVR Varanasi",         "Varanasi",    "Lahartara Mall, Varanasi"),
        ("INOX Varanasi",        "Varanasi",    "PDR Mall, Sigra"),
        ("Cinepolis Varanasi",   "Varanasi",    "Unity Mall, Varanasi"),

        # Z — Visakhapatnam
        ("PVR CMR Central",      "Visakhapatnam", "CMR Central Mall, Dwaraka Nagar"),
        ("INOX Vizag",           "Visakhapatnam", "Waltair Uplands, Vizag"),
        ("Cinepolis Vizag",      "Visakhapatnam", "Siripuram Junction, Vizag"),
        ("Sudarshan 70mm",       "Visakhapatnam", "RTC Complex, Vizag"),
    ]),

    # ── Screens (3 screens per hall, all 92 halls) ─────────────────
    ("INSERT OR IGNORE INTO screens (hall_id, name, movie_id, show_time, total_seats, ticket_price) VALUES (?,?,?,?,?,?)", [
        # Hall 1 — PVR Agra Central
        (1, "Screen 1 - IMAX",      1, "10:00 AM", 150, 450),
        (1, "Screen 2 - 4DX",       2, "02:00 PM", 100, 550),
        (1, "Screen 3 - Standard",  3, "06:30 PM", 200, 280),
        # Hall 2 — INOX Fun Republic (Agra)
        (2, "Screen A - Gold",      4, "11:00 AM",  80, 500),
        (2, "Screen B - Standard",  5, "03:00 PM", 180, 300),
        (2, "Screen C - Dolby",     6, "07:30 PM", 130, 420),
        # Hall 3 — Cinepolis Agra Mall
        (3, "Screen 1 - IMAX",      7, "10:30 AM", 160, 480),
        (3, "Screen 2 - Standard",  8, "02:30 PM", 190, 270),
        (3, "Screen 3 - Premium",   9, "07:00 PM", 120, 380),
        # Hall 4 — PVR Palladium (Ahmedabad)
        (4, "Auditorium 1 - IMAX", 10, "10:00 AM", 200, 490),
        (4, "Auditorium 2 - 4DX",  11, "02:00 PM", 100, 580),
        (4, "Auditorium 3",        12, "06:00 PM", 180, 320),
        # Hall 5 — INOX Himalaya (Ahmedabad)
        (5, "Screen 1 - Luxe",      1, "09:30 AM",  90, 520),
        (5, "Screen 2 - Standard",  2, "01:30 PM", 170, 290),
        (5, "Screen 3 - Dolby",     3, "06:30 PM", 140, 440),
        # Hall 6 — Cinepolis Ahmedabad
        (6, "VIP Screen 1",         4, "11:00 AM",  60, 700),
        (6, "VIP Screen 2",         5, "03:30 PM",  60, 700),
        (6, "Screen 3 - Standard",  6, "08:00 PM", 150, 310),
        # Hall 7 — Wide Angle Cinemas (Ahmedabad)
        (7, "Screen 1 - IMAX",      7, "10:00 AM", 145, 460),
        (7, "Screen 2 - Standard",  8, "02:00 PM", 185, 280),
        (7, "Screen 3 - 4K",        9, "07:00 PM", 120, 400),
        # Hall 8 — PVR Forum Mall (Bangalore)
        (8, "Screen A - IMAX",     10, "10:30 AM", 160, 490),
        (8, "Screen B - 4DX",      11, "02:30 PM", 100, 560),
        (8, "Screen C - Standard", 12, "07:30 PM", 200, 280),
        # Hall 9 — INOX Lido (Bangalore)
        (9, "Screen 1 - Gold",      1, "11:00 AM",  90, 520),
        (9, "Screen 2 - Standard",  2, "03:00 PM", 170, 300),
        (9, "Screen 3 - Dolby",     3, "07:00 PM", 140, 430),
        # Hall 10 — Cinepolis VIP (Bangalore)
        (10, "VIP Screen 1",        4, "10:00 AM",  60, 700),
        (10, "VIP Screen 2",        5, "02:00 PM",  60, 700),
        (10, "Screen 3",            6, "06:30 PM", 150, 320),
        # Hall 11 — Urvashi Theatre (Bangalore)
        (11, "Screen 1 - Standard", 7, "10:30 AM", 180, 260),
        (11, "Screen 2 - Standard", 8, "02:30 PM", 180, 260),
        (11, "Screen 3 - Standard", 9, "06:30 PM", 180, 260),
        # Hall 12 — PVR DB City (Bhopal)
        (12, "Screen 1 - IMAX",    10, "10:00 AM", 150, 460),
        (12, "Screen 2 - 4DX",     11, "02:00 PM", 100, 550),
        (12, "Screen 3 - Standard",12, "07:00 PM", 190, 280),
        # Hall 13 — INOX Bhopal
        (13, "Screen A - Gold",     1, "11:30 AM",  80, 510),
        (13, "Screen B - Standard", 2, "03:30 PM", 170, 290),
        (13, "Screen C - Dolby",    3, "07:30 PM", 130, 420),
        # Hall 14 — Cinepolis Bhopal
        (14, "Screen 1 - IMAX",     4, "10:00 AM", 155, 470),
        (14, "Screen 2 - Standard", 5, "02:00 PM", 185, 270),
        (14, "Screen 3 - Premium",  6, "06:30 PM", 120, 370),
        # Hall 15 — PVR Elante (Chandigarh)
        (15, "Screen 1 - IMAX",     7, "10:00 AM", 150, 460),
        (15, "Screen 2 - 4DX",      8, "02:00 PM", 100, 560),
        (15, "Screen 3 - Standard", 9, "07:00 PM", 200, 280),
        # Hall 16 — INOX Centra (Chandigarh)
        (16, "Screen A - Gold",    10, "11:00 AM",  80, 500),
        (16, "Screen B - Dolby",   11, "03:00 PM", 130, 420),
        (16, "Screen C - Standard",12, "07:30 PM", 180, 290),
        # Hall 17 — Cinepolis Chandigarh
        (17, "Screen 1 - IMAX",     1, "10:30 AM", 160, 480),
        (17, "Screen 2 - Standard", 2, "02:30 PM", 190, 270),
        (17, "Screen 3 - Premium",  3, "07:00 PM", 120, 380),
        # Hall 18 — Wave Cinemas (Chandigarh)
        (18, "Screen 1",            4, "11:00 AM", 170, 300),
        (18, "Screen 2",            5, "03:00 PM", 170, 300),
        (18, "Screen 3",            6, "07:00 PM", 170, 300),
        # Hall 19 — PVR Luxe (Chennai)
        (19, "Screen 1 - IMAX",     7, "10:00 AM", 145, 460),
        (19, "Screen 2 - 4DX",      8, "02:00 PM", 100, 560),
        (19, "Screen 3 - Luxe",     9, "06:30 PM",  80, 650),
        # Hall 20 — AGS Cinemas (Chennai)
        (20, "Screen A",           10, "10:30 AM", 160, 320),
        (20, "Screen B",           11, "02:30 PM", 160, 320),
        (20, "Screen C",           12, "07:00 PM", 160, 320),
        # Hall 21 — INOX Palladium (Chennai)
        (21, "Screen 1 - Gold",     1, "11:00 AM",  90, 520),
        (21, "Screen 2 - Dolby",    2, "03:00 PM", 140, 430),
        (21, "Screen 3 - Standard", 3, "07:30 PM", 180, 290),
        # Hall 22 — Rohini Silver Screens (Chennai)
        (22, "Screen 1",            4, "10:00 AM", 175, 270),
        (22, "Screen 2",            5, "02:00 PM", 175, 270),
        (22, "Screen 3",            6, "06:30 PM", 175, 270),
        # Hall 23 — PVR Coimbatore
        (23, "Screen 1 - IMAX",     7, "10:00 AM", 150, 440),
        (23, "Screen 2 - Standard", 8, "02:00 PM", 185, 270),
        (23, "Screen 3 - Premium",  9, "07:00 PM", 120, 370),
        # Hall 24 — INOX Sree Annamalai (Coimbatore)
        (24, "Screen A",           10, "11:00 AM", 160, 300),
        (24, "Screen B - Dolby",   11, "03:00 PM", 130, 410),
        (24, "Screen C",           12, "07:30 PM", 160, 300),
        # Hall 25 — Cinepolis Fun Cinemas (Coimbatore)
        (25, "Screen 1",            1, "10:30 AM", 170, 280),
        (25, "Screen 2",            2, "02:30 PM", 170, 280),
        (25, "Screen 3",            3, "06:30 PM", 170, 280),
        # Hall 26 — PVR Director's Cut (Delhi)
        (26, "Screen 1 - IMAX",     4, "10:00 AM", 150, 500),
        (26, "Screen 2 - 4DX",      5, "02:00 PM", 100, 600),
        (26, "Screen 3 - Director", 6, "07:00 PM",  60, 750),
        # Hall 27 — INOX Nehru Place (Delhi)
        (27, "Screen A - Gold",     7, "11:00 AM",  90, 530),
        (27, "Screen B - Dolby",    8, "03:00 PM", 140, 440),
        (27, "Screen C - Standard", 9, "07:30 PM", 180, 300),
        # Hall 28 — Cinepolis DLF (Delhi)
        (28, "Screen 1 - IMAX",    10, "10:30 AM", 165, 490),
        (28, "Screen 2 - 4DX",     11, "02:30 PM", 110, 570),
        (28, "Screen 3 - Standard",12, "07:00 PM", 195, 280),
        # Hall 29 — Odeon Cinemas (Delhi)
        (29, "Screen 1",            1, "10:00 AM", 175, 280),
        (29, "Screen 2",            2, "02:00 PM", 175, 280),
        (29, "Screen 3",            3, "07:00 PM", 175, 280),
        # Hall 30 — INOX Panaji (Goa)
        (30, "Screen 1 - Gold",     4, "11:00 AM",  80, 510),
        (30, "Screen 2 - Dolby",    5, "03:00 PM", 130, 420),
        (30, "Screen 3 - Standard", 6, "07:30 PM", 170, 290),
        # Hall 31 — PVR Goa
        (31, "Screen 1 - IMAX",     7, "10:00 AM", 145, 450),
        (31, "Screen 2 - Standard", 8, "02:00 PM", 185, 270),
        (31, "Screen 3 - Premium",  9, "07:00 PM", 120, 370),
        # Hall 32 — Cinepolis Goa
        (32, "Screen 1",           10, "10:30 AM", 160, 300),
        (32, "Screen 2",           11, "02:30 PM", 160, 300),
        (32, "Screen 3",           12, "07:30 PM", 160, 300),
        # Hall 33 — PVR Guwahati
        (33, "Screen 1 - IMAX",     1, "10:00 AM", 140, 440),
        (33, "Screen 2 - Standard", 2, "02:00 PM", 180, 270),
        (33, "Screen 3 - Premium",  3, "07:00 PM", 110, 360),
        # Hall 34 — INOX G Plus (Guwahati)
        (34, "Screen A",            4, "11:00 AM", 160, 300),
        (34, "Screen B - Dolby",    5, "03:00 PM", 130, 410),
        (34, "Screen C",            6, "07:30 PM", 160, 300),
        # Hall 35 — Cinepolis Guwahati
        (35, "Screen 1",            7, "10:30 AM", 165, 290),
        (35, "Screen 2",            8, "02:30 PM", 165, 290),
        (35, "Screen 3",            9, "07:00 PM", 165, 290),
        # Hall 36 — PVR IMAX Hyderabad
        (36, "Screen 1 - IMAX",    10, "10:00 AM", 160, 500),
        (36, "Screen 2 - 4DX",     11, "02:00 PM", 110, 580),
        (36, "Screen 3 - Standard",12, "07:00 PM", 200, 290),
        # Hall 37 — INOX GVK One (Hyderabad)
        (37, "Screen A - Gold",     1, "11:00 AM",  90, 530),
        (37, "Screen B - Dolby",    2, "03:00 PM", 140, 440),
        (37, "Screen C - Standard", 3, "07:30 PM", 180, 300),
        # Hall 38 — Cinepolis Hyderabad
        (38, "Screen 1 - IMAX",     4, "10:30 AM", 155, 480),
        (38, "Screen 2 - Standard", 5, "02:30 PM", 185, 280),
        (38, "Screen 3 - Premium",  6, "07:00 PM", 120, 380),
        # Hall 39 — Asian Cinemas (Hyderabad)
        (39, "Screen 1",            7, "10:00 AM", 170, 270),
        (39, "Screen 2",            8, "02:00 PM", 170, 270),
        (39, "Screen 3",            9, "07:00 PM", 170, 270),
        # Hall 40 — PVR C21 Mall (Indore)
        (40, "Screen 1 - IMAX",    10, "10:00 AM", 145, 450),
        (40, "Screen 2 - Standard",11, "02:00 PM", 185, 270),
        (40, "Screen 3 - Premium", 12, "07:00 PM", 120, 370),
        # Hall 41 — INOX Treasure Island (Indore)
        (41, "Screen A - Gold",     1, "11:00 AM",  80, 500),
        (41, "Screen B - Dolby",    2, "03:00 PM", 130, 410),
        (41, "Screen C - Standard", 3, "07:30 PM", 175, 280),
        # Hall 42 — Cinepolis Indore
        (42, "Screen 1",            4, "10:30 AM", 160, 290),
        (42, "Screen 2",            5, "02:30 PM", 160, 290),
        (42, "Screen 3",            6, "07:00 PM", 160, 290),
        # Hall 43 — PVR Jaipur
        (43, "Screen 1 - IMAX",     7, "10:00 AM", 150, 460),
        (43, "Screen 2 - 4DX",      8, "02:00 PM", 100, 560),
        (43, "Screen 3 - Standard", 9, "07:00 PM", 195, 280),
        # Hall 44 — INOX Raj Mandir (Jaipur)
        (44, "Screen A - Classic", 10, "11:00 AM", 500, 250),
        (44, "Screen B - Classic", 11, "03:00 PM", 500, 250),
        (44, "Screen C - Classic", 12, "07:00 PM", 500, 250),
        # Hall 45 — Cinepolis Jaipur
        (45, "Screen 1 - IMAX",     1, "10:30 AM", 155, 470),
        (45, "Screen 2 - Standard", 2, "02:30 PM", 185, 280),
        (45, "Screen 3 - Premium",  3, "07:30 PM", 120, 370),
        # Hall 46 — Movietime Jaipur
        (46, "Screen 1",            4, "11:00 AM", 165, 290),
        (46, "Screen 2",            5, "03:00 PM", 165, 290),
        (46, "Screen 3",            6, "07:00 PM", 165, 290),
        # Hall 47 — PVR Z Square (Kanpur)
        (47, "Screen 1 - IMAX",     7, "10:00 AM", 145, 440),
        (47, "Screen 2 - Standard", 8, "02:00 PM", 185, 270),
        (47, "Screen 3 - Premium",  9, "07:00 PM", 120, 360),
        # Hall 48 — INOX Kanpur
        (48, "Screen A",           10, "11:00 AM", 160, 300),
        (48, "Screen B - Dolby",   11, "03:00 PM", 130, 410),
        (48, "Screen C",           12, "07:30 PM", 160, 300),
        # Hall 49 — Cinepolis Kanpur
        (49, "Screen 1",            1, "10:30 AM", 165, 280),
        (49, "Screen 2",            2, "02:30 PM", 165, 280),
        (49, "Screen 3",            3, "07:00 PM", 165, 280),
        # Hall 50 — PVR LuLu Kochi
        (50, "Screen 1 - IMAX",     4, "10:00 AM", 155, 480),
        (50, "Screen 2 - 4DX",      5, "02:00 PM", 105, 570),
        (50, "Screen 3 - Standard", 6, "07:00 PM", 195, 290),
        # Hall 51 — INOX Gold Souk (Kochi)
        (51, "Screen A - Gold",     7, "11:00 AM",  85, 520),
        (51, "Screen B - Dolby",    8, "03:00 PM", 135, 430),
        (51, "Screen C - Standard", 9, "07:30 PM", 175, 290),
        # Hall 52 — Cinepolis Kochi
        (52, "Screen 1 - IMAX",    10, "10:30 AM", 155, 470),
        (52, "Screen 2 - Standard",11, "02:30 PM", 185, 280),
        (52, "Screen 3 - Premium", 12, "07:00 PM", 120, 370),
        # Hall 53 — Srikumar Cinemas (Kochi)
        (53, "Screen 1",            1, "10:00 AM", 170, 260),
        (53, "Screen 2",            2, "02:00 PM", 170, 260),
        (53, "Screen 3",            3, "07:00 PM", 170, 260),
        # Hall 54 — PVR Acropolis (Kolkata)
        (54, "Screen 1 - IMAX",     4, "10:00 AM", 150, 470),
        (54, "Screen 2 - 4DX",      5, "02:00 PM", 100, 560),
        (54, "Screen 3 - Standard", 6, "07:00 PM", 195, 280),
        # Hall 55 — INOX South City (Kolkata)
        (55, "Screen A - Gold",     7, "11:00 AM",  85, 520),
        (55, "Screen B - Dolby",    8, "03:00 PM", 135, 430),
        (55, "Screen C - Standard", 9, "07:30 PM", 175, 290),
        # Hall 56 — Cinepolis Quest (Kolkata)
        (56, "Screen 1 - IMAX",    10, "10:30 AM", 160, 480),
        (56, "Screen 2 - Standard",11, "02:30 PM", 190, 270),
        (56, "Screen 3 - Premium", 12, "07:00 PM", 120, 380),
        # Hall 57 — Priya Cinema (Kolkata)
        (57, "Screen 1",            1, "10:00 AM", 400, 200),
        (57, "Screen 2",            2, "02:00 PM", 400, 200),
        (57, "Screen 3",            3, "07:00 PM", 400, 200),
        # Hall 58 — PVR Phoenix (Lucknow)
        (58, "Screen 1 - IMAX",     4, "10:00 AM", 150, 460),
        (58, "Screen 2 - 4DX",      5, "02:00 PM", 100, 560),
        (58, "Screen 3 - Standard", 6, "07:00 PM", 195, 280),
        # Hall 59 — INOX Lucknow
        (59, "Screen A - Gold",     7, "11:00 AM",  85, 510),
        (59, "Screen B - Dolby",    8, "03:00 PM", 135, 420),
        (59, "Screen C - Standard", 9, "07:30 PM", 175, 290),
        # Hall 60 — Cinepolis Fun Republic (Lucknow)
        (60, "Screen 1 - IMAX",    10, "10:30 AM", 155, 470),
        (60, "Screen 2 - Standard",11, "02:30 PM", 185, 270),
        (60, "Screen 3 - Premium", 12, "07:00 PM", 120, 370),
        # Hall 61 — Wave Cinemas Lucknow
        (61, "Screen 1",            1, "11:00 AM", 165, 290),
        (61, "Screen 2",            2, "03:00 PM", 165, 290),
        (61, "Screen 3",            3, "07:30 PM", 165, 290),
        # Hall 62 — PVR Cinemas (Mumbai)
        (62, "Screen 1 - IMAX",     4, "10:00 AM", 150, 480),
        (62, "Screen 2 - 4DX",      5, "02:00 PM", 100, 580),
        (62, "Screen 3 - Standard", 6, "07:00 PM", 200, 290),
        # Hall 63 — INOX Grand (Mumbai)
        (63, "Screen A - Gold",     7, "11:00 AM",  90, 540),
        (63, "Screen B - Dolby",    8, "03:00 PM", 140, 450),
        (63, "Screen C - Standard", 9, "07:30 PM", 180, 300),
        # Hall 64 — Cinepolis Andheri (Mumbai)
        (64, "Screen 1 - IMAX",    10, "10:30 AM", 160, 490),
        (64, "Screen 2 - Standard",11, "02:30 PM", 190, 280),
        (64, "Screen 3 - Premium", 12, "07:00 PM", 120, 390),
        # Hall 65 — Regal Cinema (Mumbai)
        (65, "Screen 1",            1, "11:00 AM", 350, 220),
        (65, "Screen 2",            2, "03:00 PM", 350, 220),
        (65, "Screen 3",            3, "07:30 PM", 350, 220),
        # Hall 66 — PVR Eternity (Nagpur)
        (66, "Screen 1 - IMAX",     4, "10:00 AM", 145, 450),
        (66, "Screen 2 - Standard", 5, "02:00 PM", 185, 270),
        (66, "Screen 3 - Premium",  6, "07:00 PM", 120, 360),
        # Hall 67 — INOX Nagpur
        (67, "Screen A",            7, "11:00 AM", 160, 300),
        (67, "Screen B - Dolby",    8, "03:00 PM", 130, 410),
        (67, "Screen C",            9, "07:30 PM", 160, 300),
        # Hall 68 — Cinepolis Nagpur
        (68, "Screen 1",           10, "10:30 AM", 165, 280),
        (68, "Screen 2",           11, "02:30 PM", 165, 280),
        (68, "Screen 3",           12, "07:00 PM", 165, 280),
        # Hall 69 — PVR Patna
        (69, "Screen 1 - IMAX",     1, "10:00 AM", 140, 440),
        (69, "Screen 2 - Standard", 2, "02:00 PM", 180, 260),
        (69, "Screen 3 - Premium",  3, "07:00 PM", 110, 350),
        # Hall 70 — INOX Patna
        (70, "Screen A",            4, "11:00 AM", 155, 290),
        (70, "Screen B - Dolby",    5, "03:00 PM", 125, 400),
        (70, "Screen C",            6, "07:30 PM", 155, 290),
        # Hall 71 — Cinepolis Patna
        (71, "Screen 1",            7, "10:30 AM", 160, 270),
        (71, "Screen 2",            8, "02:30 PM", 160, 270),
        (71, "Screen 3",            9, "07:00 PM", 160, 270),
        # Hall 72 — PVR Amanora (Pune)
        (72, "Screen 1 - IMAX",    10, "10:00 AM", 155, 480),
        (72, "Screen 2 - 4DX",     11, "02:00 PM", 105, 570),
        (72, "Screen 3 - Standard",12, "07:00 PM", 195, 290),
        # Hall 73 — INOX Bund Garden (Pune)
        (73, "Screen A - Gold",     1, "11:00 AM",  85, 520),
        (73, "Screen B - Dolby",    2, "03:00 PM", 135, 430),
        (73, "Screen C - Standard", 3, "07:30 PM", 175, 290),
        # Hall 74 — Cinepolis Pune
        (74, "Screen 1 - IMAX",     4, "10:30 AM", 155, 470),
        (74, "Screen 2 - Standard", 5, "02:30 PM", 185, 280),
        (74, "Screen 3 - Premium",  6, "07:00 PM", 120, 370),
        # Hall 75 — E-Square Cinemas (Pune)
        (75, "Screen 1",            7, "10:00 AM", 170, 270),
        (75, "Screen 2",            8, "02:00 PM", 170, 270),
        (75, "Screen 3",            9, "07:00 PM", 170, 270),
        # Hall 76 — PVR Nucleus Mall (Ranchi)
        (76, "Screen 1 - IMAX",    10, "10:00 AM", 140, 430),
        (76, "Screen 2 - Standard",11, "02:00 PM", 175, 260),
        (76, "Screen 3 - Premium", 12, "07:00 PM", 110, 350),
        # Hall 77 — INOX Ranchi
        (77, "Screen A",            1, "11:00 AM", 155, 280),
        (77, "Screen B - Dolby",    2, "03:00 PM", 125, 390),
        (77, "Screen C",            3, "07:30 PM", 155, 280),
        # Hall 78 — Cinepolis Ranchi
        (78, "Screen 1",            4, "10:30 AM", 160, 260),
        (78, "Screen 2",            5, "02:30 PM", 160, 260),
        (78, "Screen 3",            6, "07:00 PM", 160, 260),
        # Hall 79 — PVR VR Mall (Surat)
        (79, "Screen 1 - IMAX",     7, "10:00 AM", 150, 460),
        (79, "Screen 2 - 4DX",      8, "02:00 PM", 100, 550),
        (79, "Screen 3 - Standard", 9, "07:00 PM", 190, 280),
        # Hall 80 — INOX Rahul Raj (Surat)
        (80, "Screen A - Gold",    10, "11:00 AM",  80, 500),
        (80, "Screen B - Dolby",   11, "03:00 PM", 130, 410),
        (80, "Screen C - Standard",12, "07:30 PM", 170, 280),
        # Hall 81 — Cinepolis Surat
        (81, "Screen 1 - IMAX",     1, "10:30 AM", 150, 460),
        (81, "Screen 2 - Standard", 2, "02:30 PM", 185, 270),
        (81, "Screen 3 - Premium",  3, "07:00 PM", 120, 360),
        # Hall 82 — Fun Republic Surat
        (82, "Screen 1",            4, "11:00 AM", 165, 280),
        (82, "Screen 2",            5, "03:00 PM", 165, 280),
        (82, "Screen 3",            6, "07:30 PM", 165, 280),
        # Hall 83 — PVR Kerala (Thiruvananthapuram)
        (83, "Screen 1 - IMAX",     7, "10:00 AM", 145, 450),
        (83, "Screen 2 - Standard", 8, "02:00 PM", 180, 270),
        (83, "Screen 3 - Premium",  9, "07:00 PM", 115, 360),
        # Hall 84 — INOX Trivandrum
        (84, "Screen A",           10, "11:00 AM", 155, 290),
        (84, "Screen B - Dolby",   11, "03:00 PM", 125, 400),
        (84, "Screen C",           12, "07:30 PM", 155, 290),
        # Hall 85 — Cinepolis Trivandrum
        (85, "Screen 1",            1, "10:30 AM", 160, 270),
        (85, "Screen 2",            2, "02:30 PM", 160, 270),
        (85, "Screen 3",            3, "07:00 PM", 160, 270),
        # Hall 86 — PVR Varanasi
        (86, "Screen 1 - IMAX",     4, "10:00 AM", 140, 430),
        (86, "Screen 2 - Standard", 5, "02:00 PM", 175, 260),
        (86, "Screen 3 - Premium",  6, "07:00 PM", 110, 350),
        # Hall 87 — INOX Varanasi
        (87, "Screen A",            7, "11:00 AM", 150, 280),
        (87, "Screen B - Dolby",    8, "03:00 PM", 120, 390),
        (87, "Screen C",            9, "07:30 PM", 150, 280),
        # Hall 88 — Cinepolis Varanasi
        (88, "Screen 1",           10, "10:30 AM", 158, 260),
        (88, "Screen 2",           11, "02:30 PM", 158, 260),
        (88, "Screen 3",           12, "07:00 PM", 158, 260),
        # Hall 89 — PVR CMR Central (Visakhapatnam)
        (89, "Screen 1 - IMAX",     1, "10:00 AM", 145, 450),
        (89, "Screen 2 - Standard", 2, "02:00 PM", 180, 270),
        (89, "Screen 3 - Premium",  3, "07:00 PM", 115, 360),
        # Hall 90 — INOX Vizag
        (90, "Screen A - Gold",     4, "11:00 AM",  80, 500),
        (90, "Screen B - Dolby",    5, "03:00 PM", 130, 410),
        (90, "Screen C - Standard", 6, "07:30 PM", 170, 280),
        # Hall 91 — Cinepolis Vizag
        (91, "Screen 1 - IMAX",     7, "10:30 AM", 150, 460),
        (91, "Screen 2 - Standard", 8, "02:30 PM", 185, 270),
        (91, "Screen 3 - Premium",  9, "07:00 PM", 120, 360),
        # Hall 92 — Sudarshan 70mm (Visakhapatnam)
        (92, "Screen 1 - 70mm",    10, "10:00 AM", 600, 200),
        (92, "Screen 2 - 70mm",    11, "02:00 PM", 600, 200),
        (92, "Screen 3 - 70mm",    12, "07:00 PM", 600, 200),
    ]),

    # ── Snack Menu (35+ items across 6 categories) ─────────────────
    ("INSERT OR IGNORE INTO snack_menu (name, category, price, description) VALUES (?,?,?,?)", [
        # Popcorn
        ("Classic Salted Popcorn (Lg)",  "Popcorn",   180, "Buttery salted popcorn, large bucket"),
        ("Classic Salted Popcorn (Sm)",  "Popcorn",   100, "Buttery salted popcorn, small cup"),
        ("Cheese Popcorn (Lg)",          "Popcorn",   220, "Loaded with cheddar cheese, large"),
        ("Cheese Popcorn (Sm)",          "Popcorn",   130, "Loaded with cheddar cheese, small"),
        ("Caramel Popcorn (Lg)",         "Popcorn",   200, "Sweet caramel coated popcorn"),
        ("Peri Peri Popcorn",            "Popcorn",   210, "Spicy peri peri flavoured popcorn"),
        ("Butter Scotch Popcorn",        "Popcorn",   215, "Sweet butterscotch glazed popcorn"),
        ("Mix Popcorn (Half & Half)",    "Popcorn",   230, "Half cheese + half caramel, large"),

        # Snacks
        ("Nachos with Salsa",            "Snacks",    250, "Crispy nachos with spicy salsa dip"),
        ("Cheese Nachos",                "Snacks",    290, "Nachos with melted cheese sauce"),
        ("Peri Peri Nachos",             "Snacks",    270, "Nachos tossed in peri peri spice"),
        ("Hot Dog",                      "Snacks",    220, "Classic American beef/veg hot dog"),
        ("Corn on the Cob",              "Snacks",    120, "Grilled corn with butter & spices"),
        ("French Fries (Lg)",            "Snacks",    160, "Golden crispy fries, large"),
        ("Peri Peri Fries",              "Snacks",    180, "Fries tossed in peri peri masala"),
        ("Cheese Fries",                 "Snacks",    210, "Fries drizzled with cheese sauce"),
        ("Spring Rolls (4 pcs)",         "Snacks",    200, "Crispy vegetable spring rolls"),
        ("Paneer Tikka Skewers",         "Snacks",    280, "Tandoor-spiced paneer skewers"),
        ("Chicken Wings (6 pcs)",        "Snacks",    350, "Spicy fried chicken wings"),

        # Meals
        ("Veg Burger Combo",             "Meals",     380, "Veg burger + fries + soft drink"),
        ("Chicken Burger Combo",         "Meals",     450, "Chicken burger + fries + soft drink"),
        ("Veg Pizza Slice",              "Meals",     220, "Single slice, margherita / veg supreme"),
        ("Chicken Pizza Slice",          "Meals",     270, "Single slice, chicken tikka / BBQ"),
        ("Veg Wrap",                     "Meals",     240, "Chapati wrap with paneer & veggies"),
        ("Chicken Wrap",                 "Meals",     290, "Chapati wrap with spiced chicken"),
        ("Pasta in Red Sauce",           "Meals",     260, "Penne pasta in spicy arrabbiata"),

        # Beverages
        ("Cold Coffee",                  "Beverages", 150, "Chilled blended coffee with milk"),
        ("Cappuccino",                   "Beverages", 130, "Hot frothy cappuccino"),
        ("Soft Drink (Lg)",              "Beverages", 120, "Pepsi / 7Up / Mountain Dew, large"),
        ("Soft Drink (Sm)",              "Beverages", 80,  "Pepsi / 7Up / Mountain Dew, small"),
        ("Fresh Lime Soda",              "Beverages", 100, "Sweet or salty fresh lime soda"),
        ("Mango Frooti",                 "Beverages", 60,  "Chilled Frooti mango drink"),
        ("Mineral Water (1L)",           "Beverages", 50,  "Bisleri / Kinley bottled water"),
        ("Masala Chai",                  "Beverages", 80,  "Spiced Indian tea, hot"),

        # Combos
        ("Combo Meal A",                 "Combos",    490, "Large popcorn + nachos + 2 soft drinks"),
        ("Combo Meal B",                 "Combos",    580, "Burger + large popcorn + 2 soft drinks"),
        ("Combo Meal C",                 "Combos",    650, "2 burgers + 2 fries + 2 soft drinks"),
        ("Date Night Combo",             "Combos",    750, "2 popcorns + 2 nachos + 2 cold coffees"),
        ("Kids Combo",                   "Combos",    320, "Small popcorn + fries + soft drink + candy"),
        ("Snack Platter",                "Combos",    520, "Nachos + spring rolls + fries + 2 drinks"),

        # Desserts
        ("Ice Cream Tub",                "Desserts",  180, "Vanilla / Chocolate / Strawberry"),
        ("Chocolate Brownie",            "Desserts",  150, "Warm fudgy brownie with ice cream"),
        ("Churros (5 pcs)",              "Desserts",  200, "Cinnamon sugar churros with dip"),
        ("Waffle Cone Ice Cream",        "Desserts",  120, "Single scoop waffle cone"),
    ]),
]


# ── Main Function ──────────────────────────────────────────────────────────────

def init_db():
    # Delete existing DB so we always start clean (no duplicates)
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
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
    print("\n📊 Seeded Data Summary:")
    print("   🏙️  Cities  : 26 (A–Z)")
    print("   🏛️  Halls   : 90+ across all cities")
    print("   🎬  Movies  : 12")
    print("   🍿  Snacks  : 44 items across 6 categories")
    print("\n🔑 Demo Login Credentials:")
    print("   Customer  → Phone: 9876543210   | Password: password123")
    print("   Manager   → ID:    MGR001        | Password: mgr@001")


if __name__ == '__main__':
    init_db()
