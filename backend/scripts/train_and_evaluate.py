"""
train_and_evaluate.py — Phase 6B: Model Training & Evaluation
==============================================================

This script:
1. Loads training matrices from Phase 6A
2. Splits by time: 2023-2024 = train, 2025 = validation
3. Trains 3 models for Physical Crime: Mean Predictor, Linear Regression, Random Forest
4. Trains 3 models for Cybercrime (regression first): Mean, Linear, Random Forest
5. If cyber regression is weak, compares with RF Classifier
6. Reports MAE, RMSE, R² for all models (train AND validation)
7. Generates Top 15 feature importance rankings
8. Saves evaluation report

Run from the backend directory:
    python scripts/train_and_evaluate.py

NO DATABASE WRITES. Models are saved as .joblib files for later use.
"""

import os
import sys
import json
import numpy as np
import pandas as pd
from collections import OrderedDict

# Add backend directory to path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(backend_dir)

from dotenv import load_dotenv
load_dotenv(os.path.join(backend_dir, '.env'))

from flask import Flask
from config import Config
from db import db

# ML imports
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.linear_model import LinearRegression
from sklearn.metrics import (
    mean_absolute_error, mean_squared_error, r2_score,
    accuracy_score, f1_score, classification_report
)
from sklearn.dummy import DummyRegressor
import joblib


def create_minimal_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    return app


def print_section(title):
    print(f"\n{'=' * 70}")
    print(f"  {title}")
    print(f"{'=' * 70}")


def rmse(y_true, y_pred):
    return np.sqrt(mean_squared_error(y_true, y_pred))


# ─── TIME-BASED SPLIT ─────────────────────────────────────────────────────────

def time_split(clean_df, feature_cols, target_col):
    """
    Split data by time: 2023-2024 for training, 2025 for validation.
    Returns X_train, X_val, y_train, y_val, and the split DataFrames.
    """
    train_mask = clean_df['year'].isin([2023, 2024])
    val_mask = clean_df['year'] == 2025

    train_df = clean_df[train_mask].copy()
    val_df = clean_df[val_mask].copy()

    X_train = train_df[feature_cols].values
    X_val = val_df[feature_cols].values
    y_train = train_df[target_col].values.astype(float)
    y_val = val_df[target_col].values.astype(float)

    return X_train, X_val, y_train, y_val, train_df, val_df, feature_cols


# ─── MODEL EVALUATION ─────────────────────────────────────────────────────────

def evaluate_regression(y_true, y_pred, set_name='Validation'):
    """Compute MAE, RMSE, R² for a regression model."""
    mae = mean_absolute_error(y_true, y_pred)
    rmse_val = rmse(y_true, y_pred)
    r2 = r2_score(y_true, y_pred)
    return {
        'set': set_name,
        'MAE': round(mae, 4),
        'RMSE': round(rmse_val, 4),
        'R2': round(r2, 4),
        'n_samples': len(y_true),
    }


def print_metrics_table(results, title):
    """Print a formatted comparison table of model metrics."""
    print(f"\n  {title}")
    print(f"  {'Model':<25s} {'Set':<12s} {'MAE':>8s} {'RMSE':>8s} {'R2':>8s} {'N':>6s}")
    print(f"  {'-'*25} {'-'*12} {'-'*8} {'-'*8} {'-'*8} {'-'*6}")
    for r in results:
        print(f"  {r['model']:<25s} {r['set']:<12s} {r['MAE']:>8.4f} {r['RMSE']:>8.4f} {r['R2']:>8.4f} {r['n_samples']:>6d}")


def print_feature_importance(feature_names, importances, top_n=15):
    """Print top N feature importance rankings."""
    indices = np.argsort(importances)[::-1][:top_n]
    print(f"\n  Top {top_n} Feature Importance (Random Forest)")
    print(f"  {'Rank':<5s} {'Feature':<30s} {'Importance':>12s} {'Bar'}")
    print(f"  {'-'*5} {'-'*30} {'-'*12} {'-'*30}")
    max_imp = importances[indices[0]] if len(indices) > 0 else 1
    for rank, idx in enumerate(indices, 1):
        bar_len = int(30 * importances[idx] / max(max_imp, 1e-9))
        bar = '#' * bar_len
        print(f"  {rank:<5d} {feature_names[idx]:<30s} {importances[idx]:>12.4f} {bar}")
    return [(feature_names[idx], round(float(importances[idx]), 6)) for idx in indices]


# ─── PHYSICAL CRIME TRAINING ──────────────────────────────────────────────────

