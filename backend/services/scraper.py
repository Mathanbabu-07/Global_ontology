import requests
import time
from config import config


def scrape_url(url):
    """
    Use Jina AI Reader to extract clean text content from a URL.
    Jina reader converts web pages to clean, readable text.
    """
    try:
        jina_url = f"https://r.jina.ai/{url}"
        headers = {
            "Accept": "text/plain",
            "X-Return-Format": "markdown",
            "X-No-Cache": "true"
        }

        # Add API key if available
        if config.JINA_API_KEY:
            headers["Authorization"] = f"Bearer {config.JINA_API_KEY}"

        max_retries = 3
        retry_delay = 2
        for attempt in range(max_retries):
            try:
                response = requests.get(jina_url, headers=headers, timeout=30)
                break
            except requests.exceptions.RequestException as e:
                if attempt < max_retries - 1:
                    print(f"[Scraper] Connection error, retrying in {retry_delay}s... (Attempt {attempt+1}/{max_retries})")
                    time.sleep(retry_delay)
                else:
                    raise e

        if response.status_code == 200:
            content = response.text.strip()
            if content:
                print(f"[Scraper] Successfully scraped {url} ({len(content)} chars)")
                return content
            else:
                print(f"[Scraper] Empty content from {url}")
                return None
        else:
            print(f"[Scraper] Jina returned status {response.status_code} for {url}")
            return None

    except requests.exceptions.Timeout:
        print(f"[Scraper] Timeout scraping {url}")
        return None
    except Exception as e:
        print(f"[Scraper] Error scraping {url}: {e}")
        return None
