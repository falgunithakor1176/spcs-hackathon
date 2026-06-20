"""
init_db.py â€” SPCS Phase 3 Database Initialization Script
=========================================================
This script:
1. Creates all tables from SQLAlchemy models
2. Imports all CSV data into PostgreSQL
3. Adds PostGIS geometry columns (POINT) for crimes & hotspots
4. Creates GiST spatial indexes for ML-ready queries
5. Creates ML training views (crime_training_view, hotspot_training_view, cybercrime_training_view)
6. Runs a validation report (row counts, nulls, duplicates)

Run once from the backend directory:
    python scripts/init_db.py
"""

import os
import sys
import csv
import ast

backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(backend_dir)

from dotenv import load_dotenv
load_dotenv(os.path.join(backend_dir, '.env'))

import psycopg2

DB_HOST = os.environ.get('DB_HOST', 'localhost')
DB_PORT = os.environ.get('DB_PORT', '5432')
DB_NAME = os.environ.get('DB_NAME', 'spcs_db')
DB_USER = os.environ.get('DB_USER', 'postgres')
DB_PASSWORD = os.environ.get('DB_PASSWORD', '')
SEED_DIR = os.path.join(backend_dir, 'data', 'seed')


def get_conn():
    return psycopg2.connect(
        host=DB_HOST, port=DB_PORT, dbname=DB_NAME,
        user=DB_USER, password=DB_PASSWORD
    )


# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# 1. Create Tables
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
CREATE_TABLES = """
DROP TABLE IF EXISTS patrol_routes CASCADE;
DROP TABLE IF EXISTS predictions CASCADE;
DROP TABLE IF EXISTS alerts CASCADE;
DROP TABLE IF EXISTS hotspots CASCADE;
DROP TABLE IF EXISTS patrol_units CASCADE;
DROP TABLE IF EXISTS cybercrimes CASCADE;
DROP TABLE IF EXISTS crimes CASCADE;

CREATE TABLE crimes (
    crime_id      VARCHAR(50) PRIMARY KEY,
    crime_type    VARCHAR(100),
    latitude      DOUBLE PRECISION,
    longitude     DOUBLE PRECISION,
    area          VARCHAR(100),
    zone          VARCHAR(50),
    timestamp     VARCHAR(50),
    severity      VARCHAR(50),
    status        VARCHAR(50),
    fir_number    VARCHAR(100),
    description   TEXT,
    hour          INTEGER,
    day_of_week   INTEGER,
    month         INTEGER,
    year          INTEGER,
    day           INTEGER,
    is_weekend    BOOLEAN,
    is_festival   BOOLEAN,
    festival_name VARCHAR(100)
);

CREATE TABLE cybercrimes (
    report_id        VARCHAR(50) PRIMARY KEY,
    fraud_type       VARCHAR(100),
    latitude         DOUBLE PRECISION,
    longitude        DOUBLE PRECISION,
    area             VARCHAR(100),
    zone             VARCHAR(50),
    amount_lost      DOUBLE PRECISION,
    timestamp        VARCHAR(50),
    status           VARCHAR(50),
    platform         VARCHAR(100),
    victim_age_group VARCHAR(50),
    hour             INTEGER,
    month            INTEGER,
    year             INTEGER,
    day_of_week      INTEGER,
    is_weekend       BOOLEAN
);

CREATE TABLE patrol_units (
    vehicle_id        VARCHAR(50) PRIMARY KEY,
    officer_id        VARCHAR(50),
    officer_name      VARCHAR(100),
    current_location  TEXT,
    area              VARCHAR(100),
    zone              VARCHAR(50),
    status            VARCHAR(50),
    vehicle_type      VARCHAR(50),
    shift_time        VARCHAR(50),
    incidents_handled INTEGER,
    last_update       VARCHAR(100)
);

CREATE TABLE hotspots (
    id           VARCHAR(50) PRIMARY KEY,
    name         VARCHAR(150),
    lat          DOUBLE PRECISION,
    lng          DOUBLE PRECISION,
    radius       INTEGER,
    risk         VARCHAR(50),
    score        INTEGER,
    crimes       INTEGER,
    primary_type VARCHAR(100),
    trend        VARCHAR(50),
    emerged      VARCHAR(50),
    zone         VARCHAR(50)
);

CREATE TABLE alerts (
    id           VARCHAR(50) PRIMARY KEY,
    type         VARCHAR(50),
    title        VARCHAR(200),
    message      TEXT,
    area         VARCHAR(100),
    timestamp    VARCHAR(100),
    acknowledged BOOLEAN,
    assigned_to  VARCHAR(50)
);

CREATE TABLE predictions (
    area             VARCHAR(100) PRIMARY KEY,
    risk_level       VARCHAR(50),
    score            INTEGER,
    predicted_crimes INTEGER,
    top_crime        VARCHAR(100),
    confidence       VARCHAR(50),
    deployment       VARCHAR(200),
    lat              DOUBLE PRECISION,
    lng              DOUBLE PRECISION
);

CREATE TABLE patrol_routes (
    id          VARCHAR(50) PRIMARY KEY,
    vehicle_id  VARCHAR(50),
    name        VARCHAR(150),
    color       VARCHAR(20),
    waypoints   TEXT,
    distance_km DOUBLE PRECISION,
    coverage    VARCHAR(20),
    eta_minutes INTEGER
);
"""


# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# 2. CSV Import helpers
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
def bool_val(v):
    return v.lower() in ('true', '1', 'yes') if isinstance(v, str) else bool(v)

def int_or_none(v):
    try: return int(float(v))
    except: return None

def float_or_none(v):
    try: return float(v)
    except: return None

def import_crimes(cur):
    path = os.path.join(SEED_DIR, 'crimes.csv')
    sql = """INSERT INTO crimes VALUES (
        %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s
    ) ON CONFLICT (crime_id) DO NOTHING"""
    count = 0
    with open(path, encoding='utf-8') as f:
        for row in csv.DictReader(f):
            cur.execute(sql, (
                row['crime_id'], row['crime_type'],
                float_or_none(row['latitude']), float_or_none(row['longitude']),
                row['area'], row['zone'], row['timestamp'], row['severity'],
                row['status'], row['fir_number'], row['description'],
                int_or_none(row['hour']), int_or_none(row['day_of_week']),
                int_or_none(row['month']), int_or_none(row['year']),
                int_or_none(row['day']), bool_val(row['is_weekend']),
                bool_val(row['is_festival']),
                row['festival_name'] if row['festival_name'] else None
            ))
            count += 1
    return count

def import_cybercrimes(cur):
    path = os.path.join(SEED_DIR, 'cybercrime.csv')
    sql = """INSERT INTO cybercrimes VALUES (
        %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s
    ) ON CONFLICT (report_id) DO NOTHING"""
    count = 0
    with open(path, encoding='utf-8') as f:
        for row in csv.DictReader(f):
            cur.execute(sql, (
                row['report_id'], row['fraud_type'],
                float_or_none(row['latitude']), float_or_none(row['longitude']),
                row['area'], row['zone'], float_or_none(row['amount_lost']),
                row['timestamp'], row['status'], row['platform'],
                row['victim_age_group'], int_or_none(row['hour']),
                int_or_none(row['month']), int_or_none(row['year']),
                int_or_none(row['day_of_week']), bool_val(row['is_weekend'])
            ))
            count += 1
    return count

def import_patrol_units(cur):
    path = os.path.join(SEED_DIR, 'patrol_units.csv')
    sql = """INSERT INTO patrol_units VALUES (
        %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s
    ) ON CONFLICT (vehicle_id) DO NOTHING"""
    count = 0
    with open(path, encoding='utf-8') as f:
        for row in csv.DictReader(f):
            cur.execute(sql, (
                row['vehicle_id'], row['officer_id'], row['officer_name'],
                row['current_location'], row['area'], row['zone'],
                row['status'], row['vehicle_type'], row['shift_time'],
                int_or_none(row['incidents_handled']), row['last_update']
            ))
            count += 1
    return count

