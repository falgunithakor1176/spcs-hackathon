import React, { useState } from 'react';
import CommandMap from '../components/map/CommandMap';
import LeftPanel from '../components/panels/LeftPanel';
import RightPanel from '../components/panels/RightPanel';
import BottomPanel from '../components/charts/BottomPanel';
import StatCard from '../components/widgets/StatCard';
import MLEngineButton from '../components/widgets/MLEngineButton';
import {
  AlertTriangle, Shield, Activity, Truck, Globe,
  Layers, ChevronDown, ChevronUp
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
  const { crimes, cybercrime, patrols, hotspots, loading, riskIndex } = useData();

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
          <StatCard icon={AlertTriangle} label="Total Crimes" value={dashboardStats.total_crimes?.toLocaleString() || '0'}
            sub={`+${dashboardStats.crimes_today} today`} trend="up" trendValue="+3.2%" color="#FF1744" />
          <StatCard icon={Activity} label="Active Hotspots" value={dashboardStats.active_hotspots || '0'}
            sub={`${dashboardStats.high_risk_areas} critical zones`} trend="up" trendValue="+2" color="#FF6D00" />
          <StatCard icon={Shield} label="Risk Index" value={`${dashboardStats.risk_index || '0'}`}
            sub="City-wide average" trend="up" trendValue="+5pts" color="#FFD600" />
          <StatCard icon={Truck} label="Patrol Units" value={`${dashboardStats.active_patrols || 0}/${dashboardStats.total_patrols || 0}`}
            sub="On patrol / Total" trend="down" trendValue="-2" color="#00D4FF" />
          <StatCard icon={Globe} label="Cyber Threats" value={dashboardStats.cybercrime_reports?.toLocaleString() || '0'}
            sub={`+${dashboardStats.cyber_today} today`} trend="up" trendValue="+1.8%" color="#A78BFA" />
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

        {/* Right Panel */}
        <RightPanel />
      </div>
    </div>
  );
}
