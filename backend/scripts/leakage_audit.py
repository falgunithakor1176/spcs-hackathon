import os
import sys
import pandas as pd
import numpy as np
import psycopg2
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
import warnings
warnings.filterwarnings('ignore')

# 1. Connect & Load Data
DB_USER = os.environ.get('DB_USER', 'postgres')
DB_PASSWORD = os.environ.get('DB_PASSWORD', 'falguni')
DB_HOST = os.environ.get('DB_HOST', 'localhost')
DB_PORT = os.environ.get('DB_PORT', '5432')
DB_NAME = os.environ.get('DB_NAME', 'spcs_db')

try:
    conn = psycopg2.connect(host=DB_HOST, port=DB_PORT, dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD)
    query = """
        SELECT area, crime_type, hour, day_of_week, month, is_weekend, is_festival, severity_score
        FROM crime_training_view
    """
    df = pd.read_sql(query, conn)
    conn.close()
except Exception as e:
    print(f"Database error: {e}")
    sys.exit(1)

print("="*60)
print(" DATA LEAKAGE & FEATURE CONTRIBUTION AUDIT")
print("="*60)

y = df['severity_score']

# ---------------------------------------------------------
# MODEL A: Baseline (ONLY crime_type)
# ---------------------------------------------------------
X_base = pd.get_dummies(df[['crime_type']], columns=['crime_type'])
X_train_b, X_test_b, y_train_b, y_test_b = train_test_split(X_base, y, test_size=0.20, random_state=42, stratify=y)

rf_base = RandomForestClassifier(n_estimators=100, random_state=42, max_depth=10, class_weight='balanced')
rf_base.fit(X_train_b, y_train_b)
acc_base = accuracy_score(y_test_b, rf_base.predict(X_test_b))

print("\n[1] BASELINE MODEL (Features: Only crime_type)")
print(f"    - Test Accuracy: {acc_base:.4f} ({acc_base*100:.1f}%)")

# ---------------------------------------------------------
# MODEL B: Full Model (All features)
# ---------------------------------------------------------
X_full = pd.get_dummies(df.drop('severity_score', axis=1), columns=['area', 'crime_type'])
X_train_f, X_test_f, y_train_f, y_test_f = train_test_split(X_full, y, test_size=0.20, random_state=42, stratify=y)

rf_full = RandomForestClassifier(n_estimators=100, random_state=42, max_depth=10, min_samples_leaf=5, class_weight='balanced')
rf_full.fit(X_train_f, y_train_f)
acc_full = accuracy_score(y_test_f, rf_full.predict(X_test_f))

print("\n[2] FULL MODEL (Features: crime_type, area, temporal variables)")
print(f"    - Test Accuracy: {acc_full:.4f} ({acc_full*100:.1f}%)")

print("\n[3] COMPARISON")
improvement = acc_full - acc_base
print(f"    - Absolute Improvement from adding Spatial/Temporal data: +{improvement*100:.2f}%")

# ---------------------------------------------------------
# 4. Feature Contribution Analysis
# ---------------------------------------------------------
importances = rf_full.feature_importances_
feature_names = X_full.columns

contributions = {
    'crime_type': 0.0,
    'area': 0.0,
    'hour': 0.0,
    'month': 0.0,
    'day_of_week': 0.0,
    'festival_flags': 0.0
}

for name, imp in zip(feature_names, importances):
    if name.startswith('crime_type_'):
        contributions['crime_type'] += imp
    elif name.startswith('area_'):
        contributions['area'] += imp
    elif name == 'hour':
        contributions['hour'] += imp
    elif name == 'month':
        contributions['month'] += imp
    elif name == 'day_of_week':
        contributions['day_of_week'] += imp
    elif name in ['is_weekend', 'is_festival']:
        contributions['festival_flags'] += imp

print("\n[4] AGGREGATE PREDICTIVE POWER BY CATEGORY (Full Model):")
sorted_contributions = sorted(contributions.items(), key=lambda item: item[1], reverse=True)
for cat, imp in sorted_contributions:
    print(f"    - {cat:<15}: {imp*100:.1f}%")

print("\nAudit Complete.\n")
