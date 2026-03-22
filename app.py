
# ============================================================
#  CineVerse — Cinema Management System
#  File: app.py
#  Description: Main Flask application — all routes, API
#               endpoints, and database query logic.
#
#  Sections:
#    1. App Configuration & Helpers
#    2. Authentication   (login, signup, logout)
#    3. Role Selection
#    4. Customer Module  (booking, payment, confirmation)
#    5. Management Module (halls, screens, movie updates)
#    6. Hospitality Module (schedule, snack delivery)
#
#  Run:   python app.py
#  Open:  http://localhost:5000
# ============================================================

from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import sqlite3
import os
from datetime import datetime
import hashlib

# ── App Configuration ──────────────────────────────────────────────────────────

app = Flask(__name__)
app.secret_key = 'cinema_secret_key_2024'   # Change this in production

# Path to SQLite database file
DB_PATH = os.path.join(os.path.dirname(__file__), 'instance', 'cinema.db')


# ── Helper Functions ───────────────────────────────────────────────────────────

def get_db():
    """Open a new database connection. Rows returned as dict-like objects."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def hash_password(password):
    """Hash a plain-text password using SHA-256 before storing in DB."""
    return hashlib.sha256(password.encode()).hexdigest()


# ============================================================
#  SECTION 2 — AUTHENTICATION
# ============================================================

@app.route('/')
def index():
    """Root URL — redirect to login page."""
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    GET  — Show login form.
    POST — Validate phone + password, create session, go to role selection.
    """
    error = None
    if request.method == 'POST':
        phone    = request.form['phone']
        password = hash_password(request.form['password'])
        db   = get_db()
        user = db.execute(
            'SELECT * FROM users WHERE phone=? AND password=?',
            (phone, password)
        ).fetchone()
        db.close()
        if user:
            session['user_id']    = user['id']
            session['user_name']  = user['name']
            session['user_phone'] = user['phone']
            return redirect(url_for('role_select'))
        error = 'Invalid phone number or password.'
    return render_template('login.html', error=error)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    """
    GET  — Show sign-up form.
    POST — Register new user, redirect to login on success.
    """
    error   = None
    success = None
    if request.method == 'POST':
        name     = request.form['name']
        phone    = request.form['phone']
        password = hash_password(request.form['password'])
        db       = get_db()
        existing = db.execute('SELECT id FROM users WHERE phone=?', (phone,)).fetchone()
        if existing:
            error = 'Phone number already registered.'
        else:
            db.execute(
                'INSERT INTO users (name, phone, password) VALUES (?,?,?)',
                (name, phone, password)
            )
            db.commit()
            success = 'Account created! Please login.'
        db.close()
    return render_template('signup.html', error=error, success=success)


@app.route('/logout')
def logout():
    """Clear session and redirect to login."""
    session.clear()
    return redirect(url_for('login'))


# ============================================================
#  SECTION 3 — ROLE SELECTION
# ============================================================

@app.route('/role-select')
def role_select():
    """Show role selection: Customer | Management | Hospitality Staff."""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('role_select.html', name=session['user_name'])


# ============================================================
#  SECTION 4 — CUSTOMER MODULE
# ============================================================

@app.route('/customer')
def customer():
    """
    Customer booking page.
    Loads cities + snack menu from DB on page load.
    Halls and screens load dynamically via AJAX.
    """
    if 'user_id' not in session:
        return redirect(url_for('login'))
    db     = get_db()
    cities = db.execute('SELECT DISTINCT city FROM halls ORDER BY city').fetchall()
    snacks = db.execute('SELECT * FROM snack_menu ORDER BY name').fetchall()
    db.close()
    return render_template('customer.html', cities=cities, snacks=snacks)


@app.route('/api/halls')
def api_halls():
    """
    AJAX API — Return halls for a given city as JSON.
    Query param: ?city=Mumbai
    """
    city  = request.args.get('city')
    db    = get_db()
    halls = db.execute('SELECT id, name FROM halls WHERE city=?', (city,)).fetchall()
    db.close()
    return jsonify([dict(h) for h in halls])


@app.route('/api/screens')
def api_screens():
    """
    AJAX API — Return screens for a given hall with live seat availability.
    Query param: ?hall_id=1
    """
    hall_id = request.args.get('hall_id')
    db      = get_db()
    screens = db.execute('''
        SELECT s.id, s.name, m.title as movie, s.show_time, s.total_seats,
               s.total_seats - COALESCE(SUM(b.seats_booked), 0) AS available_seats,
               s.ticket_price
        FROM   screens s
        LEFT JOIN movies   m ON s.movie_id  = m.id
        LEFT JOIN bookings b ON b.screen_id = s.id AND b.status = 'confirmed'
        WHERE  s.hall_id = ?
        AND    s.movie_id IS NOT NULL
        GROUP  BY s.id
    ''', (hall_id,)).fetchall()
    db.close()
    return jsonify([dict(s) for s in screens])


