from flask import Blueprint, jsonify
from config import config
from supabase import create_client

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/dashboard", methods=["GET"])
def get_dashboard_stats():
    """Return aggregate statistics for the dashboard."""
    try:
        db = create_client(config.SUPABASE_URL, config.SUPABASE_ANON_KEY)

        # Count total sources
        sources = db.table("sources").select("id, active").execute()
        total_sources = len(sources.data) if sources.data else 0
        active_crawlers = sum(1 for s in (sources.data or []) if s.get("active"))

        # Count scraped data
        scraped = db.table("scraped_data").select("id").execute()
        total_events = len(scraped.data) if scraped.data else 0

        # Count recent updates (last 24h) - simple approach
        new_updates = total_events  # In production, filter by time

        # Intelligence stats
        total_extracted_events = 0
        top_entities = []
        most_active_domain = "N/A"
        recent_intel = []

        try:
            # Total extracted events
            intel_events = db.table("extracted_events").select("id, domain, event_title, summary, created_at").order("created_at", desc=True).execute()
            total_extracted_events = len(intel_events.data) if intel_events.data else 0

            if intel_events.data:
                # Most active domain
                domain_counts = {}
                for ev in intel_events.data:
                    d = ev.get("domain", "unknown")
                    domain_counts[d] = domain_counts.get(d, 0) + 1
                most_active_domain = max(domain_counts, key=domain_counts.get)

                # Recent intel (top 4)
                recent_intel = intel_events.data[:4]

            # Top entities (most frequent)
            all_entities = db.table("entities").select("entity_name").execute()
            if all_entities.data:
                entity_counts = {}
                for ent in all_entities.data:
                    name = ent.get("entity_name", "")
                    if name:
                        entity_counts[name] = entity_counts.get(name, 0) + 1
                sorted_entities = sorted(entity_counts.items(), key=lambda x: x[1], reverse=True)
                top_entities = [{"name": n, "count": c} for n, c in sorted_entities[:8]]
        except Exception as intel_err:
            print(f"[Dashboard] Intelligence stats error: {intel_err}")

        return jsonify({
            "total_sources": total_sources,
            "active_crawlers": active_crawlers,
            "new_updates": new_updates,
            "total_events": total_events,
            "total_extracted_events": total_extracted_events,
            "top_entities": top_entities,
            "most_active_domain": most_active_domain,
            "recent_intel": recent_intel,
        }), 200

    except Exception as e:
        return jsonify({
            "total_sources": 0,
            "active_crawlers": 0,
            "new_updates": 0,
            "total_events": 0,
            "total_extracted_events": 0,
            "top_entities": [],
            "most_active_domain": "N/A",
            "recent_intel": [],
            "error": str(e),
        }), 200
