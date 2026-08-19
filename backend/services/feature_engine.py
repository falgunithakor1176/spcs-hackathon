"""
feature_engine.py — Phase 6A: Feature Engineering & Area-Month Aggregation Pipeline
====================================================================================

Purpose:
    Transforms raw crime/cybercrime records from PostgreSQL into a structured
    area-month feature matrix suitable for training Engine 2 (Random Forest).

Scope:
    - Feature engineering ONLY (no model training)
    - Physical crime features + Cybercrime features
    - Lag features, rolling averages, cyclical encoding, composition ratios

Dependencies:
    - pandas, numpy (already in venv)
    - SQLAlchemy (already in venv via Flask-SQLAlchemy)

Tables Read:
    - crimes      (10,000 rows)
    - cybercrimes (1,200 rows)

Tables Written:
    - NONE (Phase 6A is read-only; output is returned as DataFrames)

IMPORTANT:
    - Does NOT modify any existing table or data
    - Does NOT train any model
    - Does NOT touch Engine 1 (DBSCAN)
"""

import numpy as np
import pandas as pd
from db import db


# ─── CONSTANTS ────────────────────────────────────────────────────────────────

# Area base weights (from mock_service.py AREAS definition)
AREA_BASE_WEIGHTS = {
    'Naroda': 9, 'Bapunagar': 9, 'Maninagar': 8, 'Asarwa': 8,
    'Dariapur': 8, 'Gomtipur': 7, 'Isanpur': 7, 'Nikol': 7,
    'Vastral': 6, 'Ranip': 6, 'Narol': 5, 'Vatva': 5,
    'Shahibaug': 5, 'Chandkheda': 5, 'Paldi': 5,
    'Ellis Bridge': 4, 'Navrangpura': 4,
    'Ambavadi': 3, 'Vastrapur': 3, 'Satellite': 3,
    'Gota': 3, 'Vejalpur': 3, 'Sarkhej': 3,
    'Thaltej': 2, 'Prahlad Nagar': 2, 'Bodakdev': 2, 'Bopal': 2,
}

AREA_ZONES = {
    'Naroda': 'East', 'Bapunagar': 'East', 'Asarwa': 'East',
    'Gomtipur': 'East', 'Nikol': 'East', 'Vastral': 'East',
    'Maninagar': 'South', 'Isanpur': 'South', 'Narol': 'South',
    'Vatva': 'South', 'Paldi': 'South', 'Vejalpur': 'South', 'Sarkhej': 'South',
    'Dariapur': 'Central', 'Ellis Bridge': 'Central', 'Navrangpura': 'Central',
    'Ranip': 'North', 'Shahibaug': 'North', 'Chandkheda': 'North', 'Gota': 'North',
    'Ambavadi': 'West', 'Vastrapur': 'West', 'Satellite': 'West',
    'Thaltej': 'West', 'Prahlad Nagar': 'West', 'Bodakdev': 'West', 'Bopal': 'West',
}

# Severity numeric mapping
SEVERITY_MAP = {'Critical': 4, 'High': 3, 'Medium': 2, 'Low': 1}

# Violent crime types
VIOLENT_CRIMES = {'Robbery', 'Assault', 'Murder', 'Kidnapping', 'Arms Act Violation'}

# Property crime types
PROPERTY_CRIMES = {'Theft', 'Burglary', 'Vehicle Theft', 'Mobile Theft', 'Chain Snatching'}

# Festival months (months that contain at least one festival day)
FESTIVAL_MONTHS = {
    (2023, 1), (2023, 3), (2023, 10), (2023, 11), (2023, 12),
    (2024, 1), (2024, 3), (2024, 10), (2024, 11), (2024, 12),
    (2025, 1), (2025, 3), (2025, 9), (2025, 10),
}


# ─── DATA LOADING ─────────────────────────────────────────────────────────────

def load_crimes_df():
    """Load all crimes from PostgreSQL into a pandas DataFrame."""
    query = db.text("""
        SELECT crime_id, crime_type, latitude, longitude, area, zone,
               severity, hour, day_of_week, month, year, day,
               is_weekend, is_festival
        FROM crimes
        ORDER BY year, month, day, hour
    """)
    result = db.session.execute(query)
    rows = result.fetchall()
    columns = result.keys()
    df = pd.DataFrame(rows, columns=columns)
    return df


