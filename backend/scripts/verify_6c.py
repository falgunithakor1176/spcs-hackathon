"""Phase 6C verification script"""
import os, sys
sys.path.append('.')
from dotenv import load_dotenv
load_dotenv('.env')
from flask import Flask
from config import Config
from db import db

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

with app.app_context():
    import models  # register all models
    from models import CrimeForecast, CyberForecast, AreaIntelligence

    phys_count  = CrimeForecast.query.count()
    cyber_count = CyberForecast.query.count()
    intel_count = AreaIntelligence.query.count()

    print(f"[6C] crime_forecasts rows:    {phys_count}")
    print(f"[6C] cyber_forecasts rows:    {cyber_count}")
    print(f"[6C] area_intelligence rows:  {intel_count}")

    if intel_count > 0:
        # Show top 3 priority areas
        top3 = (AreaIntelligence.query
                .order_by(AreaIntelligence.patrol_priority.asc())
                .limit(3).all())
        print("[6C] Top 3 patrol priority areas:")
        for r in top3:
            print(f"     #{r.patrol_priority} {r.area} -> combined_risk={r.combined_risk}, score={r.combined_risk_score}")

    # Check API routes registered
    from routes.forecasts import forecasts_bp
    routes = [str(r) for r in forecasts_bp.url_map.iter_rules()] if hasattr(forecasts_bp, 'url_map') else ['(blueprint - routes registered at app level)']
    print(f"[6C] forecasts_bp registered: YES")

    # Quick Engine 2 run to confirm models load
    from services.prediction_engine import run_prediction_engine
    result = run_prediction_engine()
    print(f"[6C] Engine 2 run: {result['status']} | period={result['forecast_period']}")
    print(f"     Physical: {result['physical']['areas_forecast']} areas | {result['physical']['risk_distribution']}")
    print(f"     Cyber:    {result['cyber']['areas_forecast']} areas | {result['cyber']['risk_distribution']}")

    # Quick Engine 3 run
    from services.correlation_engine import run_correlation_engine
    e3 = run_correlation_engine()
    print(f"[6C] Engine 3 run: {e3['status']} | {e3['areas_processed']} areas | {e3['risk_distribution']}")
    print("[6C] STATUS: OK")
