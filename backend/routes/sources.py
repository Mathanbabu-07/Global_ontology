from flask import Blueprint, request, jsonify
from config import config
from supabase import create_client

sources_bp = Blueprint("sources", __name__)


def get_db():
    return create_client(config.SUPABASE_URL, config.SUPABASE_ANON_KEY)


@sources_bp.route("/add_source", methods=["POST"])
def add_source():
    """Add a new intelligence source URL."""
    try:
        data = request.get_json()
        if not data or not data.get("url"):
            return jsonify({"error": "URL is required"}), 400

        record = {
            "url": data["url"].strip(),
            "domain": data.get("domain", "geopolitics"),
            "frequency": data.get("frequency", "1hour"),
            "trust_score": int(data.get("trust_score", 5)),
            "active": True,
        }

        db = get_db()
        result = db.table("sources").insert(record).execute()
        return jsonify(result.data[0] if result.data else record), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@sources_bp.route("/sources", methods=["GET"])
def get_sources():
    """Retrieve all saved sources."""
    try:
        db = get_db()
        result = db.table("sources").select("*").order("created_at", desc=True).execute()
        return jsonify(result.data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@sources_bp.route("/delete_source/<source_id>", methods=["DELETE"])
def delete_source(source_id):
    """Remove a source by ID."""
    try:
        db = get_db()
        db.table("sources").delete().eq("id", source_id).execute()
        return jsonify({"message": "Source deleted"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@sources_bp.route("/toggle_source/<source_id>", methods=["PATCH"])
def toggle_source(source_id):
    """Toggle active/paused status of a source."""
    try:
        db = get_db()
        # Fetch current state
        current = db.table("sources").select("active").eq("id", source_id).execute()
        if not current.data:
            return jsonify({"error": "Source not found"}), 404

        new_active = not current.data[0]["active"]
        db.table("sources").update({"active": new_active}).eq("id", source_id).execute()
        return jsonify({"message": f"Source {'activated' if new_active else 'paused'}"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