def train_physical_models(clean_df):
    """Train and evaluate all physical crime models."""
    target_col = 'target_crime_count'
    feature_cols = [c for c in clean_df.columns if c not in
                    ['area', 'year', 'month', target_col]]

    X_train, X_val, y_train, y_val, train_df, val_df, feat_names = \
        time_split(clean_df, feature_cols, target_col)

    print(f"  Train set: {len(X_train)} samples (2023-2024)")
    print(f"  Val set:   {len(X_val)} samples (2025)")
    print(f"  Features:  {len(feat_names)}")

    results = []

    # ── Model 1: Mean Predictor (Baseline) ──
    print("\n  [1/3] Training Mean Predictor (baseline)...")
    mean_model = DummyRegressor(strategy='mean')
    mean_model.fit(X_train, y_train)

    y_train_pred_mean = mean_model.predict(X_train)
    y_val_pred_mean = mean_model.predict(X_val)

    r_train = evaluate_regression(y_train, y_train_pred_mean, 'Train')
    r_val = evaluate_regression(y_val, y_val_pred_mean, 'Validation')
    r_train['model'] = 'Mean Predictor'
    r_val['model'] = 'Mean Predictor'
    results.extend([r_train, r_val])

    # ── Model 2: Linear Regression ──
    print("  [2/3] Training Linear Regression...")
    lr_model = LinearRegression()
    lr_model.fit(X_train, y_train)

    y_train_pred_lr = lr_model.predict(X_train)
    y_val_pred_lr = lr_model.predict(X_val)

    r_train = evaluate_regression(y_train, y_train_pred_lr, 'Train')
    r_val = evaluate_regression(y_val, y_val_pred_lr, 'Validation')
    r_train['model'] = 'Linear Regression'
    r_val['model'] = 'Linear Regression'
    results.extend([r_train, r_val])

    # ── Model 3: Random Forest Regressor ──
    print("  [3/3] Training Random Forest Regressor...")
    rf_model = RandomForestRegressor(
        n_estimators=200,
        max_depth=12,
        min_samples_split=5,
        min_samples_leaf=3,
        max_features='sqrt',
        random_state=42,
        n_jobs=-1,
    )
    rf_model.fit(X_train, y_train)

    y_train_pred_rf = rf_model.predict(X_train)
    y_val_pred_rf = rf_model.predict(X_val)

    r_train = evaluate_regression(y_train, y_train_pred_rf, 'Train')
    r_val = evaluate_regression(y_val, y_val_pred_rf, 'Validation')
    r_train['model'] = 'Random Forest'
    r_val['model'] = 'Random Forest'
    results.extend([r_train, r_val])

    # Print comparison table
    print_metrics_table(results, "PHYSICAL CRIME — Model Comparison")

    # Feature importance
    importances = rf_model.feature_importances_
    top_features = print_feature_importance(feat_names, importances, top_n=15)

    # Overfitting analysis
    rf_train_r2 = results[-2]['R2']  # RF train
    rf_val_r2 = results[-1]['R2']    # RF val
    overfit_gap = rf_train_r2 - rf_val_r2
    print(f"\n  [OVERFITTING CHECK]")
    print(f"  RF Train R2: {rf_train_r2:.4f}")
    print(f"  RF Val R2:   {rf_val_r2:.4f}")
    print(f"  Gap:         {overfit_gap:.4f}")
    if overfit_gap > 0.2:
        print(f"  WARNING: Significant overfitting detected (gap > 0.2)")
    elif overfit_gap > 0.1:
        print(f"  CAUTION: Moderate overfitting (gap > 0.1)")
    else:
        print(f"  OK: No significant overfitting")

    return {
        'results': results,
        'top_features': top_features,
        'overfit_gap': round(overfit_gap, 4),
        'rf_model': rf_model,
        'feature_names': feat_names,
        'val_predictions': y_val_pred_rf.tolist(),
        'val_actuals': y_val.tolist(),
        'val_areas': val_df['area'].tolist(),
        'val_months': val_df['month'].tolist(),
    }


# ─── CYBERCRIME TRAINING ──────────────────────────────────────────────────────

