import React, { useState } from 'react';
import CommandMap from '../components/map/CommandMap';
import LeftPanel from '../components/panels/LeftPanel';
import RightPanel from '../components/panels/RightPanel';
import ForecastPanel from '../components/panels/ForecastPanel';
import BottomPanel from '../components/charts/BottomPanel';
import StatCard from '../components/widgets/StatCard';
import MLEngineButton from '../components/widgets/MLEngineButton';
import {
  AlertTriangle, Shield, Activity, Truck, Globe,
  Layers, ChevronDown, ChevronUp, TrendingUp
} from 'lucide-react';
import { useData } from '../context/DataContext';
import { getDashboardStats } from '../data/analyticsUtils';

const LAYER_DEFAULTS = {
  crimes: true, hotspots: true, patrol: true, routes: false, riskZones: true,
};

export default function CommandCenter() {
  const [filters, setFilters] = useState({});
  const [layers, setLayers] = useState(LAYER_DEFAULTS);
  const [bottomExpanded, setBottomExpanded] = useState(true);
  const [rightTab, setRightTab] = useState('live'); // 'live' | 'forecast'
  const { crimes, cybercrime, patrols, hotspots, areaIntelligence, loading, riskIndex } = useData();

  // Compute next-month high+critical area count from Engine 3
  const forecastHighCount = (areaIntelligence || []).filter(
    r => r.combined_risk === 'Critical' || r.combined_risk === 'High'
  ).length;

  const toggleLayer = (key) => setLayers(prev => ({ ...prev, [key]: !prev[key] }));

  if (loading) {
    return <div className="flex h-full items-center justify-center text-electric">Loading Command Center Data...</div>;
  }

  const dashboardStats = getDashboardStats(crimes, cybercrime, patrols, hotspots, riskIndex);

  return (
    <div className="flex flex-col h-full overflow-hidden" style={{ background: '#060d1a' }}>

      {/* KPI Stats Strip */}
      <div className="flex-shrink-0 flex items-center gap-2 px-3 py-2 border-b"
        style={{ borderColor: 'rgba(0,212,255,0.06)', background: 'rgba(6,13,26,0.98)' }}>
        <div className="flex gap-2 flex-1 min-w-0 overflow-x-auto pb-1">
          {/* Total Crimes — trend calculated from real 30d vs prev-30d window */}
          <StatCard icon={AlertTriangle} label="Total Crimes" value={dashboardStats.total_crimes?.toLocaleString() || '0'}
            sub={`${dashboardStats.crimes_30d} in last 30 days`}
            trend={dashboardStats.crimes_trend ? (dashboardStats.crimes_trend.startsWith('+') ? 'up' : 'down') : undefined}
            trendValue={dashboardStats.crimes_trend || undefined}
            color="#FF1744" />
          {/* Active Hotspots — no trend badge; hotspot table is truncated on every ML run */}
          <StatCard icon={Activity} label="Active Hotspots" value={dashboardStats.active_hotspots || '0'}
            sub={`${dashboardStats.high_risk_areas} high/critical zones`}
            color="#FF6D00" />
          {/* Risk Index — no trend badge; no historical index snapshots stored */}
          <StatCard icon={Shield} label="Risk Index" value={`${dashboardStats.risk_index || '0'}`}
            sub={`Computed from ${dashboardStats.active_hotspots} hotspots`}
            color="#FFD600" />
          {/* Patrol Units — responding count is a real operational metric */}
          <StatCard icon={Truck} label="Patrol Units" value={`${dashboardStats.active_patrols || 0}/${dashboardStats.total_patrols || 0}`}
            sub={`${dashboardStats.responding_patrols || 0} currently responding`}
            trend={dashboardStats.responding_patrols > 0 ? 'up' : undefined}
            trendValue={dashboardStats.responding_patrols > 0 ? `${dashboardStats.responding_patrols} active` : undefined}
            color="#00D4FF" />
          {/* Cyber Threats — trend calculated from real 30d vs prev-30d window */}
          <StatCard icon={Globe} label="Cyber Threats" value={dashboardStats.cybercrime_reports?.toLocaleString() || '0'}
            sub={`${dashboardStats.cyber_30d} in last 30 days`}
            trend={dashboardStats.cyber_trend ? (dashboardStats.cyber_trend.startsWith('+') ? 'up' : 'down') : undefined}
            trendValue={dashboardStats.cyber_trend || undefined}
            color="#A78BFA" />
          {/* Future Risk — Engine 3 next-month forecast */}
          <StatCard icon={TrendingUp} label="Future Risk" value={`${forecastHighCount}`}
            sub="High/Critical areas next month"
            trend={forecastHighCount > 0 ? 'up' : undefined}
            trendValue={forecastHighCount > 0 ? `${forecastHighCount} areas` : undefined}
            color="#FF6D00" />

        </div>

        {/* ML Engine Button */}
        <div className="flex-shrink-0 ml-2 pl-2 border-l border-electric/10">
          <MLEngineButton />
        </div>

        {/* Layer Controls */}
        <div className="flex-shrink-0 flex items-center gap-1 ml-2 pl-2 border-l border-electric/10">
          <Layers size={12} style={{ color: 'var(--electric)' }} />
          {Object.entries(layers).map(([key, active]) => (
            <button
              key={key}
              onClick={() => toggleLayer(key)}
              className="layer-btn px-2 py-1"
              style={{
                fontSize: 9, minWidth: 'auto', padding: '3px 8px',
                background: active ? 'rgba(0,212,255,0.08)' : 'transparent',
                borderColor: active ? 'rgba(0,212,255,0.25)' : 'rgba(0,212,255,0.08)',
                color: active ? 'var(--electric)' : 'var(--text-muted)',
              }}>
              {key === 'riskZones' ? 'Zones' : key.charAt(0).toUpperCase() + key.slice(1)}
            </button>
          ))}
        </div>
      </div>

      {/* Main 3-Column Area */}
      <div className="flex flex-1 min-h-0 overflow-hidden">
        {/* Left Panel */}
        <LeftPanel onFilterChange={setFilters} />

        {/* Center: Map + Bottom Panel */}
        <div className="flex flex-col flex-1 min-w-0">
          {/* Map */}
          <div className="flex-1 relative overflow-hidden">
            <CommandMap layers={layers} filters={filters} />
          </div>

          {/* Bottom Panel Toggle */}
          <div className="flex-shrink-0">
            <button
              onClick={() => setBottomExpanded(e => !e)}
              className="w-full flex items-center justify-center gap-2 py-1 border-t border-b border-electric/08"
              style={{ background: 'rgba(6,13,26,0.95)', cursor: 'pointer' }}>
              <span style={{ fontSize: 9, color: 'var(--text-muted)', fontFamily: 'Orbitron', letterSpacing: '0.1em' }}>
                {bottomExpanded ? '▼ ANALYTICS' : '▲ ANALYTICS'}
              </span>
            </button>
            {bottomExpanded && <BottomPanel />}
          </div>
        </div>

        {/* Right Panel with tab switcher */}
        <div style={{ display: 'flex', flexDirection: 'column', height: '100%', borderLeft: '1px solid rgba(0,212,255,0.06)' }}>
          {/* Tab bar */}
          <div style={{
            display: 'flex', flexShrink: 0,
            borderBottom: '1px solid rgba(0,212,255,0.08)',
            background: 'rgba(6,13,26,0.98)',
          }}>
            {[['live', 'LIVE OPS'], ['forecast', 'FORECAST']].map(([key, label]) => (
              <button
                key={key}
                onClick={() => setRightTab(key)}
                style={{
                  flex: 1, padding: '6px 4px', fontSize: 9, fontFamily: 'Orbitron',
                  letterSpacing: '0.08em', cursor: 'pointer', border: 'none',
                  borderBottom: rightTab === key ? '2px solid var(--electric)' : '2px solid transparent',
                  background: 'transparent',
                  color: rightTab === key ? 'var(--electric)' : 'var(--text-muted)',
                  transition: 'all 0.2s',
                }}>
                {label}
              </button>
            ))}
          </div>
          {/* Panel content */}
          <div style={{ flex: 1, overflow: 'hidden', width: 290 }}>
            {rightTab === 'live' ? <RightPanel /> : <ForecastPanel />}
          </div>
        </div>
      </div>
    </div>
  );
}
