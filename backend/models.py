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
