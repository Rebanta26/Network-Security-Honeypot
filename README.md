NetSentry: Web Scraper Honeypot

Overview

NetSentry is a decoy e-commerce honeypot designed to identify and analyze malicious bot traffic targeting online stores. It simulates a realistic web shop, logs detailed request data, and alerts on suspicious behaviors to help security teams develop effective countermeasures.

Features
• Flask-based honeypot web application serving fake products and hidden trap endpoints
• CAPTCHA integration to distinguish human users from bots
• Request logging: IP address, user-agent, URL path, timestamp
• Automated alerts via email when high-risk patterns are detected
• Rate-limiting and IP blacklisting to slow down aggressive scrapers
• Network-level monitoring using Scapy/Wireshark for packet analysis
• Bot simulation scripts (Selenium, Python requests) for testing detection

Tech Stack
• Backend: Python 3.x, Flask
• Database: SQLite/MySQL (configurable)
• Frontend: Bootstrap 5, Montserrat font
• Monitoring: Scapy, Wireshark
• Notifications: Gmail SMTP
• Containerization: Docker (optional)

Installation 1. Clone the repository

git clone https://github.com/<your-username>/NetSentry.git
cd NetSentry

    2.	Create a virtual environment

python3 -m venv venv
source venv/bin/activate # macOS/Linux
venv\Scripts\activate # Windows

    3.	Install dependencies

pip install -r requirements.txt

    4.	Configure environment variables

export FLASK_APP=app.py
export FLASK_ENV=development
export SECRET_KEY="your_secret_key"

# SMTP settings for email alerts

export SMTP_USER="you@gmail.com"
export SMTP_PASS="app_password"

Usage 1. Generate and serve CAPTCHA images
• The serve_captcha endpoint provides CAPTCHA on /signup and /login. 2. Run the Flask app

flask run

The honeypot will be available at http://127.0.0.1:5000/.

    3.	Simulate bot traffic

python simulate_bot.py # Basic scraper simulation
python advanced_bot.py # More evasive behavior

    4.	View logs
    •	Inspect the database tables (interactions, bot_flags) to analyze captured data.
    5.	Network analysis
    •	Use Wireshark or scapy_capture.py to sniff and inspect packets against trap endpoints.

Contributing

Contributions are welcome! Please: 1. Fork the repository 2. Create a new branch (git checkout -b feature/my-feature) 3. Commit your changes (git commit -m "Add my feature") 4. Push to your branch (git push origin feature/my-feature) 5. Open a pull request

License

This project is licensed under the MIT License.

⸻
