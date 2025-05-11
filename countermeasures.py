import datetime
import os
import random
import string
from io import BytesIO
from flask import request, abort, session, send_file
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from captcha.image import ImageCaptcha

# ---- Rate Limiter ----
def init_rate_limiter(app):
    Limiter(
        key_func        = get_remote_address,
        app             = app,
        default_limits  = ["5 per minute"],
        headers_enabled = True,
    )

# ---- IP Blacklist ----
def init_ip_blacklist(app, get_db_connection):
    @app.before_request
    def block_banned_ips():
        ip   = request.remote_addr
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT banned_at FROM banned_ips WHERE ip = %s", (ip,))
        row = cursor.fetchone()
        if row:
            banned_at = row[0]
            now = datetime.datetime.utcnow()
            if now - banned_at < datetime.timedelta(minutes=2):
                cursor.close(); conn.close()
                abort(403, "🚫 Your IP is temporarily banned.")
            else:
                cursor.execute("DELETE FROM banned_ips WHERE ip = %s", (ip,))
                conn.commit()
        cursor.close(); conn.close()

# ---- CAPTCHA ----
def init_captcha(app):
    # ensure we have a secret key for sessions
    app.secret_key = os.getenv('FLASK_SECRET_KEY', os.urandom(24))
    image_captcha = ImageCaptcha()

    @app.route('/captcha.png')
    def serve_captcha():
        # generate random 5-char code
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
        session['captcha_code'] = code
        data = image_captcha.generate(code)
        return send_file(data, mimetype='image/png')

    @app.before_request
    def verify_captcha():
        # Only enforce on login/signup POST if CAPTCHA is enabled
        if request.endpoint in ('fake_login', 'signup') and request.method == 'POST':
            user_input = request.form.get('captcha', '').strip().upper()
            expected = session.get('captcha_code', '').upper()
            if not expected or user_input != expected:
                abort(403, "❌ CAPTCHA verification failed.")
