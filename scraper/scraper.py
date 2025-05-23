#!/usr/bin/env python3

import requests
from bs4 import BeautifulSoup
import json
import os
import re
import time
import argparse
import sys
from urllib.parse import urljoin, urlparse, urldefrag
from tqdm import tqdm

# --- Configuration ---
BASE_URL = "https://wiki.pmease.com/display/QB14/"
OUTPUT_DIR = "scraper/output"

class QuickBuildScraper:
    def __init__(self, base_url=BASE_URL, output_dir=OUTPUT_DIR):
        """
        Initialize the QuickBuild documentation scraper.
        
        Args:
            base_url: The base URL of the QuickBuild documentation wiki.
            output_dir: Directory to save the scraped content.
        """
        self.base_url = base_url
        self.output_dir = output_dir
        self.visited_urls = set()
        self.session = requests.Session()
        
        # Create output directory structure
        os.makedirs(output_dir, exist_ok=True)
        os.makedirs(f"{output_dir}/json", exist_ok=True)
        os.makedirs(f"{output_dir}/text", exist_ok=True)
        
        # Headers to mimic a browser request
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        }
    
    def is_valid_url(self, url):
        """
        Check if a URL is valid and belongs to the QB14 documentation ONLY.
        
        Args:
            url: The URL to check.
            
        Returns:
            bool: True if the URL is valid, False otherwise.
        """
        # Make sure it's a full URL
        if not url.startswith('http'):
            return False
        
        # Make sure it's from the same domain
        parsed_base = urlparse(self.base_url)
        parsed_url = urlparse(url)
        if parsed_base.netloc != parsed_url.netloc:
            return False
        
        # CRITICAL: Only allow QB14 URLs - reject other versions
        if not url.startswith("https://wiki.pmease.com/display/QB14/"):
            return False
        
        # Avoid non-documentation pages
        excluded_paths = [
            '/login', '/logout', '/register', '/preferences',
            '/attachment/', '/history/', '/info/', '/compare/',
        ]
        for path in excluded_paths:
            if path in url:
                return False
        
        # Avoid URLs with anchors
        if '#' in url:
            return False
        
        return True
    
    def clean_text(self, text):
        """
        Clean extracted text.
        
        Args:
            text: The text to clean.
            
        Returns:
            str: Cleaned text.
        """
        # Remove extra whitespace and normalize line breaks
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    
    def extract_content(self, soup, url):
        """
        Extract content from a BeautifulSoup object.
        
        Args:
            soup: BeautifulSoup object of the page.
            url: The URL of the page.
            
        Returns:
            dict: Extracted content.
        """
        # Extract title
        title_elem = soup.find('h1')
        title = title_elem.get_text().strip() if title_elem else "Unknown Title"
        
        # Try multiple content selectors for different page layouts
        content_elem = (soup.find('article') or 
                       soup.find(class_='wiki-content') or 
                       soup.find(id='main-content'))
        
        if not content_elem:
            content_text = "No content found."
            sections = []
        else:
            # Extract all text from content area
            content_text = content_elem.get_text(separator='\n', strip=True)
            
            # Extract sections with headers and content
            sections = []
            headers = content_elem.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
            
            for header in headers:
                header_text = header.get_text().strip()
                section_content = []
                
                # Get all content until the next header
                sibling = header.next_sibling
                while sibling and not (sibling.name and sibling.name.startswith('h')):
                    if hasattr(sibling, 'get_text'):
                        text = sibling.get_text(strip=True)
                        if text:
                            section_content.append(text)
                    sibling = sibling.next_sibling
                
                sections.append({
                    'header': header_text,
                    'content': ' '.join(section_content)
                })
        
        # Extract links for recursive scraping
        links = []
        for a_tag in soup.find_all('a', href=True):
            link_url = urljoin(url, a_tag['href'])
            # Normalize URL by removing fragments
            link_url = urldefrag(link_url).url
            if self.is_valid_url(link_url) and link_url not in self.visited_urls:
                links.append(link_url)
        
        # Extract breadcrumb for context
        breadcrumb_elem = soup.find(class_='breadcrumbs') or soup.find(class_='breadcrumb')
        breadcrumb = []
        
        if breadcrumb_elem:
            for crumb in breadcrumb_elem.find_all('a'):
                breadcrumb.append(crumb.get_text().strip())
        
        # Create structured content
        structured_content = {
            'url': url,
            'title': title,
            'breadcrumb': breadcrumb,
            'full_text': content_text,
            'sections': sections,
            'links': links
        }
        
        return structured_content
    
    def scrape_page(self, url):
        """
        Scrape a single page.
        
        Args:
            url: The URL of the page to scrape.
            
        Returns:
            dict: Scraped content, or None if the page couldn't be scraped.
        """
        # Normalize the URL by removing any #fragments
        url = urldefrag(url).url
        
        # Skip if already visited
        if url in self.visited_urls:
            return None
        
        self.visited_urls.add(url)
        
        try:
            # Make the request with a small delay to be polite
            time.sleep(1)
            response = self.session.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            # Parse the HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract content
            content = self.extract_content(soup, url)
            
            # Save the content
            self.save_content(content)
            
            return content
        except Exception as e:
            print(f"  -> ERROR scraping {url}: {str(e)}")
            return None
    
    def save_content(self, content):
        """
        Save content to JSON and text files.
        
        Args:
            content: The content to save.
        """
        if not content:
            return
        
        # Generate a filename from the URL
        parsed_url = urlparse(content['url'])
        filename = parsed_url.path.strip('/').replace('/', '_')
        if not filename or filename == 'display_QB14':
            filename = 'index'
        
        # Save as JSON
        json_path = f"{self.output_dir}/json/{filename}.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(content, f, indent=2, ensure_ascii=False)
        
        # Save as text
        text_path = f"{self.output_dir}/text/{filename}.txt"
        with open(text_path, 'w', encoding='utf-8') as f:
            f.write(f"Title: {content['title']}\n")
            f.write(f"URL: {content['url']}\n")
            f.write(f"Breadcrumb: {' > '.join(content['breadcrumb'])}\n\n")
            f.write(content['full_text'])
    
    def recursive_scrape(self, start_url, max_pages=None):
        """
        Recursively scrape pages starting from a URL.
        
        Args:
            start_url: The URL to start scraping from.
            max_pages: Maximum number of pages to scrape (None for no limit).
            
        Returns:
            list: List of all scraped content.
        """
        to_visit = [start_url]
        scraped_content = []
        visited_count = 0
        
        with tqdm(total=1, desc="Scraping pages") as progress_bar:
            while to_visit and (max_pages is None or visited_count < max_pages):
                current_url = to_visit.pop(0)
                
                if current_url in self.visited_urls:
                    continue
                
                print(f"Scraping: {current_url}")
                content = self.scrape_page(current_url)
                
                if content:
                    scraped_content.append(content)
                    visited_count += 1
                    
                    # Add new links to visit
                    for link in content['links']:
                        if link not in self.visited_urls and link not in to_visit:
                            to_visit.append(link)
                
                progress_bar.update(1)
                progress_bar.total = len(to_visit) + visited_count
                progress_bar.refresh()
        
        print(f"Scraped {visited_count} pages.")
        return scraped_content
    
    def create_combined_output(self):
        """
        Create combined output files with all content.
        """
        # Combined JSON
        all_content = []
        json_dir = f"{self.output_dir}/json"
        
        if os.path.exists(json_dir):
            for filename in os.listdir(json_dir):
                if filename.endswith('.json'):
                    try:
                        with open(os.path.join(json_dir, filename), 'r', encoding='utf-8') as f:
                            all_content.append(json.load(f))
                    except Exception as e:
                        print(f"Error reading {filename}: {e}")
        
        # Save combined JSON
        with open(f"{self.output_dir}/all_content.json", 'w', encoding='utf-8') as f:
            json.dump(all_content, f, indent=2, ensure_ascii=False)
        
        # Save combined text
        with open(f"{self.output_dir}/all_content.txt", 'w', encoding='utf-8') as f:
            for content in all_content:
                f.write(f"Title: {content['title']}\n")
                f.write(f"URL: {content['url']}\n")
                f.write(f"Breadcrumb: {' > '.join(content['breadcrumb'])}\n\n")
                f.write(content['full_text'])
                f.write("\n\n" + "="*80 + "\n\n")
        
        print(f"Created combined output files in {self.output_dir}/")
        print(f"  - all_content.json ({len(all_content)} pages)")
        print(f"  - all_content.txt")


