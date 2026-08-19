from db import db
from sqlalchemy import Column, String, Float, Integer, Boolean, Text, DateTime
from sqlalchemy.dialects.postgresql import JSONB

# We import geoalchemy2 only when PostGIS is available
try:
    from geoalchemy2 import Geometry
    POSTGIS_AVAILABLE = True
except ImportError:
    POSTGIS_AVAILABLE = False


class Crime(db.Model):
    __tablename__ = 'crimes'

    crime_id     = Column(String(50), primary_key=True)
    crime_type   = Column(String(100))
    latitude     = Column(Float)
    longitude    = Column(Float)
    area         = Column(String(100))
    zone         = Column(String(50))
    timestamp    = Column(String(50))
    severity     = Column(String(50))
    status       = Column(String(50))
    fir_number   = Column(String(100))
    description  = Column(Text)
    hour         = Column(Integer)
    day_of_week  = Column(Integer)
    month        = Column(Integer)
    year         = Column(Integer)
    day          = Column(Integer)
    is_weekend   = Column(Boolean)
    is_festival  = Column(Boolean)
    festival_name = Column(String(100))
    # PostGIS geometry column (added by init_db.py)

    def to_dict(self):
        return {
            'crime_id':     self.crime_id,
            'crime_type':   self.crime_type,
            'latitude':     self.latitude,
            'longitude':    self.longitude,
            'area':         self.area,
            'zone':         self.zone,
            'timestamp':    self.timestamp,
            'severity':     self.severity,
            'status':       self.status,
            'fir_number':   self.fir_number,
            'description':  self.description,
            'hour':         self.hour,
            'day_of_week':  self.day_of_week,
            'month':        self.month,
            'year':         self.year,
            'day':          self.day,
            'is_weekend':   self.is_weekend,
            'is_festival':  self.is_festival,
            'festival_name': self.festival_name,
        }


class Cybercrime(db.Model):
    __tablename__ = 'cybercrimes'

    report_id       = Column(String(50), primary_key=True)
    fraud_type      = Column(String(100))
    latitude        = Column(Float)
    longitude       = Column(Float)
    area            = Column(String(100))
    zone            = Column(String(50))
    amount_lost     = Column(Float)
    timestamp       = Column(String(50))
    status          = Column(String(50))
    platform        = Column(String(100))
    victim_age_group = Column(String(50))
    hour            = Column(Integer)
    month           = Column(Integer)
    year            = Column(Integer)
    day_of_week     = Column(Integer)
    is_weekend      = Column(Boolean)

    def to_dict(self):
        return {
            'report_id':        self.report_id,
            'fraud_type':       self.fraud_type,
            'latitude':         self.latitude,
            'longitude':        self.longitude,
            'area':             self.area,
            'zone':             self.zone,
            'amount_lost':      self.amount_lost,
            'timestamp':        self.timestamp,
            'status':           self.status,
            'platform':         self.platform,
            'victim_age_group': self.victim_age_group,
            'hour':             self.hour,
            'month':            self.month,
            'year':             self.year,
            'day_of_week':      self.day_of_week,
            'is_weekend':       self.is_weekend,
        }


class PatrolUnit(db.Model):
    __tablename__ = 'patrol_units'

    vehicle_id        = Column(String(50), primary_key=True)
    officer_id        = Column(String(50))
    officer_name      = Column(String(100))
    current_location  = Column(String(200))
    area              = Column(String(100))
    zone              = Column(String(50))
    status            = Column(String(50))
    vehicle_type      = Column(String(50))
    shift_time        = Column(String(50))
    incidents_handled = Column(Integer)
    last_update       = Column(String(100))

    def to_dict(self):
        import json, ast
        loc = self.current_location
        try:
            loc = ast.literal_eval(loc) if isinstance(loc, str) else loc
        except Exception:
            loc = {}
        return {
            'vehicle_id':        self.vehicle_id,
            'officer_id':        self.officer_id,
            'officer_name':      self.officer_name,
            'current_location':  loc,
            'area':              self.area,
            'zone':              self.zone,
            'status':            self.status,
            'vehicle_type':      self.vehicle_type,
            'shift_time':        self.shift_time,
            'incidents_handled': self.incidents_handled,
            'last_update':       self.last_update,
        }


class Hotspot(db.Model):
    __tablename__ = 'hotspots'

    id           = Column(String(50), primary_key=True)
    name         = Column(String(150))
    lat          = Column(Float)
    lng          = Column(Float)
    radius       = Column(Integer)
    risk         = Column(String(50))
    score        = Column(Integer)
    crimes       = Column(Integer)
    primary_type = Column(String(100))
    trend        = Column(String(50))
    emerged      = Column(String(50))
    zone         = Column(String(50))

    def to_dict(self):
        return {
            'id':           self.id,
            'name':         self.name,
            'lat':          self.lat,
            'lng':          self.lng,
            'radius':       self.radius,
            'risk':         self.risk,
            'score':        self.score,
            'crimes':       self.crimes,
            'primary_type': self.primary_type,
            'trend':        self.trend,
            'emerged':      self.emerged,
            'zone':         self.zone,
        }


