# ============================================================
#  CineVerse — Cinema Management System
#  File: init_db.py
#  Description: Database initialization script.
#               Creates all 9 SQL tables and seeds sample data.
#               24 Indian cities with halls, screens and managers.
# ============================================================

import sqlite3
import os
import hashlib

DB_PATH = os.path.join(os.path.dirname(__file__), 'instance', 'cinema.db')
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)


def hash_password(p):
    return hashlib.sha256(p.encode()).hexdigest()


SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    name       TEXT    NOT NULL,
    phone      TEXT    UNIQUE NOT NULL,
    password   TEXT    NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS managers (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    name         TEXT NOT NULL,
    manager_code TEXT UNIQUE NOT NULL,
    password     TEXT NOT NULL,
    city         TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS halls (
    id      INTEGER PRIMARY KEY AUTOINCREMENT,
    name    TEXT NOT NULL,
    city    TEXT NOT NULL,
    address TEXT
);

CREATE TABLE IF NOT EXISTS movies (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    title         TEXT    NOT NULL,
    genre         TEXT,
    duration_mins INTEGER,
    language      TEXT DEFAULT 'English',
    rating        TEXT
);

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

CREATE TABLE IF NOT EXISTS snack_menu (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT NOT NULL,
    category    TEXT,
    price       REAL NOT NULL,
    description TEXT
);

CREATE TABLE IF NOT EXISTS snack_orders (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    booking_id INTEGER NOT NULL,
    snack_id   INTEGER NOT NULL,
    quantity   INTEGER DEFAULT 1,
    person_num INTEGER DEFAULT 1,
    FOREIGN KEY (booking_id) REFERENCES bookings(id),
    FOREIGN KEY (snack_id)   REFERENCES snack_menu(id)
);

CREATE TABLE IF NOT EXISTS payments (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    booking_id INTEGER NOT NULL,
    amount     REAL    NOT NULL,
    method     TEXT    DEFAULT 'card',
    paid_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (booking_id) REFERENCES bookings(id)
);
"""


SEED_DATA = [

    # ── Users ──────────────────────────────────────────────────────
    ("INSERT OR IGNORE INTO users (name, phone, password) VALUES (?,?,?)", [
        ("Arjun Sharma",  "9876543210", hash_password("password123")),
        ("Priya Patel",   "9123456780", hash_password("priya456")),
        ("Rahul Mehta",   "9988776655", hash_password("rahul789")),
    ]),

    # ── Managers (one per city) ────────────────────────────────────
    ("INSERT OR IGNORE INTO managers (name, manager_code, password, city) VALUES (?,?,?,?)", [
        ("Vikram Singh",      "MGR-MUM", hash_password("mgr@mumbai"),          "Mumbai"),
        ("Neha Kapoor",       "MGR-DEL", hash_password("mgr@delhi"),           "Delhi"),
        ("Suresh Reddy",      "MGR-BLR", hash_password("mgr@bangalore"),       "Bangalore"),
        ("Priya Nair",        "MGR-CHN", hash_password("mgr@chennai"),         "Chennai"),
        ("Arnab Das",         "MGR-KOL", hash_password("mgr@kolkata"),         "Kolkata"),
        ("Ramesh Rao",        "MGR-HYD", hash_password("mgr@hyderabad"),       "Hyderabad"),
        ("Sneha Joshi",       "MGR-PUN", hash_password("mgr@pune"),            "Pune"),
        ("Kiran Shah",        "MGR-AHM", hash_password("mgr@ahmedabad"),       "Ahmedabad"),
        ("Pooja Sharma",      "MGR-JAI", hash_password("mgr@jaipur"),          "Jaipur"),
        ("Amit Verma",        "MGR-LUC", hash_password("mgr@lucknow"),         "Lucknow"),
        ("Riya Patel",        "MGR-SUR", hash_password("mgr@surat"),           "Surat"),
        ("Anoop Menon",       "MGR-KOC", hash_password("mgr@kochi"),           "Kochi"),
        ("Gurpreet Singh",    "MGR-CHD", hash_password("mgr@chandigarh"),      "Chandigarh"),
        ("Deepak Tiwari",     "MGR-BHO", hash_password("mgr@bhopal"),          "Bhopal"),
        ("Rahul Gupta",       "MGR-IND", hash_password("mgr@indore"),          "Indore"),
        ("Sanjay Deshmukh",   "MGR-NAG", hash_password("mgr@nagpur"),          "Nagpur"),
        ("Anjali Singh",      "MGR-PAT", hash_password("mgr@patna"),           "Patna"),
        ("Rounak Narayan",    "MGR-BHU", hash_password("mgr@bhubaneswar"),     "Bhubaneswar"),
        ("Venkat Rao",        "MGR-VIZ", hash_password("mgr@visakhapatnam"),   "Visakhapatnam"),
        ("Kavitha Rajan",     "MGR-COI", hash_password("mgr@coimbatore"),      "Coimbatore"),
        ("Praveen Kumar",     "MGR-MYS", hash_password("mgr@mysore"),          "Mysore"),
        ("Hardik Patel",      "MGR-VAD", hash_password("mgr@vadodara"),        "Vadodara"),
        ("Lakshmi Pillai",    "MGR-TVM", hash_password("mgr@trivandrum"),      "Thiruvananthapuram"),
        ("Bhaskar Dutta",     "MGR-GUW", hash_password("mgr@guwahati"),        "Guwahati"),
    ]),

    # ── Movies ─────────────────────────────────────────────────────
    ("INSERT OR IGNORE INTO movies (title, genre, duration_mins, language, rating) VALUES (?,?,?,?,?)", [
        ("Kalki 2898 AD",  "Sci-Fi/Action",    181, "Telugu",  "U/A"),
        ("Fighter",        "Action/Thriller",  166, "Hindi",   "UA"),
        ("Animal",         "Action/Drama",     201, "Hindi",   "A"),
        ("Dunki",          "Drama/Comedy",     161, "Hindi",   "U/A"),
        ("Salaar",         "Action",           173, "Telugu",  "A"),
        ("Sam Bahadur",    "Biographical",     156, "Hindi",   "U/A"),
        ("Oppenheimer",    "Historical Drama", 180, "English", "UA"),
        ("Dune Part 2",    "Sci-Fi",           166, "English", "UA"),
        ("Pushpa 2",       "Action/Drama",     190, "Telugu",  "A"),
        ("Stree 2",        "Horror/Comedy",    135, "Hindi",   "U/A"),
        ("Singham Again",  "Action",           150, "Hindi",   "U/A"),
        ("Devara",         "Action/Thriller",  166, "Telugu",  "A"),
    ]),

    # ── Cinema Halls ───────────────────────────────────────────────
    ("INSERT OR IGNORE INTO halls (name, city, address) VALUES (?,?,?)", [
        # Mumbai
        ("PVR Cinemas",            "Mumbai",             "Phoenix Mall, Lower Parel"),
        ("INOX Grand",             "Mumbai",             "R-City Mall, Ghatkopar"),
        # Delhi
        ("Cinepolis Gold",         "Delhi",              "DLF Mall of India, Noida"),
        ("PVR Director's Cut",     "Delhi",              "Ambience Mall, Vasant Kunj"),
        # Bangalore
        ("INOX Lido",              "Bangalore",          "MG Road, Bangalore"),
        ("Cinepolis VIP",          "Bangalore",          "Orion Mall, Malleswaram"),
        # Chennai
        ("PVR Luxe",               "Chennai",            "Express Avenue, Royapettah"),
        ("AGS Cinemas",            "Chennai",            "Grand Square Mall, Anna Nagar"),
        # Kolkata
        ("INOX South City",        "Kolkata",            "South City Mall, Prince Anwar Shah Road"),
        ("Cinepolis Acropolis",    "Kolkata",            "Acropolis Mall, Rajdanga"),
        # Hyderabad
        ("PVR IMAX Hyderabad",     "Hyderabad",          "Inorbit Mall, Cyberabad"),
        ("Cinepolis Hyderabad",    "Hyderabad",          "Manjeera Mall, Kukatpally"),
        # Pune
        ("PVR Pune",               "Pune",               "Phoenix Marketcity, Viman Nagar"),
        ("INOX Bund Garden",       "Pune",               "Bund Garden Road, Pune"),
        # Ahmedabad
        ("PVR Ahmedabad",          "Ahmedabad",          "Achlaj Mall, SG Highway"),
        ("INOX Ahmedabad",         "Ahmedabad",          "Alpha One Mall, Vastrapur"),
        # Jaipur
        ("PVR Jaipur",             "Jaipur",             "Crystal Palm Mall, Tonk Road"),
        ("Cinepolis Jaipur",       "Jaipur",             "GT Central Mall, Ajmer Road"),
        # Lucknow
        ("PVR Lucknow",            "Lucknow",            "Phoenix Palassio, Faizabad Road"),
        ("INOX Lucknow",           "Lucknow",            "Fun Republic Mall, Gomti Nagar"),
        # Surat
        ("PVR Surat",              "Surat",              "VR Mall, Dumas Road"),
        ("INOX Surat",             "Surat",              "L'Lamel Mall, Adajan"),
        # Kochi
        ("PVR Kochi",              "Kochi",              "Lulu Mall, Edapally"),
        ("Cinepolis Kochi",        "Kochi",              "Centre Square Mall, MG Road"),
        # Chandigarh
        ("PVR Chandigarh",         "Chandigarh",         "Elante Mall, Industrial Area"),
        ("INOX Chandigarh",        "Chandigarh",         "Centra Mall, Sector 22"),
        # Bhopal
        ("PVR Bhopal",             "Bhopal",             "DB City Mall, Arera Hills"),
        ("INOX Bhopal",            "Bhopal",             "Treasure Island Mall, MP Nagar"),
        # Indore
        ("PVR Indore",             "Indore",             "Treasure Island Mall, MG Road"),
        ("INOX Indore",            "Indore",             "C21 Mall, Scheme 54"),
        # Nagpur
        ("PVR Nagpur",             "Nagpur",             "Empress Mall, Chhindwara Road"),
        ("INOX Nagpur",            "Nagpur",             "Poonam Mall, Wardha Road"),
        # Patna
        ("PVR Patna",              "Patna",              "P&M Mall, Fraser Road"),
        ("INOX Patna",             "Patna",              "Patna Central Mall, Exhibition Road"),
        # Bhubaneswar
        ("PVR Bhubaneswar",        "Bhubaneswar",        "Esplanade Mall, Rasulgarh"),
        ("Cinepolis Bhubaneswar",  "Bhubaneswar",        "Odisha Mall, Janpath"),
        # Visakhapatnam
        ("PVR Vizag",              "Visakhapatnam",      "CMR Central Mall, Siripuram"),
        ("INOX Vizag",             "Visakhapatnam",      "Mega Mall, MVP Colony"),
        # Coimbatore
        ("PVR Coimbatore",         "Coimbatore",         "Prozone Mall, Avinashi Road"),
        ("INOX Coimbatore",        "Coimbatore",         "Brookefields Mall, Brookefields"),
        # Mysore
        ("PVR Mysore",             "Mysore",             "Forum Mysore Mall, Nazarbad"),
        ("INOX Mysore",            "Mysore",             "Silver Tower, Sayyaji Rao Road"),
        # Vadodara
        ("PVR Vadodara",           "Vadodara",           "Inorbit Mall, Gotri Road"),
        ("INOX Vadodara",          "Vadodara",           "Vadodara Central Mall, Race Course"),
        # Thiruvananthapuram
        ("PVR Trivandrum",         "Thiruvananthapuram", "LuLu Mall, Thiruvananthapuram"),
        ("INOX Trivandrum",        "Thiruvananthapuram", "Oberon Mall, Edapally"),
        # Guwahati
        ("PVR Guwahati",           "Guwahati",           "Gopinath Nagar, GS Road"),
        ("INOX Guwahati",          "Guwahati",           "Baruah Complex, Fancy Bazar"),
    ]),

    # ── Screens ────────────────────────────────────────────────────
    ("INSERT OR IGNORE INTO screens (hall_id, name, movie_id, show_time, total_seats, ticket_price) VALUES (?,?,?,?,?,?)", [
        # Mumbai — Hall 1 (PVR)
        (1,  "Screen 1 - IMAX",     1,  "10:00 AM", 150, 450),
        (1,  "Screen 2 - 4DX",      2,  "01:30 PM", 100, 550),
        (1,  "Screen 3 - Standard", 3,  "06:00 PM", 200, 280),
        # Mumbai — Hall 2 (INOX)
        (2,  "Screen A - Gold",     4,  "11:00 AM",  80, 500),
        (2,  "Screen B - Standard", 5,  "03:00 PM", 180, 300),
        # Delhi — Hall 3 (Cinepolis)
        (3,  "Screen 1 - IMAX",     6,  "10:30 AM", 160, 480),
        (3,  "Screen 2 - Standard", 7,  "05:30 PM", 190, 270),
        # Delhi — Hall 4 (PVR)
        (4,  "Auditorium 1",        8,  "11:30 AM", 200, 350),
        (4,  "Auditorium 2",        9,  "04:00 PM", 180, 350),
        # Bangalore — Hall 5 (INOX)
        (5,  "Screen 1 - Luxe",     10, "09:00 AM",  90, 520),
        (5,  "Screen 2 - Standard", 11, "12:30 PM", 170, 290),
        # Bangalore — Hall 6 (Cinepolis)
        (6,  "VIP Screen 1",        12, "10:00 AM",  60, 700),
        (6,  "VIP Screen 2",        1,  "02:30 PM",  60, 700),
        # Chennai — Hall 7 (PVR)
        (7,  "Screen 1 - IMAX",     2,  "10:00 AM", 145, 460),
        (7,  "Screen 2 - Standard", 3,  "01:00 PM", 185, 280),
        # Chennai — Hall 8 (AGS)
        (8,  "Screen A",            4,  "11:00 AM", 160, 320),
        (8,  "Screen B - 4K",       5,  "03:30 PM", 120, 400),
        # Kolkata — Hall 9 (INOX)
        (9,  "Screen 1 - IMAX",     6,  "10:00 AM", 140, 440),
        (9,  "Screen 2 - Standard", 7,  "02:00 PM", 180, 280),
        # Kolkata — Hall 10 (Cinepolis)
        (10, "Screen A - Gold",     8,  "11:00 AM",  90, 480),
        (10, "Screen B - Standard", 9,  "05:00 PM", 160, 300),
        # Hyderabad — Hall 11 (PVR IMAX)
        (11, "Screen 1 - IMAX",     10, "10:30 AM", 155, 470),
        (11, "Screen 2 - 4DX",      11, "02:30 PM", 105, 560),
        # Hyderabad — Hall 12 (Cinepolis)
        (12, "Screen A - Standard", 12, "11:00 AM", 175, 290),
        (12, "Screen B - Dolby",    1,  "06:00 PM", 130, 420),
        # Pune — Hall 13 (PVR)
        (13, "Screen 1 - IMAX",     2,  "10:00 AM", 145, 450),
        (13, "Screen 2 - Standard", 3,  "03:00 PM", 185, 280),
        # Pune — Hall 14 (INOX)
        (14, "Screen A - Gold",     4,  "12:00 PM",  85, 490),
        (14, "Screen B - Standard", 5,  "06:30 PM", 165, 300),
        # Ahmedabad — Hall 15 (PVR)
        (15, "Screen 1 - IMAX",     6,  "10:00 AM", 150, 440),
        (15, "Screen 2 - Standard", 7,  "04:00 PM", 190, 270),
        # Ahmedabad — Hall 16 (INOX)
        (16, "Screen A - Dolby",    8,  "11:30 AM", 130, 410),
        (16, "Screen B - Standard", 9,  "07:00 PM", 170, 290),
        # Jaipur — Hall 17 (PVR)
        (17, "Screen 1 - Standard", 10, "10:30 AM", 160, 320),
        (17, "Screen 2 - Premium",  11, "05:00 PM", 120, 380),
        # Jaipur — Hall 18 (Cinepolis)
        (18, "Screen A - Standard", 12, "12:00 PM", 175, 280),
        (18, "Screen B - Gold",     1,  "07:30 PM",  85, 460),
        # Lucknow — Hall 19 (PVR)
        (19, "Screen 1 - IMAX",     2,  "10:00 AM", 145, 440),
        (19, "Screen 2 - Standard", 3,  "04:30 PM", 185, 270),
        # Lucknow — Hall 20 (INOX)
        (20, "Screen A - Standard", 4,  "11:00 AM", 170, 290),
        (20, "Screen B - Dolby",    5,  "06:00 PM", 130, 400),
        # Surat — Hall 21 (PVR)
        (21, "Screen 1 - Standard", 6,  "10:30 AM", 155, 300),
        (21, "Screen 2 - Premium",  7,  "05:30 PM", 115, 370),
        # Surat — Hall 22 (INOX)
        (22, "Screen A - Standard", 8,  "12:00 PM", 165, 280),
        (22, "Screen B - Gold",     9,  "07:00 PM",  80, 450),
        # Kochi — Hall 23 (PVR)
        (23, "Screen 1 - IMAX",     10, "10:00 AM", 150, 460),
        (23, "Screen 2 - Standard", 11, "03:30 PM", 185, 280),
        # Kochi — Hall 24 (Cinepolis)
        (24, "Screen A - Gold",     12, "11:30 AM",  85, 490),
        (24, "Screen B - Standard", 1,  "06:30 PM", 160, 300),
        # Chandigarh — Hall 25 (PVR)
        (25, "Screen 1 - IMAX",     2,  "10:00 AM", 145, 440),
        (25, "Screen 2 - Standard", 3,  "04:00 PM", 180, 270),
        # Chandigarh — Hall 26 (INOX)
        (26, "Screen A - Dolby",    4,  "12:00 PM", 125, 400),
        (26, "Screen B - Standard", 5,  "07:00 PM", 165, 290),
        # Bhopal — Hall 27 (PVR)
        (27, "Screen 1 - Standard", 6,  "10:30 AM", 155, 300),
        (27, "Screen 2 - Premium",  7,  "05:00 PM", 115, 360),
        # Bhopal — Hall 28 (INOX)
        (28, "Screen A - Standard", 8,  "11:00 AM", 165, 280),
        (28, "Screen B - Gold",     9,  "06:30 PM",  80, 440),
        # Indore — Hall 29 (PVR)
        (29, "Screen 1 - IMAX",     10, "10:00 AM", 145, 430),
        (29, "Screen 2 - Standard", 11, "04:00 PM", 180, 270),
        # Indore — Hall 30 (INOX)
        (30, "Screen A - Dolby",    12, "12:00 PM", 125, 390),
        (30, "Screen B - Standard", 1,  "07:00 PM", 165, 280),
        # Nagpur — Hall 31 (PVR)
        (31, "Screen 1 - Standard", 2,  "10:30 AM", 155, 290),
        (31, "Screen 2 - Premium",  3,  "05:00 PM", 110, 350),
        # Nagpur — Hall 32 (INOX)
        (32, "Screen A - Standard", 4,  "11:00 AM", 160, 270),
        (32, "Screen B - Gold",     5,  "06:30 PM",  80, 430),
        # Patna — Hall 33 (PVR)
        (33, "Screen 1 - Standard", 6,  "10:00 AM", 150, 280),
        (33, "Screen 2 - Premium",  7,  "04:30 PM", 110, 340),
        # Patna — Hall 34 (INOX)
        (34, "Screen A - Standard", 8,  "11:30 AM", 160, 270),
        (34, "Screen B - Dolby",    9,  "07:00 PM", 120, 380),
        # Bhubaneswar — Hall 35 (PVR)
        (35, "Screen 1 - IMAX",     10, "10:00 AM", 145, 430),
        (35, "Screen 2 - Standard", 11, "04:00 PM", 180, 270),
        # Bhubaneswar — Hall 36 (Cinepolis)
        (36, "Screen A - Gold",     12, "11:00 AM",  80, 460),
        (36, "Screen B - Standard", 1,  "06:30 PM", 160, 290),
        # Visakhapatnam — Hall 37 (PVR)
        (37, "Screen 1 - IMAX",     2,  "10:30 AM", 145, 440),
        (37, "Screen 2 - Standard", 3,  "04:30 PM", 180, 270),
        # Visakhapatnam — Hall 38 (INOX)
        (38, "Screen A - Dolby",    4,  "12:00 PM", 125, 390),
        (38, "Screen B - Standard", 5,  "07:00 PM", 160, 280),
        # Coimbatore — Hall 39 (PVR)
        (39, "Screen 1 - Standard", 6,  "10:00 AM", 150, 290),
        (39, "Screen 2 - Premium",  7,  "05:00 PM", 110, 350),
        # Coimbatore — Hall 40 (INOX)
        (40, "Screen A - Standard", 8,  "11:30 AM", 160, 270),
        (40, "Screen B - Gold",     9,  "06:30 PM",  80, 430),
        # Mysore — Hall 41 (PVR)
        (41, "Screen 1 - Standard", 10, "10:30 AM", 145, 280),
        (41, "Screen 2 - Premium",  11, "04:30 PM", 105, 340),
        # Mysore — Hall 42 (INOX)
        (42, "Screen A - Standard", 12, "11:00 AM", 155, 270),
        (42, "Screen B - Dolby",    1,  "06:00 PM", 120, 370),
        # Vadodara — Hall 43 (PVR)
        (43, "Screen 1 - IMAX",     2,  "10:00 AM", 145, 420),
        (43, "Screen 2 - Standard", 3,  "04:00 PM", 175, 270),
        # Vadodara — Hall 44 (INOX)
        (44, "Screen A - Dolby",    4,  "12:00 PM", 120, 380),
        (44, "Screen B - Standard", 5,  "07:00 PM", 160, 280),
        # Thiruvananthapuram — Hall 45 (PVR)
        (45, "Screen 1 - IMAX",     6,  "10:00 AM", 145, 440),
        (45, "Screen 2 - Standard", 7,  "04:30 PM", 175, 270),
        # Thiruvananthapuram — Hall 46 (INOX)
        (46, "Screen A - Gold",     8,  "11:30 AM",  80, 460),
        (46, "Screen B - Standard", 9,  "06:30 PM", 155, 280),
        # Guwahati — Hall 47 (PVR)
        (47, "Screen 1 - Standard", 10, "10:30 AM", 140, 280),
        (47, "Screen 2 - Premium",  11, "05:00 PM", 100, 340),
        # Guwahati — Hall 48 (INOX)
        (48, "Screen A - Standard", 12, "11:00 AM", 150, 270),
        (48, "Screen B - Dolby",    1,  "06:30 PM", 115, 360),
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
        ("Masala Chai",             "Beverages", 60,  "Hot spiced Indian tea"),
        ("Samosa (2 pcs)",          "Snacks",    80,  "Crispy fried samosas with chutney"),
        ("Veg Sandwich",            "Meals",     150, "Grilled vegetable sandwich"),
        ("Chicken Wrap",            "Meals",     220, "Spicy chicken wrap with sauce"),
        ("Brownie + Ice Cream",     "Desserts",  220, "Warm brownie with vanilla scoop"),
        ("Fruit Juice (Large)",     "Beverages", 130, "Fresh seasonal fruit juice"),
    ]),
]


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
    print("\n🏙️ 24 Cities Added!")
    print("\n🔑 Demo Login Credentials:")
    print("   Customer      → Phone: 9876543210  | Password: password123")
    print("   Mumbai Mgr    → MGR-MUM            | mgr@mumbai")
    print("   Delhi Mgr     → MGR-DEL            | mgr@delhi")
    print("   Bangalore Mgr → MGR-BLR            | mgr@bangalore")
    print("   Chennai Mgr   → MGR-CHN            | mgr@chennai")
    print("   Kolkata Mgr   → MGR-KOL            | mgr@kolkata")
    print("   Hyderabad Mgr → MGR-HYD            | mgr@hyderabad")
    print("   ... and 18 more cities!")


if __name__ == '__main__':
    init_db()
