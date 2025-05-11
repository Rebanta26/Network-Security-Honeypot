from flask import Flask, render_template, request, abort
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import sqlite3
import datetime

app = Flask(__name__)

# 1) Turn on the headers so you can see X-RateLimit-* on every response
app.config['RATELIMIT_HEADERS_ENABLED'] = True

# 2) Create a single Limiter instance, no default limits
limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=[],
)

# ———————————————— Your existing logging and routes ————————————————

def log_activity(endpoint, user_agent, ip_address, extra_info=""):
    conn = sqlite3.connect("honeypot.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            endpoint TEXT,
            user_agent TEXT,
            ip_address TEXT,
            extra_info TEXT
        )
    """)
    conn.commit()
    cursor.execute(
        "INSERT INTO logs (timestamp, endpoint, user_agent, ip_address, extra_info) VALUES (?, ?, ?, ?, ?)",
        (datetime.datetime.now(), endpoint, user_agent, ip_address, extra_info)
    )
    conn.commit()
    conn.close()

@app.route("/")
def index():
    log_activity("/", request.headers.get("User-Agent"), request.remote_addr)
    return render_template("index.html", products=[
        {"id": 1, "name": "Fake Product 1", "price": "$99"},
        {"id": 2, "name": "Fake Product 2", "price": "$149"},
    ])

@app.route("/product/<int:product_id>")
def product(product_id):
    # … your existing code …
    pass

@app.route("/checkout")
def checkout():
    # … your existing code …
    pass

@app.route("/login", methods=["GET", "POST"])
def login():
    # … your existing code …
    pass

# 3) A simple ping endpoint so you can verify rate-limiter in isolation
@app.route("/ping")
@limiter.limit("3 per minute")
def ping():
    return "pong", 200

# 4) Your real honeypot route, rate-limited *before* your 404/403 logic
@app.route("/hidden-trap")
@limiter.limit("5 per minute")
def hidden_trap():
    log_activity("/hidden-trap", request.headers.get("User-Agent"), request.remote_addr)
    # your existing bot-detection...
    return abort(403)

# 5) Finally, your app entrypoint
if __name__ == "__main__":
    app.run(debug=True)