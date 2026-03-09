from flask import Blueprint, jsonify
from config import config
from supabase import create_client

monitor_bp = Blueprint("monitor", __name__)


@monitor_bp.route("/monitor", methods=["GET"])
def get_monitor_data():
    """Retrieve scraped intelligence data for the Data Monitor page."""
    try:
        db = create_client(config.SUPABASE_URL, config.SUPABASE_ANON_KEY)
        result = (
            db.table("scraped_data")
            .select("*")
            .order("fetched_at", desc=True)
            .limit(50)
            .execute()
        )
        return jsonify(result.data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
