import sys
import os

# Add backend to path so imports work
sys.path.append(os.path.dirname(__file__))

from services.ai_pipeline import analyze_content
from services.scraper import scrape_url

url = "https://www.reuters.com/technology/"
print(f"Scraping {url}...")
content = scrape_url(url)
print(f"Scraped {len(content)} chars")

print("Extracting intelligence via ai_pipeline.py...")
result = analyze_content(content, "technology")
print("--- RESULT ---")
print(result)
