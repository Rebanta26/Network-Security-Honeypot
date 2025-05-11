from flask import Flask, render_template, request, abort, session, send_file
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from countermeasures import init_rate_limiter, init_ip_blacklist, init_captcha
from db import get_db_connection
from captcha.image import ImageCaptcha
import random, string
import unicodedata
import io
import os
import re
import mysql.connector
import datetime
import smtplib

app = Flask(__name__)
app.secret_key = "want to get over w it"

# Feature flag from the environment:
ENABLE_CM = os.getenv("ENABLE_COUNTERMEASURES", "false").lower() == "true"
# app.config["ENABLE_IP_BLACKLIST"] = ENABLE_CM

if ENABLE_CM:
    # activate rate-limiter
    init_rate_limiter(app)
    # activate IP blacklisting
    init_ip_blacklist(app, get_db_connection)
    # activate CAPTCHA
    init_captcha(app)

# Dummy product data
dummy_products = [
    {'id': 1, 'name': 'Apple iPhone 15', 'price': '$1399', 'image': 'iphone15.jpg', 'category': 'electronics'},
    {'id': 2, 'name': 'Apple MacBook Pro M3 Chip', 'price': '$1499', 'image': 'macbook-m3.jpg', 'category': 'electronics'},
    {'id': 3, 'name': 'Lenovo Wireless Earbuds', 'price': '$259', 'image': 'lenovo.jpg', 'category': 'electronics'},
    {'id': 4, 'name': 'WHOOP - 4.0 Health and Fitness Tracker', 'price': '$229', 'image': 'whoop.jpg', 'category': 'electronics'},
    {'id': 5, 'name': 'Samsung 65" QLED Smart TV', 'price': '$1199', 'image': 'samsung.jpg', 'category': 'electronics'},
    {'id': 6, 'name': 'Bose Noise Cancelling Headphones 700', 'price': '$379', 'image': 'bose.jpg', 'category': 'electronics'},
    {'id': 7, 'name': 'Sony PlayStation 5 Console', 'price': '$499', 'image': 'ps5.jpg', 'category': 'electronics'},
    {'id': 8, 'name': 'Logitech MX Master 3 Wireless Mouse', 'price': '$99', 'image': 'logitech.jpg', 'category': 'electronics'},
    {'id': 9, 'name': 'Organic Almond Milk - 64oz', 'price': '$4.99', 'image': 'milk.jpg', 'category': 'grocery'},
    {'id': 10, 'name': 'Starbucks Medium Roast Coffee Beans - 12oz', 'price': '$8.49', 'image': 'starbucks.jpg', 'category': 'grocery'},
    {'id': 11, 'name': 'Organic Cage-Free Brown Eggs (12 count)', 'price': '$5.99', 'image': 'eggs.jpg', 'category': 'grocery'},
    {'id': 12, 'name': 'Quaker Oats Old Fashioned - 42oz', 'price': '$6.49', 'image': 'oats.jpg', 'category': 'grocery'},
    {'id': 13, 'name': 'Kirkland Organic Raw Honey - 3lb', 'price': '$17.99', 'image': 'honey.jpg', 'category': 'grocery'},
    {'id': 14, 'name': 'Beyond Meat Plant-Based Burger Patties (8 count)', 'price': '$11.99', 'image': 'patties.jpg', 'category': 'grocery'},
    {'id': 15, 'name': 'Frozen Mixed Berries (4lb bag)', 'price': '$9.99', 'image': 'berries.jpg', 'category': 'grocery'},
]

def normalize(text):
    return re.sub(r'\W+', '',
        unicodedata.normalize('NFKD', text)
                   .encode('ASCII','ignore')
                   .decode('utf-8')
    ).lower()

def get_db_connection():
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='rebanta26',
        database='honeypot_db'
    )

def send_email_alert(subject, body):
    try:
        EMAIL_ADDRESS = "rebantadaadhiich26@gmail.com"
        EMAIL_PASSWORD = "jedn bnul wzka zeaz"
        TO_EMAIL = "harrydavis230@gmail.com"
        msg = MIMEMultipart()
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = TO_EMAIL
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(msg)
        print("✅ Alert email sent.")
    except Exception as e:
        print(f"❌ Email alert failed: {e}")

@app.before_request
def ensure_tables():
    """Create tables if they don't exist."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS logs (
          id INT AUTO_INCREMENT PRIMARY KEY,
          ip VARCHAR(255),
          user_agent TEXT,
          accessed_url TEXT,
          extra_info TEXT,
          timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bot_flags (
          id INT AUTO_INCREMENT PRIMARY KEY,
          ip VARCHAR(255),
          reason TEXT,
          user_agent TEXT,
          timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS banned_ips (
          ip VARCHAR(255) PRIMARY KEY,
          banned_at DATETIME
        )
    """)
    conn.commit()
    cursor.close()
    conn.close()

