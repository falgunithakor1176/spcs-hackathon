import os
import sys
import pandas as pd
import numpy as np
import psycopg2
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, mean_absolute_error, r2_score
import warnings
warnings.filterwarnings('ignore')

DB_USER = os.environ.get('DB_USER', 'postgres')
DB_PASSWORD = os.environ.get('DB_PASSWORD', 'falguni')
DB_HOST = os.environ.get('DB_HOST', 'localhost')
DB_PORT = os.environ.get('DB_PORT', '5432')
DB_NAME = os.environ.get('DB_NAME', 'spcs_db')

try:
    conn = psycopg2.connect(host=DB_HOST, port=DB_PORT, dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD)
    query = """
        SELECT area, timestamp
        FROM crimes
    """
    df_raw = pd.read_sql(query, conn)
    conn.close()
    
    # Process in pandas
    df_raw['dt'] = pd.to_datetime(df_raw['timestamp'], format='%d-%m-%Y %H:%M')
    df_raw['crime_date'] = df_raw['dt'].dt.date
    df_raw['month'] = df_raw['dt'].dt.month
    df_raw['day_of_week'] = df_raw['dt'].dt.dayofweek
    df_raw['is_weekend'] = df_raw['day_of_week'].isin([5, 6]).astype(int)
    # Simple mock for festival: let's just group by area and date
    df = df_raw.groupby(['area', 'crime_date', 'month', 'day_of_week', 'is_weekend']).size().reset_index(name='crime_count')

except Exception as e:
    print(f"Database error: {e}")
    sys.exit(1)

print("="*60)
print(" ALTERNATIVE ML EXPERIMENTS (AVOIDING LEAKAGE)")
print("="*60)
print(f"Dataset Grouped by Area & Date: {len(df)} records\n")

# Prepare base features
X_base = df[['area', 'month', 'day_of_week', 'is_weekend']]
X = pd.get_dummies(X_base, columns=['area'])

# ---------------------------------------------------------
# EXPERIMENT 1: Area Risk Classification
# ---------------------------------------------------------
print("-" * 60)
print(" EXPERIMENT 1: Area Risk Classification (Low/Medium/High)")
print("-" * 60)
# Target: 1 (Low: 1 crime), 2 (Medium: 2-3 crimes), 3 (High: 4+ crimes)
def classify_risk(count):
    if count <= 1: return 1
    elif count <= 3: return 2
    else: return 3

y_risk = df['crime_count'].apply(classify_risk)
print("Class Distribution:")
print(y_risk.value_counts().sort_index())

X_tr1, X_te1, y_tr1, y_te1 = train_test_split(X, y_risk, test_size=0.20, random_state=42, stratify=y_risk)
rf1 = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42, class_weight='balanced')
rf1.fit(X_tr1, y_tr1)
y_pr1 = rf1.predict(X_te1)

acc1 = accuracy_score(y_te1, y_pr1)
pr1 = precision_score(y_te1, y_pr1, average='weighted', zero_division=0)
rc1 = recall_score(y_te1, y_pr1, average='weighted', zero_division=0)
f1_1 = f1_score(y_te1, y_pr1, average='weighted', zero_division=0)

print(f"\nResults:")
print(f"Accuracy:  {acc1:.4f} ({acc1*100:.1f}%)")
print(f"Precision: {pr1:.4f}")
print(f"Recall:    {rc1:.4f}")
print(f"F1 Score:  {f1_1:.4f}")


# ---------------------------------------------------------
# EXPERIMENT 2: Crime Volume Forecasting
# ---------------------------------------------------------
print("\n" + "-" * 60)
print(" EXPERIMENT 2: Crime Volume Forecasting (Regression)")
print("-" * 60)
y_vol = df['crime_count']

X_tr2, X_te2, y_tr2, y_te2 = train_test_split(X, y_vol, test_size=0.20, random_state=42)
rf2 = RandomForestRegressor(n_estimators=100, max_depth=10, random_state=42)
rf2.fit(X_tr2, y_tr2)
y_pr2 = rf2.predict(X_te2)

mae = mean_absolute_error(y_te2, y_pr2)
r2 = r2_score(y_te2, y_pr2)

print(f"Target variable: Exact crime count per area per day.")
print(f"Average crimes per group: {y_vol.mean():.2f}")
print(f"\nResults:")
print(f"Mean Absolute Error (MAE): {mae:.4f} crimes")
print(f"R^2 Score: {r2:.4f} (1.0 is perfect prediction)")


# ---------------------------------------------------------
# EXPERIMENT 3: Hotspot Risk Prediction
# ---------------------------------------------------------
print("\n" + "-" * 60)
print(" EXPERIMENT 3: Hotspot Risk Prediction (Binary)")
print("-" * 60)
# Target: 1 (Hotspot: >= 5 crimes), 0 (Normal)
y_hot = (df['crime_count'] >= 5).astype(int)
print("Class Distribution:")
print(y_hot.value_counts())

X_tr3, X_te3, y_tr3, y_te3 = train_test_split(X, y_hot, test_size=0.20, random_state=42, stratify=y_hot)
rf3 = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42, class_weight='balanced')
rf3.fit(X_tr3, y_tr3)
y_pr3 = rf3.predict(X_te3)

acc3 = accuracy_score(y_te3, y_pr3)
pr3 = precision_score(y_te3, y_pr3, average='binary', zero_division=0)
rc3 = recall_score(y_te3, y_pr3, average='binary', zero_division=0)
f1_3 = f1_score(y_te3, y_pr3, average='binary', zero_division=0)

print(f"\nResults:")
print(f"Accuracy:  {acc3:.4f} ({acc3*100:.1f}%)")
print(f"Precision: {pr3:.4f}")
print(f"Recall:    {rc3:.4f}")
print(f"F1 Score:  {f1_3:.4f}")

print("\nDone.")
