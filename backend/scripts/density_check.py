import os
import sys
import pandas as pd
import psycopg2

# Connect to DB
DB_USER = os.environ.get('DB_USER', 'postgres')
DB_PASSWORD = os.environ.get('DB_PASSWORD', 'falguni')
DB_HOST = os.environ.get('DB_HOST', 'localhost')
DB_PORT = os.environ.get('DB_PORT', '5432')
DB_NAME = os.environ.get('DB_NAME', 'spcs_db')

try:
    conn = psycopg2.connect(host=DB_HOST, port=DB_PORT, dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD)
    query = "SELECT TO_TIMESTAMP(timestamp, 'DD-MM-YYYY HH24:MI') as dt FROM crimes"
    df = pd.read_sql(query, conn)
    conn.close()
except Exception as e:
    print(f"Database error: {e}")
    sys.exit(1)

# Ensure datetime
df['dt'] = pd.to_datetime(df['dt'])
df = df.dropna(subset=['dt'])

print("="*50)
print(" CRIME DENSITY ANALYSIS")
print("="*50)

# 1. Crimes in specific months of 2025
months_to_check = {
    1: "January 2025",
    3: "March 2025",
    6: "June 2025",
    9: "September 2025",
    11: "November 2025"
}

print("\n[1] Specific Month Counts (2025):")
df_2025 = df[df['dt'].dt.year == 2025]
for m_num, m_name in months_to_check.items():
    count = len(df_2025[df_2025['dt'].dt.month == m_num])
    print(f"    - {m_name}: {count} crimes")

# 2. Find the 30-day period with highest density
print("\n[2] Highest 30-Day Density Period:")
# Sort by date
df_sorted = df.sort_values('dt').reset_index(drop=True)
# Set index to datetime for rolling window
df_indexed = df_sorted.set_index('dt')
# Calculate rolling 30-day count
rolling_30d = df_indexed.assign(count=1).rolling('30D').sum()

# Find max
max_period_end = rolling_30d['count'].idxmax()
max_crimes = rolling_30d['count'].max()

# The start of this 30-day window
max_period_start = max_period_end - pd.Timedelta(days=30)

print(f"    - Peak Window Start: {max_period_start.strftime('%Y-%m-%d')}")
print(f"    - Peak Window End:   {max_period_end.strftime('%Y-%m-%d')}")
print(f"    - Total Crimes in this 30-day window: {int(max_crimes)}")

print("\n[3] DBSCAN Sample Size Estimate:")
print(f"    If we hardcode DBSCAN to cluster data between '{max_period_start.strftime('%Y-%m-%d')}' and '{max_period_end.strftime('%Y-%m-%d')}',")
print(f"    it will process exactly {int(max_crimes)} records.")
print("    (For comparison, a healthy sample size for DBSCAN at 250m radius is typically 150-400 points).")

print("\nDone.")