def train_cyber_models(clean_df):
    """
    Train and evaluate cybercrime models.
    Step 1: Train as regression (Mean, Linear, RF)
    Step 2: If RF regression R² < 0.3, compare with RF Classifier
    """
    target_col = 'target_cyber_count'
    feature_cols = [c for c in clean_df.columns if c not in
                    ['area', 'year', 'month', target_col]]

    X_train, X_val, y_train, y_val, train_df, val_df, feat_names = \
        time_split(clean_df, feature_cols, target_col)

    print(f"  Train set: {len(X_train)} samples (2023-2024)")
    print(f"  Val set:   {len(X_val)} samples (2025)")
    print(f"  Features:  {len(feat_names)}")

    results = []

    # ── Regression Models ──
    # Model 1: Mean Predictor
    print("\n  [1/3] Training Mean Predictor (baseline)...")
    mean_model = DummyRegressor(strategy='mean')
    mean_model.fit(X_train, y_train)
    y_train_pred_mean = mean_model.predict(X_train)
    y_val_pred_mean = mean_model.predict(X_val)

    r_train = evaluate_regression(y_train, y_train_pred_mean, 'Train')
    r_val = evaluate_regression(y_val, y_val_pred_mean, 'Validation')
    r_train['model'] = 'Mean Predictor'
    r_val['model'] = 'Mean Predictor'
    results.extend([r_train, r_val])

    # Model 2: Linear Regression
    print("  [2/3] Training Linear Regression...")
    lr_model = LinearRegression()
    lr_model.fit(X_train, y_train)
    y_train_pred_lr = lr_model.predict(X_train)
    y_val_pred_lr = lr_model.predict(X_val)

    r_train = evaluate_regression(y_train, y_train_pred_lr, 'Train')
    r_val = evaluate_regression(y_val, y_val_pred_lr, 'Validation')
    r_train['model'] = 'Linear Regression'
    r_val['model'] = 'Linear Regression'
    results.extend([r_train, r_val])

    # Model 3: Random Forest Regressor
    print("  [3/3] Training Random Forest Regressor...")
    rf_model = RandomForestRegressor(
        n_estimators=200,
        max_depth=10,
        min_samples_split=5,
        min_samples_leaf=3,
        max_features='sqrt',
        random_state=42,
        n_jobs=-1,
    )
    rf_model.fit(X_train, y_train)
    y_train_pred_rf = rf_model.predict(X_train)
    y_val_pred_rf = rf_model.predict(X_val)

    r_train = evaluate_regression(y_train, y_train_pred_rf, 'Train')
    r_val = evaluate_regression(y_val, y_val_pred_rf, 'Validation')
    r_train['model'] = 'RF Regressor'
    r_val['model'] = 'RF Regressor'
    results.extend([r_train, r_val])

    # Print regression comparison
    print_metrics_table(results, "CYBERCRIME — Regression Model Comparison")

    # Feature importance (regression)
    importances = rf_model.feature_importances_
    top_features = print_feature_importance(feat_names, importances, top_n=15)

    # Overfitting check
    rf_train_r2 = results[-2]['R2']
    rf_val_r2 = results[-1]['R2']
    overfit_gap = rf_train_r2 - rf_val_r2
    print(f"\n  [OVERFITTING CHECK]")
    print(f"  RF Train R2: {rf_train_r2:.4f}")
    print(f"  RF Val R2:   {rf_val_r2:.4f}")
    print(f"  Gap:         {overfit_gap:.4f}")

    # ── Step 2: If regression is weak, compare with classifier ──
    classifier_results = None
    classifier_report_text = None
    recommendation = 'regression'

    # Define risk categories from training target distribution
    q25 = np.percentile(y_train, 25)
    q50 = np.percentile(y_train, 50)
    q75 = np.percentile(y_train, 75)

    def count_to_risk(count):
        if count <= q25:
            return 'Low'
        elif count <= q50:
            return 'Medium'
        elif count <= q75:
            return 'High'
        else:
            return 'Critical'

    # Always show regression-derived risk performance
    y_val_risk_from_reg = [count_to_risk(c) for c in y_val_pred_rf]
    y_val_risk_actual = [count_to_risk(c) for c in y_val]

    reg_derived_accuracy = accuracy_score(y_val_risk_actual, y_val_risk_from_reg)
    reg_derived_f1 = f1_score(y_val_risk_actual, y_val_risk_from_reg, average='weighted', zero_division=0)

    print(f"\n  [REGRESSION-DERIVED RISK CATEGORIES]")
    print(f"  Thresholds: Low <= {q25:.0f}, Medium <= {q50:.0f}, High <= {q75:.0f}, Critical > {q75:.0f}")
    print(f"  Accuracy (from regression): {reg_derived_accuracy:.4f}")
    print(f"  Weighted F1 (from regression): {reg_derived_f1:.4f}")

    # If regression R2 on validation < 0.3, also train classifier for comparison
    REGRESSION_WEAK_THRESHOLD = 0.3
    if rf_val_r2 < REGRESSION_WEAK_THRESHOLD:
        print(f"\n  [!] Regression R2 ({rf_val_r2:.4f}) < {REGRESSION_WEAK_THRESHOLD}")
        print(f"  Training RF Classifier for comparison...\n")

        # Create classification labels
        y_train_class = np.array([count_to_risk(c) for c in y_train])
        y_val_class = np.array([count_to_risk(c) for c in y_val])

        clf_model = RandomForestClassifier(
            n_estimators=200,
            max_depth=10,
            min_samples_split=5,
            min_samples_leaf=3,
            max_features='sqrt',
            random_state=42,
            n_jobs=-1,
            class_weight='balanced',
        )
        clf_model.fit(X_train, y_train_class)

        y_train_pred_clf = clf_model.predict(X_train)
        y_val_pred_clf = clf_model.predict(X_val)

        clf_train_acc = accuracy_score(y_train_class, y_train_pred_clf)
        clf_val_acc = accuracy_score(y_val_class, y_val_pred_clf)
        clf_train_f1 = f1_score(y_train_class, y_train_pred_clf, average='weighted', zero_division=0)
        clf_val_f1 = f1_score(y_val_class, y_val_pred_clf, average='weighted', zero_division=0)

        print(f"  [CLASSIFIER COMPARISON]")
        print(f"  {'Approach':<30s} {'Accuracy':>10s} {'Weighted F1':>12s}")
        print(f"  {'-'*30} {'-'*10} {'-'*12}")
        print(f"  {'Regression -> Risk (val)':<30s} {reg_derived_accuracy:>10.4f} {reg_derived_f1:>12.4f}")
        print(f"  {'Direct Classifier (train)':<30s} {clf_train_acc:>10.4f} {clf_train_f1:>12.4f}")
        print(f"  {'Direct Classifier (val)':<30s} {clf_val_acc:>10.4f} {clf_val_f1:>12.4f}")

        classifier_report_text = classification_report(
            y_val_class, y_val_pred_clf, zero_division=0
        )
        print(f"\n  Classification Report (Validation):")
        for line in classifier_report_text.split('\n'):
            print(f"  {line}")

        classifier_results = {
            'train_accuracy': round(clf_train_acc, 4),
            'val_accuracy': round(clf_val_acc, 4),
            'train_f1': round(clf_train_f1, 4),
            'val_f1': round(clf_val_f1, 4),
            'classification_report': classifier_report_text,
        }

        # Recommend based on comparison
        if clf_val_f1 > reg_derived_f1 + 0.05:
            recommendation = 'classification'
            print(f"\n  RECOMMENDATION: Use CLASSIFICATION (F1 improvement > 0.05)")
        else:
            recommendation = 'regression'
            print(f"\n  RECOMMENDATION: Keep REGRESSION (classifier does not significantly outperform)")
    else:
        print(f"\n  Regression R2 ({rf_val_r2:.4f}) >= {REGRESSION_WEAK_THRESHOLD}")
        print(f"  Regression performance is acceptable. No classifier comparison needed.")

    return {
        'results': results,
        'top_features': top_features,
        'overfit_gap': round(overfit_gap, 4),
        'rf_model': rf_model,
        'feature_names': feat_names,
        'val_predictions': y_val_pred_rf.tolist(),
        'val_actuals': y_val.tolist(),
        'val_areas': val_df['area'].tolist(),
        'val_months': val_df['month'].tolist(),
        'risk_thresholds': {
            'q25': round(float(q25), 2),
            'q50': round(float(q50), 2),
            'q75': round(float(q75), 2),
        },
        'regression_derived_risk': {
            'accuracy': round(reg_derived_accuracy, 4),
            'f1': round(reg_derived_f1, 4),
        },
        'classifier_comparison': classifier_results,
        'recommendation': recommendation,
    }


