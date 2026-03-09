from flask import Blueprint, request, jsonify
from config import config
from supabase import create_client
from services.scraper import scrape_url
from services.ontology_builder import build_ontology_from_content

graph_bp = Blueprint("graph", __name__)

@graph_bp.route("/build_graph", methods=["POST"])
def build_graph():
    try:
        data = request.get_json()
        if not data or not data.get("url"):
            return jsonify({"error": "URL is required"}), 400

        url = data["url"].strip()
        print(f"[Graph API] Building graph for: {url}")

        content = scrape_url(url)
        if not content:
            return jsonify({
                "error": "Failed to scrape content from URL",
                "url": url,
            }), 422
            
        result = build_ontology_from_content(content, url)
        if result.get("error"):
            return jsonify({"error": result["error"]}), 500
            
        return jsonify(result), 201

    except Exception as e:
        print(f"[Graph API] Error: {e}")
        return jsonify({"error": str(e)}), 500


@graph_bp.route("/graph", methods=["GET"])
def get_graph():
    try:
        db = create_client(config.SUPABASE_URL, config.SUPABASE_ANON_KEY)
        
        nodes_result = db.table("graph_nodes").select("*").execute()
        edges_result = db.table("graph_edges").select("*").execute()
        
        nodes_data = nodes_result.data or []
        edges_data = edges_result.data or []
        
        formatted_nodes = [
            {
                "id": n["entity_name"],
                "data": {
                    "label": n["entity_name"],
                    "type": n["entity_type"],
                    "domain": n["domain"]
                }
            } 
            for n in nodes_data
        ]
        
        formatted_edges = [
            {
                "id": e["id"],
                "source": e["source_node"],
                "target": e["target_node"],
                "label": e["relation"],
                "data": {
                    "event_reference": e["event_reference"]
                }
            }
            for e in edges_data
        ]
        
        return jsonify({
            "nodes": formatted_nodes,
            "edges": formatted_edges
        }), 200

    except Exception as e:
        print(f"[Graph API] Error: {e}")
        return jsonify({"nodes": [], "edges": []}), 500


@graph_bp.route("/events", methods=["GET"])
def get_events():
    """Fetch all extracted intelligence events from Supabase to list in Chatbox."""
    try:
        db = create_client(config.SUPABASE_URL, config.SUPABASE_ANON_KEY)
        # Fetch extracted events
        events_result = (
            db.table("extracted_events")
            .select("id, event_title, summary, domain, created_at")
            .order("created_at", desc=True)
            .limit(100)
            .execute()
        )
        events = events_result.data or []
        return jsonify(events), 200
    except Exception as e:
        print(f"[Graph API] Get Events Error: {e}")
        return jsonify([]), 500


@graph_bp.route("/relate", methods=["POST"])
def relate_events():
    """Takes a list of event IDs, fetches their content, and calls Gemini to relate them."""
    try:
        data = request.get_json()
        event_ids = data.get("event_ids", [])
        
        if not event_ids:
            return jsonify({"error": "No event IDs provided"}), 400
            
        print(f"[Graph API] Relating {len(event_ids)} events...")
            
        db = create_client(config.SUPABASE_URL, config.SUPABASE_ANON_KEY)
        
        # Fetch full data for these events
        events_data = []
        for eid in event_ids[:10]: # limit to 10 context events
            res = db.table("extracted_events").select("*").eq("id", eid).execute()
            if res.data:
                events_data.append(res.data[0])
                
        if not events_data:
             return jsonify({"error": "Failed to fetch event data"}), 404
             
        from services.ontology_builder import generate_insights_from_events
        result = generate_insights_from_events(events_data)
        
        if result.get("error"):
            return jsonify({"error": result["error"]}), 500
            
        return jsonify(result), 200

    except Exception as e:
        print(f"[Graph API] Relate Error: {e}")
        return jsonify({"error": str(e)}), 500
