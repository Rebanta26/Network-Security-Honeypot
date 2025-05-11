import requests
from bs4 import BeautifulSoup
import time

# Target base URL
BASE_URL = "http://127.0.0.1:5000"  

# Fake headers to mimic a scraper
HEADERS = {
    'User-Agent': 'python-requests/2.25.1',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Connection': 'keep-alive',
}

# List of pages to hit (including honeypot traps)
paths = [
    '/',
    '/product/1',
    '/search?query=iphone',
    '/hidden-trap',          # Trap page
    '/hidden-api'            # Fake API
]

def scrape():
    for path in paths:
        url = f"{BASE_URL}{path}"
        print(f"Requesting: {url}")
        try:
            response = requests.get(url, headers=HEADERS)
            soup = BeautifulSoup(response.text, 'html.parser')
            print(f"Status: {response.status_code}, Length: {len(response.text)}")
        except Exception as e:
            print(f"Error fetching {url}: {e}")
        time.sleep(1)  # Sleep between requests to mimic slow scraper

if __name__ == "__main__":
    scrape()