@app.route('/customer/book', methods=['POST'])
def book():
    """
    Process booking form submission.
    Calculates total (tickets + snacks).
    Saves to session and renders payment page.
    """
    if 'user_id' not in session:
        return redirect(url_for('login'))

    data = {
        'date':      request.form['date'],
        'city':      request.form['city'],
        'hall_id':   request.form['hall_id'],
        'screen_id': request.form['screen_id'],
        'seats':     int(request.form['seats']),
        'snack_id':  request.form.get('snack_id') or None
    }

    db     = get_db()
    screen = db.execute('''
        SELECT s.*, m.title AS movie, h.name AS hall_name, h.city
        FROM   screens s
        JOIN   movies  m ON s.movie_id = m.id
        JOIN   halls   h ON s.hall_id  = h.id
        WHERE  s.id = ?
    ''', (data['screen_id'],)).fetchone()

    snack       = None
    snack_price = 0
    if data['snack_id']:
        snack       = db.execute('SELECT * FROM snack_menu WHERE id=?', (data['snack_id'],)).fetchone()
        snack_price = snack['price'] * data['seats']

    ticket_total = screen['ticket_price'] * data['seats']
    total        = ticket_total + snack_price
    db.close()

    session['pending_booking'] = {
        **data,
        'total':        total,
        'movie':        screen['movie'],
        'hall':         screen['hall_name'],
        'screen_name':  screen['name'],
        'show_time':    screen['show_time'],
        'snack_name':   snack['name'] if snack else 'None',
        'ticket_price': screen['ticket_price'],
        'snack_price':  snack_price
    }

    return render_template(
        'payment.html',
        booking=session['pending_booking'],
        screen=dict(screen),
        snack=dict(snack) if snack else None,
        total=total
    )


@app.route('/customer/pay', methods=['POST'])
def pay():
    """
    Confirm payment and write booking to database.
    Inserts into: bookings, payments, snack_orders tables.
    """
    if 'user_id' not in session or 'pending_booking' not in session:
        return redirect(url_for('login'))

    b  = session['pending_booking']
    db = get_db()

    cur        = db.execute('''
        INSERT INTO bookings (user_id, screen_id, booking_date, seats_booked, status)
        VALUES (?, ?, ?, ?, 'confirmed')
    ''', (session['user_id'], b['screen_id'], b['date'], b['seats']))
    booking_id = cur.lastrowid

    db.execute(
        'INSERT INTO payments (booking_id, amount, method) VALUES (?, ?, ?)',
        (booking_id, b['total'], request.form.get('method', 'card'))
    )

    if b['snack_id']:
        db.execute(
            'INSERT INTO snack_orders (booking_id, snack_id, quantity) VALUES (?, ?, ?)',
            (booking_id, b['snack_id'], b['seats'])
        )

    db.commit()
    db.close()

    session['last_booking'] = {**b, 'booking_id': booking_id}
    session.pop('pending_booking', None)
    return redirect(url_for('confirmation'))


@app.route('/confirmation')
def confirmation():
    """Show the booking confirmation ticket."""
    if 'last_booking' not in session:
        return redirect(url_for('customer'))
    return render_template(
        'confirmation.html',
        booking=session['last_booking'],
        name=session['user_name']
    )


# ============================================================
#  SECTION 5 — MANAGEMENT MODULE
# ============================================================

@app.route('/management', methods=['GET', 'POST'])
def management():
    """
    GET  — Show manager login form.
    POST — Validate manager credentials (separate from user accounts).
    """
    if 'user_id' not in session:
        return redirect(url_for('login'))
    error = None
    if request.method == 'POST':
        mgr_id   = request.form['manager_id']
        mgr_pass = hash_password(request.form['manager_password'])
        db  = get_db()
        mgr = db.execute(
            'SELECT * FROM managers WHERE manager_code=? AND password=?',
            (mgr_id, mgr_pass)
        ).fetchone()
        db.close()
        if mgr:
            session['manager_id']   = mgr['id']
            session['manager_name'] = mgr['name']
            return redirect(url_for('management_dashboard'))
        error = 'Invalid Manager ID or Password.'
    return render_template('management_login.html', error=error)


@app.route('/management/dashboard')
def management_dashboard():
    """Show all cinema halls across all cities."""
    if 'manager_id' not in session:
        return redirect(url_for('management'))
    db    = get_db()
    halls = db.execute('SELECT * FROM halls ORDER BY city, name').fetchall()
    db.close()
    return render_template('management_dashboard.html', halls=halls, manager=session['manager_name'])


