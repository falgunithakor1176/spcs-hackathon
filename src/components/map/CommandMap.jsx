import { useData } from '../../context/DataContext';
import { AREAS, CRIME_TYPES } from '../../data/mockData';
import { getCrimesByType, getCrimesByArea, getCrimesByMonth, getCrimesByHour, getCyberByType, getTotalAmountLost } from '../../data/analyticsUtils';
import React, { useState, useMemo } from 'react';
import { MapContainer, TileLayer, CircleMarker, Circle, Popup, Polyline, useMap } from 'react-leaflet';

const SEVERITY_COLORS = {
  Critical: '#FF1744',
  High: '#FF6D00',
  Medium: '#FFD600',
  Low: '#00E676',
};

const CRIME_COLORS = {
  Theft: '#60A5FA',
  'Chain Snatching': '#F97316',
  'Mobile Theft': '#A78BFA',
  'Vehicle Theft': '#34D399',
  Robbery: '#FF1744',
  Burglary: '#FB923C',
  Assault: '#F43F5E',
  'Domestic Violence': '#E879F9',
  'Drug Offense': '#818CF8',
  Fraud: '#FCD34D',
  Kidnapping: '#FF1744',
  Murder: '#7F1D1D',
  default: '#60A5FA',
};

const HOTSPOT_RISK_CONFIG = {
  Critical: { color: '#FF1744', fillOpacity: 0.15, strokeOpacity: 0.6, weight: 2 },
  High: { color: '#FF6D00', fillOpacity: 0.12, strokeOpacity: 0.5, weight: 2 },
  Medium: { color: '#FFD600', fillOpacity: 0.08, strokeOpacity: 0.4, weight: 1.5 },
  Low: { color: '#00E676', fillOpacity: 0.07, strokeOpacity: 0.35, weight: 1 },
};

const DARK_TILES = 'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png';
const DARK_TILES_ATTR = '&copy; <a href="https://carto.com/">CARTO</a>';

// Layer toggle state
const DEFAULT_LAYERS = {
  crimes: true,
  hotspots: true,
  patrol: true,
  routes: true,
  riskZones: true,
};

function MapResize() {
  const map = useMap();
  React.useEffect(() => {
    setTimeout(() => map.invalidateSize(), 100);
  }, [map]);
  return null;
}

function CrimePopup({ crime }) {
  const color = SEVERITY_COLORS[crime.severity] || '#60A5FA';
  return (
    <div style={{ minWidth: 200, fontFamily: 'Inter, sans-serif' }}>
      <div style={{
        background: `linear-gradient(135deg, rgba(8,17,32,0.98), rgba(11,22,42,0.98))`,
        margin: '-8px -12px 8px',
        padding: '8px 12px',
        borderBottom: `1px solid ${color}30`,
      }}>
        <div style={{ color, fontSize: 11, fontFamily: 'Orbitron, monospace', letterSpacing: '0.1em', fontWeight: 600 }}>
          {crime.severity.toUpperCase()} SEVERITY
        </div>
        <div style={{ color: '#E8F4FD', fontSize: 13, fontWeight: 600, marginTop: 2 }}>
          {crime.crime_type}
        </div>
      </div>
      <div style={{ fontSize: 11, color: '#7BA7C4', lineHeight: 1.6 }}>
        <div>📍 <strong style={{ color: '#E8F4FD' }}>{crime.area}</strong></div>
        <div>🕐 {new Date(crime.timestamp).toLocaleString('en-IN')}</div>
        <div>📋 FIR: <span style={{ color: 'var(--electric, #00D4FF)' }}>{crime.fir_number}</span></div>
        <div style={{ marginTop: 6, color: '#94A3B8', fontSize: 10 }}>{crime.description}</div>
        <div style={{ marginTop: 4 }}>
          <span style={{
            background: crime.status === 'Closed' ? 'rgba(0,230,118,0.1)' : 'rgba(255,214,0,0.1)',
            border: `1px solid ${crime.status === 'Closed' ? 'rgba(0,230,118,0.3)' : 'rgba(255,214,0,0.3)'}`,
            color: crime.status === 'Closed' ? '#00E676' : '#FFD600',
            padding: '1px 6px', borderRadius: 3, fontSize: 10,
          }}>{crime.status}</span>
        </div>
      </div>
    </div>
  );
}