def load_cybercrimes_df():
    """Load all cybercrimes from PostgreSQL into a pandas DataFrame."""
    query = db.text("""
        SELECT report_id, fraud_type, latitude, longitude, area, zone,
               amount_lost, platform, victim_age_group,
               hour, month, year, day_of_week, is_weekend
        FROM cybercrimes
        ORDER BY year, month
    """)
    result = db.session.execute(query)
    rows = result.fetchall()
    columns = result.keys()
    df = pd.DataFrame(rows, columns=columns)
    return df


# ─── PHYSICAL CRIME AGGREGATION ──────────────────────────────────────────────

def aggregate_physical_features(crimes_df):
    """
    Aggregate raw crime records into area-month level features.

    Input:  DataFrame with individual crime records (10,000 rows)
    Output: DataFrame with one row per (area, year, month) combination

    Returns features suitable for predicting next-month crime count.
    """
    # Group by area + year + month
    grouped = crimes_df.groupby(['area', 'year', 'month'])

    # --- Base count (this becomes our target for regression) ---
    agg = grouped.agg(
        crime_count=('crime_id', 'count'),
        avg_severity=('severity', lambda x: np.mean([SEVERITY_MAP.get(s, 1) for s in x])),
        pct_critical=('severity', lambda x: np.mean([1 if s == 'Critical' else 0 for s in x])),
        pct_high=('severity', lambda x: np.mean([1 if s == 'High' else 0 for s in x])),
        pct_night=('hour', lambda x: np.mean([1 if h >= 22 or h <= 4 else 0 for h in x])),
        pct_weekend=('is_weekend', 'mean'),
        pct_festival=('is_festival', 'mean'),
        pct_violent=('crime_type', lambda x: np.mean([1 if c in VIOLENT_CRIMES else 0 for c in x])),
        pct_property=('crime_type', lambda x: np.mean([1 if c in PROPERTY_CRIMES else 0 for c in x])),
        n_crime_types=('crime_type', 'nunique'),
        avg_hour=('hour', 'mean'),
    ).reset_index()

    return agg