def main():
    """Main execution function with error handling."""
    
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Scrape QuickBuild documentation wiki.')
    parser.add_argument('--url', default=BASE_URL,
                        help='Starting URL for scraping.')
    parser.add_argument('--output', default=OUTPUT_DIR,
                        help='Output directory for scraped content.')
    parser.add_argument('--single', action='store_true', 
                        help='Scrape only a single page (for testing).')
    parser.add_argument('--max_pages', type=int, default=None,
                        help='Maximum number of pages to scrape.')
    
    args = parser.parse_args()
    
    try:
        # Initialize scraper
        scraper = QuickBuildScraper(base_url=args.url, output_dir=args.output)
        
        # Scrape
        if args.single:
            print(f"Scraping single page: {args.url}")
            scraper.scrape_page(args.url)
        else:
            print(f"Recursively scraping from: {args.url}")
            scraper.recursive_scrape(args.url, args.max_pages)
            scraper.create_combined_output()
        
        print(f"Scraping complete. Content saved to {args.output}/")
        
    except Exception as e:
        print("--- SCRIPT FAILED WITH AN ERROR ---")
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"ERROR TYPE: {exc_type}\nIN FILE: {fname}\nAT LINE: {exc_tb.tb_lineno}\nDETAILS: {e}")
        print("-----------------------------------")
        sys.exit(1)


if __name__ == "__main__":
    main()