def log_activity(ip, user_agent, accessed_url, extra_info=""):
    conn = get_db_connection()
    cursor = conn.cursor()

    # write to logs
    cursor.execute("""
        INSERT INTO logs (ip, user_agent, accessed_url, extra_info)
        VALUES (%s, %s, %s, %s)
    """, (ip, user_agent, accessed_url, extra_info))

    # check for honeypot or suspicious UA
    reason = None
    if accessed_url in ['/hidden-trap', '/hidden-api']:
        reason = f"Accessed honeypot URL: {accessed_url}"
    elif "python-requests" in user_agent.lower():
        reason = "Suspicious user-agent"

    if reason:
        cursor.execute("""
            INSERT INTO bot_flags (ip, reason, user_agent)
            VALUES (%s, %s, %s)
        """, (ip, reason, user_agent))
        send_email_alert("🚨 Honeypot Alert", f"{ip} flagged: {reason}\nUA: {user_agent}")

        # Ban after 10 flags
        cursor.execute("SELECT COUNT(*) FROM bot_flags WHERE ip = %s", (ip,))
        (flag_count,) = cursor.fetchone()
        if flag_count >= 10:
            cursor.execute(
                """
                INSERT INTO banned_ips (ip, banned_at)
                VALUES (%s, UTC_TIMESTAMP())
                ON DUPLICATE KEY UPDATE banned_at = UTC_TIMESTAMP()
                """, (ip,)
            )
            send_email_alert("🚨 IP Banned", f"{ip} has been banned after {flag_count} flags")
    conn.commit()
    cursor.close()
    conn.close()

@app.route('/captcha')
def serve_captcha():
    # generate random text
    text = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    session['captcha_text'] = text

    # render image
    img = ImageCaptcha(width=280, height=90)
    data = img.generate(text)
    return send_file(io.BytesIO(data.read()), mimetype='image/png')

@app.route('/favicon.ico')
def favicon():
    return "", 204

@app.route('/')
def home():
    log_activity(request.remote_addr, request.headers.get('User-Agent'), '/')
    return render_template('index.html', products=dummy_products)

@app.route('/category/<category_name>')
def category_page(category_name):
    filtered = [p for p in dummy_products if p['category'].lower() == category_name.lower()]
    log_activity(request.remote_addr, request.headers.get('User-Agent'), f'/category/{category_name}')
    return render_template('index.html', products=filtered)

@app.route('/search')
def search():
    query = request.args.get('query','').strip().lower()
    filtered = [p for p in dummy_products
                if query in p['name'].lower() or query in p['category'].lower()] if query else dummy_products
    log_activity(request.remote_addr, request.headers.get('User-Agent'), f'/search?query={query}')
    return render_template('index.html', products=filtered)

@app.route('/product/<int:product_id>')
def product_page(product_id):
    product = next((p for p in dummy_products if p['id']==product_id), None)
    if not product:
        return "Product not found", 404
    log_activity(request.remote_addr, request.headers.get('User-Agent'), f'/product/{product_id}')
    return render_template('product.html', product=product)

@app.route('/checkout')
def checkout():
    log_activity(request.remote_addr, request.headers.get('User-Agent'), '/checkout')
    return render_template('checkout.html')

@app.route('/login', methods=['GET','POST'])
def fake_login():
    if request.method == 'POST':
        log_activity(request.remote_addr, request.headers.get('User-Agent'), '/login_attempt')
        return render_template('login_success.html')
    return render_template('login.html')

@app.route('/signup', methods=['GET','POST'])
def signup():
    if request.method == 'POST':
        log_activity(request.remote_addr, request.headers.get('User-Agent'), '/signup_attempt')
        return "Fake signup recorded."
    return render_template('signup.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/hidden-trap')
# @limiter.limit("5 per minute")
def hidden_trap():
    log_activity(request.remote_addr, request.headers.get('User-Agent'), '/hidden-trap', extra_info="Hidden trap")
    return "Not Found", 404

@app.route('/hidden-api')
# @limiter.limit("5 per minute")
def hidden_api():
    log_activity(request.remote_addr, request.headers.get('User-Agent'), '/hidden-api', extra_info="Unauthorized API")
    return {"error":"Unauthorized access detected"}, 403

@app.route('/metrics')
def metrics():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT accessed_url, COUNT(*) AS count
              FROM logs
             GROUP BY accessed_url
             ORDER BY count DESC
        """)
        data = cursor.fetchall()
        cursor.close()
        conn.close()
        return {"metrics": data}, 200
    except Exception as e:
        return {"error": str(e)}, 500

if __name__ == '__main__':
    app.run(debug=True)