@app.route('/management/hall/<int:hall_id>')
def management_hall(hall_id):
    """
    Show all screens inside a specific hall.
    Includes booking counts, seats sold, current movie, show time.
    """
    if 'manager_id' not in session:
        return redirect(url_for('management'))
    db      = get_db()
    hall    = db.execute('SELECT * FROM halls WHERE id=?', (hall_id,)).fetchone()
    screens = db.execute('''
        SELECT s.*, m.title AS movie, m.genre, m.duration_mins,
               COUNT(b.id) AS bookings_count,
               COALESCE(SUM(b.seats_booked), 0) AS seats_sold
        FROM   screens s
        LEFT JOIN movies   m ON s.movie_id  = m.id
        LEFT JOIN bookings b ON b.screen_id = s.id AND b.status = 'confirmed'
        WHERE  s.hall_id = ?
        GROUP  BY s.id
    ''', (hall_id,)).fetchall()
    movies  = db.execute('SELECT * FROM movies ORDER BY title').fetchall()
    db.close()
    return render_template('management_hall.html', hall=hall, screens=screens, movies=movies)


@app.route('/management/screen/<int:screen_id>/bookings')
def screen_bookings(screen_id):
    """Show all confirmed bookings for a specific screen."""
    if 'manager_id' not in session:
        return redirect(url_for('management'))
    db       = get_db()
    screen   = db.execute('''
        SELECT s.*, m.title AS movie, h.name AS hall
        FROM   screens s
        JOIN   movies m ON s.movie_id = m.id
        JOIN   halls  h ON s.hall_id  = h.id
        WHERE  s.id = ?
    ''', (screen_id,)).fetchone()
    bookings = db.execute('''
        SELECT b.*, u.name AS customer, u.phone,
               p.amount, p.method,
               GROUP_CONCAT(sm.name) AS snacks
        FROM   bookings b
        JOIN   users       u  ON b.user_id    = u.id
        LEFT JOIN payments    p  ON p.booking_id = b.id
        LEFT JOIN snack_orders so ON so.booking_id = b.id
        LEFT JOIN snack_menu  sm ON sm.id = so.snack_id
        WHERE  b.screen_id = ? AND b.status = 'confirmed'
        GROUP  BY b.id
        ORDER  BY b.id DESC
    ''', (screen_id,)).fetchall()
    db.close()
    return render_template('screen_bookings.html', screen=screen, bookings=bookings)


@app.route('/management/screen/<int:screen_id>/change-movie', methods=['POST'])
def change_movie(screen_id):
    """Update the movie playing on a given screen."""
    if 'manager_id' not in session:
        return redirect(url_for('management'))
    movie_id = request.form['movie_id']
    db       = get_db()
    screen   = db.execute('SELECT hall_id FROM screens WHERE id=?', (screen_id,)).fetchone()
    db.execute('UPDATE screens SET movie_id=? WHERE id=?', (movie_id, screen_id))
    db.commit()
    db.close()
    return redirect(url_for('management_hall', hall_id=screen['hall_id']))


# ============================================================
#  SECTION 6 — HOSPITALITY STAFF MODULE
# ============================================================

@app.route('/hospitality')
def hospitality():
    """
    Hospitality staff dashboard.
    Shows: live clock, today's show schedule with intermission times,
    and snack delivery queue for all screens.
    """
    if 'user_id' not in session:
        return redirect(url_for('login'))

    db  = get_db()
    now = datetime.now()

    screens = db.execute('''
        SELECT s.id, s.name AS screen_name, h.name AS hall, h.city,
               m.title AS movie, m.duration_mins, s.show_time,
               COALESCE(SUM(b.seats_booked), 0) AS audience
        FROM   screens s
        JOIN   movies  m ON s.movie_id  = m.id
        JOIN   halls   h ON s.hall_id   = h.id
        LEFT JOIN bookings b ON b.screen_id = s.id
                             AND b.booking_date = ?
                             AND b.status = 'confirmed'
        GROUP  BY s.id
        ORDER  BY h.city, h.name, s.name
    ''', (now.strftime('%Y-%m-%d'),)).fetchall()

    snack_deliveries = db.execute('''
        SELECT b.id AS booking_id, u.name AS customer, b.seats_booked,
               s.name AS screen, h.name AS hall,
               sm.name AS snack, sm.category, so.quantity, b.booking_date
        FROM   snack_orders so
        JOIN   bookings    b  ON so.booking_id = b.id
        JOIN   users       u  ON b.user_id     = u.id
        JOIN   screens     s  ON b.screen_id   = s.id
        JOIN   halls       h  ON s.hall_id     = h.id
        JOIN   snack_menu  sm ON so.snack_id   = sm.id
        WHERE  b.booking_date = ? AND b.status = 'confirmed'
        ORDER  BY h.name, s.name
    ''', (now.strftime('%Y-%m-%d'),)).fetchall()

    db.close()
    return render_template(
        'hospitality.html',
        screens=screens,
        deliveries=snack_deliveries,
        now=now
    )


# ── Entry Point ────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    os.makedirs('instance', exist_ok=True)
    from init_db import init_db
    init_db()
    app.run(debug=True, port=5000)
