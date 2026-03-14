from flask import Flask, jsonify
from flask_cors import CORS
from config import config


def create_app():
    app = Flask(__name__)

    # Load configuration
    app.config.from_object(config)

    # Enable CORS for frontend (Netlify / Vercel etc.)
    CORS(app, resources={r"/*": {"origins": "*"}})

    # -------------------------
    # Root route (health check)
    # -------------------------
    @app.route("/")
    def home():
        return jsonify({
            "status": "Global Ontology Engine Backend Running",
            "service": "AI Intelligence Engine API"
        })

    # -------------------------
    # Register API Blueprints
    # -------------------------
    from routes.sources import sources_bp
    from routes.monitor import monitor_bp
    from routes.query import query_bp
    from routes.dashboard import dashboard_bp
    from routes.intelligence import intelligence_bp
    from routes.graph import graph_bp

    app.register_blueprint(sources_bp)
    app.register_blueprint(monitor_bp)
    app.register_blueprint(query_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(intelligence_bp)
    app.register_blueprint(graph_bp)

    return app


# Create app instance
app = create_app()


# -------------------------
# Start Background Scheduler
# -------------------------
from services.scheduler import start_scheduler

try:
    start_scheduler()
    print("[Scheduler] Background scheduler started")
except Exception as e:
    print(f"[Scheduler] Warning: Could not start scheduler: {e}")


# -------------------------
# Run locally
# -------------------------
if __name__ == "__main__":
    print("=" * 60)
    print("Global Ontology Engine - Backend API")
    print("Running on http://localhost:5000")
    print("=" * 60)

    app.run(
        debug=True,
        host="0.0.0.0",
        port=5000,
        use_reloader=False
    )