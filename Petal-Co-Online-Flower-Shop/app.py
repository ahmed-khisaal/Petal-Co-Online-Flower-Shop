from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

# ─── Flower Catalog ───────────────────────────────────────────────────────────

FLOWERS = [
    {"id": 1, "name": "Red Rose Bouquet",   "price": 499,  "image": "rose.jpg",       "category": "Romantic",     "description": "12 fresh red roses tied with satin ribbon — perfect for love & anniversaries."},
    {"id": 2, "name": "Tulip Basket",        "price": 699,  "image": "tulip.jpg",      "category": "Gift",         "description": "Vibrant mixed tulips in a rustic wicker basket. A cheerful gift for anyone."},
    {"id": 3, "name": "Orchid Flower",       "price": 899,  "image": "orchid.jpg",     "category": "Premium",      "description": "Exotic purple orchids in a sleek ceramic pot. Long-lasting elegance."},
    {"id": 4, "name": "White Lily",          "price": 599,  "image": "lily.jpg",       "category": "Elegant",      "description": "Pure white lilies symbolising grace and serenity. Ideal for condolences."},
    {"id": 5, "name": "Sunflower Bunch",     "price": 549,  "image": "sunflower.jpg",  "category": "Bright",       "description": "10 golden sunflowers bursting with warmth — bring sunshine indoors."},
    {"id": 6, "name": "Jasmine Combo",       "price": 399,  "image": "jasmine.jpg",    "category": "Traditional",  "description": "Fragrant jasmine garlands and blooms for festivals & puja offerings."},
    {"id": 7, "name": "Lavender Dreams",     "price": 649,  "image": "lavender.jpg",   "category": "Calming",      "description": "Dried lavender bundles for a calming aroma and rustic home décor."},
    {"id": 8, "name": "Peony Bliss",         "price": 849,  "image": "peony.jpg",      "category": "Romantic",     "description": "Lush pink peonies — extravagant, full-bodied blooms for grand gestures."},
]

# ─── Database Helpers ─────────────────────────────────────────────────────────

def get_db():
    conn = sqlite3.connect("flowershop.db")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cur = conn.cursor()
    cur.executescript("""
        CREATE TABLE IF NOT EXISTS customers (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            name     TEXT NOT NULL,
            email    TEXT NOT NULL UNIQUE,
            phone    TEXT NOT NULL,
            address  TEXT NOT NULL,
            password TEXT NOT NULL,
            joined   TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS orders (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER REFERENCES customers(id),
            name       TEXT NOT NULL,
            flower     TEXT NOT NULL,
            quantity   INTEGER NOT NULL,
            total      INTEGER NOT NULL,
            status     TEXT DEFAULT 'Pending',
            order_date TEXT NOT NULL
        );
    """)
    conn.commit()
    conn.close()

init_db()

# ─── Utility ──────────────────────────────────────────────────────────────────

def flower_by_name(name):
    return next((f for f in FLOWERS if f["name"] == name), None)

def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("customer_id"):
            flash("Please log in to continue.", "warning")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("admin_logged_in"):
            return redirect(url_for("admin_login"))
        return f(*args, **kwargs)
    return decorated

# ─── Public Routes ────────────────────────────────────────────────────────────

@app.route("/")
def home():
    featured = FLOWERS[:4]
    return render_template("index.html", featured=featured)

@app.route("/flowers")
def flowers():
    search = request.args.get("search", "").strip().lower()
    category = request.args.get("category", "")
    filtered = FLOWERS
    if search:
        filtered = [f for f in filtered if search in f["name"].lower() or search in f["category"].lower()]
    if category:
        filtered = [f for f in filtered if f["category"] == category]
    categories = sorted(set(f["category"] for f in FLOWERS))
    return render_template("flowers.html", flowers=filtered, search=search, category=category, categories=categories)

@app.route("/order")
@login_required
def order():
    flower_name = request.args.get("flower", "")
    flower = flower_by_name(flower_name)
    if not flower:
        flash("Flower not found.", "error")
        return redirect(url_for("flowers"))
    return render_template("order.html", flower=flower)

@app.route("/place_order", methods=["POST"])
@login_required
def place_order():
    name     = request.form["name"].strip()
    flower_n = request.form["flower"]
    qty      = int(request.form["quantity"])

    flower = flower_by_name(flower_n)
    if not flower or qty < 1:
        flash("Invalid order details.", "error")
        return redirect(url_for("flowers"))

    total      = flower["price"] * qty
    order_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cid        = session.get("customer_id")

    conn = get_db(); cur = conn.cursor()
    cur.execute(
        "INSERT INTO orders (customer_id, name, flower, quantity, total, order_date) VALUES (?,?,?,?,?,?)",
        (cid, name, flower_n, qty, total, order_date)
    )
    conn.commit()
    oid = cur.lastrowid
    conn.close()

    return render_template("success.html", name=name, flower=flower_n,
                           quantity=qty, total=total, order_date=order_date, order_id=oid)

