import { useData } from '../context/DataContext';
import { AREAS, CRIME_TYPES } from '../data/mockData';
import { getCrimesByType, getCrimesByArea, getCrimesByMonth, getCrimesByHour, getCyberByType, getTotalAmountLost } from '../data/analyticsUtils';
import React, { useState } from 'react';
import { MapContainer, TileLayer, CircleMarker, Popup, Polyline, Marker, useMap } from 'react-leaflet';
import { Truck, Navigation, Clock, MapPin, Activity, BarChart3 } from 'lucide-react';

const DARK_TILES = 'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png';

const STATUS_COLORS = {
  'On Patrol': '#00D4FF',
  'Responding': '#FF6D00',
  'At Station': '#4A6580',
  'Standby': '#00E676',
};

function MapResize() {
  const map = useMap();
  React.useEffect(() => { setTimeout(() => map.invalidateSize(), 100); }, [map]);
  return null;
}

function UnitCard({ unit }) {
  const color = STATUS_COLORS[unit.status] || '#00D4FF';
  return (
    <div className="glass-card p-3 rounded-lg mb-2"
      style={{ borderLeft: `3px solid ${color}` }}>
      <div className="flex items-center justify-between mb-1">
        <span className="font-orbitron font-bold text-xs" style={{ color }}>{unit.vehicle_id}</span>
        <span style={{
          background: `${color}15`, border: `1px solid ${color}30`,
          color, fontSize: 9, padding: '1px 5px', borderRadius: 3, fontFamily: 'Orbitron',
        }}>{unit.status}</span>
      </div>
      <div style={{ color: '#E8F4FD', fontSize: 11, marginBottom: 2 }}>{unit.officer_name}</div>
      <div className="flex items-center gap-3" style={{ color: 'var(--text-muted)', fontSize: 10 }}>
        <span>📍 {unit.area}</span>
        <span>🚗 {unit.vehicle_type}</span>
      </div>
      <div style={{ color: 'var(--text-muted)', fontSize: 10 }}>
        ⏰ {unit.shift_time} | Cases: {unit.incidents_handled}
      </div>
    </div>
  );
}

