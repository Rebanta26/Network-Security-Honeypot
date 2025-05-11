from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time

# Set up headless Chrome options
options = Options()
options.headless = True  # Run in headless mode (no browser UI)
options.add_argument("user-agent=python-requests/2.31.0")  # Mimic bot-like UA

# Path to chromedriver (ensure it's installed and in PATH)
driver = webdriver.Chrome(options=options)

# List of endpoints to simulate bot access
endpoints = [
    "http://localhost:5000/",
    "http://localhost:5000/hidden-trap",
    "http://localhost:5000/hidden-api",
    "http://localhost:5000/search?query=iphone"
]

# Visit each page with short delays
for url in endpoints:
    print(f"Accessing: {url}")
    driver.get(url)
    time.sleep(1)

driver.quit()
print("✅ Bot simulation complete. Check your MySQL logs and inbox.")