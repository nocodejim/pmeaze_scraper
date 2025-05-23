# scraper/scraper.py
import os
import sys
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, urldefrag

# --- Configuration ---
BASE_URL = "https://wiki.pmease.com/display/QB14"
OUTPUT_DIR = "scraper/output"
VISITED_URLS = set()

def scrape_page(url):
    """
    Scrapes a single page, saves its content, and finds new links to crawl.
    Now tailored for Docusaurus sites.
    """
    # Normalize the URL by removing any #fragments
    url = urldefrag(url).url

    if url in VISITED_URLS:
        return

    print(f"Scraping: {url}")
    VISITED_URLS.add(url)

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"  -> ERROR fetching {url}: {e}")
        return

    soup = BeautifulSoup(response.content, 'html.parser')

    # --- Content Extraction for Docusaurus ---
    # CHANGE 1: Docusaurus places its main content inside an <article> tag.
    # This is the correct selector for this type of site.
    content_area = soup.find('article')

    if content_area:
        parsed_url = urlparse(url)
        path_segment = parsed_url.path.strip('/').replace('/', '_')
        if not path_segment or path_segment == "display_QB14":
             path_segment = "home" # Make the homepage filename cleaner
        filename = os.path.join(OUTPUT_DIR, path_segment + ".txt")

        # Get text, using a space separator for better readability between elements
        page_text = content_area.get_text(separator=' ', strip=True)

        with open(filename, 'w', encoding='utf-8') as f:
            f.write(page_text)
        print(f"  -> Saved content to {filename}")
    else:
        print(f"  -> No <article> content found on page: {url}")

    # --- Find and Follow Links (Entire Page) ---
    # CHANGE 2: We search the *entire document* for links (<a> tags).
    # This ensures we find the navigation sidebar and crawl the whole site.
    for link in soup.find_all('a', href=True):
        href = link['href']
        full_url = urljoin(BASE_URL, href)
        cleaned_url = urldefrag(full_url).url

        if cleaned_url.startswith(BASE_URL) and cleaned_url not in VISITED_URLS:
            # Recursively call the function for the new, valid link
            scrape_page(full_url)

# --- Main Execution Block ---
if __name__ == "__main__":
    try:
        if not os.path.exists(OUTPUT_DIR):
            os.makedirs(OUTPUT_DIR)
        print("Starting Docusaurus web scraper...")
        scrape_page(BASE_URL)
        print("Scraping complete.")
    except Exception as e:
        print("--- SCRIPT FAILED WITH AN ERROR ---")
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"ERROR TYPE: {exc_type}\nIN FILE: {fname}\nAT LINE: {exc_tb.tb_lineno}\nDETAILS: {e}")
        print("-----------------------------------")