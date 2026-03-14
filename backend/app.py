from flask import Flask
from flask_cors import CORS
from config import config

def create_app():
    app = Flask(__name__)
    CORS(app, resources={r"/*": {"origins": "*"}})

    # Register blueprints
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


app = create_app()

# Start the background scheduler outside the __main__ block 
# so Gunicorn executes it when importing the app
from services.scheduler import start_scheduler
try:
    start_scheduler()
    print("[Scheduler] Background scheduler started")
except Exception as e:
    print(f"[Scheduler] Warning: Could not start scheduler: {e}")

if __name__ == "__main__":
    print("=" * 50)
    print("  Global Ontology Engine - Backend API")
    print("  Running on http://localhost:5000")
    print("=" * 50)

    app.run(debug=True, host="0.0.0.0", port=5000, use_reloader=False)
