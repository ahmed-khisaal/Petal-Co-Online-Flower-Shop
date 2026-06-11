# 🌸 Petal & Co — Online Flower Shop
### BCA Final Year Project | 2026

---

## Project Overview

**Petal & Co** is a full-stack web application for an Online Flower Shop, built using **Python (Flask)** as the backend framework and **SQLite** as the database. The system supports two types of users — **Customers** and **Administrators** — with distinct interfaces and functionality.

---

## Features

### Customer Side
- 🏠 **Landing Page** — Hero section, featured flowers, "Why Us" benefits, CTA
- 🌺 **Flower Catalog** — Browse all flowers with search and category filter
- 🛒 **Order System** — Live price calculator, receipt on success
- 👤 **Registration & Login** — Secure account with password hashing (Werkzeug)
- 📦 **Order History** — Customers can view all their past orders with status

### Admin Panel (Dark Theme Dashboard)
- 📊 **Dashboard** — Stats: total orders, pending orders, customers, revenue
- 📋 **Order Management** — View all orders, update status (Pending/Processing/Delivered/Cancelled), delete
- 👥 **Customer Management** — View all registered customers
- 🔐 **Secure Login** — Separate admin login, session-protected routes

---

## Technology Stack

| Layer       | Technology         |
|-------------|--------------------|
| Backend     | Python 3, Flask    |
| Database    | SQLite3            |
| Frontend    | HTML5, CSS3, JS    |
| Auth        | Werkzeug (bcrypt)  |
| Sessions    | Flask sessions     |

---

## Project Structure

```
flowershop/
├── app.py               # Main Flask application
├── database.py          # DB initialisation script
├── requirements.txt     # Python dependencies
├── flowershop.db        # SQLite database (auto-created)
├── templates/
│   ├── base.html        # Shared layout with navbar + footer
│   ├── index.html       # Homepage
│   ├── flowers.html     # Flower catalog with search/filter
│   ├── order.html       # Order form with live price calc
│   ├── success.html     # Order confirmation receipt
│   ├── register.html    # Customer registration
│   ├── login.html       # Customer login
│   ├── my_orders.html   # Customer order history
│   ├── admin.html       # Admin dashboard
│   ├── admin_login.html # Admin login
│   └── customers.html   # Admin customer list
└── static/
    ├── css/             # (optional extra CSS)
    └── images/          # Flower images
```

---

## Setup Instructions

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Initialise the database
```bash
python database.py
```

### 3. Run the application
```bash
python app.py
```

### 4. Open in browser
```
http://localhost:5000
```

---

## Default Admin Credentials
| Field    | Value      |
|----------|------------|
| Username | `admin`    |
| Password | `admin123` |

---

## Security Improvements Over Basic Version

| Feature                | Basic Version | This Project |
|------------------------|---------------|--------------|
| Password storage       | Plain text    | Bcrypt hash (Werkzeug) |
| Duplicate email check  | ❌            | ✅ |
| Login sessions         | ❌            | ✅ Flask sessions |
| Route protection       | ❌            | ✅ Decorators |
| Flash messages         | ❌            | ✅ |
| Password confirmation  | ❌            | ✅ |
| Order status tracking  | ❌            | ✅ (4 states) |
| Customer-order linkage | ❌            | ✅ Foreign key |
| Input validation       | Basic         | Server-side |

---

## Database Schema

### `customers`
| Column   | Type    | Notes              |
|----------|---------|--------------------|
| id       | INTEGER | Primary Key        |
| name     | TEXT    |                    |
| email    | TEXT    | Unique             |
| phone    | TEXT    |                    |
| address  | TEXT    |                    |
| password | TEXT    | Hashed             |
| joined   | TEXT    | Auto timestamp     |

### `orders`
| Column      | Type    | Notes                    |
|-------------|---------|--------------------------|
| id          | INTEGER | Primary Key              |
| customer_id | INTEGER | FK → customers.id        |
| name        | TEXT    |                          |
| flower      | TEXT    |                          |
| quantity    | INTEGER |                          |
| total       | INTEGER | Calculated server-side   |
| status      | TEXT    | Pending/Processing/etc.  |
| order_date  | TEXT    | datetime string          |

---

*Submitted as BCA Final Year Project — 2026*