function RouteCard({ route, isActive, onSelect }) {
  const risk = route.color === '#FF1744' ? 'Critical' : route.color === '#FF6D00' ? 'High' : 'Medium';
  return (
    <div onClick={() => onSelect(route.id)}
      className="glass-card p-3 rounded-lg mb-2 cursor-pointer transition-all hover:scale-[1.01]"
      style={{
        borderLeft: `3px solid ${route.color}`,
        background: isActive ? `${route.color}08` : undefined,
        boxShadow: isActive ? `0 0 15px ${route.color}20` : undefined,
      }}>
      <div className="flex items-center justify-between mb-1">
        <span className="font-orbitron font-bold text-xs" style={{ color: route.color }}>{route.id}</span>
        <span style={{ color: route.color, fontSize: 9, fontFamily: 'Orbitron' }}>{risk} ZONE</span>
      </div>
      <div style={{ color: '#E8F4FD', fontSize: 11, marginBottom: 4 }}>{route.name}</div>
      <div className="grid grid-cols-3 gap-1">
        {[
          { label: 'DIST', value: `${route.distance_km}km` },
          { label: 'ETA', value: `${route.eta_minutes}m` },
          { label: 'CVG', value: route.coverage },
        ].map(({ label, value }) => (
          <div key={label} className="text-center p-1 rounded" style={{ background: 'rgba(0,0,0,0.2)' }}>
            <div style={{ color: route.color, fontSize: 11, fontFamily: 'JetBrains Mono', fontWeight: 700 }}>{value}</div>
            <div style={{ color: 'var(--text-muted)', fontSize: 8, fontFamily: 'Orbitron' }}>{label}</div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default function PatrolRouting() {
  const { crimes, hotspots, patrols, routes, cybercrime, alerts, predictions, loading } = useData();
  if (loading) return <div>Loading...</div>;

  const [selectedRoute, setSelectedRoute] = useState('RT-001');
  const [activeTab, setActiveTab] = useState('routes');

  const activeRoute = routes.find(r => r.id === selectedRoute);

  return (
    <div className="flex h-full overflow-hidden page-enter" style={{ background: '#060d1a' }}>

      {/* Left: Controls */}
      <div className="flex-shrink-0 flex flex-col overflow-hidden panel-surface"
        style={{ width: 280, borderRight: '1px solid rgba(0,212,255,0.06)' }}>

        {/* Tabs */}
        <div className="flex border-b" style={{ borderColor: 'rgba(0,212,255,0.06)' }}>
          {['routes', 'units'].map(tab => (
            <button key={tab} onClick={() => setActiveTab(tab)}
              className="flex-1 py-2.5 text-center"
              style={{
                fontSize: 9, fontFamily: 'Orbitron', letterSpacing: '0.1em',
                color: activeTab === tab ? 'var(--electric)' : 'var(--text-muted)',
                borderBottom: activeTab === tab ? '2px solid var(--electric)' : '2px solid transparent',
                background: activeTab === tab ? 'rgba(0,212,255,0.04)' : 'transparent',
              }}>
              {tab === 'routes' ? 'PATROL ROUTES' : 'PATROL UNITS'}
            </button>
          ))}
        </div>

        <div className="flex-1 overflow-y-auto p-3">
          {activeTab === 'routes' ? (
            <>
              <div className="section-header mb-3">AI-OPTIMIZED ROUTES</div>
              {routes.map(route => (
                <RouteCard key={route.id} route={route}
                  isActive={selectedRoute === route.id}
                  onSelect={setSelectedRoute} />
              ))}

              {/* Algorithm info */}
              <div className="intel-card p-3 mt-3 rounded">
                <div className="section-header mb-2">ALGORITHM INFO</div>
                <div style={{ color: 'var(--text-muted)', fontSize: 10, lineHeight: 1.6 }}>
                  <div>🔹 Algorithm: <span style={{ color: 'var(--electric)' }}>Dijkstra + A*</span></div>
                  <div>🔹 Optimization: <span style={{ color: 'var(--electric)' }}>Risk-Weighted</span></div>
                  <div>🔹 Coverage: <span style={{ color: '#00E676' }}>94% hotspot area</span></div>
                  <div>🔹 Last computed: <span style={{ color: 'var(--electric)' }}>2 min ago</span></div>
                </div>
              </div>
            </>
          ) : (
            <>
              <div className="section-header mb-3">ACTIVE UNITS ({patrols.length})</div>
              {patrols.slice(0, 12).map(unit => (
                <UnitCard key={unit.vehicle_id} unit={unit} />
              ))}
            </>
          )}
        </div>
      </div>

      {/* Right: Map */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Stats strip */}
        <div className="flex-shrink-0 flex items-center gap-6 px-4 py-2 border-b"
          style={{ borderColor: 'rgba(0,212,255,0.06)', background: 'rgba(6,13,26,0.98)' }}>
          {activeRoute && [
            { icon: Navigation, label: 'Route', value: activeRoute.name, color: activeRoute.color },
            { icon: MapPin, label: 'Distance', value: `${activeRoute.distance_km} km`, color: '#00D4FF' },
            { icon: Clock, label: 'Est. Time', value: `${activeRoute.eta_minutes} min`, color: '#00E676' },
            { icon: Activity, label: 'Coverage', value: activeRoute.coverage, color: '#FFD600' },
          ].map(({ icon: Icon, label, value, color }) => (
            <div key={label} className="flex items-center gap-2">
              <Icon size={12} style={{ color }} />
              <div>
                <div style={{ color: 'var(--text-muted)', fontSize: 9 }}>{label.toUpperCase()}</div>
                <div style={{ color, fontSize: 11, fontWeight: 600 }}>{value}</div>
              </div>
            </div>
          ))}

          <div className="ml-auto flex items-center gap-2">
            <div className="live-dot" />
            <span style={{ color: '#00E676', fontSize: 9, fontFamily: 'JetBrains Mono' }}>LIVE TRACKING</span>
          </div>
        </div>

        {/* Map */}
        <div className="flex-1 relative">
          <MapContainer center={[23.0225, 72.5714]} zoom={12}
            style={{ width: '100%', height: '100%', background: '#040810' }}>
            <MapResize />
            <TileLayer url={DARK_TILES} attribution="" />

            {/* Hotspots */}
            {hotspots.slice(0, 8).map(hs => (
              <CircleMarker key={hs.id} center={[hs.lat, hs.lng]}
                radius={hs.radius / 70}
                fillColor={hs.risk === 'Critical' ? '#FF1744' : hs.risk === 'High' ? '#FF6D00' : '#FFD600'}
                fillOpacity={0.1}
                color={hs.risk === 'Critical' ? '#FF1744' : hs.risk === 'High' ? '#FF6D00' : '#FFD600'}
                opacity={0.4} weight={1.5} />
            ))}

            {/* All routes (dimmed) */}
            {routes.map(route => (
              <Polyline key={route.id}
                positions={route.waypoints.map(wp => [wp.lat, wp.lng])}
                color={route.color}
                opacity={route.id === selectedRoute ? 0.9 : 0.25}
                weight={route.id === selectedRoute ? 4 : 2}
                dashArray={route.id === selectedRoute ? undefined : '6, 4'} />
            ))}

            {/* Waypoints for active route */}
            {activeRoute && activeRoute.waypoints.map((wp, i) => (
              <CircleMarker key={i} center={[wp.lat, wp.lng]}
                radius={i === 0 || i === activeRoute.waypoints.length - 1 ? 8 : 5}
                fillColor={activeRoute.color} fillOpacity={0.9}
                color="white" opacity={0.8} weight={2}>
                <Popup>
                  <div style={{ fontFamily: 'Inter', fontSize: 12 }}>
                    <div style={{ color: activeRoute.color, fontFamily: 'Orbitron', fontSize: 10, fontWeight: 700 }}>
                      WAYPOINT {i + 1}
                    </div>
                    <div style={{ color: '#E8F4FD', fontWeight: 600 }}>{wp.name}</div>
                  </div>
                </Popup>
              </CircleMarker>
            ))}

            {/* Patrol units */}
            {patrols.filter(u => u.status !== 'At Station').map(unit => (
              <CircleMarker key={unit.vehicle_id}
                center={[unit.current_location.lat, unit.current_location.lng]}
                radius={6}
                fillColor={STATUS_COLORS[unit.status] || '#00D4FF'} fillOpacity={0.9}
                color="rgba(255,255,255,0.4)" opacity={1} weight={2}>
                <Popup>
                  <div style={{ fontFamily: 'Inter', fontSize: 12 }}>
                    <div style={{ color: STATUS_COLORS[unit.status], fontFamily: 'Orbitron', fontSize: 10, fontWeight: 700 }}>
                      {unit.vehicle_id}
                    </div>
                    <div style={{ color: '#E8F4FD' }}>{unit.officer_name}</div>
                    <div style={{ color: '#7BA7C4' }}>{unit.status} — {unit.area}</div>
                  </div>
                </Popup>
              </CircleMarker>
            ))}
          </MapContainer>

          {/* Legend */}
          <div className="absolute bottom-4 left-4 z-[1000] glass-card p-3 rounded-lg">
            <div className="section-header mb-2">Legend</div>
            {routes.map(r => (
              <div key={r.id} className="flex items-center gap-2 mb-1">
                <div className="w-6 h-1 rounded" style={{ background: r.color, opacity: r.id === selectedRoute ? 1 : 0.35 }} />
                <span style={{ color: 'var(--text-secondary)', fontSize: 10 }}>{r.name.slice(0, 18)}...</span>
              </div>
            ))}
            <div className="h-px my-1" style={{ background: 'rgba(0,212,255,0.1)' }} />
            {Object.entries(STATUS_COLORS).map(([s, c]) => (
              <div key={s} className="flex items-center gap-2 mb-0.5">
                <div className="w-2 h-2 rounded-full" style={{ background: c }} />
                <span style={{ color: 'var(--text-secondary)', fontSize: 10 }}>{s}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