# ─── MAIN ──────────────────────────────────────────────────────────────────────

def main():
    app = create_minimal_app()

    with app.app_context():
        from services.feature_engine import (
            build_physical_training_matrix,
            build_cyber_training_matrix,
        )

        # ─── PHYSICAL CRIME ──────────────────────────────────────────────
        print_section("PHASE 6B: PHYSICAL CRIME — Model Training")

        print("  Building feature matrix...")
        phys_features, phys_target, phys_raw, phys_clean = build_physical_training_matrix()
        print(f"  Matrix ready: {phys_clean.shape[0]} samples")

        phys_results = train_physical_models(phys_clean)

        # ─── CYBERCRIME ──────────────────────────────────────────────────
        print_section("PHASE 6B: CYBERCRIME — Model Training")

        print("  Building feature matrix...")
        cyber_features, cyber_target, cyber_raw, cyber_clean = build_cyber_training_matrix()
        print(f"  Matrix ready: {cyber_clean.shape[0]} samples")

        cyber_results = train_cyber_models(cyber_clean)

        # ─── SAVE MODELS ──────────────────────────────────────────────────
        model_dir = os.path.join(backend_dir, 'ml_models')
        os.makedirs(model_dir, exist_ok=True)

        joblib.dump(phys_results['rf_model'],
                    os.path.join(model_dir, 'physical_rf_model.joblib'))
        joblib.dump(cyber_results['rf_model'],
                    os.path.join(model_dir, 'cyber_rf_model.joblib'))
        joblib.dump(phys_results['feature_names'],
                    os.path.join(model_dir, 'physical_feature_names.joblib'))
        joblib.dump(cyber_results['feature_names'],
                    os.path.join(model_dir, 'cyber_feature_names.joblib'))

        print(f"\n  Models saved to: {model_dir}")

        # ─── SAVE EVALUATION REPORT ───────────────────────────────────────
        report = {
            'physical': {
                'model_comparison': phys_results['results'],
                'top_15_features': phys_results['top_features'],
                'overfit_gap': phys_results['overfit_gap'],
                'val_sample_predictions': [
                    {
                        'area': phys_results['val_areas'][i],
                        'month': int(phys_results['val_months'][i]),
                        'actual': int(phys_results['val_actuals'][i]),
                        'predicted': round(phys_results['val_predictions'][i], 1),
                    }
                    for i in range(min(20, len(phys_results['val_actuals'])))
                ],
            },
            'cyber': {
                'model_comparison': cyber_results['results'],
                'top_15_features': cyber_results['top_features'],
                'overfit_gap': cyber_results['overfit_gap'],
                'risk_thresholds': cyber_results['risk_thresholds'],
                'regression_derived_risk': cyber_results['regression_derived_risk'],
                'classifier_comparison': cyber_results['classifier_comparison'],
                'recommendation': cyber_results['recommendation'],
                'val_sample_predictions': [
                    {
                        'area': cyber_results['val_areas'][i],
                        'month': int(cyber_results['val_months'][i]),
                        'actual': int(cyber_results['val_actuals'][i]),
                        'predicted': round(cyber_results['val_predictions'][i], 1),
                    }
                    for i in range(min(20, len(cyber_results['val_actuals'])))
                ],
            },
        }

        report_path = os.path.join(backend_dir, 'data', 'training', 'phase6b_evaluation_report.json')
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        print(f"  Evaluation report saved to: {report_path}")

        # ─── FINAL SUMMARY ────────────────────────────────────────────────
        print_section("PHASE 6B — FINAL SUMMARY")

        # Find best physical model
        phys_val_results = [r for r in phys_results['results'] if r['set'] == 'Validation']
        best_phys = max(phys_val_results, key=lambda x: x['R2'])
        print(f"  Physical Crime Best Model: {best_phys['model']}")
        print(f"    Val MAE:  {best_phys['MAE']}")
        print(f"    Val RMSE: {best_phys['RMSE']}")
        print(f"    Val R2:   {best_phys['R2']}")
        print(f"    Overfit Gap: {phys_results['overfit_gap']}")

        # Find best cyber model
        cyber_val_results = [r for r in cyber_results['results'] if r['set'] == 'Validation']
        best_cyber = max(cyber_val_results, key=lambda x: x['R2'])
        print(f"\n  Cybercrime Best Model: {best_cyber['model']}")
        print(f"    Val MAE:  {best_cyber['MAE']}")
        print(f"    Val RMSE: {best_cyber['RMSE']}")
        print(f"    Val R2:   {best_cyber['R2']}")
        print(f"    Overfit Gap: {cyber_results['overfit_gap']}")
        print(f"    Recommendation: {cyber_results['recommendation'].upper()}")

        if cyber_results['classifier_comparison']:
            print(f"    Classifier Val F1: {cyber_results['classifier_comparison']['val_f1']}")
            print(f"    Regression-derived Risk F1: {cyber_results['regression_derived_risk']['f1']}")

        print(f"\n  Phase 6B COMPLETE. Awaiting user approval before Phase 6C.\n")


if __name__ == '__main__':
    main()