class Alert(db.Model):
    __tablename__ = 'alerts'

    id           = Column(String(50), primary_key=True)
    type         = Column(String(50))
    title        = Column(String(200))
    message      = Column(Text)
    area         = Column(String(100))
    timestamp    = Column(String(100))
    acknowledged = Column(Boolean)
    assigned_to  = Column(String(50))

    def to_dict(self):
        return {
            'id':           self.id,
            'type':         self.type,
            'title':        self.title,
            'message':      self.message,
            'area':         self.area,
            'timestamp':    self.timestamp,
            'acknowledged': self.acknowledged,
            'assigned_to':  self.assigned_to,
        }


class Prediction(db.Model):
    __tablename__ = 'predictions'

    area             = Column(String(100), primary_key=True)
    risk_level       = Column(String(50))
    score            = Column(Integer)
    predicted_crimes = Column(Integer)
    top_crime        = Column(String(100))
    confidence       = Column(String(50))
    deployment       = Column(String(200))
    lat              = Column(Float)
    lng              = Column(Float)

    def to_dict(self):
        return {
            'area':             self.area,
            'risk_level':       self.risk_level,
            'score':            self.score,
            'predicted_crimes': self.predicted_crimes,
            'top_crime':        self.top_crime,
            'confidence':       self.confidence,
            'deployment':       self.deployment,
            'lat':              self.lat,
            'lng':              self.lng,
        }


class PatrolRoute(db.Model):
    __tablename__ = 'patrol_routes'

    id           = Column(String(50), primary_key=True)
    vehicle_id   = Column(String(50))
    name         = Column(String(150))
    color        = Column(String(20))
    waypoints    = Column(Text)
    distance_km  = Column(Float)
    coverage     = Column(String(20))
    eta_minutes  = Column(Integer)

    def to_dict(self):
        import ast
        wps = self.waypoints
        try:
            wps = ast.literal_eval(wps) if isinstance(wps, str) else wps
        except Exception:
            wps = []
        return {
            'id':          self.id,
            'vehicle_id':  self.vehicle_id,
            'name':        self.name,
            'color':       self.color,
            'waypoints':   wps,
            'distance_km': self.distance_km,
            'coverage':    self.coverage,
            'eta_minutes': self.eta_minutes,
        }


# ─── PHASE 6C: ENGINE 2 & ENGINE 3 TABLES ────────────────────────────────────

class CrimeForecast(db.Model):
    """
    Engine 2 output — Physical crime count prediction per area per month.
    Populated by prediction_engine.py. Used by the Correlation Engine and API.
    """
    __tablename__ = 'crime_forecasts'

    id                 = Column(Integer, primary_key=True, autoincrement=True)
    area               = Column(String(100), nullable=False, index=True)
    zone               = Column(String(50))
    forecast_year      = Column(Integer, nullable=False)
    forecast_month     = Column(Integer, nullable=False)
    predicted_count    = Column(Float, nullable=False)
    physical_risk      = Column(String(20), nullable=False)   # Low/Medium/High/Critical
    generated_at       = Column(DateTime, nullable=False)

    def to_dict(self):
        return {
            'id':              self.id,
            'area':            self.area,
            'zone':            self.zone,
            'forecast_year':   self.forecast_year,
            'forecast_month':  self.forecast_month,
            'predicted_count': self.predicted_count,
            'physical_risk':   self.physical_risk,
            'generated_at':    self.generated_at.isoformat() if self.generated_at else None,
        }


class CyberForecast(db.Model):
    """
    Engine 2 output — Cybercrime risk category per area per month.
    Populated by prediction_engine.py. Used by the Correlation Engine and API.
    """
    __tablename__ = 'cyber_forecasts'

    id              = Column(Integer, primary_key=True, autoincrement=True)
    area            = Column(String(100), nullable=False, index=True)
    zone            = Column(String(50))
    forecast_year   = Column(Integer, nullable=False)
    forecast_month  = Column(Integer, nullable=False)
    cyber_risk      = Column(String(20), nullable=False)    # Low/Medium/High/Critical
    generated_at    = Column(DateTime, nullable=False)

    def to_dict(self):
        return {
            'id':             self.id,
            'area':           self.area,
            'zone':           self.zone,
            'forecast_year':  self.forecast_year,
            'forecast_month': self.forecast_month,
            'cyber_risk':     self.cyber_risk,
            'generated_at':   self.generated_at.isoformat() if self.generated_at else None,
        }


