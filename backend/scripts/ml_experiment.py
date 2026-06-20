import os
import sys
import pandas as pd
import psycopg2
import joblib
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
import warnings
warnings.filterwarnings('ignore')

# 1. Connect to Database & Load Data
DB_USER = os.environ.get('DB_USER', 'postgres')
DB_PASSWORD = os.environ.get('DB_PASSWORD', 'falguni')
DB_HOST = os.environ.get('DB_HOST', 'localhost')
DB_PORT = os.environ.get('DB_PORT', '5432')
DB_NAME = os.environ.get('DB_NAME', 'spcs_db')

try:
    conn = psycopg2.connect(host=DB_HOST, port=DB_PORT, dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD)
    # Read from the ML training view we created in Phase 3
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
print(" STANDALONE ML EXPERIMENT: RANDOM FOREST RISK PREDICTOR")
print("="*60)

print(f"\n[1] Dataset Loaded: {len(df)} records")
print("\n[2] Features Used:")
print("    - Categorical: area, crime_type")
print("    - Numerical/Boolean: hour, day_of_week, month, is_weekend, is_festival")

print("\n[3] Target Variable:")
print("    - 'severity_score' (1=Low, 2=Medium, 3=High, 4=Critical)")

print("\n[8] Class Distribution:")
print(df['severity_score'].value_counts().sort_index())

# Feature Engineering: One-Hot Encode 'area' and 'crime_type'
X = pd.get_dummies(df.drop('severity_score', axis=1), columns=['area', 'crime_type'])
y = df['severity_score']

# 4. Train/Test Split (80/20)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20, random_state=42, stratify=y)
print(f"\n[4] Data Split: {len(X_train)} train, {len(X_test)} test")

# 5. Train Random Forest (Tuned Hyperparameters to reduce overfitting)
print("\n[5] Training RandomForestClassifier with Tuned Hyperparameters...")
rf_model = RandomForestClassifier(
    n_estimators=200, 
    random_state=42, 
    max_depth=10, 
    min_samples_leaf=5,
    min_samples_split=10,
    class_weight='balanced'
)
rf_model.fit(X_train, y_train)

# Predictions
y_train_pred = rf_model.predict(X_train)
y_test_pred = rf_model.predict(X_test)

# 6. Evaluation Metrics (Weighted for multi-class)
accuracy = accuracy_score(y_test, y_test_pred)
precision = precision_score(y_test, y_test_pred, average='weighted')
recall = recall_score(y_test, y_test_pred, average='weighted')
f1 = f1_score(y_test, y_test_pred, average='weighted')
cm = confusion_matrix(y_test, y_test_pred)

print("\n[6] Evaluation Report (Test Set):")
print(f"    - Accuracy:  {accuracy:.4f} ({accuracy*100:.1f}%)")
print(f"    - Precision: {precision:.4f}")
print(f"    - Recall:    {recall:.4f}")
print(f"    - F1 Score:  {f1:.4f}")

print("\n    Confusion Matrix:")
print("                Predicted")
print("              1   2   3   4")
print("           -----------------")
for i, row in enumerate(cm):
    print(f"  Actual {i+1} | {row[0]:>3} {row[1]:>3} {row[2]:>3} {row[3]:>3}")

# 9. Overfitting Check
train_acc = accuracy_score(y_train, y_train_pred)
print("\n[9] Overfitting Check:")
print(f"    - Train Accuracy: {train_acc:.4f}")
print(f"    - Test Accuracy:  {accuracy:.4f}")
diff = train_acc - accuracy
if diff > 0.15:
    print("    -> ⚠️ WARNING: High overfitting detected.")
else:
    print("    -> ✅ Model generalizes well (no severe overfitting).")

# 7. Feature Importance
print("\n[7] Top 10 Feature Importances:")
importances = rf_model.feature_importances_
feature_names = X.columns
feat_imp = pd.DataFrame({'feature': feature_names, 'importance': importances})
feat_imp = feat_imp.sort_values('importance', ascending=False).head(10)
for _, row in feat_imp.iterrows():
    print(f"    - {row['feature']:<25}: {row['importance']:.4f}")

# 10. Save Model
model_dir = os.path.join(os.path.dirname(__file__), '..', 'ml_models')
os.makedirs(model_dir, exist_ok=True)
model_path = os.path.join(model_dir, 'rf_risk_model.pkl')
joblib.dump(rf_model, model_path)
print(f"\n[10] Model Saved successfully to:")
print(f"     {model_path}")

# 8. Accuracy by class
print("\n[8] Accuracy by Class:")
classes = [1, 2, 3, 4]
class_names = {1: 'Low', 2: 'Medium', 3: 'High', 4: 'Critical'}
for cls in classes:
    cls_mask = y_test == cls
    if cls_mask.sum() > 0:
        cls_acc = accuracy_score(y_test[cls_mask], y_test_pred[cls_mask])
        print(f"    - {class_names[cls]} (Class {cls}): {cls_acc:.4f} ({cls_acc*100:.1f}%)")

# 7. Top 10 Prediction Mistakes
print("\n[12] Top 10 Prediction Mistakes (Actual vs Predicted):")
mistakes = X_test[y_test != y_test_pred].copy()
mistakes['Actual Risk'] = y_test[y_test != y_test_pred]
mistakes['Predicted Risk'] = y_test_pred[y_test != y_test_pred]
print(f"     Index | Actual Risk | Predicted Risk | Key Features")
print(f"     ---------------------------------------------------")
count = 0
for idx, row in mistakes.iterrows():
    if count >= 10:
        break
    # Get active crime type
    active_crimes = [col.replace('crime_type_', '') for col in mistakes.columns if col.startswith('crime_type_') and row[col] == 1]
    crime_str = active_crimes[0] if active_crimes else 'Unknown'
    print(f"     {idx:<5} | {row['Actual Risk']:<11} | {row['Predicted Risk']:<14} | Hour: {row['hour']}, Month: {row['month']}, Crime: {crime_str}")
    count += 1

print("\nExperiment Complete.\n")
