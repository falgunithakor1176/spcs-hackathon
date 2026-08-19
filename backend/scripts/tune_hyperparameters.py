"""
tune_hyperparameters.py — Phase 6B+: Hyperparameter Tuning
============================================================

Tests combinations of max_depth, min_samples_leaf, min_samples_split
for both Physical (RF Regressor) and Cyber (RF Classifier).

Selects based on VALIDATION performance, not training.
Saves the best models as .joblib files.

Run from backend directory:
    python scripts/tune_hyperparameters.py
"""

import os
import sys
import json
import numpy as np
import pandas as pd
from itertools import product

backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(backend_dir)

from dotenv import load_dotenv
load_dotenv(os.path.join(backend_dir, '.env'))

from flask import Flask
from config import Config
from db import db

from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.metrics import (
    mean_absolute_error, mean_squared_error, r2_score,
    f1_score, accuracy_score
)
import joblib


def create_minimal_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    return app


def rmse(y_true, y_pred):
    return np.sqrt(mean_squared_error(y_true, y_pred))


def time_split(clean_df, feature_cols, target_col):
    train_mask = clean_df['year'].isin([2023, 2024])
    val_mask = clean_df['year'] == 2025
    train_df = clean_df[train_mask].copy()
    val_df = clean_df[val_mask].copy()
    X_train = train_df[feature_cols].values
    X_val = val_df[feature_cols].values
    y_train = train_df[target_col].values.astype(float)
    y_val = val_df[target_col].values.astype(float)
    return X_train, X_val, y_train, y_val, train_df, val_df


