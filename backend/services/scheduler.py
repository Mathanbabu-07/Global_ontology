from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from config import config

scheduler = BackgroundScheduler()


def process_sources():
    """
    Background job: iterate active sources, scrape via Jina, analyze via OpenRouter,
    and store results in Supabase.
    """
    try:
        from supabase import create_client
        from services.scraper import scrape_url
        from services.ai_pipeline import analyze_content

        db = create_client(config.SUPABASE_URL, config.SUPABASE_ANON_KEY)

        # Fetch all active sources
        sources = db.table("sources").select("*").eq("active", True).execute()

        if not sources.data:
            print("[Scheduler] No active sources to process")
            return

        print(f"[Scheduler] Processing {len(sources.data)} active source(s)...")

        for source in sources.data:
            try:
                url = source["url"]
                print(f"[Scheduler] Scraping: {url}")

                # Scrape content
                content = scrape_url(url)
                if not content:
                    print(f"[Scheduler] No content from {url}, skipping")
                    continue

                # Analyze with AI
                analysis = analyze_content(content[:3000], source.get("domain", "general"))

                # Store results
                db.table("scraped_data").insert({
                    "source_id": source["id"],
                    "source_url": url,
                    "domain": source.get("domain", "general"),
                    "summary": analysis.get("summary", ""),
                    "entities": analysis.get("entities", []),
                    "events": analysis.get("events", []),
                    "relationships": analysis.get("relationships", []),
                }).execute()

                print(f"[Scheduler] Completed: {url}")

            except Exception as e:
                print(f"[Scheduler] Error processing {source.get('url', '?')}: {e}")
                continue

        print("[Scheduler] Cycle complete")

    except Exception as e:
        print(f"[Scheduler] Fatal error: {e}")


def start_scheduler():
    """Start the background scheduler to run every 10 minutes."""
    scheduler.add_job(
        process_sources,
        "interval",
        minutes=10,
        id="source_processor",
        replace_existing=True,
    )
    scheduler.start()
    print("[Scheduler] Background scheduler running (every 10 min)")
