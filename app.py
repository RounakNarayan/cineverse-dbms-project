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
app.secret_key = 'cinema_secret_key_2024'

DB_PATH = os.path.join(os.path.dirname(__file__), 'instance', 'cinema.db')


# ── Helper Functions ───────────────────────────────────────────────────────────

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


# ============================================================
#  SECTION 2 — AUTHENTICATION
# ============================================================

@app.route('/')
def index():
    return redirect(url_for('role_choice'))


@app.route('/role-choice')
def role_choice():
    """Landing page — choose login type before seeing login form."""
    return render_template('role_choice.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Customer login page."""
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
            return redirect(url_for('customer'))
        error = 'Invalid phone number or password.'
    return render_template('login.html', error=error)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
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
    session.clear()
    return redirect(url_for('role_choice'))


# ============================================================
#  SECTION 3 — HOSPITALITY LOGIN
# ============================================================

@app.route('/hospitality-login', methods=['GET', 'POST'])
def hospitality_login():
    """Hospitality staff login — uses same user accounts."""
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
            session['role']       = 'hospitality'
            return redirect(url_for('hospitality'))
        error = 'Invalid phone number or password.'
    return render_template('hospitality_login.html', error=error)


# ============================================================
#  SECTION 4 — CUSTOMER MODULE
# ============================================================

@app.route('/customer')
def customer():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    db     = get_db()
    snacks = db.execute('SELECT * FROM snack_menu ORDER BY category, name').fetchall()
    db.close()
    return render_template('customer.html', snacks=snacks)


@app.route('/api/cities')
def api_cities():
    """AJAX API — Return all cities as JSON."""
    db     = get_db()
    cities = db.execute('SELECT DISTINCT city FROM halls ORDER BY city').fetchall()
    db.close()
    return jsonify([c['city'] for c in cities])


@app.route('/api/halls')
def api_halls():
    city  = request.args.get('city')
    db    = get_db()
    halls = db.execute('SELECT id, name FROM halls WHERE city=?', (city,)).fetchall()
    db.close()
    return jsonify([dict(h) for h in halls])


@app.route('/api/screens')
def api_screens():
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
        GROUP  BY s.id
    ''', (hall_id,)).fetchall()
    db.close()
    return jsonify([dict(s) for s in screens])


@app.route('/customer/book', methods=['POST'])
def book():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    seats = int(request.form['seats'])

    person_snacks = []
    for i in range(1, seats + 1):
        snack_id = request.form.get(f'snack_person_{i}') or None
        person_snacks.append({
            'person': i,
            'snack_id': snack_id
        })

    data = {
        'date':          request.form['date'],
        'city':          request.form['city'],
        'hall_id':       request.form['hall_id'],
        'screen_id':     request.form['screen_id'],
        'seats':         seats,
        'person_snacks': person_snacks
    }

    db     = get_db()
    screen = db.execute('''
        SELECT s.*, m.title AS movie, h.name AS hall_name, h.city
        FROM   screens s
        JOIN   movies  m ON s.movie_id = m.id
        JOIN   halls   h ON s.hall_id  = h.id
        WHERE  s.id = ?
    ''', (data['screen_id'],)).fetchone()

    snack_details = []
    snack_total   = 0
    for ps in person_snacks:
        if ps['snack_id']:
            snack = db.execute(
                'SELECT * FROM snack_menu WHERE id=?', (ps['snack_id'],)
            ).fetchone()
            if snack:
                snack_total += snack['price']
                snack_details.append({
                    'person':     ps['person'],
                    'snack_id':   ps['snack_id'],
                    'snack_name': snack['name'],
                    'price':      snack['price']
                })
            else:
                snack_details.append({
                    'person':     ps['person'],
                    'snack_id':   None,
                    'snack_name': 'None',
                    'price':      0
                })
        else:
            snack_details.append({
                'person':     ps['person'],
                'snack_id':   None,
                'snack_name': 'None',
                'price':      0
            })

    ticket_total = screen['ticket_price'] * seats
    total        = ticket_total + snack_total
    db.close()

    session['pending_booking'] = {
        **data,
        'total':         total,
        'movie':         screen['movie'],
        'hall':          screen['hall_name'],
        'screen_name':   screen['name'],
        'show_time':     screen['show_time'],
        'ticket_price':  screen['ticket_price'],
        'snack_details': snack_details,
        'snack_total':   snack_total,
        'person_snacks': person_snacks
    }

    return render_template(
        'payment.html',
        booking=session['pending_booking'],
        screen=dict(screen),
        total=total
    )


@app.route('/customer/pay', methods=['POST'])
def pay():
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

    for sd in b['snack_details']:
        if sd['snack_id']:
            db.execute(
                'INSERT INTO snack_orders (booking_id, snack_id, quantity, person_num) VALUES (?, ?, ?, ?)',
                (booking_id, sd['snack_id'], 1, sd['person'])
            )

    db.commit()
    db.close()

    session['last_booking'] = {**b, 'booking_id': booking_id}
    session.pop('pending_booking', None)
    return redirect(url_for('confirmation'))


@app.route('/confirmation')
def confirmation():
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
    """Manager login — city-wise access."""
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
            session['manager_city'] = mgr['city']
            return redirect(url_for('management_dashboard'))
        error = 'Invalid Manager ID or Password.'
    return render_template('management_login.html', error=error)


@app.route('/management/dashboard')
def management_dashboard():
    """Show only halls in the manager's assigned city."""
    if 'manager_id' not in session:
        return redirect(url_for('management'))
    db    = get_db()
    halls = db.execute(
        'SELECT * FROM halls WHERE city=? ORDER BY name',
        (session['manager_city'],)
    ).fetchall()
    db.close()
    return render_template(
        'management_dashboard.html',
        halls=halls,
        manager=session['manager_name'],
        city=session['manager_city']
    )


@app.route('/management/hall/<int:hall_id>')
def management_hall(hall_id):
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
               p.amount, p.method
        FROM   bookings b
        JOIN   users    u  ON b.user_id    = u.id
        LEFT JOIN payments p  ON p.booking_id = b.id
        WHERE  b.screen_id = ? AND b.status = 'confirmed'
        ORDER  BY b.id DESC
    ''', (screen_id,)).fetchall()

    booking_snacks = {}
    for bk in bookings:
        snacks = db.execute('''
            SELECT so.person_num, sm.name, sm.price
            FROM   snack_orders so
            JOIN   snack_menu   sm ON so.snack_id = sm.id
            WHERE  so.booking_id = ?
            ORDER  BY so.person_num
        ''', (bk['id'],)).fetchall()
        booking_snacks[bk['id']] = [dict(s) for s in snacks]

    db.close()
    return render_template(
        'screen_bookings.html',
        screen=screen,
        bookings=bookings,
        booking_snacks=booking_snacks
    )


@app.route('/management/screen/<int:screen_id>/change-movie', methods=['POST'])
def change_movie(screen_id):
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
    if 'user_id' not in session:
        return redirect(url_for('hospitality_login'))

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
               sm.name AS snack, sm.category, so.quantity,
               so.person_num, b.booking_date
        FROM   snack_orders so
        JOIN   bookings    b  ON so.booking_id = b.id
        JOIN   users       u  ON b.user_id     = u.id
        JOIN   screens     s  ON b.screen_id   = s.id
        JOIN   halls       h  ON s.hall_id     = h.id
        JOIN   snack_menu  sm ON so.snack_id   = sm.id
        WHERE  b.booking_date = ? AND b.status = 'confirmed'
        ORDER  BY h.name, s.name, so.person_num
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
    app.run(debug=True, port=5000)
