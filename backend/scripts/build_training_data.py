"""
build_training_data.py — Phase 6A CLI Runner
==============================================

Run from the backend directory:
    python scripts/build_training_data.py

This script:
1. Connects to the PostgreSQL database
2. Runs the feature engineering pipeline
3. Generates a comprehensive validation report
4. Saves the training matrices as CSV files for inspection
5. Prints the report to console

NO MODEL TRAINING. NO DATABASE WRITES.
"""

import os
import sys
import json

# Add backend directory to path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(backend_dir)

from dotenv import load_dotenv
load_dotenv(os.path.join(backend_dir, '.env'))

from flask import Flask
from config import Config
from db import db


def create_minimal_app():
    """Create a minimal Flask app just for database access."""
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    return app


def print_section(title):
    """Print a formatted section header."""
    print(f"\n{'=' * 70}")
    print(f"  {title}")
    print(f"{'=' * 70}")


def print_report(report, prefix=''):
    """Pretty-print a validation report."""
    print(f"\n{prefix}Dataset: {report['dataset_name']}")
    print(f"{prefix}Feature matrix shape: {report['feature_matrix_shape']}")
    print(f"{prefix}Training samples: {report['n_training_samples']}")
    print(f"{prefix}Number of features: {report['n_features']}")

    print(f"\n{prefix}[FEATURES]")
    for i, name in enumerate(report['feature_names'], 1):
        dtype = report['feature_dtypes'].get(name, 'unknown')
        print(f"{prefix}  {i:2d}. {name:<30s}  ({dtype})")

    print(f"\n{prefix}[MISSING VALUES]")
    if report['missing_values']['total_nan'] == 0:
        print(f"{prefix}  ✅ Zero NaN values in entire feature matrix")
    else:
        print(f"{prefix}  ⚠️  Total NaN: {report['missing_values']['total_nan']}")
        for col, count in report['missing_values']['per_column'].items():
            print(f"{prefix}    {col}: {count} NaN")

    print(f"\n{prefix}[INFINITE VALUES]")
    if report['infinite_values'] == 0:
        print(f"{prefix}  ✅ Zero infinite values")
    else:
        print(f"{prefix}  ⚠️  {report['infinite_values']} infinite values detected")

    print(f"\n{prefix}[TARGET DISTRIBUTION]")
    stats = report['target_stats']
    print(f"{prefix}  Min:    {stats['min']}")
    print(f"{prefix}  Q25:    {stats['q25']}")
    print(f"{prefix}  Median: {stats['median']}")
    print(f"{prefix}  Mean:   {stats['mean']}")
    print(f"{prefix}  Q75:    {stats['q75']}")
    print(f"{prefix}  Max:    {stats['max']}")
    print(f"{prefix}  Std:    {stats['std']}")

    print(f"\n{prefix}[DERIVED RISK THRESHOLDS (from count quantiles)]")
    for level, threshold in report['risk_thresholds'].items():
        count = report['risk_category_counts'][level]
        print(f"{prefix}  {level:<10s}: {threshold:<20s}  ({count} samples)")


def main():
    app = create_minimal_app()

    with app.app_context():
        # Import here so db context is available
        from services.feature_engine import (
            build_physical_training_matrix,
            build_cyber_training_matrix,
            generate_validation_report,
        )

        # ─── PHYSICAL CRIME PIPELINE ─────────────────────────────────────
        print_section("PHYSICAL CRIME — Feature Engineering Pipeline")

        print("  Loading crimes from PostgreSQL...")
        phys_features, phys_target, phys_raw, phys_clean = build_physical_training_matrix()

        print(f"  ✅ Aggregation complete: {len(phys_raw)} area-month rows (raw)")
        print(f"  ✅ After cleaning: {len(phys_features)} training samples")

        phys_report = generate_validation_report(phys_features, phys_target, 'Physical Crime')
        print_report(phys_report)

        # ─── CYBERCRIME PIPELINE ──────────────────────────────────────────
        print_section("CYBERCRIME — Feature Engineering Pipeline")

        print("  Loading cybercrimes from PostgreSQL...")
        cyber_features, cyber_target, cyber_raw, cyber_clean = build_cyber_training_matrix()

        print(f"  ✅ Aggregation complete: {len(cyber_raw)} area-month rows (raw)")
        print(f"  ✅ After cleaning: {len(cyber_features)} training samples")

        cyber_report = generate_validation_report(cyber_features, cyber_target, 'Cybercrime')
        print_report(cyber_report)

        # ─── SAVE OUTPUTS ─────────────────────────────────────────────────
        output_dir = os.path.join(backend_dir, 'data', 'training')
        os.makedirs(output_dir, exist_ok=True)

        # Save physical training data
        phys_output = phys_clean.copy()
        phys_output.to_csv(os.path.join(output_dir, 'physical_training_data.csv'), index=False)
        print(f"\n  ✅ Saved: {os.path.join(output_dir, 'physical_training_data.csv')}")

        # Save cyber training data
        cyber_output = cyber_clean.copy()
        cyber_output.to_csv(os.path.join(output_dir, 'cyber_training_data.csv'), index=False)
        print(f"  ✅ Saved: {os.path.join(output_dir, 'cyber_training_data.csv')}")

        # Save combined report as JSON
        combined_report = {
            'physical': phys_report,
            'cyber': cyber_report,
        }
        # Convert tuples to lists for JSON serialization
        combined_report['physical']['feature_matrix_shape'] = list(
            combined_report['physical']['feature_matrix_shape']
        )
        combined_report['cyber']['feature_matrix_shape'] = list(
            combined_report['cyber']['feature_matrix_shape']
        )

        report_path = os.path.join(output_dir, 'phase6a_validation_report.json')
        with open(report_path, 'w') as f:
            json.dump(combined_report, f, indent=2, default=str)
        print(f"  ✅ Saved: {report_path}")

        # ─── SAMPLE DATA DISPLAY ──────────────────────────────────────────
        print_section("SAMPLE TRAINING DATA — Physical Crime (first 5 rows)")
        sample = phys_clean[['area', 'year', 'month', 'crime_count',
                             'target_crime_count']].head(10)
        print(sample.to_string(index=False))

        print_section("SAMPLE TRAINING DATA — Cybercrime (first 5 rows)")
        sample_cyber = cyber_clean[['area', 'year', 'month', 'cyber_count',
                                     'target_cyber_count']].head(10)
        print(sample_cyber.to_string(index=False))

        # ─── FINAL SUMMARY ────────────────────────────────────────────────
        print_section("PHASE 6A — FINAL SUMMARY")
        print(f"  Physical Crime Training Matrix: {phys_features.shape[0]} samples × {phys_features.shape[1]} features")
        print(f"  Cybercrime Training Matrix:     {cyber_features.shape[0]} samples × {cyber_features.shape[1]} features")
        print(f"  Total NaN (Physical):           {phys_report['missing_values']['total_nan']}")
        print(f"  Total NaN (Cyber):              {cyber_report['missing_values']['total_nan']}")
        print(f"  Physical Target Range:          {phys_report['target_stats']['min']} – {phys_report['target_stats']['max']}")
        print(f"  Cyber Target Range:             {cyber_report['target_stats']['min']} – {cyber_report['target_stats']['max']}")
        print(f"\n  All files saved to: {output_dir}")
        print(f"\n  ✅ Phase 6A COMPLETE. Ready for Phase 6B (model training).")
        print(f"  ⏸️  Awaiting user approval before proceeding.\n")


if __name__ == '__main__':
    main()
