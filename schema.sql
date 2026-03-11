-- ============================================================
--  CineVerse — Cinema Management System
--  File: schema.sql
--  Description: Complete SQL schema with all 9 tables.
--               For reference / documentation purposes.
--               The actual DB is created by running init_db.py
-- ============================================================


-- Table 1: users — registered customer accounts
CREATE TABLE IF NOT EXISTS users (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    name       TEXT    NOT NULL,
    phone      TEXT    UNIQUE NOT NULL,   -- login identifier
    password   TEXT    NOT NULL,          -- SHA-256 hashed
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- Table 2: managers — management staff (separate from customers)
CREATE TABLE IF NOT EXISTS managers (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    name         TEXT NOT NULL,
    manager_code TEXT UNIQUE NOT NULL,    -- e.g. MGR001
    password     TEXT NOT NULL            -- SHA-256 hashed
);


-- Table 3: halls — physical cinema buildings
CREATE TABLE IF NOT EXISTS halls (
    id      INTEGER PRIMARY KEY AUTOINCREMENT,
    name    TEXT NOT NULL,                -- e.g. PVR Cinemas
    city    TEXT NOT NULL,                -- e.g. Mumbai
    address TEXT
);


-- Table 4: movies — movie catalogue
CREATE TABLE IF NOT EXISTS movies (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    title         TEXT    NOT NULL,
    genre         TEXT,
    duration_mins INTEGER,
    language      TEXT DEFAULT 'English',
    rating        TEXT                    -- e.g. U/A, A
);


-- Table 5: screens — auditoriums within a hall
CREATE TABLE IF NOT EXISTS screens (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    hall_id      INTEGER NOT NULL,
    name         TEXT    NOT NULL,        -- e.g. Screen 1 - IMAX
    movie_id     INTEGER,                 -- currently playing movie
    show_time    TEXT,                    -- e.g. 10:00 AM
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
    booking_date TEXT    NOT NULL,        -- YYYY-MM-DD
    seats_booked INTEGER NOT NULL,
    status       TEXT    DEFAULT 'confirmed',
    created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id)   REFERENCES users(id),
    FOREIGN KEY (screen_id) REFERENCES screens(id)
);


-- Table 7: snack_menu — food and drinks available for pre-order
CREATE TABLE IF NOT EXISTS snack_menu (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT NOT NULL,
    category    TEXT,                     -- Snacks | Meals | Beverages | Combos | Desserts
    price       REAL NOT NULL,
    description TEXT
);


-- Table 8: snack_orders — pre-ordered snacks linked to a booking
CREATE TABLE IF NOT EXISTS snack_orders (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    booking_id INTEGER NOT NULL,
    snack_id   INTEGER NOT NULL,
    quantity   INTEGER DEFAULT 1,
    FOREIGN KEY (booking_id) REFERENCES bookings(id),
    FOREIGN KEY (snack_id)   REFERENCES snack_menu(id)
);


-- Table 9: payments — payment record per booking
CREATE TABLE IF NOT EXISTS payments (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    booking_id INTEGER NOT NULL,
    amount     REAL    NOT NULL,
    method     TEXT    DEFAULT 'card',    -- card | upi | netbanking | wallet
    paid_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (booking_id) REFERENCES bookings(id)
);


-- ============================================================
--  RELATIONSHIPS SUMMARY
-- ============================================================
--  users       ──< bookings      (1 user → many bookings)
--  halls       ──< screens       (1 hall → many screens)
--  movies      ──< screens       (1 movie shown on many screens)
--  screens     ──< bookings      (1 screen → many bookings)
--  bookings    ──< snack_orders  (1 booking → 1 snack order)
--  snack_menu  ──< snack_orders  (1 snack item → many orders)
--  bookings    ──< payments      (1 booking → 1 payment)
-- ============================================================
