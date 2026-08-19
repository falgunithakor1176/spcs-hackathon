import { useData } from '../context/DataContext';
import { AREAS, CRIME_TYPES } from '../data/mockData';
import { getCrimesByType, getCrimesByArea, getCrimesByMonth, getCrimesByHour, getCyberByType, getTotalAmountLost } from '../data/analyticsUtils';
import React, { useState, useEffect, useCallback, useRef } from 'react';
import { MapContainer, TileLayer, CircleMarker, Popup, Polyline, useMap } from 'react-leaflet';
import { Navigation, Clock, MapPin, Activity, ShieldAlert, CheckCircle2, Radio } from 'lucide-react';
import { generateDynamicRoute } from '../services/routingService';
import { getDispatchRecommendations, executeDispatch, getActiveDispatches, updatePatrolPosition, notifyArrival } from '../services/dispatchService';

const DARK_TILES = 'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png';

const STATUS_COLORS = {
  'On Patrol': '#00D4FF',
  'Responding': '#FF6D00',
  'At Station': '#4A6580',
  'Standby': '#00E676',
};

// Simulation tick interval in milliseconds (1.5 seconds per step)
const SIM_TICK_MS = 1500;

function MapResize() {
  const map = useMap();
  useEffect(() => { setTimeout(() => map.invalidateSize(), 100); }, [map]);
  return null;
}

