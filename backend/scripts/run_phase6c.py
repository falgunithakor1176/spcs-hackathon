"""
run_phase6c.py — End-to-end Phase 6C pipeline runner
=====================================================
1. Creates the 3 new tables (crime_forecasts, cyber_forecasts, area_intelligence)
2. Runs Engine 2 (RF predictions) for the next calendar month
3. Runs Engine 3 (Correlation Engine) for the same period
4. Prints a full summary report

Run from backend directory:
    python scripts/run_phase6c.py
"""

import os, sys

backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(backend_dir)

from dotenv import load_dotenv
load_dotenv(os.path.join(backend_dir, '.env'))

from flask import Flask
from config import Config
from db import db


def create_minimal_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    return app


def sep(title=''):
    print(f"\n{'=' * 70}")
    if title:
        print(f"  {title}")
        print(f"{'=' * 70}")


def main():
    app = create_minimal_app()

    with app.app_context():
        # ── Step 1: Create new tables ─────────────────────────────────────
        sep("STEP 1: Creating Phase 6C DB Tables")
        # Import models so SQLAlchemy registers them
        import models  # noqa — registers all models including new 6C ones
        db.create_all()
        print("  crime_forecasts    — OK")
        print("  cyber_forecasts    — OK")
        print("  area_intelligence  — OK")

        # ── Step 2: Engine 2 ──────────────────────────────────────────────
        sep("STEP 2: Engine 2 — Crime Prediction (RF Models)")
        from services.prediction_engine import run_prediction_engine
        e2_result = run_prediction_engine()

        print(f"  Forecast period:  {e2_result['forecast_period']}")
        print(f"  Physical areas:   {e2_result['physical']['areas_forecast']}")
        print(f"  Physical dist:    {e2_result['physical']['risk_distribution']}")
        print(f"  Cyber areas:      {e2_result['cyber']['areas_forecast']}")
        print(f"  Cyber dist:       {e2_result['cyber']['risk_distribution']}")

        # ── Step 3: Engine 3 ──────────────────────────────────────────────
        sep("STEP 3: Engine 3 — Correlation Engine (Combined Risk)")
        from services.correlation_engine import run_correlation_engine
        e3_result = run_correlation_engine()

        print(f"  Forecast period:  {e3_result['forecast_period']}")
        print(f"  Weights used:     {e3_result['weights_used']}")
        print(f"  Areas processed:  {e3_result['areas_processed']}")
        print(f"  Combined risk dist: {e3_result['risk_distribution']}")

        print(f"\n  TOP 5 PATROL PRIORITY AREAS:")
        print(f"  {'Rank':<5} {'Area':<20} {'Combined':<10} {'Score':<7} {'Physical':<10} {'Cyber':<10} {'Spatial'}")
        print(f"  {'-'*5} {'-'*20} {'-'*10} {'-'*7} {'-'*10} {'-'*10} {'-'*10}")
        for a in e3_result['top_5_priority_areas']:
            print(f"  {a['rank']:<5} {a['area']:<20} {a['combined_risk']:<10} "
                  f"{a['score']:<7.4f} {a['physical_risk']:<10} "
                  f"{a['cyber_risk']:<10} {a['hotspot_risk']}")

        # ── Step 4: Verify DB rows ─────────────────────────────────────────
        sep("STEP 4: Database Verification")
        from models import CrimeForecast, CyberForecast, AreaIntelligence
        phys_count  = CrimeForecast.query.count()
        cyber_count = CyberForecast.query.count()
        intel_count = AreaIntelligence.query.count()
        print(f"  crime_forecasts rows:    {phys_count}")
        print(f"  cyber_forecasts rows:    {cyber_count}")
        print(f"  area_intelligence rows:  {intel_count}")

        sep("PHASE 6C COMPLETE")
        print("  All engines operational. API endpoints live:")
        print("    POST  /api/engine2/run")
        print("    GET   /api/engine2/forecasts")
        print("    POST  /api/engine3/run")
        print("    GET   /api/engine3/area-intelligence")
        print("    GET   /api/engine3/config")
        print()


if __name__ == '__main__':
    main()
