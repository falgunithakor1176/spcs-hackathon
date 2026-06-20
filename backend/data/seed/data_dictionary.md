# Data Dictionary

## 1. crimes.csv
| Field | Data Type | Description |
|-------|-----------|-------------|
| `crime_id` | VARCHAR | Unique identifier (e.g., CRM-000001) |
| `crime_type` | VARCHAR | Category of crime (e.g., Theft, Robbery) |
| `latitude` | DOUBLE PRECISION | GPS Latitude |
| `longitude` | DOUBLE PRECISION | GPS Longitude |
| `area` | VARCHAR | Neighborhood/Area name |
| `zone` | VARCHAR | Broader city zone (East, West, etc.) |
| `timestamp` | TIMESTAMP | Exact time of occurrence |
| `severity` | VARCHAR | Critical, High, Medium, or Low |
| `status` | VARCHAR | Current investigation status |
| `fir_number` | VARCHAR | Official Police FIR Number |
| `description` | TEXT | Auto-generated realistic incident narrative |
| `hour` | INTEGER | Hour of day (0-23) |
| `day_of_week` | INTEGER | 0=Mon, 6=Sun |
| `month` | INTEGER | Month (1-12) |
| `year` | INTEGER | Year (e.g., 2024) |
| `day` | INTEGER | Day of month (1-31) |
| `is_weekend` | BOOLEAN | True if Saturday or Sunday |
| `is_festival` | BOOLEAN | True if occurred during a major festival |
| `festival_name` | VARCHAR | Name of festival, if applicable |

## 2. cybercrime.csv
| Field | Data Type | Description |
|-------|-----------|-------------|
| `report_id` | VARCHAR | Unique identifier |
| `fraud_type` | VARCHAR | Category of digital fraud |
| `latitude` | DOUBLE PRECISION | Victim's GPS Latitude |
| `longitude` | DOUBLE PRECISION | Victim's GPS Longitude |
| `area` | VARCHAR | Neighborhood/Area name |
| `zone` | VARCHAR | Broader city zone |
| `amount_lost` | DOUBLE PRECISION | Financial loss in INR |
| `timestamp` | TIMESTAMP | Exact time of report |
| `status` | VARCHAR | Investigation status |
| `platform` | VARCHAR | Platform used for fraud (WhatsApp, Telegram) |
| `victim_age_group` | VARCHAR | Age bucket of the victim |
| `hour` | INTEGER | Hour of day |
| `month` | INTEGER | Month |
| `year` | INTEGER | Year |
| `day_of_week` | INTEGER | Day of week |
| `is_weekend` | BOOLEAN | True if weekend |

## 3. patrol_units.csv
| Field | Data Type | Description |
|-------|-----------|-------------|
| `vehicle_id` | VARCHAR | Identifier for the cruiser |
| `officer_id` | VARCHAR | Assigned officer ID |
| `officer_name` | VARCHAR | Officer's name |
| `current_location` | VARCHAR | JSON string or coordinates |
| `area` | VARCHAR | Assigned patrol area |
| `zone` | VARCHAR | Broader zone |
| `status` | VARCHAR | On Patrol, Responding, Available |
| `vehicle_type` | VARCHAR | PCR Van, Bike, Interceptor |
| `shift_time` | VARCHAR | Assigned shift hours |
| `incidents_handled` | INTEGER | Number of incidents cleared today |
| `last_update` | TIMESTAMP | Last GPS ping time |

## 4. hotspots.csv
| Field | Data Type | Description |
|-------|-----------|-------------|
| `id` | VARCHAR | Unique ID |
| `name` | VARCHAR | Descriptive name of the hotspot |
| `lat` | DOUBLE PRECISION | Center latitude |
| `lng` | DOUBLE PRECISION | Center longitude |
| `radius` | INTEGER | Size of the hotspot in meters |
| `risk` | VARCHAR | Critical, High |
| `score` | INTEGER | Calculated risk index (0-100) |
| `crimes` | INTEGER | Number of incidents clustered here |
| `primary_type` | VARCHAR | Most common crime type |
| `trend` | VARCHAR | Increasing, Decreasing, Stable |
| `emerged` | VARCHAR | When the hotspot was first detected |
| `zone` | VARCHAR | City zone |

## 5. alerts.csv
| Field | Data Type | Description |
|-------|-----------|-------------|
| `id` | VARCHAR | Unique ID |
| `type` | VARCHAR | Severity/Type of alert |
| `title` | VARCHAR | Headline |
| `message` | TEXT | Description of the alert |
| `area` | VARCHAR | Associated area |
| `timestamp` | TIMESTAMP | Time generated |
| `acknowledged` | BOOLEAN | True if seen by operator |
| `assigned_to` | VARCHAR | Officer ID if assigned |

## 6. predictions.csv
| Field | Data Type | Description |
|-------|-----------|-------------|
| `area` | VARCHAR | Targeted neighborhood |
| `risk_level` | VARCHAR | High, Medium |
| `score` | INTEGER | ML Confidence score |
| `predicted_crimes` | INTEGER | Estimated incidents in next 48h |
| `top_crime` | VARCHAR | Most likely offense |
| `confidence` | VARCHAR | Percentage string |
| `deployment` | VARCHAR | Recommended unit deployment |
| `lat` | DOUBLE PRECISION | Prediction center lat |
| `lng` | DOUBLE PRECISION | Prediction center lng |
