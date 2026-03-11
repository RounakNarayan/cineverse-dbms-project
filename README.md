# 🎬 CineVerse — Cinema Management System

> **DBMS Project** | Python (Flask) + SQLite  
> A full-stack cinema management system with three role-based modules.

---

## 👥 Modules

| Module | Role | Features |
|--------|------|----------|
| 🎟 Customer | Moviegoer | Book tickets, select seats, pre-order snacks, pay |
| 🏛 Management | Manager | Manage halls, screens, update movies, view bookings |
| 🍿 Hospitality | Staff | View show schedule, intermission times, snack delivery queue |

---

## 🗄️ Database (9 Tables)
```
users · managers · halls · movies · screens · bookings · snack_menu · snack_orders · payments
```

---

## ⚙️ Tech Stack

| | |
|--|--|
| Backend | Python 3, Flask |
| Database | SQLite (built-in sqlite3) |
| Frontend | HTML, CSS, JavaScript (Jinja2 templates) |
| Auth | SHA-256 hashing + Flask sessions |

---

## 🚀 How to Run
```bash
# 1. Clone the repo
git clone https://github.com/YOUR_USERNAME/cineverse-dbms-project.git
cd cineverse-dbms-project

# 2. Install dependencies
pip install -r requirements.txt

# 3. Initialize the database
python init_db.py

# 4. Run the app
python app.py

# 5. Open in browser
http://localhost:5000
```

---

## 🔑 Demo Credentials

| Role | Field | Value |
|------|-------|-------|
| Customer | Phone | `9876543210` |
| Customer | Password | `password123` |
| Manager | Manager ID | `MGR001` |
| Manager | Password | `mgr@001` |

---

## 📁 Project Structure
```
cineverse-dbms-project/
├── app.py                        ← Flask app — all routes & logic
├── init_db.py                    ← DB setup — creates tables + sample data
├── schema.sql                    ← SQL schema (for reference)
├── requirements.txt              ← Python dependencies
├── .gitignore
├── README.md
└── templates/
    ├── base.html                 ← Shared layout
    ├── login.html                ← Login page
    ├── signup.html               ← Registration page
    ├── role_select.html          ← Role selection
    ├── customer.html             ← Booking form
    ├── payment.html              ← Payment page
    ├── confirmation.html         ← Booking ticket
    ├── management_login.html     ← Manager auth
    ├── management_dashboard.html ← All halls
    ├── management_hall.html      ← Screens per hall
    ├── screen_bookings.html      ← Bookings per screen
    └── hospitality.html          ← Staff dashboard
```

---

## 📊 Sample Data Included

- 4 Cities: Mumbai, Delhi, Bangalore, Chennai
- 8 Cinema Halls (PVR, INOX, Cinepolis, AGS)
- 21 Screens (IMAX, 4DX, Dolby, VIP, Standard)
- 8 Movies
- 14 Snack Items