class AreaIntelligence(db.Model):
    """
    Engine 3 (Correlation Engine) output — Combined risk per area per month.
    Merges Engine 1 (DBSCAN spatial), Engine 2 physical & cyber predictions.
    Heuristic weights are configurable domain-informed parameters, not fixed AI.
    """
    __tablename__ = 'area_intelligence'

    id                    = Column(Integer, primary_key=True, autoincrement=True)
    area                  = Column(String(100), nullable=False, index=True)
    zone                  = Column(String(50))
    forecast_year         = Column(Integer, nullable=False)
    forecast_month        = Column(Integer, nullable=False)

    # Engine 1 (DBSCAN) inputs
    hotspot_count         = Column(Integer, default=0)
    hotspot_risk          = Column(String(20))     # worst risk level from active hotspots

    # Engine 2 inputs
    physical_risk         = Column(String(20))     # from CrimeForecast
    predicted_count       = Column(Float)
    cyber_risk            = Column(String(20))     # from CyberForecast

    # Engine 3 output
    combined_risk         = Column(String(20), nullable=False)   # Low/Medium/High/Critical
    combined_risk_score   = Column(Float, nullable=False)        # 0.0 – 1.0
    patrol_priority       = Column(Integer, nullable=False)      # 1 (highest) – 27 (lowest)
    top_contributing_engine = Column(String(50))                 # which engine drove risk

    generated_at          = Column(DateTime, nullable=False)

    def to_dict(self):
        return {
            'id':                       self.id,
            'area':                     self.area,
            'zone':                     self.zone,
            'forecast_year':            self.forecast_year,
            'forecast_month':           self.forecast_month,
            'hotspot_count':            self.hotspot_count,
            'hotspot_risk':             self.hotspot_risk,
            'physical_risk':            self.physical_risk,
            'predicted_count':          self.predicted_count,
            'cyber_risk':               self.cyber_risk,
            'combined_risk':            self.combined_risk,
            'combined_risk_score':      self.combined_risk_score,
            'patrol_priority':          self.patrol_priority,
            'top_contributing_engine':  self.top_contributing_engine,
            'generated_at':             self.generated_at.isoformat() if self.generated_at else None,
        }


# ─── AUDIT LOG TABLE ──────────────────────────────────────────────────────────

class AuditLog(db.Model):
    """
    Tracks all significant system actions for compliance and accountability.
    Written by audit_service.log_action() — never modified after insertion.
    """
    __tablename__ = 'audit_logs'

    id          = Column(Integer, primary_key=True, autoincrement=True)
    username    = Column(String(100), nullable=False)
    role        = Column(String(50))
    action      = Column(String(100), nullable=False)   # LOGIN, ENGINE_RUN, EXPORT, ACK_ALERT etc.
    resource    = Column(String(100))                   # which API / page / engine
    detail      = Column(Text)                          # extra context
    ip_address  = Column(String(50))
    timestamp   = Column(DateTime, nullable=False)

    def to_dict(self):
        return {
            'id':         self.id,
            'username':   self.username,
            'role':       self.role,
            'action':     self.action,
            'resource':   self.resource,
            'detail':     self.detail,
            'ip_address': self.ip_address,
            'timestamp':  self.timestamp.isoformat() if self.timestamp else None,
        }


# ─── ACTIVE DISPATCH TABLE (Phase 7C) ─────────────────────────────────────────

class ActiveDispatch(db.Model):
    """
    Tracks active patrol dispatches with their OSRM route geometry.
    Created on dispatch, updated during simulated GPS tracking,
    marked as Arrived when patrol reaches destination.
    One active dispatch per patrol unit (unique constraint).
    """
    __tablename__ = 'active_dispatches'

    id              = Column(Integer, primary_key=True, autoincrement=True)
    patrol_id       = Column(String(50), nullable=False, unique=True)
    hotspot_id      = Column(String(50), nullable=False)
    alert_id        = Column(String(50))
    route_geometry  = Column(Text, nullable=False)       # JSON: [[lat,lng], ...]
    total_points    = Column(Integer, nullable=False)
    current_index   = Column(Integer, nullable=False, default=0)
    distance_km     = Column(Float)
    eta_minutes     = Column(Integer)
    status          = Column(String(50), nullable=False, default='Responding')
    dispatched_at   = Column(DateTime, nullable=False)
    arrived_at      = Column(DateTime)

    def to_dict(self):
        import json
        try:
            geometry = json.loads(self.route_geometry)
        except Exception:
            geometry = []
        return {
            'id':             self.id,
            'patrol_id':      self.patrol_id,
            'hotspot_id':     self.hotspot_id,
            'alert_id':       self.alert_id,
            'route_geometry':  geometry,
            'total_points':   self.total_points,
            'current_index':  self.current_index,
            'distance_km':    self.distance_km,
            'eta_minutes':    self.eta_minutes,
            'status':         self.status,
            'dispatched_at':  self.dispatched_at.isoformat() if self.dispatched_at else None,
            'arrived_at':     self.arrived_at.isoformat() if self.arrived_at else None,
        }
