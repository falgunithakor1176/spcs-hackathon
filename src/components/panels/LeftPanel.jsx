import { useData } from '../../context/DataContext';
import { AREAS, CRIME_TYPES } from '../../data/mockData';
import { getCrimesByType, getCrimesByArea, getCrimesByMonth, getCrimesByHour, getCyberByType, getTotalAmountLost } from '../../data/analyticsUtils';
import React, { useState } from 'react';
import { AlertTriangle, Filter, Activity, ChevronDown } from 'lucide-react';

const SEVERITY_COLORS = {
  Critical: '#FF1744', High: '#FF6D00', Medium: '#FFD600', Low: '#00E676',
};

function SectionHeader({ icon: Icon, title, count }) {
  return (
    <div className="flex items-center justify-between mb-2 pb-2"
      style={{ borderBottom: '1px solid rgba(0,212,255,0.06)' }}>
      <div className="flex items-center gap-1.5">
        {Icon && <Icon size={12} style={{ color: 'var(--electric)' }} />}
        <span className="section-header">{title}</span>
      </div>
      {count !== undefined && (
        <span className="text-xs px-1.5 py-0.5 rounded font-mono-code"
          style={{ background: 'rgba(0,212,255,0.1)', color: 'var(--electric)', fontSize: 10 }}>
          {count}
        </span>
      )}
    </div>
  );
}

function IncidentRow({ crime, index }) {
  const color = SEVERITY_COLORS[crime.severity] || '#60A5FA';
  return (
    <div className="data-row flex items-start gap-2 py-2 px-1 cursor-pointer rounded-sm transition-all hover:px-2"
      style={{ animation: `fadeIn 0.3s ease-out ${index * 0.04}s both` }}>
      <div className="flex-shrink-0 mt-0.5 w-2 h-2 rounded-full"
        style={{ background: color, boxShadow: `0 0 4px ${color}`, marginTop: 4 }} />
      <div className="flex-1 min-w-0">
        <div className="flex items-center justify-between gap-1">
          <span className="text-xs font-medium truncate" style={{ color: '#E8F4FD' }}>
            {crime.crime_type}
          </span>
          <span className="text-xs flex-shrink-0 px-1 rounded"
            style={{ color, background: `${color}15`, fontSize: 9 }}>
            {crime.severity}
          </span>
        </div>
        <div className="text-xs truncate" style={{ color: 'var(--text-muted)', fontSize: 10 }}>
          📍 {crime.area}
        </div>
        <div style={{ color: 'var(--text-muted)', fontSize: 9 }}>
          {new Date(crime.timestamp).toLocaleString('en-IN', { day:'2-digit', month:'short', hour:'2-digit', minute:'2-digit' })}
        </div>
      </div>
    </div>
  );
}

function HotspotRow({ hs, index }) {
  const color = SEVERITY_COLORS[hs.risk] || '#FF6D00';
  return (
    <div className="data-row py-2 px-1 rounded-sm"
      style={{ animation: `fadeIn 0.3s ease-out ${index * 0.05}s both` }}>
      <div className="flex items-center justify-between mb-1">
        <span className="text-xs font-medium truncate" style={{ color: '#E8F4FD', maxWidth: '70%' }}>
          {hs.name}
        </span>
        <span className="text-xs font-bold font-orbitron" style={{ color }}>
          {hs.score}
        </span>
      </div>
      <div className="progress-track h-1 mb-1">
        <div className="progress-fill" style={{ width: `${hs.score}%`, background: `linear-gradient(90deg, ${color}80, ${color})` }} />
      </div>
      <div className="flex items-center justify-between">
        <span style={{ color: 'var(--text-muted)', fontSize: 9 }}>{hs.crimes} crimes</span>
        <span style={{
          color: hs.trend.startsWith('+') ? '#FF1744' : '#00E676',
          fontSize: 9, fontFamily: 'JetBrains Mono',
        }}>{hs.trend}</span>
      </div>
    </div>
  );
}