def add_temporal_features(df):
    """
    Add cyclical month encoding, quarter, and festival month flag.
    Operates in-place on an area-month DataFrame.
    """
    # Cyclical month encoding
    df['month_sin'] = np.sin(2 * np.pi * df['month'] / 12)
    df['month_cos'] = np.cos(2 * np.pi * df['month'] / 12)

    # Quarter
    df['quarter'] = ((df['month'] - 1) // 3) + 1

    # Festival month flag
    df['is_festival_month'] = df.apply(
        lambda row: 1 if (int(row['year']), int(row['month'])) in FESTIVAL_MONTHS else 0,
        axis=1
    )

    return df


def add_area_profile_features(df):
    """
    Add static area-level features: base weight and zone encoding.
    """
    df['area_base_weight'] = df['area'].map(AREA_BASE_WEIGHTS).fillna(5)

    # One-hot encode zone
    zone_series = df['area'].map(AREA_ZONES).fillna('Unknown')
    zone_dummies = pd.get_dummies(zone_series, prefix='zone', dtype=int)
    df = pd.concat([df, zone_dummies], axis=1)

    return df


def add_lag_features(df, target_col='crime_count'):
    """
    Add lag features per area: crime_count at T-1, T-2, T-3, T-12.

    The DataFrame must be sorted by (area, year, month) before calling this.
    Lag values for months with no prior data will be NaN (handled later).
    """
    # Create a sortable time index: year*12 + month
    df = df.sort_values(['area', 'year', 'month']).copy()
    df['time_idx'] = df['year'] * 12 + df['month']

    lag_dfs = []

    for area, group in df.groupby('area'):
        group = group.sort_values('time_idx').copy()

        # Lag features
        group[f'{target_col}_lag_1'] = group[target_col].shift(1)
        group[f'{target_col}_lag_2'] = group[target_col].shift(2)
        group[f'{target_col}_lag_3'] = group[target_col].shift(3)
        group[f'{target_col}_lag_12'] = group[target_col].shift(12)

        # Rolling averages
        group[f'rolling_avg_3m'] = group[target_col].shift(1).rolling(window=3, min_periods=1).mean()
        group[f'rolling_avg_6m'] = group[target_col].shift(1).rolling(window=6, min_periods=1).mean()
        group[f'rolling_std_3m'] = group[target_col].shift(1).rolling(window=3, min_periods=1).std().fillna(0)

        # Trend features
        group['mom_change'] = group[target_col].pct_change(periods=1)
        group['yoy_change'] = group[target_col].pct_change(periods=12)

        lag_dfs.append(group)

    result = pd.concat(lag_dfs, ignore_index=True)

    # Drop the temporary time index
    result.drop(columns=['time_idx'], inplace=True)

    return result


# ─── CYBERCRIME AGGREGATION ──────────────────────────────────────────────────

def aggregate_cyber_features(cyber_df):
    """
    Aggregate raw cybercrime records into area-month level features.

    Input:  DataFrame with individual cybercrime records (1,200 rows)
    Output: DataFrame with one row per (area, year, month) combination
    """
    grouped = cyber_df.groupby(['area', 'year', 'month'])

    agg = grouped.agg(
        cyber_count=('report_id', 'count'),
        avg_amount_lost=('amount_lost', 'mean'),
        max_amount_lost=('amount_lost', 'max'),
        total_amount_lost=('amount_lost', 'sum'),
        pct_upi_fraud=('fraud_type', lambda x: np.mean([1 if f == 'UPI Fraud' else 0 for f in x])),
        pct_high_value=('amount_lost', lambda x: np.mean([1 if a > 100000 else 0 for a in x])),
        platform_diversity=('platform', 'nunique'),
        pct_elderly=('victim_age_group', lambda x: np.mean([1 if g == '60+' else 0 for g in x])),
        pct_weekend_cyber=('is_weekend', 'mean'),
        n_fraud_types=('fraud_type', 'nunique'),
    ).reset_index()

    return agg


def add_cyber_lag_features(df, target_col='cyber_count'):
    """
    Add lag features for cybercrime data per area.
    """
    df = df.sort_values(['area', 'year', 'month']).copy()
    df['time_idx'] = df['year'] * 12 + df['month']

    lag_dfs = []

    for area, group in df.groupby('area'):
        group = group.sort_values('time_idx').copy()

        group[f'{target_col}_lag_1'] = group[target_col].shift(1)
        group[f'{target_col}_lag_2'] = group[target_col].shift(2)
        group[f'{target_col}_lag_3'] = group[target_col].shift(3)

        group['cyber_rolling_avg_3m'] = group[target_col].shift(1).rolling(window=3, min_periods=1).mean()
        group['cyber_mom_change'] = group[target_col].pct_change(periods=1)

        # Amount trend
        group['amount_lag_1'] = group['total_amount_lost'].shift(1)

        lag_dfs.append(group)

    result = pd.concat(lag_dfs, ignore_index=True)
    result.drop(columns=['time_idx'], inplace=True)

    return result


# ─── FULL PIPELINE ────────────────────────────────────────────────────────────

def build_physical_training_matrix():
    """
    Full pipeline: Load → Aggregate → Features → Lags → Clean

    Returns:
        features_df: DataFrame with all features (X)
        target_series: Series with the target variable (y = next month's crime count)
        raw_df: The aggregated df before target shift (for inspection)
    """
    # Step 1: Load raw data
    crimes_df = load_crimes_df()

    # Step 2: Aggregate to area-month
    agg_df = aggregate_physical_features(crimes_df)

    # Step 3: Add temporal features
    agg_df = add_temporal_features(agg_df)

    # Step 4: Add area profile features
    agg_df = add_area_profile_features(agg_df)

    # Step 5: Add lag features
    agg_df = add_lag_features(agg_df, target_col='crime_count')

    # Step 6: Create TARGET — next month's crime count
    # The target for row (area, year, month) is the crime_count at (area, year, month+1)
    agg_df = agg_df.sort_values(['area', 'year', 'month']).copy()
    target_dfs = []
    for area, group in agg_df.groupby('area'):
        group = group.sort_values(['year', 'month']).copy()
        group['target_crime_count'] = group['crime_count'].shift(-1)
        target_dfs.append(group)
    agg_df = pd.concat(target_dfs, ignore_index=True)

    # Step 7: Drop rows where target is NaN (last month of each area has no "next month")
    raw_df = agg_df.copy()
    clean_df = agg_df.dropna(subset=['target_crime_count']).copy()

    # Step 8: Handle remaining NaN in lag features (first few months per area)
    # Strategy: fill with area mean, then global mean, then 0
    feature_cols = [c for c in clean_df.columns if c not in
                    ['area', 'year', 'month', 'target_crime_count']]

    for col in feature_cols:
        if clean_df[col].isna().any():
            # Fill with area-level mean first
            clean_df[col] = clean_df.groupby('area')[col].transform(
                lambda x: x.fillna(x.mean())
            )
            # Then fill any remaining with global mean
            clean_df[col] = clean_df[col].fillna(clean_df[col].mean())
            # Final fallback to 0
            clean_df[col] = clean_df[col].fillna(0)

    # Replace infinite values
    clean_df = clean_df.replace([np.inf, -np.inf], 0)

    target = clean_df['target_crime_count'].astype(int)
    features = clean_df[feature_cols].copy()

    return features, target, raw_df, clean_df


def build_cyber_training_matrix():
    """
    Full pipeline for cybercrime: Load → Aggregate → Features → Lags → Clean

    Returns:
        features_df: DataFrame with all features (X)
        target_series: Series with the target variable (y = next month's cyber count)
        raw_df: The aggregated df before target shift (for inspection)
    """
    # Step 1: Load raw data
    cyber_df = load_cybercrimes_df()

    # Step 2: Aggregate to area-month
    agg_df = aggregate_cyber_features(cyber_df)

    # Step 3: Add temporal features (reuse same function)
    agg_df = add_temporal_features(agg_df)

    # Step 4: Add area profile features
    agg_df = add_area_profile_features(agg_df)

    # Step 5: Add cyber lag features
    agg_df = add_cyber_lag_features(agg_df, target_col='cyber_count')

    # Step 6: Create TARGET — next month's cyber count
    agg_df = agg_df.sort_values(['area', 'year', 'month']).copy()
    target_dfs = []
    for area, group in agg_df.groupby('area'):
        group = group.sort_values(['year', 'month']).copy()
        group['target_cyber_count'] = group['cyber_count'].shift(-1)
        target_dfs.append(group)
    agg_df = pd.concat(target_dfs, ignore_index=True)

    # Step 7: Drop rows where target is NaN
    raw_df = agg_df.copy()
    clean_df = agg_df.dropna(subset=['target_cyber_count']).copy()

    # Step 8: Handle NaN
    feature_cols = [c for c in clean_df.columns if c not in
                    ['area', 'year', 'month', 'target_cyber_count']]

    for col in feature_cols:
        if clean_df[col].isna().any():
            clean_df[col] = clean_df.groupby('area')[col].transform(
                lambda x: x.fillna(x.mean())
            )
            clean_df[col] = clean_df[col].fillna(clean_df[col].mean())
            clean_df[col] = clean_df[col].fillna(0)

    clean_df = clean_df.replace([np.inf, -np.inf], 0)

    target = clean_df['target_cyber_count'].astype(int)
    features = clean_df[feature_cols].copy()

    return features, target, raw_df, clean_df


# ─── VALIDATION REPORT ────────────────────────────────────────────────────────

def generate_validation_report(features_df, target_series, dataset_name='Physical'):
    """
    Generate a comprehensive validation report for the training data.

    Returns a dict with all validation metrics.
    """
    report = {
        'dataset_name': dataset_name,
        'feature_matrix_shape': features_df.shape,
        'n_training_samples': len(features_df),
        'n_features': features_df.shape[1],
        'feature_names': list(features_df.columns),
        'missing_values': {
            'total_nan': int(features_df.isna().sum().sum()),
            'per_column': {
                col: int(features_df[col].isna().sum())
                for col in features_df.columns
                if features_df[col].isna().sum() > 0
            }
        },
        'infinite_values': int(np.isinf(features_df.select_dtypes(include=[np.number])).sum().sum()),
        'target_stats': {
            'min': int(target_series.min()),
            'max': int(target_series.max()),
            'mean': round(float(target_series.mean()), 2),
            'median': round(float(target_series.median()), 2),
            'std': round(float(target_series.std()), 2),
            'q25': round(float(target_series.quantile(0.25)), 2),
            'q75': round(float(target_series.quantile(0.75)), 2),
        },
        'target_distribution': {
            str(k): int(v) for k, v in
            target_series.value_counts().sort_index().head(20).items()
        },
        'feature_dtypes': {
            col: str(features_df[col].dtype) for col in features_df.columns
        },
        'sample_rows': features_df.head(5).to_dict('records'),
        'sample_targets': target_series.head(5).tolist(),
    }

    # Derive risk categories from target counts for reference
    q25 = target_series.quantile(0.25)
    q50 = target_series.quantile(0.50)
    q75 = target_series.quantile(0.75)
    report['risk_thresholds'] = {
        'Low': f'≤ {q25:.0f}',
        'Medium': f'{q25:.0f} – {q50:.0f}',
        'High': f'{q50:.0f} – {q75:.0f}',
        'Critical': f'> {q75:.0f}',
    }
    report['risk_category_counts'] = {
        'Low': int((target_series <= q25).sum()),
        'Medium': int(((target_series > q25) & (target_series <= q50)).sum()),
        'High': int(((target_series > q50) & (target_series <= q75)).sum()),
        'Critical': int((target_series > q75).sum()),
    }

    return report