function HotspotPopup({ hs }) {
  const color = SEVERITY_COLORS[hs.risk] || '#FF6D00';
  return (
    <div style={{ minWidth: 200, fontFamily: 'Inter, sans-serif' }}>
      <div style={{ color, fontSize: 11, fontFamily: 'Orbitron, monospace', fontWeight: 700, letterSpacing: '0.08em', marginBottom: 6 }}>
        ⚠ HOTSPOT — {hs.risk.toUpperCase()}
      </div>
      <div style={{ color: '#E8F4FD', fontSize: 13, fontWeight: 600, marginBottom: 4 }}>{hs.name}</div>
      <div style={{ fontSize: 11, color: '#7BA7C4', lineHeight: 1.7 }}>
        <div>🔴 Risk Score: <strong style={{ color }}>{hs.score}/100</strong></div>
        <div>📊 Total Crimes: <strong style={{ color: '#E8F4FD' }}>{hs.crimes}</strong></div>
        <div>🔍 Primary: <span style={{ color: '#60A5FA' }}>{hs.primary_type}</span></div>
        <div>📈 Trend: <span style={{ color: hs.trend.startsWith('+') ? '#FF1744' : '#00E676' }}>{hs.trend}</span></div>
      </div>
    </div>
  );
}

export default function CommandMap({ layers: externalLayers, filters }) {
  const { crimes, hotspots, patrols, routes, cybercrime, alerts, predictions, loading } = useData();
  if (loading) return <div>Loading...</div>;

  const [activeLayers, setActiveLayers] = useState(DEFAULT_LAYERS);

  const layers = externalLayers || activeLayers;

  // Filter crimes based on active filters
  const filteredCrimes = useMemo(() => {
    let result = crimes.slice(0, 2000);
    if (filters?.crimeType && filters.crimeType !== 'all') {
      result = result.filter(c => c.crime_type === filters.crimeType);
    }
    if (filters?.severity && filters.severity !== 'all') {
      result = result.filter(c => c.severity === filters.severity);
    }
    if (filters?.area && filters.area !== 'all') {
      result = result.filter(c => c.area === filters.area);
    }
    return result.slice(0, 1500); // performance cap
  }, [filters]);

  const toggleLayer = (key) => {
    setActiveLayers(prev => ({ ...prev, [key]: !prev[key] }));
  };

  return (
    <div className="relative w-full h-full">
      <MapContainer
        center={[23.0225, 72.5714]}
        zoom={12}
        style={{ width: '100%', height: '100%', background: '#040810' }}
        zoomControl={true}
        attributionControl={true}
      >
        <MapResize />

        {/* Dark base tiles */}
        <TileLayer url={DARK_TILES} attribution={DARK_TILES_ATTR} />

        {/* LAYER: Crime Incidents */}
        {layers.crimes && filteredCrimes.map(crime => {
          const color = SEVERITY_COLORS[crime.severity] || '#60A5FA';
          return (
            <CircleMarker
              key={crime.crime_id}
              center={[crime.latitude, crime.longitude]}
              radius={crime.severity === 'Critical' ? 5 : crime.severity === 'High' ? 4 : 3}
              fillColor={color}
              fillOpacity={0.75}
              color={color}
              opacity={0.9}
              weight={1}
            >
              <Popup>
                <CrimePopup crime={crime} />
              </Popup>
            </CircleMarker>
          );
        })}

        {/* LAYER: Hotspot Risk Zones */}
        {layers.riskZones && hotspots.map(hs => {
          const cfg = HOTSPOT_RISK_CONFIG[hs.risk] || HOTSPOT_RISK_CONFIG.Medium;
          return (
            <Circle
              key={`hz-${hs.id}`}
              center={[hs.lat, hs.lng]}
              radius={hs.radius}
              fillColor={cfg.color}
              fillOpacity={cfg.fillOpacity}
              color={cfg.color}
              opacity={cfg.strokeOpacity}
              weight={cfg.weight}
            />
          );
        })}

        {/* LAYER: Crime Hotspots (inner highlight) */}
        {layers.hotspots && hotspots.map(hs => {
          const color = SEVERITY_COLORS[hs.risk] || '#FF6D00';
          return (
            <CircleMarker
              key={`hs-${hs.id}`}
              center={[hs.lat, hs.lng]}
              radius={12}
              fillColor={color}
              fillOpacity={0.25}
              color={color}
              opacity={0.8}
              weight={1.5}
            >
              <Popup className="dark-popup">
                <HotspotPopup hs={hs} />
              </Popup>
            </CircleMarker>
          );
        })}



        {/* LAYER: Patrol Vehicles */}
        {layers.patrol && patrols.filter(u => u.status !== 'At Station').map(unit => (
          <CircleMarker
            key={unit.vehicle_id}
            center={[unit.current_location.lat, unit.current_location.lng]}
            radius={6}
            fillColor={unit.status === 'On Patrol' ? '#00D4FF' : unit.status === 'Responding' ? '#FF6D00' : '#00E676'}
            fillOpacity={0.9}
            color="rgba(0,212,255,0.4)"
            opacity={1}
            weight={2}
          >
            <Popup>
              <div style={{ fontFamily: 'Inter, sans-serif', fontSize: 12 }}>
                <div style={{ color: '#00D4FF', fontFamily: 'Orbitron', fontSize: 10, fontWeight: 700, marginBottom: 4 }}>
                  PATROL UNIT
                </div>
                <div style={{ color: '#E8F4FD', fontWeight: 600 }}>{unit.vehicle_id}</div>
                <div style={{ color: '#7BA7C4', lineHeight: 1.6, marginTop: 4 }}>
                  <div>👮 {unit.officer_name}</div>
                  <div>🚗 {unit.vehicle_type}</div>
                  <div>📍 {unit.area}</div>
                  <div>🕐 Shift: {unit.shift_time}</div>
                  <div style={{ marginTop: 4 }}>
                    <span style={{
                      background: unit.status === 'On Patrol' ? 'rgba(0,212,255,0.1)' : 'rgba(255,109,0,0.1)',
                      border: `1px solid ${unit.status === 'On Patrol' ? 'rgba(0,212,255,0.3)' : 'rgba(255,109,0,0.3)'}`,
                      color: unit.status === 'On Patrol' ? '#00D4FF' : '#FF6D00',
                      padding: '1px 6px', borderRadius: 3, fontSize: 10,
                    }}>{unit.status}</span>
                  </div>
                </div>
              </div>
            </Popup>
          </CircleMarker>
        ))}

        {/* LAYER: Patrol Routes */}
        {layers.routes && routes.map(route => (
          <Polyline
            key={route.id}
            positions={route.waypoints.map(wp => [wp.lat, wp.lng])}
            color={route.color}
            opacity={0.7}
            weight={3}
            dashArray="8, 4"
          />
        ))}

        {/* LAYER: Dispatch Vectors (Straight-line routes to assigned hotspots) */}
        {layers.routes && alerts.filter(a => a.assigned_to).map(alert => {
          // Find matching patrol
          const patrol = patrols.find(p => p.vehicle_id === alert.assigned_to);
          // Find matching hotspot (Alert ID ALT-ML-001 -> Hotspot ID HS-ML-001)
          const hsId = alert.id.replace('ALT-', 'HS-');
          const hotspot = hotspots.find(h => h.id === hsId);
          
          if (!patrol || !hotspot || !patrol.current_location) return null;
          
          return (
            <Polyline
              key={`dispatch-${alert.id}`}
              positions={[
                [patrol.current_location.lat, patrol.current_location.lng],
                [hotspot.lat, hotspot.lng]
              ]}
              color="#FF6D00"
              opacity={0.8}
              weight={3}
              dashArray="10, 10"
            >
              <Popup>
                <div style={{ fontFamily: 'Inter, sans-serif', fontSize: 11, color: '#FF6D00', fontWeight: 'bold' }}>
                  DISPATCH VECTOR (OSRM OFFLINE FALLBACK)
                </div>
                <div style={{ color: '#E8F4FD', fontSize: 12 }}>{patrol.vehicle_id} ➔ {hotspot.name}</div>
              </Popup>
            </Polyline>
          );
        })}
      </MapContainer>

      {/* Built-in Layer Toggle (if no external layer control) */}
      {!externalLayers && (
        <div className="absolute top-3 right-3 z-[1000] glass-card p-2 rounded-lg" style={{ minWidth: 150 }}>
          <div className="section-header mb-2 px-1">Layers</div>
          {Object.entries(activeLayers).map(([key, active]) => (
            <button key={key} className={`layer-btn ${active ? 'active' : ''}`} onClick={() => toggleLayer(key)}>
              <div className="layer-dot" style={{
                background: key === 'crimes' ? '#60A5FA' : key === 'hotspots' ? '#FF6D00' :
                  key === 'patrol' ? '#00D4FF' : key === 'routes' ? '#FFD600' : '#00E676',
                opacity: active ? 1 : 0.3,
              }} />
              <span style={{ textTransform: 'capitalize' }}>{key.replace(/([A-Z])/g, ' $1')}</span>
            </button>
          ))}
        </div>
      )}

      {/* Map Legend */}
      <div className="absolute bottom-5 left-3 z-[1000] glass-card p-3 rounded-lg">
        <div className="section-header mb-2">Risk Legend</div>
        {[
          { color: '#FF1744', label: 'Critical' },
          { color: '#FF6D00', label: 'High' },
          { color: '#FFD600', label: 'Medium' },
          { color: '#00E676', label: 'Low' },
          { color: '#00D4FF', label: 'Patrol Unit' },
        ].map(({ color, label }) => (
          <div key={label} className="flex items-center gap-2 mb-1">
            <div className="w-2.5 h-2.5 rounded-full" style={{ background: color, boxShadow: `0 0 4px ${color}` }} />
            <span style={{ color: 'var(--text-secondary)', fontSize: 11 }}>{label}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
