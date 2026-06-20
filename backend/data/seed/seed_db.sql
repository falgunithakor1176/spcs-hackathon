-- ==========================================================
-- SPCS PostgreSQL Database Seed Script
-- Phase 3 Target Schema and COPY Scripts
-- ==========================================================

-- 1. Create Tables
CREATE TABLE IF NOT EXISTS crimes (
    crime_id VARCHAR(50) PRIMARY KEY,
    crime_type VARCHAR(100),
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    area VARCHAR(100),
    zone VARCHAR(50),
    timestamp TIMESTAMP,
    severity VARCHAR(50),
    status VARCHAR(50),
    fir_number VARCHAR(100),
    description TEXT,
    hour INTEGER,
    day_of_week INTEGER,
    month INTEGER,
    year INTEGER,
    day INTEGER,
    is_weekend BOOLEAN,
    is_festival BOOLEAN,
    festival_name VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS cybercrimes (
    report_id VARCHAR(50) PRIMARY KEY,
    fraud_type VARCHAR(100),
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    area VARCHAR(100),
    zone VARCHAR(50),
    amount_lost DOUBLE PRECISION,
    timestamp TIMESTAMP,
    status VARCHAR(50),
    platform VARCHAR(100),
    victim_age_group VARCHAR(50),
    hour INTEGER,
    month INTEGER,
    year INTEGER,
    day_of_week INTEGER,
    is_weekend BOOLEAN
);

CREATE TABLE IF NOT EXISTS patrol_units (
    vehicle_id VARCHAR(50) PRIMARY KEY,
    officer_id VARCHAR(50),
    officer_name VARCHAR(100),
    current_location VARCHAR(100),
    area VARCHAR(100),
    zone VARCHAR(50),
    status VARCHAR(50),
    vehicle_type VARCHAR(50),
    shift_time VARCHAR(50),
    incidents_handled INTEGER,
    last_update TIMESTAMP
);

CREATE TABLE IF NOT EXISTS hotspots (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(150),
    lat DOUBLE PRECISION,
    lng DOUBLE PRECISION,
    radius INTEGER,
    risk VARCHAR(50),
    score INTEGER,
    crimes INTEGER,
    primary_type VARCHAR(100),
    trend VARCHAR(50),
    emerged VARCHAR(50),
    zone VARCHAR(50)
);

CREATE TABLE IF NOT EXISTS alerts (
    id VARCHAR(50) PRIMARY KEY,
    type VARCHAR(50),
    title VARCHAR(200),
    message TEXT,
    area VARCHAR(100),
    timestamp TIMESTAMP,
    acknowledged BOOLEAN,
    assigned_to VARCHAR(50)
);

CREATE TABLE IF NOT EXISTS predictions (
    area VARCHAR(100) PRIMARY KEY,
    risk_level VARCHAR(50),
    score INTEGER,
    predicted_crimes INTEGER,
    top_crime VARCHAR(100),
    confidence VARCHAR(50),
    deployment VARCHAR(100),
    lat DOUBLE PRECISION,
    lng DOUBLE PRECISION
);

CREATE TABLE IF NOT EXISTS patrol_routes (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(150),
    unit VARCHAR(50),
    status VARCHAR(50),
    eta VARCHAR(50),
    coverage VARCHAR(50),
    waypoints TEXT -- JSON string
);

-- ==========================================================
-- 2. COPY Data from CSV
-- NOTE: Replace '/absolute/path/to/backend/data/seed/' with 
-- the actual absolute path to your CSV files when running.
-- ==========================================================

\copy crimes FROM '/absolute/path/to/backend/data/seed/crimes.csv' DELIMITER ',' CSV HEADER;
\copy cybercrimes FROM '/absolute/path/to/backend/data/seed/cybercrime.csv' DELIMITER ',' CSV HEADER;
\copy patrol_units FROM '/absolute/path/to/backend/data/seed/patrol_units.csv' DELIMITER ',' CSV HEADER;
\copy hotspots FROM '/absolute/path/to/backend/data/seed/hotspots.csv' DELIMITER ',' CSV HEADER;
\copy alerts FROM '/absolute/path/to/backend/data/seed/alerts.csv' DELIMITER ',' CSV HEADER;
\copy predictions FROM '/absolute/path/to/backend/data/seed/predictions.csv' DELIMITER ',' CSV HEADER;
\copy patrol_routes FROM '/absolute/path/to/backend/data/seed/patrol_routes.csv' DELIMITER ',' CSV HEADER;

-- 3. Post-Import: Add PostGIS spatial columns (Phase 3 Prep)
-- SELECT AddGeometryColumn('crimes', 'geom', 4326, 'POINT', 2);
-- UPDATE crimes SET geom = ST_SetSRID(ST_MakePoint(longitude, latitude), 4326);
