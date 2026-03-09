from flask import Blueprint, request, jsonify
from config import config
from supabase import create_client
from services.scraper import scrape_url
from services.intelligence_extractor import extract_intelligence, store_intelligence

intelligence_bp = Blueprint("intelligence", __name__)


@intelligence_bp.route("/process_source", methods=["POST"])
def process_source():
    """
    Full intelligence pipeline:
    1. Scrape URL via Jina
    2. Extract intelligence via OpenRouter
    3. Store in Supabase
    4. Return structured result
    """
    try:
        data = request.get_json()
        if not data or not data.get("url"):
            return jsonify({"error": "URL is required"}), 400

        url = data["url"].strip()
        print(f"[Process] Starting pipeline for: {url}")

        # Step 1: Scrape with Jina
        print(f"[Process] Step 1 — Scraping with Jina...")
        content = scrape_url(url)
        if not content:
            return jsonify({
                "error": "Failed to scrape content from URL",
                "url": url,
            }), 422

        print(f"[Process] Scraped {len(content)} characters")

        # Step 2: Extract intelligence with OpenRouter
        print(f"[Process] Step 2 — Extracting intelligence...")
        intelligence = extract_intelligence(content, url)

        if intelligence.get("error"):
            # Still try to store partial results
            print(f"[Process] Extraction had error: {intelligence['error']}")

        # Step 3: Store in Supabase
        print(f"[Process] Step 3 — Storing in Supabase...")
        stored = store_intelligence(intelligence, url)

        if stored:
            print(f"[Process] Pipeline complete for {url}")
            return jsonify({
                "success": True,
                "url": url,
                "intelligence": stored,
            }), 201
        else:
            # Return the extracted data even if storage failed
            return jsonify({
                "success": False,
                "url": url,
                "intelligence": intelligence,
                "warning": "Extraction succeeded but storage failed. Check Supabase tables exist.",
            }), 200

    except Exception as e:
        print(f"[Process] Pipeline error: {e}")
        return jsonify({"error": str(e)}), 500


@intelligence_bp.route("/intelligence_feed", methods=["GET"])
def intelligence_feed():
    """
    Return the latest extracted intelligence events with their entities.
    """
    try:
        db = create_client(config.SUPABASE_URL, config.SUPABASE_ANON_KEY)

        # Fetch extracted events
        events_result = (
            db.table("extracted_events")
            .select("*")
            .order("created_at", desc=True)
            .limit(50)
            .execute()
        )

        events = events_result.data or []

        # Enrich each event with its entities
        for event in events:
            eid = event["id"]

            # Fetch entities for this event
            entities_result = (
                db.table("entities")
                .select("entity_name, entity_type")
                .eq("event_id", eid)
                .execute()
            )
            event["entities"] = entities_result.data or []

            # Fetch relationships for this event
            rels_result = (
                db.table("relationships")
                .select("source_entity, relation, target_entity")
                .eq("event_id", eid)
                .execute()
            )
            event["relationships"] = rels_result.data or []

        return jsonify(events), 200

    except Exception as e:
        print(f"[Intelligence Feed] Error: {e}")
        return jsonify([]), 200


@intelligence_bp.route("/intelligence_feed/<string:event_id>", methods=["DELETE"])
def delete_intelligence_event(event_id):
    """
    Delete an extracted intelligence event by ID.
    Cascade delete will handle associated entities and relationships 
    if foreign keys are correctly set up, otherwise we just delete the event.
    """
    try:
        db = create_client(config.SUPABASE_URL, config.SUPABASE_ANON_KEY)
        
        # Delete the event
        result = db.table("extracted_events").delete().eq("id", event_id).execute()
        
        if result.data:
            return jsonify({"success": True, "message": f"Deleted event {event_id}"}), 200
        else:
            return jsonify({"error": "Event not found or could not be deleted"}), 404

    except Exception as e:
        print(f"[Delete Intelligence] Error: {e}")
        return jsonify({"error": str(e)}), 500


@intelligence_bp.route("/process_bulk_sources", methods=["POST"])
def process_bulk_sources():
    """
    Fetch sources from the registry based on domain and process them all.
    """
    try:
        data = request.get_json()
        domain = data.get("domain", "all").strip().lower()
        
        db = create_client(config.SUPABASE_URL, config.SUPABASE_ANON_KEY)
        
        # 1. Fetch sources
        query = db.table("sources").select("url, domain")
        if domain != "all":
            query = query.eq("domain", domain)
            
        sources_result = query.execute()
        sources = sources_result.data or []
        
        if not sources:
            return jsonify({"error": f"No active sources found for domain: {domain}"}), 404
            
        print(f"[Bulk Process] Found {len(sources)} sources for domain '{domain}'. Starting bulk extraction...")
        
        results = []
        success_count = 0
        
        # 2. Process each source systematically
        for src in sources:
            url = src.get("url")
            print(f"[Bulk Process] Processing: {url}")
            
            # Scrape
            content = scrape_url(url)
            if not content:
                print(f"[Bulk Process] Failed to scrape {url}")
                results.append({"url": url, "status": "failed", "reason": "Scraping failed"})
                continue
                
            # Extract
            intelligence = extract_intelligence(content, url)
            if intelligence.get("error"):
                 print(f"[Bulk Process] Extraction error for {url}: {intelligence['error']}")
                 
            # Store
            stored = store_intelligence(intelligence, url)
            if stored:
                 success_count += 1
                 results.append({"url": url, "status": "success"})
            else:
                 results.append({"url": url, "status": "failed", "reason": "Storage failed or no entities extracted"})
                 
        print(f"[Bulk Process] Complete. Successfully processed {success_count}/{len(sources)} sources.")
        
        return jsonify({
            "message": f"Bulk processing complete. {success_count}/{len(sources)} succeeded.",
            "success_count": success_count,
            "total_count": len(sources),
            "details": results
        }), 200

    except Exception as e:
        print(f"[Bulk Process] Error: {e}")
        return jsonify({"error": str(e)}), 500