function UnitCard({ unit, isActive, onSelect }) {
  const color = STATUS_COLORS[unit.status] || '#00D4FF';
  return (
    <div onClick={() => onSelect(unit.vehicle_id)}
      className="glass-card p-3 rounded-lg mb-2 cursor-pointer transition-all hover:scale-[1.01]"
      style={{
        borderLeft: `3px solid ${color}`,
        background: isActive ? 'rgba(0, 212, 255, 0.08)' : undefined,
        border: isActive ? '1px solid rgba(0, 212, 255, 0.3)' : undefined,
      }}>
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
  const { crimes, hotspots, patrols, routes, cybercrime, alerts, predictions, loading, refreshData } = useData();
  
  const [selectedRoute, setSelectedRoute] = useState('RT-001');
  const [activeTab, setActiveTab] = useState('dispatch'); // Default to commander dispatch tab
  
  // Dynamic Route & Selector States
  const [selectedUnit, setSelectedUnit] = useState(null);
  const [selectedHotspot, setSelectedHotspot] = useState('');
  const [dynamicRoute, setDynamicRoute] = useState(null);
  const [generatingRoute, setGeneratingRoute] = useState(false);
  const [routeError, setRouteError] = useState(null);

  // Dispatch Recommendations States
  const [recs, setRecs] = useState([]);
  const [recsLoading, setRecsLoading] = useState(false);
  const [dispatchStatus, setDispatchStatus] = useState({}); // maps hotspot_id -> 'idle' | 'loading' | 'success' | 'conflict' | 'error'
  const [dispatchMsg, setDispatchMsg] = useState('');

  // ─── Phase 7C: Simulated GPS Tracking State ───────────────────────────────
  const [activeDispatches, setActiveDispatches] = useState([]);
  // Track simulation progress per patrol: { patrolId: { stepIndex, position, progressPct, simulatedEta, totalPoints, routeGeometry, hotspotId } }
  const [simState, setSimState] = useState({});
  const simulationIntervals = useRef(new Map()); // patrolId -> intervalId

  const fetchRecs = useCallback(async () => {
    setRecsLoading(true);
    try {
      const res = await getDispatchRecommendations();
      if (res.status === 'success') {
        setRecs(res.recommendations || []);
      }
    } catch (err) {
      console.error("Failed to fetch dispatches:", err);
    } finally {
      setRecsLoading(false);
    }
  }, []);

  // ─── Phase 7C: Fetch active dispatches ───────────────────────────────────
  const fetchActiveDispatches = useCallback(async () => {
    try {
      const res = await getActiveDispatches();
      if (res.status === 'success') {
        setActiveDispatches(res.dispatches || []);
        return res.dispatches || [];
      }
    } catch (err) {
      console.error("Failed to fetch active dispatches:", err);
    }
    return [];
  }, []);

  // ─── Phase 7C: Start simulation for a single dispatch ────────────────────
  const startSimulation = useCallback((dispatch) => {
    const patrolId = dispatch.patrol_id;

    // Prevent duplicate intervals for the same patrol
    if (simulationIntervals.current.has(patrolId)) {
      return;
    }

    const geometry = dispatch.route_geometry;
    if (!geometry || geometry.length === 0) {
      console.warn(`[SimGPS] No route geometry for patrol ${patrolId}`);
      return;
    }

    let currentStep = dispatch.current_index || 0;
    const totalPoints = dispatch.total_points || geometry.length;

    // Initialize sim state
    const coord = geometry[currentStep];
    setSimState(prev => ({
      ...prev,
      [patrolId]: {
        stepIndex: currentStep,
        position: { lat: coord[0], lng: coord[1] },
        progressPct: totalPoints > 1 ? Math.round((currentStep / (totalPoints - 1)) * 100) : 100,
        simulatedEta: dispatch.eta_minutes || 0,
        totalPoints,
        routeGeometry: geometry,
        hotspotId: dispatch.hotspot_id,
        distanceKm: dispatch.distance_km,
        originalEta: dispatch.eta_minutes,
      }
    }));

    // Set interval
    const intervalId = setInterval(async () => {
      currentStep += 1;

      if (currentStep >= totalPoints) {
        // Arrived — clear interval, notify backend
        clearInterval(intervalId);
        simulationIntervals.current.delete(patrolId);

        try {
          await notifyArrival(patrolId);
          console.log(`[SimGPS] Patrol ${patrolId} ARRIVED at destination.`);
        } catch (err) {
          console.error(`[SimGPS] Arrival notification failed for ${patrolId}:`, err);
        }

        // Remove from sim state
        setSimState(prev => {
          const next = { ...prev };
          delete next[patrolId];
          return next;
        });

        // Refresh all data
        refreshData();
        fetchRecs();
        fetchActiveDispatches();
        return;
      }

      // Update position on backend
      try {
        const res = await updatePatrolPosition(patrolId, currentStep);
        if (res.status === 'success') {
          setSimState(prev => ({
            ...prev,
            [patrolId]: {
              ...prev[patrolId],
              stepIndex: currentStep,
              position: res.position,
              progressPct: res.progress_pct,
              simulatedEta: res.simulated_eta_minutes,
            }
          }));
        }
      } catch (err) {
        console.error(`[SimGPS] Position update failed for ${patrolId}:`, err);
        // Stop simulation on persistent error
        clearInterval(intervalId);
        simulationIntervals.current.delete(patrolId);
      }
    }, SIM_TICK_MS);

    simulationIntervals.current.set(patrolId, intervalId);
    console.log(`[SimGPS] Simulation started for patrol ${patrolId} at step ${currentStep}/${totalPoints}`);
  }, [refreshData, fetchRecs, fetchActiveDispatches]);

  // ─── Phase 7C: Auto-resume simulations on mount / after refresh ──────────
  useEffect(() => {
    if (loading) return;

    const initSimulations = async () => {
      const dispatches = await fetchActiveDispatches();
      dispatches.forEach(d => {
        if (d.status === 'Responding' && !simulationIntervals.current.has(d.patrol_id)) {
          startSimulation(d);
        }
      });
    };

    initSimulations();
  }, [loading, fetchActiveDispatches, startSimulation]);

  // ─── Cleanup all simulation intervals on unmount ─────────────────────────
  useEffect(() => {
    return () => {
      simulationIntervals.current.forEach((intervalId) => {
        clearInterval(intervalId);
      });
      simulationIntervals.current.clear();
    };
  }, []);

  // Fetch recommendations on mount or when dashboard refreshes
  useEffect(() => {
    if (!loading) {
      fetchRecs();
    }
  }, [loading, fetchRecs]);

  if (loading) return <div>Loading...</div>;

  const handleGenerateRoute = async () => {
    if (!selectedUnit || !selectedHotspot) return;
    setGeneratingRoute(true);
    setRouteError(null);
    setDynamicRoute(null);
    try {
      const data = await generateDynamicRoute(selectedUnit, selectedHotspot);
      if (data.status === 'success') {
        setDynamicRoute(data);
      } else {
        setRouteError(data.message || 'Routing failure');
      }
    } catch (err) {
      setRouteError(err.response?.data?.message || err.message || 'OSRM service error');
    } finally {
      setGeneratingRoute(false);
    }
  };

  const handleCommanderDispatch = async (hotspotId, patrolId) => {
    if (!hotspotId || !patrolId) return;
    setDispatchStatus(prev => ({ ...prev, [hotspotId]: 'loading' }));
    setDispatchMsg('');
    try {
      const res = await executeDispatch(hotspotId, patrolId);
      if (res.status === 'success') {
        setDispatchStatus(prev => ({ ...prev, [hotspotId]: 'success' }));
        // Plot returned OSRM route immediately on map
        setDynamicRoute(res);
        setDispatchMsg(`Dispatch confirmed! Unit ${patrolId} responding to Hotspot ${hotspotId}. Simulated tracking active.`);
        // Refresh full platform data
        await refreshData();
        // Refresh recommendations
        await fetchRecs();
        // Phase 7C: Fetch and start simulation for the new dispatch
        const dispatches = await fetchActiveDispatches();
        const newDispatch = dispatches.find(d => d.patrol_id === patrolId && d.status === 'Responding');
        if (newDispatch) {
          startSimulation(newDispatch);
        }
      }
    } catch (err) {
      const status = err.response?.status;
      const msg = err.response?.data?.message || 'Dispatch action failed.';
      if (status === 409) {
        setDispatchStatus(prev => ({ ...prev, [hotspotId]: 'conflict' }));
        setDispatchMsg(`Race Condition: ${msg}`);
        // Auto-refresh recommendations to clear stale unit options
        refreshData();
        fetchRecs();
      } else {
        setDispatchStatus(prev => ({ ...prev, [hotspotId]: 'error' }));
        setDispatchMsg(msg);
      }
    }
  };

  const activeRoute = routes.find(r => r.id === selectedRoute);

  // Check if any simulations are active
  const activeSims = Object.keys(simState);
  const hasActiveSim = activeSims.length > 0;

  // Stats bar calculations — show simulation info if active
  const primarySim = hasActiveSim ? simState[activeSims[0]] : null;
  
  const displayRouteName = hasActiveSim
    ? `Simulated Tracking: ${activeSims[0]} → ${primarySim?.hotspotId || '?'}`
    : dynamicRoute 
      ? `Dynamic Road Route: ${dynamicRoute.patrol_id} → ${dynamicRoute.hotspot_id}`
      : (activeRoute ? activeRoute.name : 'No Route Selected');

  const displayDistance = hasActiveSim
    ? `${primarySim?.distanceKm || '—'} km`
    : dynamicRoute 
      ? `${dynamicRoute.distance_km} km`
      : (activeRoute ? `${activeRoute.distance_km} km` : '—');

  const displayETA = hasActiveSim
    ? `~${primarySim?.simulatedEta || 0} min`
    : dynamicRoute 
      ? `${dynamicRoute.eta_minutes} min`
      : (activeRoute ? `${activeRoute.eta_minutes} min` : '—');

  const displayCoverage = hasActiveSim
    ? `Progress: ${primarySim?.progressPct || 0}%`
    : dynamicRoute 
      ? 'Dynamic Road Route'
      : (activeRoute ? activeRoute.coverage : '—');

  const displayColor = hasActiveSim ? '#FF6D00' : dynamicRoute ? '#00D4FF' : (activeRoute ? activeRoute.color : '#7A9BB5');

  return (
    <div className="flex h-full overflow-hidden page-enter" style={{ background: '#060d1a' }}>

      {/* Left: Controls */}
      <div className="flex-shrink-0 flex flex-col overflow-hidden panel-surface"
        style={{ width: 280, borderRight: '1px solid rgba(0,212,255,0.06)' }}>

        {/* Tabs */}
        <div className="flex border-b" style={{ borderColor: 'rgba(0,212,255,0.06)' }}>
          {[
            { key: 'dispatch', label: 'DISPATCH' },
            { key: 'units', label: 'PATROL UNITS' },
            { key: 'routes', label: 'PATROL ROUTES' },
          ].map(tab => (
            <button key={tab.key} onClick={() => {
              setActiveTab(tab.key);
              // Clear route views on reset
              if (!hasActiveSim) {
                setDynamicRoute(null);
              }
              setRouteError(null);
              setDispatchMsg('');
            }}
              className="flex-1 py-2.5 text-center"
              style={{
                fontSize: 8, fontFamily: 'Orbitron', letterSpacing: '0.05em',
                color: activeTab === tab.key ? 'var(--electric)' : 'var(--text-muted)',
                borderBottom: activeTab === tab.key ? '2px solid var(--electric)' : '2px solid transparent',
                background: activeTab === tab.key ? 'rgba(0,212,255,0.04)' : 'transparent',
              }}>
              {tab.label}
            </button>
          ))}
        </div>

        <div className="flex-1 overflow-y-auto p-3">
          
          {/* TAB 1: Dispatch Recommendations */}
          {activeTab === 'dispatch' && (
            <>
              <div className="section-header mb-3">PATROL DISPATCH RECOMMENDATIONS</div>

              {/* Phase 7C: Active Simulations Status */}
              {hasActiveSim && (
                <div className="intel-card p-3 mb-3 rounded" style={{
                  border: '1px solid rgba(255, 109, 0, 0.25)',
                  background: 'rgba(255, 109, 0, 0.04)'
                }}>
                  <div style={{ fontSize: 8, fontFamily: 'Orbitron', color: '#FF6D00', letterSpacing: '0.08em', marginBottom: 6 }}>
                    🚔 SIMULATED GPS TRACKING
                  </div>
                  {activeSims.map(patrolId => {
                    const sim = simState[patrolId];
                    return (
                      <div key={patrolId} style={{
                        background: 'rgba(0,0,0,0.3)', padding: 8, borderRadius: 4, marginBottom: 4
                      }}>
                        <div className="flex justify-between items-center">
                          <span style={{ color: '#FF6D00', fontFamily: 'Orbitron', fontSize: 10, fontWeight: 700 }}>
                            {patrolId}
                          </span>
                          <span style={{ color: '#00E676', fontSize: 9, fontFamily: 'JetBrains Mono' }}>
                            {sim.progressPct}%
                          </span>
                        </div>
                        <div style={{ color: 'var(--text-muted)', fontSize: 9, marginTop: 2 }}>
                          → {sim.hotspotId} | Simulated ETA: ~{sim.simulatedEta} min
                        </div>
                        {/* Progress bar */}
                        <div style={{
                          marginTop: 4, height: 3, borderRadius: 2,
                          background: 'rgba(255,255,255,0.08)',
                        }}>
                          <div style={{
                            width: `${sim.progressPct}%`, height: '100%', borderRadius: 2,
                            background: 'linear-gradient(90deg, #FF6D00, #00E676)',
                            transition: 'width 1s ease-out'
                          }} />
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}

              {recsLoading && recs.length === 0 ? (
                <div style={{ padding: 12, color: 'var(--text-muted)', fontSize: 11 }}>Calculating recommendations...</div>
              ) : recs.length === 0 ? (
                <div style={{ padding: 12, color: 'var(--text-muted)', fontSize: 11 }}>No active High/Critical hotspots found.</div>
              ) : (
                recs.map(rec => {
                  const state = dispatchStatus[rec.hotspot_id] || 'idle';
                  const isDispatched = rec.dispatched;
                  const unit = rec.recommended_unit;
                  // Check if there's an active sim for this dispatched unit
                  const dispatchSim = isDispatched && rec.assigned_patrol_id ? simState[rec.assigned_patrol_id] : null;

                  return (
                    <div key={rec.hotspot_id} className="intel-card p-3 mb-3 rounded" style={{
                      border: isDispatched 
                        ? '1px solid rgba(0, 230, 118, 0.15)' 
                        : '1px solid rgba(255, 255, 255, 0.05)',
                      background: isDispatched ? 'rgba(0, 230, 118, 0.02)' : 'rgba(0,0,0,0.1)'
                    }}>
                      <div className="flex justify-between items-center mb-1">
                        <span style={{ fontFamily: 'Orbitron', fontSize: 10, fontWeight: 700, color: rec.risk === 'Critical' ? '#FF1744' : '#FF6D00' }}>
                          {rec.risk} HOTSPOT
                        </span>
                        <span style={{ fontSize: 9, color: 'var(--text-muted)', fontFamily: 'JetBrains Mono' }}>
                          Score: {rec.score}
                        </span>
                      </div>
                      
                      <div style={{ color: '#E8F4FD', fontSize: 12, fontWeight: 600 }}>Area: {rec.area}</div>
                      <div style={{ fontSize: 10, color: 'var(--text-muted)', marginBottom: 8 }}>
                        Clustered Crimes: {rec.crimes}
                      </div>

                      <div style={{ background: 'rgba(0,0,0,0.3)', padding: 6, borderRadius: 4, marginBottom: 8 }}>
                        {isDispatched ? (
                          <div>
                            <div className="flex items-center gap-1.5" style={{ color: '#00E676', fontSize: 10, fontWeight: 600 }}>
                              <CheckCircle2 size={12} />
                              Dispatched: Unit {rec.assigned_patrol_id}
                            </div>
                            {/* Show simulation progress if available */}
                            {dispatchSim && (
                              <div style={{ marginTop: 4, fontSize: 9, color: '#FF6D00' }}>
                                🚔 En Route — {dispatchSim.progressPct}% | ~{dispatchSim.simulatedEta} min
                              </div>
                            )}
                          </div>
                        ) : unit ? (
                          <div>
                            <div style={{ fontSize: 8, color: 'var(--text-muted)', fontFamily: 'Orbitron', letterSpacing: '0.05em' }}>RECOMMENDED PATROL</div>
                            <div style={{ color: '#E8F4FD', fontSize: 10, fontWeight: 500 }}>
                              {unit.vehicle_id} ({unit.officer_name})
                            </div>
                            <div style={{ color: 'var(--text-muted)', fontSize: 9 }}>
                              {unit.vehicle_type} · Distance: <strong style={{ color: 'var(--electric)' }}>{unit.distance_km} km</strong>
                            </div>
                          </div>
                        ) : (
                          <div style={{ color: '#FF1744', fontSize: 9 }}>
                            No patrol units available in network.
                          </div>
                        )}
                      </div>

                      {!isDispatched && unit && (
                        <button
                          onClick={() => handleCommanderDispatch(rec.hotspot_id, unit.vehicle_id)}
                          disabled={state === 'loading' || state === 'success'}
                          className="w-full py-1.5 rounded text-xs font-orbitron transition-all"
                          style={{
                            background: state === 'loading' ? 'rgba(0,212,255,0.04)' : 'linear-gradient(135deg, #0052cc, #0084ff)',
                            border: '1px solid rgba(0,212,255,0.2)',
                            color: '#fff',
                            cursor: (state === 'loading' || state === 'success') ? 'not-allowed' : 'pointer'
                          }}
                        >
                          {state === 'loading' ? 'DISPATCHING...' :
                           state === 'success' ? 'DISPATCHED' :
                           state === 'conflict' ? 'UNIT NO LONGER AVAILABLE' :
                           'DISPATCH PATROL'}
                        </button>
                      )}
                    </div>
                  );
                })
              )}

              {dispatchMsg && (
                <div className="intel-card p-3 rounded" style={{
                  border: dispatchMsg.includes('Dispatch') ? '1px solid rgba(0,230,118,0.2)' : '1px solid rgba(255,23,68,0.3)',
                  background: dispatchMsg.includes('Dispatch') ? 'rgba(0,230,118,0.04)' : 'rgba(255,23,68,0.04)',
                  fontSize: 10, color: dispatchMsg.includes('Dispatch') ? '#00E676' : '#FF1744',
                  lineHeight: 1.4
                }}>
                  {dispatchMsg}
                </div>
              )}
            </>
          )}

          {/* TAB 2: Active Units */}
          {activeTab === 'units' && (
            <>
              <div className="section-header mb-3">ACTIVE UNITS ({patrols.length})</div>
              <div style={{ maxHeight: 280, overflowY: 'auto' }}>
                {patrols.slice(0, 12).map(unit => (
                  <UnitCard 
                    key={unit.vehicle_id} 
                    unit={unit} 
                    isActive={selectedUnit === unit.vehicle_id}
                    onSelect={(id) => {
                      setSelectedUnit(id);
                      setDynamicRoute(null);
                      setRouteError(null);
                      
                      const assignedAlert = alerts.find(a => a.assigned_to === id);
                      if (assignedAlert) {
                        const matchedHs = hotspots.find(h => h.name.toLowerCase().includes(assignedAlert.area.toLowerCase()));
                        if (matchedHs) {
                          setSelectedHotspot(matchedHs.id);
                          return;
                        }
                      }
                      if (hotspots.length > 0) {
                        setSelectedHotspot(hotspots[0].id);
                      }
                    }}
                  />
                ))}
              </div>

              {selectedUnit && (
                <div className="intel-card p-3 mt-3 rounded" style={{ border: '1px solid rgba(0, 212, 255, 0.15)' }}>
                  <div className="section-header mb-2" style={{ color: 'var(--electric)' }}>DISPATCH ROUTING</div>
                  <div style={{ color: 'var(--text-muted)', fontSize: 10, marginBottom: 8 }}>
                    Calculate a Dynamic Road Route from <strong>{selectedUnit}</strong>:
                  </div>

                  <div className="mb-3">
                    <label style={{ display: 'block', fontSize: 8, color: 'var(--text-muted)', marginBottom: 2, fontFamily: 'Orbitron' }}>TARGET HOTSPOT</label>
                    <select
                      value={selectedHotspot}
                      onChange={(e) => {
                        setSelectedHotspot(e.target.value);
                        setDynamicRoute(null);
                        setRouteError(null);
                      }}
                      className="cmd-input w-full px-2 py-1 text-xs"
                      style={{ background: 'rgba(0,0,0,0.3)', border: '1px solid rgba(0,212,255,0.15)', color: '#E8F4FD' }}
                    >
                      <option value="" disabled>Select Target Hotspot</option>
                      {hotspots.map(h => (
                        <option key={h.id} value={h.id}>
                          {h.id} — {h.name} ({h.risk})
                        </option>
                      ))}
                    </select>
                  </div>

                  <button
                    onClick={handleGenerateRoute}
                    disabled={generatingRoute || !selectedHotspot}
                    className="w-full py-2 rounded text-xs font-orbitron transition-all"
                    style={{
                      background: 'rgba(0, 212, 255, 0.08)',
                      border: '1px solid rgba(0, 212, 255, 0.3)',
                      color: 'var(--electric)',
                      cursor: (generatingRoute || !selectedHotspot) ? 'not-allowed' : 'pointer'
                    }}
                  >
                    {generatingRoute ? 'GENERATING...' : 'GENERATE ROAD ROUTE'}
                  </button>

                  {routeError && (
                    <div style={{ marginTop: 8, padding: 8, background: 'rgba(255,23,68,0.1)', border: '1px solid rgba(255,23,68,0.3)', borderRadius: 4, color: '#FF1744', fontSize: 10 }}>
                      ⚠️ {routeError}
                    </div>
                  )}
                </div>
              )}
            </>
          )}

          {/* TAB 3: Predefined Routes */}
          {activeTab === 'routes' && (
            <>
              <div className="section-header mb-3">AI-OPTIMIZED ROUTES</div>
              {routes.map(route => (
                <RouteCard key={route.id} route={route}
                  isActive={selectedRoute === route.id && !dynamicRoute}
                  onSelect={(id) => {
                    setSelectedRoute(id);
                    setDynamicRoute(null);
                    setRouteError(null);
                  }} />
              ))}

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
          )}
        </div>
      </div>

      {/* Right: Map */}
      <div className="flex-1 flex flex-col min-w-0">
        
        {/* Stats strip */}
        <div className="flex-shrink-0 flex items-center gap-6 px-4 py-2 border-b"
          style={{ borderColor: 'rgba(0,212,255,0.06)', background: 'rgba(6,13,26,0.98)' }}>
          {[
            { icon: Navigation, label: 'Route', value: displayRouteName, color: displayColor },
            { icon: MapPin, label: 'Distance', value: displayDistance, color: '#00D4FF' },
            { icon: Clock, label: hasActiveSim ? 'Sim. ETA' : 'Est. Time', value: displayETA, color: '#00E676' },
            { icon: Activity, label: hasActiveSim ? 'Progress' : 'Coverage', value: displayCoverage, color: '#FFD600' },
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
            <span style={{ color: hasActiveSim ? '#FF6D00' : '#00E676', fontSize: 9, fontFamily: 'JetBrains Mono' }}>
              {hasActiveSim ? 'SIMULATED GPS TRACKING' : dynamicRoute ? 'DYNAMIC ROUTE ACTIVE' : 'SIMULATED TRACKING'}
            </span>
          </div>
        </div>

        {/* Leaflet Map */}
        <div className="flex-1 relative">
          <MapContainer center={[23.0225, 72.5714]} zoom={12}
            style={{ width: '100%', height: '100%', background: '#040810' }}>
            <MapResize />
            <TileLayer url={DARK_TILES} attribution="" />

            {/* Hotspots */}
            {hotspots.map(hs => (
              <CircleMarker key={hs.id} center={[hs.lat, hs.lng]}
                radius={hs.radius / 70}
                fillColor={hs.risk === 'Critical' ? '#FF1744' : hs.risk === 'High' ? '#FF6D00' : '#FFD600'}
                fillOpacity={0.1}
                color={hs.risk === 'Critical' ? '#FF1744' : hs.risk === 'High' ? '#FF6D00' : '#FFD600'}
                opacity={0.4} weight={1.5} />
            ))}

            {/* Dim predefined routes if dynamicRoute or simulation is active */}
            {!dynamicRoute && !hasActiveSim && routes.map(route => (
              <Polyline key={route.id}
                positions={route.waypoints.map(wp => [wp.lat, wp.lng])}
                color={route.color}
                opacity={route.id === selectedRoute ? 0.9 : 0.25}
                weight={route.id === selectedRoute ? 4 : 2}
                dashArray={route.id === selectedRoute ? undefined : '6, 4'} />
            ))}

            {/* Render OSRM Road Route (static, no simulation) */}
            {dynamicRoute && !hasActiveSim && (
              <Polyline 
                positions={dynamicRoute.waypoints}
                color="#00D4FF"
                opacity={0.9}
                weight={5}
              />
            )}

            {/* Phase 7C: Render simulation routes and moving markers */}
            {activeSims.map(patrolId => {
              const sim = simState[patrolId];
              if (!sim || !sim.routeGeometry) return null;

              const traversed = sim.routeGeometry.slice(0, sim.stepIndex + 1);
              const remaining = sim.routeGeometry.slice(sim.stepIndex);

              return (
                <React.Fragment key={`sim-${patrolId}`}>
                  {/* Traversed portion — dimmed */}
                  {traversed.length > 1 && (
                    <Polyline
                      positions={traversed}
                      color="#4A6580"
                      opacity={0.4}
                      weight={4}
                    />
                  )}
                  {/* Remaining portion — bright */}
                  {remaining.length > 1 && (
                    <Polyline
                      positions={remaining}
                      color="#FF6D00"
                      opacity={0.9}
                      weight={5}
                    />
                  )}
                  {/* Origin marker */}
                  <CircleMarker
                    center={sim.routeGeometry[0]}
                    radius={6}
                    fillColor="#00E676"
                    fillOpacity={0.8}
                    color="#fff"
                    weight={2}
                  >
                    <Popup>
                      <div style={{ fontSize: 11, fontFamily: 'Inter' }}>
                        <strong style={{ color: '#00E676', fontFamily: 'Orbitron' }}>PATROL ORIGIN</strong>
                        <div>Unit: {patrolId}</div>
                      </div>
                    </Popup>
                  </CircleMarker>
                  {/* Destination marker */}
                  <CircleMarker
                    center={sim.routeGeometry[sim.routeGeometry.length - 1]}
                    radius={6}
                    fillColor="#FF1744"
                    fillOpacity={0.8}
                    color="#fff"
                    weight={2}
                  >
                    <Popup>
                      <div style={{ fontSize: 11, fontFamily: 'Inter' }}>
                        <strong style={{ color: '#FF1744', fontFamily: 'Orbitron' }}>HOTSPOT DESTINATION</strong>
                        <div>Hotspot: {sim.hotspotId}</div>
                      </div>
                    </Popup>
                  </CircleMarker>
                  {/* Moving patrol marker — pulsing */}
                  <CircleMarker
                    center={[sim.position.lat, sim.position.lng]}
                    radius={10}
                    fillColor="#FF6D00"
                    fillOpacity={1}
                    color="#FFD600"
                    opacity={0.9}
                    weight={3}
                  >
                    <Popup>
                      <div style={{ fontFamily: 'Inter', fontSize: 11, minWidth: 180 }}>
                        <div style={{ color: '#FF6D00', fontFamily: 'Orbitron', fontSize: 10, fontWeight: 700, marginBottom: 4 }}>
                          🚔 {patrolId}
                        </div>
                        <div style={{ color: '#E8F4FD', lineHeight: 1.6 }}>
                          <div>Status: <strong style={{ color: '#FF6D00' }}>RESPONDING</strong></div>
                          <div>Destination: <strong>{sim.hotspotId}</strong></div>
                          <div>Progress: <strong style={{ color: '#00E676' }}>{sim.progressPct}%</strong></div>
                          <div>Simulated ETA: <strong style={{ color: '#00D4FF' }}>~{sim.simulatedEta} min</strong></div>
                        </div>
                        <div style={{ marginTop: 6, fontSize: 8, color: '#7BA7C4', fontStyle: 'italic' }}>
                          ⚠ Simulated GPS — Route from OSRM/OpenStreetMap
                        </div>
                      </div>
                    </Popup>
                  </CircleMarker>
                </React.Fragment>
              );
            })}

            {/* Dispatch Origin / Destination markers (when no simulation active) */}
            {dynamicRoute && !hasActiveSim && (
              <>
                <CircleMarker
                  center={dynamicRoute.waypoints[0]}
                  radius={7}
                  fillColor="#00E676"
                  fillOpacity={1}
                  color="#fff"
                  weight={2}
                >
                  <Popup>
                    <div style={{ fontSize: 11, fontFamily: 'Inter' }}>
                      <strong style={{ color: '#00E676', fontFamily: 'Orbitron' }}>PATROL ORIGIN</strong>
                      <div>Unit: {dynamicRoute.patrol_id}</div>
                    </div>
                  </Popup>
                </CircleMarker>

                <CircleMarker
                  center={dynamicRoute.waypoints[dynamicRoute.waypoints.length - 1]}
                  radius={7}
                  fillColor="#FF1744"
                  fillOpacity={1}
                  color="#fff"
                  weight={2}
                >
                  <Popup>
                    <div style={{ fontSize: 11, fontFamily: 'Inter' }}>
                      <strong style={{ color: '#FF1744', fontFamily: 'Orbitron' }}>HOTSPOT DESTINATION</strong>
                      <div>Hotspot: {dynamicRoute.hotspot_id}</div>
                    </div>
                  </Popup>
                </CircleMarker>
              </>
            )}

            {/* Route Waypoints (predefined routes only, no sim, no dynamic) */}
            {!dynamicRoute && !hasActiveSim && activeRoute && activeRoute.waypoints.map((wp, i) => (
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

            {/* Patrol Units (non-simulated ones) */}
            {patrols.filter(u => u.status !== 'At Station').filter(u => !simState[u.vehicle_id]).map(unit => (
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
            {hasActiveSim ? (
              <>
                <div className="flex items-center gap-2 mb-1">
                  <div className="w-6 h-1 rounded" style={{ background: '#FF6D00' }} />
                  <span style={{ color: '#FF6D00', fontSize: 10, fontWeight: 'bold' }}>Remaining Route</span>
                </div>
                <div className="flex items-center gap-2 mb-1">
                  <div className="w-6 h-1 rounded" style={{ background: '#4A6580' }} />
                  <span style={{ color: '#4A6580', fontSize: 10 }}>Traversed Route</span>
                </div>
                <div className="flex items-center gap-2 mb-1">
                  <div className="w-3 h-3 rounded-full" style={{ background: '#FF6D00', border: '2px solid #FFD600' }} />
                  <span style={{ color: '#FF6D00', fontSize: 10, fontWeight: 'bold' }}>Moving Patrol</span>
                </div>
              </>
            ) : !dynamicRoute ? routes.map(r => (
              <div key={r.id} className="flex items-center gap-2 mb-1">
                <div className="w-6 h-1 rounded" style={{ background: r.color, opacity: r.id === selectedRoute ? 1 : 0.35 }} />
                <span style={{ color: 'var(--text-secondary)', fontSize: 10 }}>{r.name.slice(0, 18)}...</span>
              </div>
            )) : (
              <div className="flex items-center gap-2 mb-1">
                <div className="w-6 h-1 rounded animate-pulse" style={{ background: '#00D4FF' }} />
                <span style={{ color: '#00D4FF', fontSize: 10, fontWeight: 'bold' }}>Dynamic Road Route</span>
              </div>
            )}
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
