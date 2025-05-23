# scraper/scraper.py
import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

# --- Configuration ---
BASE_URL = "https://wiki.pmease.com/display/QB14"
OUTPUT_DIR = "scraper/output"
VISITED_URLS = set()

def scrape_page(url):
    """
    Scrapes a single page, saves its content, and finds new links to crawl.
    """
    if url in VISITED_URLS:
        return
    print(f"Scraping: {url}")
    VISITED_URLS.add(url)

    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad status codes
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return

    soup = BeautifulSoup(response.content, 'html.parser')

    # --- Content Extraction ---
    # This selector targets the main content area of the QuickBase wiki.
    content_area = soup.find('div', id='main-content')
    if content_area:
        # Create a filename from the URL path
        parsed_url = urlparse(url)
        # Use a safe filename
        filename = os.path.join(OUTPUT_DIR, parsed_url.path.strip('/').replace('/', '_') + ".txt")
        if not filename.endswith('.txt'):
            filename += ".txt"

        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content_area.get_text(separator='\n', strip=True))
        print(f"Saved content to {filename}")

    # --- Find and Follow Links ---
    for link in soup.find_all('a', href=True):
        href = link['href']
        # Create an absolute URL from a relative one
        full_url = urljoin(BASE_URL, href)

        # Only follow links that are within the base URL scope
        if full_url.startswith(BASE_URL) and full_url not in VISITED_URLS:
            scrape_page(full_url)

if __name__ == "__main__":
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
    print("Starting the web scraper...")
    scrape_page(BASE_URL)
    print("Scraping complete.")