def main():
    app = create_minimal_app()

    with app.app_context():
        from services.feature_engine import (
            build_physical_training_matrix,
            build_cyber_training_matrix,
        )

        # ═══════════════════════════════════════════════════════════════════
        #  PHYSICAL CRIME — HYPERPARAMETER GRID SEARCH
        # ═══════════════════════════════════════════════════════════════════
        print("=" * 70)
        print("  PHYSICAL CRIME — Hyperparameter Tuning")
        print("=" * 70)

        _, _, _, phys_clean = build_physical_training_matrix()
        target_col = 'target_crime_count'
        feature_cols = [c for c in phys_clean.columns if c not in
                        ['area', 'year', 'month', target_col]]

        X_train, X_val, y_train, y_val, _, _ = \
            time_split(phys_clean, feature_cols, target_col)

        print(f"  Train: {len(X_train)}, Val: {len(X_val)}, Features: {len(feature_cols)}")

        # Grid
        max_depths = [6, 8, 10, 12]
        min_samples_leafs = [1, 3, 5]
        min_samples_splits = [2, 5, 10]

        configs = list(product(max_depths, min_samples_leafs, min_samples_splits))
        print(f"  Testing {len(configs)} configurations...\n")

        print(f"  {'#':>3s}  {'depth':>5s} {'leaf':>4s} {'split':>5s}  "
              f"{'Tr_MAE':>7s} {'Tr_R2':>7s}  {'Val_MAE':>7s} {'Val_R2':>7s}  {'Gap':>6s}")
        print(f"  {'---':>3s}  {'-----':>5s} {'----':>4s} {'-----':>5s}  "
              f"{'-------':>7s} {'-------':>7s}  {'-------':>7s} {'-------':>7s}  {'------':>6s}")

        phys_results = []
        for i, (md, ml, ms) in enumerate(configs, 1):
            model = RandomForestRegressor(
                n_estimators=200, max_depth=md,
                min_samples_leaf=ml, min_samples_split=ms,
                max_features='sqrt', random_state=42, n_jobs=-1,
            )
            model.fit(X_train, y_train)

            tr_pred = model.predict(X_train)
            val_pred = model.predict(X_val)

            tr_mae = mean_absolute_error(y_train, tr_pred)
            tr_r2 = r2_score(y_train, tr_pred)
            v_mae = mean_absolute_error(y_val, val_pred)
            v_rmse = rmse(y_val, val_pred)
            v_r2 = r2_score(y_val, val_pred)
            gap = tr_r2 - v_r2

            phys_results.append({
                'max_depth': md, 'min_samples_leaf': ml, 'min_samples_split': ms,
                'train_mae': round(tr_mae, 4), 'train_r2': round(tr_r2, 4),
                'val_mae': round(v_mae, 4), 'val_rmse': round(v_rmse, 4),
                'val_r2': round(v_r2, 4), 'gap': round(gap, 4),
                'model': model,
            })

            print(f"  {i:3d}  {md:5d} {ml:4d} {ms:5d}  "
                  f"{tr_mae:7.4f} {tr_r2:7.4f}  {v_mae:7.4f} {v_r2:7.4f}  {gap:6.4f}")

        # Select best by validation MAE (lower is better), then by R2 as tiebreaker
        best_phys = min(phys_results, key=lambda x: (x['val_mae'], -x['val_r2']))

        print(f"\n  BEST PHYSICAL CONFIG:")
        print(f"    max_depth={best_phys['max_depth']}, "
              f"min_samples_leaf={best_phys['min_samples_leaf']}, "
              f"min_samples_split={best_phys['min_samples_split']}")
        print(f"    Train MAE: {best_phys['train_mae']}, Train R2: {best_phys['train_r2']}")
        print(f"    Val MAE:   {best_phys['val_mae']}, Val R2: {best_phys['val_r2']}")
        print(f"    Overfit gap: {best_phys['gap']}")

        # Previous model stats (from Phase 6B)
        print(f"\n  COMPARISON WITH PREVIOUS MODEL (depth=12, leaf=3, split=5):")
        print(f"    Previous: Val MAE=7.6661, Val R2=0.2914, Gap=0.5656")
        print(f"    Tuned:    Val MAE={best_phys['val_mae']}, Val R2={best_phys['val_r2']}, Gap={best_phys['gap']}")
        mae_improved = 7.6661 - best_phys['val_mae']
        r2_improved = best_phys['val_r2'] - 0.2914
        gap_improved = 0.5656 - best_phys['gap']
        print(f"    MAE change:  {mae_improved:+.4f} ({'better' if mae_improved > 0 else 'worse'})")
        print(f"    R2 change:   {r2_improved:+.4f} ({'better' if r2_improved > 0 else 'worse'})")
        print(f"    Gap change:  {gap_improved:+.4f} ({'less overfit' if gap_improved > 0 else 'more overfit'})")

        # ═══════════════════════════════════════════════════════════════════
        #  CYBERCRIME — HYPERPARAMETER GRID SEARCH (CLASSIFIER)
        # ═══════════════════════════════════════════════════════════════════
        print(f"\n{'=' * 70}")
        print("  CYBERCRIME — Hyperparameter Tuning (Classifier)")
        print("=" * 70)

        _, _, _, cyber_clean = build_cyber_training_matrix()
        cyber_target_col = 'target_cyber_count'
        cyber_feature_cols = [c for c in cyber_clean.columns if c not in
                              ['area', 'year', 'month', cyber_target_col]]

        cX_train, cX_val, cy_train_raw, cy_val_raw, _, _ = \
            time_split(cyber_clean, cyber_feature_cols, cyber_target_col)

        # Create classification labels
        q25 = np.percentile(cy_train_raw, 25)
        q50 = np.percentile(cy_train_raw, 50)
        q75 = np.percentile(cy_train_raw, 75)

        def count_to_risk(count):
            if count <= q25: return 'Low'
            elif count <= q50: return 'Medium'
            elif count <= q75: return 'High'
            else: return 'Critical'

        cy_train = np.array([count_to_risk(c) for c in cy_train_raw])
        cy_val = np.array([count_to_risk(c) for c in cy_val_raw])

        print(f"  Train: {len(cX_train)}, Val: {len(cX_val)}, Features: {len(cyber_feature_cols)}")
        print(f"  Classes: {np.unique(cy_train)}")
        print(f"  Testing {len(configs)} configurations...\n")

        print(f"  {'#':>3s}  {'depth':>5s} {'leaf':>4s} {'split':>5s}  "
              f"{'Tr_Acc':>7s} {'Tr_F1':>7s}  {'Val_Acc':>7s} {'Val_F1':>7s}  {'Gap_F1':>6s}")
        print(f"  {'---':>3s}  {'-----':>5s} {'----':>4s} {'-----':>5s}  "
              f"{'-------':>7s} {'-------':>7s}  {'-------':>7s} {'-------':>7s}  {'------':>6s}")

        cyber_results = []
        for i, (md, ml, ms) in enumerate(configs, 1):
            model = RandomForestClassifier(
                n_estimators=200, max_depth=md,
                min_samples_leaf=ml, min_samples_split=ms,
                max_features='sqrt', random_state=42, n_jobs=-1,
                class_weight='balanced',
            )
            model.fit(cX_train, cy_train)

            tr_pred = model.predict(cX_train)
            val_pred = model.predict(cX_val)

            tr_acc = accuracy_score(cy_train, tr_pred)
            tr_f1 = f1_score(cy_train, tr_pred, average='weighted', zero_division=0)
            v_acc = accuracy_score(cy_val, val_pred)
            v_f1 = f1_score(cy_val, val_pred, average='weighted', zero_division=0)
            gap_f1 = tr_f1 - v_f1

            cyber_results.append({
                'max_depth': md, 'min_samples_leaf': ml, 'min_samples_split': ms,
                'train_acc': round(tr_acc, 4), 'train_f1': round(tr_f1, 4),
                'val_acc': round(v_acc, 4), 'val_f1': round(v_f1, 4),
                'gap_f1': round(gap_f1, 4),
                'model': model,
            })

            print(f"  {i:3d}  {md:5d} {ml:4d} {ms:5d}  "
                  f"{tr_acc:7.4f} {tr_f1:7.4f}  {v_acc:7.4f} {v_f1:7.4f}  {gap_f1:6.4f}")

        # Select best by validation F1
        best_cyber = max(cyber_results, key=lambda x: (x['val_f1'], -x['gap_f1']))

        print(f"\n  BEST CYBER CONFIG:")
        print(f"    max_depth={best_cyber['max_depth']}, "
              f"min_samples_leaf={best_cyber['min_samples_leaf']}, "
              f"min_samples_split={best_cyber['min_samples_split']}")
        print(f"    Train Acc: {best_cyber['train_acc']}, Train F1: {best_cyber['train_f1']}")
        print(f"    Val Acc:   {best_cyber['val_acc']}, Val F1: {best_cyber['val_f1']}")
        print(f"    Overfit gap (F1): {best_cyber['gap_f1']}")

        print(f"\n  COMPARISON WITH PREVIOUS MODEL (depth=10, leaf=3, split=5):")
        print(f"    Previous: Val Acc=0.4907, Val F1=0.4785, Gap=0.4546")
        print(f"    Tuned:    Val Acc={best_cyber['val_acc']}, Val F1={best_cyber['val_f1']}, Gap={best_cyber['gap_f1']}")
        f1_improved = best_cyber['val_f1'] - 0.4785
        gap_f1_improved = 0.4546 - best_cyber['gap_f1']
        print(f"    F1 change:   {f1_improved:+.4f} ({'better' if f1_improved > 0 else 'worse'})")
        print(f"    Gap change:  {gap_f1_improved:+.4f} ({'less overfit' if gap_f1_improved > 0 else 'more overfit'})")

        # ═══════════════════════════════════════════════════════════════════
        #  SAVE FINAL MODELS
        # ═══════════════════════════════════════════════════════════════════
        model_dir = os.path.join(backend_dir, 'ml_models')
        os.makedirs(model_dir, exist_ok=True)

        # Save physical model
        joblib.dump(best_phys['model'], os.path.join(model_dir, 'physical_rf_model.joblib'))
        joblib.dump(feature_cols, os.path.join(model_dir, 'physical_feature_names.joblib'))

        # Save cyber classifier model
        joblib.dump(best_cyber['model'], os.path.join(model_dir, 'cyber_rf_classifier.joblib'))
        joblib.dump(cyber_feature_cols, os.path.join(model_dir, 'cyber_feature_names.joblib'))

        # Save hyperparameters and thresholds
        frozen_config = {
            'physical': {
                'model_type': 'RandomForestRegressor',
                'n_estimators': 200,
                'max_depth': best_phys['max_depth'],
                'min_samples_leaf': best_phys['min_samples_leaf'],
                'min_samples_split': best_phys['min_samples_split'],
                'max_features': 'sqrt',
                'random_state': 42,
                'metrics': {
                    'train_mae': best_phys['train_mae'],
                    'train_r2': best_phys['train_r2'],
                    'val_mae': best_phys['val_mae'],
                    'val_rmse': best_phys['val_rmse'],
                    'val_r2': best_phys['val_r2'],
                    'overfit_gap': best_phys['gap'],
                },
                'feature_names': feature_cols,
            },
            'cyber': {
                'model_type': 'RandomForestClassifier',
                'n_estimators': 200,
                'max_depth': best_cyber['max_depth'],
                'min_samples_leaf': best_cyber['min_samples_leaf'],
                'min_samples_split': best_cyber['min_samples_split'],
                'max_features': 'sqrt',
                'random_state': 42,
                'class_weight': 'balanced',
                'risk_thresholds': {
                    'q25': float(q25), 'q50': float(q50), 'q75': float(q75),
                },
                'metrics': {
                    'train_acc': best_cyber['train_acc'],
                    'train_f1': best_cyber['train_f1'],
                    'val_acc': best_cyber['val_acc'],
                    'val_f1': best_cyber['val_f1'],
                    'overfit_gap_f1': best_cyber['gap_f1'],
                },
                'feature_names': cyber_feature_cols,
            },
        }

        config_path = os.path.join(model_dir, 'frozen_model_config.json')
        with open(config_path, 'w') as f:
            json.dump(frozen_config, f, indent=2)

        # Also save full grid results
        grid_results = {
            'physical_grid': [
                {k: v for k, v in r.items() if k != 'model'}
                for r in phys_results
            ],
            'cyber_grid': [
                {k: v for k, v in r.items() if k != 'model'}
                for r in cyber_results
            ],
        }
        grid_path = os.path.join(model_dir, 'grid_search_results.json')
        with open(grid_path, 'w') as f:
            json.dump(grid_results, f, indent=2)

        print(f"\n{'=' * 70}")
        print("  MODELS FROZEN")
        print(f"{'=' * 70}")
        print(f"  Physical RF model:   {os.path.join(model_dir, 'physical_rf_model.joblib')}")
        print(f"  Cyber RF classifier: {os.path.join(model_dir, 'cyber_rf_classifier.joblib')}")
        print(f"  Config:              {config_path}")
        print(f"  Grid results:        {grid_path}")
        print(f"\n  Ready for Phase 6C.\n")


if __name__ == '__main__':
    main()