def import_hotspots(cur):
    path = os.path.join(SEED_DIR, 'hotspots.csv')
    sql = """INSERT INTO hotspots VALUES (
        %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s
    ) ON CONFLICT (id) DO NOTHING"""
    count = 0
    with open(path, encoding='utf-8') as f:
        for row in csv.DictReader(f):
            cur.execute(sql, (
                row['id'], row['name'],
                float_or_none(row['lat']), float_or_none(row['lng']),
                int_or_none(row['radius']), row['risk'],
                int_or_none(row['score']), int_or_none(row['crimes']),
                row['primary_type'], row['trend'], row['emerged'], row['zone']
            ))
            count += 1
    return count

def import_alerts(cur):
    path = os.path.join(SEED_DIR, 'alerts.csv')
    sql = """INSERT INTO alerts VALUES (
        %s,%s,%s,%s,%s,%s,%s,%s
    ) ON CONFLICT (id) DO NOTHING"""
    count = 0
    with open(path, encoding='utf-8') as f:
        for row in csv.DictReader(f):
            cur.execute(sql, (
                row['id'], row['type'], row['title'], row['message'],
                row['area'], row['timestamp'],
                bool_val(row['acknowledged']),
                row['assigned_to'] if row.get('assigned_to') else None
            ))
            count += 1
    return count

def import_predictions(cur):
    path = os.path.join(SEED_DIR, 'predictions.csv')
    sql = """INSERT INTO predictions VALUES (
        %s,%s,%s,%s,%s,%s,%s,%s,%s
    ) ON CONFLICT (area) DO NOTHING"""
    count = 0
    with open(path, encoding='utf-8') as f:
        for row in csv.DictReader(f):
            cur.execute(sql, (
                row['area'], row['risk_level'],
                int_or_none(row['score']), int_or_none(row['predicted_crimes']),
                row['top_crime'], row['confidence'], row['deployment'],
                float_or_none(row['lat']), float_or_none(row['lng'])
            ))
            count += 1
    return count

def import_patrol_routes(cur):
    path = os.path.join(SEED_DIR, 'patrol_routes.csv')
    sql = """INSERT INTO patrol_routes VALUES (
        %s,%s,%s,%s,%s,%s,%s,%s
    ) ON CONFLICT (id) DO NOTHING"""
    count = 0
    with open(path, encoding='utf-8') as f:
        for row in csv.DictReader(f):
            cur.execute(sql, (
                row['id'], row['vehicle_id'], row['name'], row.get('color',''),
                row['waypoints'], float_or_none(row['distance_km']),
                row['coverage'], int_or_none(row['eta_minutes'])
            ))
            count += 1
    return count


# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# 3. PostGIS Geometry Columns & GiST Indexes
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
POSTGIS_SQL = """
-- Add geometry columns
ALTER TABLE crimes ADD COLUMN IF NOT EXISTS geom GEOMETRY(POINT, 4326);
ALTER TABLE cybercrimes ADD COLUMN IF NOT EXISTS geom GEOMETRY(POINT, 4326);
ALTER TABLE hotspots ADD COLUMN IF NOT EXISTS geom GEOMETRY(POINT, 4326);

-- Populate geometry from lat/lng
UPDATE crimes SET geom = ST_SetSRID(ST_MakePoint(longitude, latitude), 4326) WHERE longitude IS NOT NULL AND latitude IS NOT NULL;
UPDATE cybercrimes SET geom = ST_SetSRID(ST_MakePoint(longitude, latitude), 4326) WHERE longitude IS NOT NULL AND latitude IS NOT NULL;
UPDATE hotspots SET geom = ST_SetSRID(ST_MakePoint(lng, lat), 4326) WHERE lng IS NOT NULL AND lat IS NOT NULL;

-- GiST spatial indexes for fast geospatial queries
CREATE INDEX IF NOT EXISTS idx_crimes_geom ON crimes USING GIST(geom);
CREATE INDEX IF NOT EXISTS idx_cybercrimes_geom ON cybercrimes USING GIST(geom);
CREATE INDEX IF NOT EXISTS idx_hotspots_geom ON hotspots USING GIST(geom);

-- Additional B-tree indexes for ML and filtering
CREATE INDEX IF NOT EXISTS idx_crimes_area ON crimes(area);
CREATE INDEX IF NOT EXISTS idx_crimes_severity ON crimes(severity);
CREATE INDEX IF NOT EXISTS idx_crimes_year_month ON crimes(year, month);
CREATE INDEX IF NOT EXISTS idx_crimes_type ON crimes(crime_type);
CREATE INDEX IF NOT EXISTS idx_cyber_year ON cybercrimes(year);
CREATE INDEX IF NOT EXISTS idx_cyber_type ON cybercrimes(fraud_type);
"""


# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# 4. ML Training Views
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
ML_VIEWS_SQL = """
-- crime_training_view: For DBSCAN clustering and Random Forest feature engineering
CREATE OR REPLACE VIEW crime_training_view AS
SELECT
    crime_id,
    crime_type,
    latitude,
    longitude,
    area,
    zone,
    severity,
    hour,
    day_of_week,
    month,
    year,
    is_weekend,
    is_festival,
    festival_name,
    CASE severity
        WHEN 'Critical' THEN 4
        WHEN 'High'     THEN 3
        WHEN 'Medium'   THEN 2
        WHEN 'Low'      THEN 1
        ELSE 0
    END AS severity_score,
    geom
FROM crimes;

-- hotspot_training_view: For spatial risk modeling
CREATE OR REPLACE VIEW hotspot_training_view AS
SELECT
    h.id,
    h.name,
    h.lat,
    h.lng,
    h.radius,
    h.risk,
    h.score,
    h.crimes AS crime_count,
    h.primary_type,
    h.zone,
    h.geom,
    COUNT(c.crime_id) AS nearby_crimes_1km
FROM hotspots h
LEFT JOIN crimes c
    ON ST_DWithin(h.geom::geography, c.geom::geography, 1000)
GROUP BY h.id, h.name, h.lat, h.lng, h.radius,
         h.risk, h.score, h.crimes, h.primary_type,
         h.zone, h.geom;

-- cybercrime_training_view: For cybercrime pattern analysis
CREATE OR REPLACE VIEW cybercrime_training_view AS
SELECT
    report_id,
    fraud_type,
    latitude,
    longitude,
    area,
    zone,
    amount_lost,
    platform,
    victim_age_group,
    hour,
    day_of_week,
    month,
    year,
    is_weekend,
    geom,
    CASE
        WHEN amount_lost > 100000 THEN 'High'
        WHEN amount_lost > 10000  THEN 'Medium'
        ELSE 'Low'
    END AS financial_impact
FROM cybercrimes;
"""


# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# 5. Validation Report
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
TABLES = ['crimes', 'cybercrimes', 'patrol_units', 'hotspots', 'alerts', 'predictions', 'patrol_routes']

