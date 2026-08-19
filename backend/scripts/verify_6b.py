"""Phase 6B verification script"""
import os, sys, json
sys.path.append('.')
from dotenv import load_dotenv
load_dotenv('.env')
from flask import Flask
from config import Config
from db import db
import joblib

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

with app.app_context():
    model_dir = 'ml_models'
    phys_model  = joblib.load(os.path.join(model_dir, 'physical_rf_model.joblib'))
    cyber_model = joblib.load(os.path.join(model_dir, 'cyber_rf_classifier.joblib'))
    phys_feats  = joblib.load(os.path.join(model_dir, 'physical_feature_names.joblib'))
    cyber_feats = joblib.load(os.path.join(model_dir, 'cyber_feature_names.joblib'))

    with open(os.path.join(model_dir, 'frozen_model_config.json')) as f:
        cfg = json.load(f)

    pm = cfg['physical']
    cm = cfg['cyber']

    print(f"[6B] Physical model: {type(phys_model).__name__}")
    print(f"     max_depth={pm['max_depth']}, n_estimators={pm['n_estimators']}")
    print(f"     Val MAE={pm['metrics']['val_mae']}, Val R2={pm['metrics']['val_r2']}")
    print(f"     Features: {len(phys_feats)}")
    print(f"[6B] Cyber model:    {type(cyber_model).__name__}")
    print(f"     max_depth={cm['max_depth']}, n_estimators={cm['n_estimators']}")
    print(f"     Val Acc={cm['metrics']['val_acc']}, Val F1={cm['metrics']['val_f1']}")
    print(f"     Features: {len(cyber_feats)}")
    print("[6B] STATUS: OK")
