import sys, os, time
sys.path.append(os.path.join(os.getcwd(), 'backend'))
from app import create_app
from db import db
from sqlalchemy import text
from services.ml_service import run_dbscan_engine

app = create_app()
with app.app_context():
    print('==============================')
    print(' PHASE 5 VERIFICATION SCRIPT')
    print('==============================\n')

    # Trigger ML Engine to do assignments
    print('--- Running Automated ML Engine ---')
    res = run_dbscan_engine()
    print(f"Risk Index Calculated: {res.get('summary').get('city_risk_index')}")
    
    # 1. Check Hotspots Count
    hs_count = db.session.execute(text('SELECT COUNT(*) FROM hotspots')).scalar()
    print(f'\n[DB Check] SELECT COUNT(*) FROM hotspots; => {hs_count}')
    
    # 2. Check Predictions Count
    pred_count = db.session.execute(text('SELECT COUNT(*) FROM predictions')).scalar()
    print(f'[DB Check] SELECT COUNT(*) FROM predictions; => {pred_count}')
    
    # 3. Check Alerts Count
    alerts_count = db.session.execute(text('SELECT COUNT(*) FROM alerts')).scalar()
    print(f'[DB Check] SELECT COUNT(*) FROM alerts; => {alerts_count}')

    print('\n--- 5 Sample Hotspots ---')
    for row in db.session.execute(text('SELECT * FROM hotspots LIMIT 5')).fetchall():
        print(dict(row._mapping))
        
    print('\n--- 5 Sample Predictions ---')
    for row in db.session.execute(text('SELECT * FROM predictions LIMIT 5')).fetchall():
        print(dict(row._mapping))
        
    print('\n--- 5 Sample Alerts ---')
    for row in db.session.execute(text('SELECT * FROM alerts LIMIT 5')).fetchall():
        print(dict(row._mapping))
        
    print('\n--- Assigned Patrols (ML Engine Module 3) ---')
    assigned_alerts = db.session.execute(text('SELECT id, type, title, area, assigned_to FROM alerts WHERE id LIKE \'ALT-ML-%\' AND assigned_to IS NOT NULL LIMIT 5')).fetchall()
    for row in assigned_alerts:
        print(dict(row._mapping))
        
    print('\n--- Updated Patrol Statuses ---')
    patrols = db.session.execute(text('SELECT vehicle_id, status FROM patrol_units WHERE status = \'Responding\' LIMIT 5')).fetchall()
    for row in patrols:
        print(dict(row._mapping))