# ─── Auth Routes ──────────────────────────────────────────────────────────────

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name    = request.form["name"].strip()
        email   = request.form["email"].strip().lower()
        phone   = request.form["phone"].strip()
        address = request.form["address"].strip()
        pw      = request.form["password"]
        pw2     = request.form["confirm_password"]

        if pw != pw2:
            flash("Passwords do not match.", "error")
            return render_template("register.html")

        if len(pw) < 6:
            flash("Password must be at least 6 characters.", "error")
            return render_template("register.html")

        hashed = generate_password_hash(pw)
        try:
            conn = get_db(); cur = conn.cursor()
            cur.execute(
                "INSERT INTO customers (name, email, phone, address, password) VALUES (?,?,?,?,?)",
                (name, email, phone, address, hashed)
            )
            conn.commit()
            conn.close()
            flash(f"Welcome, {name}! Your account has been created.", "success")
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            flash("An account with this email already exists.", "error")
            return render_template("register.html")

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if session.get("customer_id"):
        return redirect(url_for("home"))

    if request.method == "POST":
        email = request.form["email"].strip().lower()
        pw    = request.form["password"]

        conn = get_db(); cur = conn.cursor()
        cur.execute("SELECT * FROM customers WHERE email=?", (email,))
        user = cur.fetchone()
        conn.close()

        if user and check_password_hash(user["password"], pw):
            session["customer_id"]   = user["id"]
            session["customer_name"] = user["name"]
            flash(f"Welcome back, {user['name']}!", "success")
            return redirect(url_for("home"))
        else:
            flash("Invalid email or password.", "error")

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("customer_id", None)
    session.pop("customer_name", None)
    flash("You have been logged out.", "info")
    return redirect(url_for("home"))

@app.route("/my_orders")
@login_required
def my_orders():
    cid = session["customer_id"]
    conn = get_db(); cur = conn.cursor()
    cur.execute("SELECT * FROM orders WHERE customer_id=? ORDER BY id DESC", (cid,))
    orders = cur.fetchall()
    conn.close()
    return render_template("my_orders.html", orders=orders)

# ─── Admin Routes ─────────────────────────────────────────────────────────────

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

@app.route("/admin_login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        u = request.form["username"]
        p = request.form["password"]
        if u == ADMIN_USERNAME and p == ADMIN_PASSWORD:
            session["admin_logged_in"] = True
            return redirect(url_for("admin"))
        flash("Invalid credentials.", "error")
    return render_template("admin_login.html")

@app.route("/admin")
@admin_required
def admin():
    conn = get_db(); cur = conn.cursor()
    cur.execute("SELECT o.*, c.email FROM orders o LEFT JOIN customers c ON o.customer_id=c.id ORDER BY o.id DESC")
    orders = cur.fetchall()
    cur.execute("SELECT COUNT(*) AS n FROM orders")
    total_orders = cur.fetchone()["n"]
    cur.execute("SELECT COUNT(*) AS n FROM customers")
    total_customers = cur.fetchone()["n"]
    cur.execute("SELECT COALESCE(SUM(total),0) AS n FROM orders")
    total_revenue = cur.fetchone()["n"]
    cur.execute("SELECT COUNT(*) AS n FROM orders WHERE status='Pending'")
    pending = cur.fetchone()["n"]
    conn.close()
    return render_template("admin.html", orders=orders,
                           total_orders=total_orders, total_customers=total_customers,
                           total_revenue=total_revenue, pending=pending)

@app.route("/admin/customers")
@admin_required
def admin_customers():
    conn = get_db(); cur = conn.cursor()
    cur.execute("SELECT id, name, email, phone, address, joined FROM customers ORDER BY id DESC")
    customers = cur.fetchall()
    conn.close()
    return render_template("customers.html", customers=customers)

@app.route("/admin/update_status/<int:order_id>", methods=["POST"])
@admin_required
def update_status(order_id):
    status = request.form["status"]
    conn = get_db(); cur = conn.cursor()
    cur.execute("UPDATE orders SET status=? WHERE id=?", (status, order_id))
    conn.commit(); conn.close()
    flash("Order status updated.", "success")
    return redirect(url_for("admin"))

@app.route("/admin/delete_order/<int:order_id>")
@admin_required
def delete_order(order_id):
    conn = get_db(); cur = conn.cursor()
    cur.execute("DELETE FROM orders WHERE id=?", (order_id,))
    conn.commit(); conn.close()
    flash("Order deleted.", "info")
    return redirect(url_for("admin"))

@app.route("/admin/clear_orders")
@admin_required
def clear_orders():
    conn = get_db(); cur = conn.cursor()
    cur.execute("DELETE FROM orders")
    conn.commit(); conn.close()
    flash("All orders cleared.", "info")
    return redirect(url_for("admin"))

@app.route("/admin_logout")
def admin_logout():
    session.pop("admin_logged_in", None)
    return redirect(url_for("admin_login"))

if __name__ == "__main__":
    app.run(debug=True)
