import sys
import os

# Add backend to path so imports work
sys.path.append(os.path.dirname(__file__))

from services.intelligence_extractor import extract_intelligence
from services.scraper import scrape_url

url = "https://www.reuters.com/world/"
print(f"Scraping {url}...")
content = scrape_url(url)
print(f"Scraped {len(content)} chars")

print("Extracting intelligence...")
result = extract_intelligence(content, url)
print("--- RESULT ---")
print(result)