def run_validation(cur):
    print("\n" + "="*60)
    print("  DATABASE VALIDATION REPORT")
    print("="*60)

    # Row counts
    print("\n[1] ROW COUNTS")
    for t in TABLES:
        cur.execute(f"SELECT COUNT(*) FROM {t}")
        print(f"    {t:<20}: {cur.fetchone()[0]:>6} rows")

    # Duplicate check
    print("\n[2] DUPLICATE RECORDS")
    dup_queries = {
        'crimes':       ("crime_id",   "SELECT crime_id, COUNT(*) FROM crimes GROUP BY crime_id HAVING COUNT(*) > 1"),
        'cybercrimes':  ("report_id",  "SELECT report_id, COUNT(*) FROM cybercrimes GROUP BY report_id HAVING COUNT(*) > 1"),
        'patrol_units': ("vehicle_id", "SELECT vehicle_id, COUNT(*) FROM patrol_units GROUP BY vehicle_id HAVING COUNT(*) > 1"),
        'hotspots':     ("id",         "SELECT id, COUNT(*) FROM hotspots GROUP BY id HAVING COUNT(*) > 1"),
        'alerts':       ("id",         "SELECT id, COUNT(*) FROM alerts GROUP BY id HAVING COUNT(*) > 1"),
        'predictions':  ("area",       "SELECT area, COUNT(*) FROM predictions GROUP BY area HAVING COUNT(*) > 1"),
    }
    for table, (pk, q) in dup_queries.items():
        cur.execute(q)
        dups = cur.fetchall()
        status = f"âœ… 0 duplicates" if not dups else f"âŒ {len(dups)} duplicate(s) found"
        print(f"    {table:<20}: {status}")

    # Null checks on key columns
    print("\n[3] NULL VALUE REPORT")
    null_queries = [
        ('crimes',       'latitude', "SELECT COUNT(*) FROM crimes WHERE latitude IS NULL"),
        ('crimes',       'longitude',"SELECT COUNT(*) FROM crimes WHERE longitude IS NULL"),
        ('crimes',       'severity', "SELECT COUNT(*) FROM crimes WHERE severity IS NULL"),
        ('cybercrimes',  'amount_lost',"SELECT COUNT(*) FROM cybercrimes WHERE amount_lost IS NULL"),
        ('hotspots',     'score',    "SELECT COUNT(*) FROM hotspots WHERE score IS NULL"),
    ]
    for table, col, q in null_queries:
        cur.execute(q)
        nulls = cur.fetchone()[0]
        status = f"âœ… 0 nulls" if nulls == 0 else f"âš ï¸  {nulls} null(s)"
        print(f"    {table}.{col:<25}: {status}")

    # Geometry check
    print("\n[4] POSTGIS GEOMETRY VALIDATION")
    geo_tables = [('crimes','geom'), ('cybercrimes','geom'), ('hotspots','geom')]
    for table, col in geo_tables:
        try:
            cur.execute(f"SELECT COUNT(*) FROM {table} WHERE {col} IS NOT NULL")
            populated = cur.fetchone()[0]
            cur.execute(f"SELECT COUNT(*) FROM {table}")
            total = cur.fetchone()[0]
            print(f"    {table:<20}: {populated}/{total} geometry points populated")
        except Exception as e:
            print(f"    {table:<20}: âš ï¸  {e}")

    # Index verification
    print("\n[5] SPATIAL INDEX VERIFICATION")
    cur.execute("""
        SELECT tablename, indexname
        FROM pg_indexes
        WHERE indexname LIKE 'idx_%geom%'
        ORDER BY tablename
    """)
    indexes = cur.fetchall()
    if indexes:
        for table, idx in indexes:
            print(f"    âœ… GiST index: {idx} on {table}")
    else:
        print("    âš ï¸  No spatial indexes found")

    # ML Views
    print("\n[6] ML TRAINING VIEWS")
    for view in ['crime_training_view', 'hotspot_training_view', 'cybercrime_training_view']:
        cur.execute(f"SELECT COUNT(*) FROM {view}")
        rows = cur.fetchone()[0]
        print(f"    âœ… {view}: {rows} rows ready")

    print("\n" + "="*60)
    print("  VALIDATION COMPLETE")
    print("="*60 + "\n")


# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# Main
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
def main():
    print("Connecting to PostgreSQL...")
    conn = get_conn()
    conn.autocommit = False
    cur = conn.cursor()

    print("Creating tables...")
    cur.execute(CREATE_TABLES)
    conn.commit()
    print("âœ… Tables created")

    print("\nImporting CSV data...")
    importers = [
        ("crimes",         import_crimes),
        ("cybercrimes",    import_cybercrimes),
        ("patrol_units",   import_patrol_units),
        ("hotspots",       import_hotspots),
        ("alerts",         import_alerts),
        ("predictions",    import_predictions),
        ("patrol_routes",  import_patrol_routes),
    ]
    for name, fn in importers:
        count = fn(cur)
        print(f"  âœ… {name}: {count} records imported")
    conn.commit()

    # Check if PostGIS is available before adding geometry
    cur.execute("SELECT COUNT(*) FROM pg_extension WHERE extname='postgis'")
    has_postgis = cur.fetchone()[0] > 0

    if has_postgis:
        print("\nAdding PostGIS geometry columns and GiST indexes...")
        cur.execute(POSTGIS_SQL)
        conn.commit()
        print("âœ… Geometry columns and spatial indexes created")

        print("\nCreating ML training views...")
        cur.execute(ML_VIEWS_SQL)
        conn.commit()
        print("âœ… ML views created")
    else:
        print("\nâš ï¸  PostGIS not found â€” skipping geometry columns and ML views.")
        print("   Install PostGIS via Stack Builder, then re-run this script.")

    run_validation(cur)
    cur.close()
    conn.close()

if __name__ == '__main__':
    main()
