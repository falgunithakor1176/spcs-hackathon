import os
import logging
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from config import Config
from db import db
from apscheduler.schedulers.background import BackgroundScheduler
from services.ml_service import run_dbscan_engine

from routes.auth import auth_bp
from routes.data import data_bp
from routes.ml import ml_bp

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger('scheduler')

def run_scheduled_ml(app):
    logger.info("[Scheduler] Triggering automated hourly DBSCAN execution...")
    try:
        with app.app_context():
            result = run_dbscan_engine()
            if result.get('status') == 'success':
                summary = result.get('summary', {})
                logger.info(
                    f"[Scheduler] Automated DBSCAN execution succeeded. "
                    f"Hotspots: {summary.get('hotspots_generated')}, "
                    f"Alerts: {summary.get('alerts_generated')}, "
                    f"Risk Index: {summary.get('city_risk_index')}."
                )
            else:
                logger.error(f"[Scheduler] Automated DBSCAN failed: {result.get('message')}")
    except Exception as e:
        logger.exception(f"[Scheduler] Exception during automated DBSCAN execution: {str(e)}")

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Allow CORS from the Vite dev server
    CORS(app, supports_credentials=True, origins=["http://localhost:3000", "http://127.0.0.1:3000"])

    # Initialize extensions
    db.init_app(app)
    jwt = JWTManager(app)

    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(data_bp, url_prefix='/api')
    app.register_blueprint(ml_bp, url_prefix='/api')

    @app.route('/api/health')
    def health_check():
        try:
            db.session.execute(db.text('SELECT 1'))
            db_status = 'connected'
        except Exception as e:
            db_status = f'error: {str(e)}'
        return {'status': 'healthy', 'message': 'SPCS API is running', 'database': db_status}, 200

    # Initialize background scheduler
    scheduler = BackgroundScheduler(daemon=True)
    scheduler.add_job(
        func=run_scheduled_ml,
        trigger='interval',
        hours=1,
        args=[app],
        id='hourly_dbscan'
    )
    
    # Prevent double starting in debug mode
    if not app.debug or os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
        scheduler.start()
        logger.info("[Scheduler] Background scheduler started successfully.")

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)