export default function LeftPanel({ onFilterChange }) {
  const { crimes, hotspots, patrols, routes, cybercrime, alerts, predictions, loading } = useData();
  if (loading) return <div>Loading...</div>;

  const [filters, setFilters] = useState({ crimeType: 'all', severity: 'all', area: 'all' });
  const [showFilters, setShowFilters] = useState(true);

  const handleFilter = (key, value) => {
    const updated = { ...filters, [key]: value };
    setFilters(updated);
    onFilterChange?.(updated);
  };

  return (
    <div className="flex flex-col h-full overflow-hidden panel-surface animate-slide-in-left"
      style={{ width: 272, borderRight: '1px solid rgba(0,212,255,0.06)' }}>

      {/* Active Incidents */}
      <div className="flex-shrink-0 p-3 border-b" style={{ borderColor: 'rgba(0,212,255,0.05)' }}>
        <SectionHeader icon={AlertTriangle} title="Active Incidents" count={crimes.slice(0, 20).length} />
        <div className="overflow-y-auto" style={{ maxHeight: 200 }}>
          {crimes.slice(0, 20).map((crime, i) => (
            <IncidentRow key={crime.crime_id} crime={crime} index={i} />
          ))}
        </div>
      </div>

      {/* Filters */}
      <div className="flex-shrink-0 p-3 border-b" style={{ borderColor: 'rgba(0,212,255,0.05)' }}>
        <div className="flex items-center justify-between mb-2">
          <SectionHeader icon={Filter} title="Crime Filters" />
          <button onClick={() => setShowFilters(s => !s)} className="text-electric">
            <ChevronDown size={12} style={{ transform: showFilters ? 'rotate(180deg)' : 'none', transition: 'transform 0.2s' }} />
          </button>
        </div>
        {showFilters && (
          <div className="space-y-2">
            {/* Crime Type */}
            <div>
              <label style={{ color: 'var(--text-muted)', fontSize: 10, display: 'block', marginBottom: 3 }}>
                CRIME TYPE
              </label>
              <select
                className="cmd-input w-full px-2 py-1.5 text-xs"
                value={filters.crimeType}
                onChange={e => handleFilter('crimeType', e.target.value)}
              >
                <option value="all">All Types</option>
                {CRIME_TYPES.map(t => <option key={t} value={t}>{t}</option>)}
              </select>
            </div>
            {/* Severity */}
            <div>
              <label style={{ color: 'var(--text-muted)', fontSize: 10, display: 'block', marginBottom: 3 }}>
                SEVERITY
              </label>
              <div className="flex gap-1">
                {['all', 'Critical', 'High', 'Medium', 'Low'].map(sev => (
                  <button
                    key={sev}
                    onClick={() => handleFilter('severity', sev)}
                    className="flex-1 py-1 rounded text-center"
                    style={{
                      fontSize: 9, border: '1px solid',
                      borderColor: filters.severity === sev ? (SEVERITY_COLORS[sev] || 'var(--electric)') : 'rgba(0,212,255,0.12)',
                      color: filters.severity === sev ? (SEVERITY_COLORS[sev] || 'var(--electric)') : 'var(--text-muted)',
                      background: filters.severity === sev ? `${(SEVERITY_COLORS[sev] || '#00D4FF')}15` : 'transparent',
                      fontFamily: 'Orbitron, monospace', letterSpacing: '0.04em',
                    }}>
                    {sev === 'all' ? 'ALL' : sev.slice(0, 3).toUpperCase()}
                  </button>
                ))}
              </div>
            </div>
            {/* Area */}
            <div>
              <label style={{ color: 'var(--text-muted)', fontSize: 10, display: 'block', marginBottom: 3 }}>
                AREA / SECTOR
              </label>
              <select
                className="cmd-input w-full px-2 py-1.5 text-xs"
                value={filters.area}
                onChange={e => handleFilter('area', e.target.value)}
              >
                <option value="all">All Areas</option>
                {AREAS.map(a => <option key={a.name} value={a.name}>{a.name}</option>)}
              </select>
            </div>
          </div>
        )}
      </div>

      {/* Hotspot Summary */}
      <div className="flex-1 overflow-y-auto p-3">
        <SectionHeader icon={Activity} title="Top Hotspots" count={hotspots.length} />
        <div className="space-y-1">
          {hotspots.filter(h => h.risk === 'Critical' || h.risk === 'High').slice(0, 8).map((hs, i) => (
            <HotspotRow key={hs.id} hs={hs} index={i} />
          ))}
        </div>
      </div>
    </div>
  );
}
