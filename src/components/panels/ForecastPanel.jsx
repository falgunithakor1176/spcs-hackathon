import React, { useState } from 'react';
import { useData } from '../../context/DataContext';
import { runEngine2, runEngine3 } from '../../services/forecastService';
import { TrendingUp, Cpu, Shield, Globe, AlertTriangle, RefreshCw, Info } from 'lucide-react';

const RISK_COLORS = {
  Critical: '#FF1744',
  High: '#FF6D00',
  Medium: '#FFD600',
  Low: '#00E676',
};

const RISK_BG = {
  Critical: 'rgba(255,23,68,0.12)',
  High: 'rgba(255,109,0,0.12)',
  Medium: 'rgba(255,214,0,0.10)',
  Low: 'rgba(0,230,118,0.10)',
};

function RiskBadge({ level }) {
  const color = RISK_COLORS[level] || '#aaa';
  return (
    <span style={{
      background: RISK_BG[level] || 'transparent',
      color, border: `1px solid ${color}40`,
      fontSize: 9, fontFamily: 'Orbitron', letterSpacing: '0.08em',
      padding: '2px 6px', borderRadius: 3,
    }}>
      {level?.toUpperCase()}
    </span>
  );
}

function WeightsBar() {
  return (
    <div style={{ marginBottom: 10 }}>
      <div style={{ fontSize: 9, color: 'var(--text-muted)', marginBottom: 4, fontFamily: 'Orbitron' }}>
        HEURISTIC WEIGHTS (configurable)
      </div>
      <div style={{ display: 'flex', height: 8, borderRadius: 4, overflow: 'hidden', gap: 1 }}>
        <div title="Physical Crime (Engine 2) — 45%" style={{
          flex: 45, background: 'linear-gradient(90deg,#FF6D00,#FF1744)',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
        }}>
          <span style={{ fontSize: 7, color: '#fff', fontWeight: 700 }}>45%</span>
        </div>
        <div title="Cyber Risk (Engine 2) — 25%" style={{
          flex: 25, background: 'linear-gradient(90deg,#A78BFA,#7C3AED)',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
        }}>
          <span style={{ fontSize: 7, color: '#fff', fontWeight: 700 }}>25%</span>
        </div>
        <div title="Spatial Hotspots (Engine 1) — 30%" style={{
          flex: 30, background: 'linear-gradient(90deg,#00D4FF,#0066FF)',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
        }}>
          <span style={{ fontSize: 7, color: '#fff', fontWeight: 700 }}>30%</span>
        </div>
      </div>
      <div style={{ display: 'flex', gap: 8, marginTop: 3 }}>
        {[['#FF1744', 'Physical'], ['#A78BFA', 'Cyber'], ['#00D4FF', 'Spatial']].map(([c, l]) => (
          <div key={l} style={{ display: 'flex', alignItems: 'center', gap: 3 }}>
            <div style={{ width: 6, height: 6, borderRadius: 1, background: c }} />
            <span style={{ fontSize: 8, color: 'var(--text-muted)' }}>{l}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

function AreaCard({ row, rank }) {
  const color = RISK_COLORS[row.combined_risk] || '#aaa';
  const score = Math.round((row.combined_risk_score || 0) * 100);

  return (
    <div style={{
      background: 'rgba(0,0,0,0.25)',
      border: `1px solid ${color}20`,
      borderLeft: `3px solid ${color}`,
      borderRadius: 4,
      padding: '8px 10px',
      marginBottom: 6,
    }}>
      {/* Header row */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 5 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
          <span style={{
            fontFamily: 'Orbitron', fontSize: 10, color, fontWeight: 700,
            background: `${color}18`, padding: '1px 5px', borderRadius: 2,
          }}>#{rank}</span>
          <span style={{ fontSize: 11, color: '#E8F4FD', fontWeight: 600 }}>{row.area}</span>
          <span style={{ fontSize: 9, color: 'var(--text-muted)' }}>{row.zone}</span>
        </div>
        <RiskBadge level={row.combined_risk} />
      </div>

      {/* Score bar */}
      <div style={{ background: 'rgba(255,255,255,0.05)', borderRadius: 2, height: 4, marginBottom: 6 }}>
        <div style={{
          height: '100%', borderRadius: 2, width: `${score}%`,
          background: `linear-gradient(90deg, ${color}60, ${color})`,
          boxShadow: `0 0 6px ${color}40`,
          transition: 'width 0.8s ease',
        }} />
      </div>

      {/* Engine breakdown */}
      <div style={{ display: 'flex', gap: 4 }}>
        {[
          { label: 'PHYSICAL', value: row.physical_risk, icon: '⚡' },
          { label: 'CYBER', value: row.cyber_risk, icon: '🌐' },
          { label: 'SPATIAL', value: row.hotspot_risk, icon: '📍' },
        ].map(({ label, value, icon }) => (
          <div key={label} style={{
            flex: 1, textAlign: 'center', padding: '3px 2px',
            background: `${RISK_COLORS[value] || '#666'}10`,
            borderRadius: 3, border: `1px solid ${RISK_COLORS[value] || '#666'}20`,
          }}>
            <div style={{ fontSize: 9, marginBottom: 1 }}>{icon}</div>
            <div style={{ fontSize: 8, color: RISK_COLORS[value] || '#aaa', fontFamily: 'Orbitron', fontWeight: 700 }}>
              {value || 'N/A'}
            </div>
            <div style={{ fontSize: 7, color: 'var(--text-muted)', marginTop: 1 }}>{label}</div>
          </div>
        ))}
        <div style={{
          flex: 1, textAlign: 'center', padding: '3px 2px',
          background: 'rgba(0,212,255,0.06)', borderRadius: 3,
          border: '1px solid rgba(0,212,255,0.12)',
        }}>
          <div style={{ fontSize: 9, marginBottom: 1 }}>🎯</div>
          <div style={{ fontSize: 9, color: 'var(--electric)', fontFamily: 'Orbitron', fontWeight: 700 }}>
            {score}
          </div>
          <div style={{ fontSize: 7, color: 'var(--text-muted)', marginTop: 1 }}>SCORE</div>
        </div>
      </div>

      {/* Top contributing engine */}
      {row.top_contributing_engine && (
        <div style={{
          marginTop: 5, fontSize: 9, color: 'var(--text-muted)',
          borderTop: '1px solid rgba(255,255,255,0.04)', paddingTop: 4,
        }}>
          <span style={{ color: 'rgba(0,212,255,0.6)' }}>▲ </span>
          Driven by: <span style={{ color: '#60A5FA' }}>{row.top_contributing_engine}</span>
        </div>
      )}
    </div>
  );
}

export default function ForecastPanel({ maxItems = 10 }) {
  const { areaIntelligence, engineConfig, refreshData } = useData();
  const [running, setRunning] = useState(false);
  const [showAll, setShowAll] = useState(false);

  const sorted = [...(areaIntelligence || [])].sort((a, b) => a.patrol_priority - b.patrol_priority);
  const displayed = showAll ? sorted : sorted.slice(0, 5);

  const period = sorted[0]
    ? `${sorted[0].forecast_year}-${String(sorted[0].forecast_month).padStart(2, '0')}`
    : '—';

  // Risk distribution counts
  const dist = sorted.reduce((acc, r) => {
    acc[r.combined_risk] = (acc[r.combined_risk] || 0) + 1;
    return acc;
  }, {});

  const handleRefresh = async () => {
    setRunning(true);
    try {
      await runEngine2();
      await runEngine3();
      await refreshData();
    } catch (e) {
      console.error('Engine refresh failed:', e);
    } finally {
      setRunning(false);
    }
  };

  return (
    <div style={{ padding: '12px 10px', height: '100%', overflowY: 'auto' }}>

      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 10 }}>
        <div>
          <div style={{ fontFamily: 'Orbitron', fontSize: 11, color: 'var(--electric)', letterSpacing: '0.1em' }}>
            FUTURE RISK FORECAST
          </div>
          <div style={{ fontSize: 9, color: 'var(--text-muted)', marginTop: 2 }}>
            Engine 2 + Engine 3 · Period: <span style={{ color: '#60A5FA' }}>{period}</span>
          </div>
        </div>
        <button
          onClick={handleRefresh}
          disabled={running}
          title="Re-run Engine 2 + Engine 3"
          style={{
            background: 'rgba(0,212,255,0.08)', border: '1px solid rgba(0,212,255,0.2)',
            borderRadius: 4, padding: '4px 8px', cursor: running ? 'not-allowed' : 'pointer',
            display: 'flex', alignItems: 'center', gap: 4, color: 'var(--electric)',
          }}>
          <RefreshCw size={11} style={{ animation: running ? 'spin 1s linear infinite' : 'none' }} />
          <span style={{ fontSize: 9, fontFamily: 'Orbitron' }}>{running ? 'RUNNING' : 'REFRESH'}</span>
        </button>
      </div>

      {/* Risk distribution summary */}
      <div style={{
        display: 'flex', gap: 4, marginBottom: 10, padding: '6px 8px',
        background: 'rgba(0,0,0,0.2)', borderRadius: 6, border: '1px solid rgba(0,212,255,0.06)',
      }}>
        {['Critical', 'High', 'Medium', 'Low'].map(level => (
          <div key={level} style={{ flex: 1, textAlign: 'center' }}>
            <div style={{ fontFamily: 'Orbitron', fontSize: 14, color: RISK_COLORS[level], fontWeight: 700 }}>
              {dist[level] || 0}
            </div>
            <div style={{ fontSize: 8, color: 'var(--text-muted)' }}>{level}</div>
          </div>
        ))}
        <div style={{
          flex: 1, textAlign: 'center', borderLeft: '1px solid rgba(255,255,255,0.06)', paddingLeft: 4
        }}>
          <div style={{ fontFamily: 'Orbitron', fontSize: 14, color: 'var(--electric)', fontWeight: 700 }}>
            {sorted.length}
          </div>
          <div style={{ fontSize: 8, color: 'var(--text-muted)' }}>Areas</div>
        </div>
      </div>

      {/* Weights bar */}
      <WeightsBar />

      {/* Area cards */}
      <div style={{ marginBottom: 4 }}>
        <div style={{
          fontSize: 9, color: 'var(--text-muted)', fontFamily: 'Orbitron',
          letterSpacing: '0.08em', marginBottom: 6,
        }}>
          PATROL PRIORITY AREAS
        </div>
        {sorted.length === 0 ? (
          <div style={{ color: 'var(--text-muted)', fontSize: 11, textAlign: 'center', padding: 20 }}>
            No forecast data. Click REFRESH to run engines.
          </div>
        ) : (
          displayed.map(row => (
            <AreaCard key={row.area} row={row} rank={row.patrol_priority} />
          ))
        )}
      </div>

      {/* Show more */}
      {sorted.length > 5 && (
        <button
          onClick={() => setShowAll(s => !s)}
          style={{
            width: '100%', padding: '6px', marginTop: 4,
            background: 'rgba(0,212,255,0.05)', border: '1px solid rgba(0,212,255,0.12)',
            borderRadius: 4, color: 'var(--electric)', fontSize: 9,
            fontFamily: 'Orbitron', cursor: 'pointer', letterSpacing: '0.08em',
          }}>
          {showAll ? `▲ SHOW TOP 5 ONLY` : `▼ SHOW ALL ${sorted.length} AREAS`}
        </button>
      )}

      {/* Methodology note */}
      <div style={{
        marginTop: 10, padding: '6px 8px', borderRadius: 4,
        background: 'rgba(96,165,250,0.06)', border: '1px solid rgba(96,165,250,0.12)',
        display: 'flex', gap: 6,
      }}>
        <Info size={10} style={{ color: '#60A5FA', flexShrink: 0, marginTop: 1 }} />
        <span style={{ fontSize: 9, color: 'var(--text-muted)', lineHeight: 1.5 }}>
          Scores combine RF-predicted crime counts (45%), cyber risk classification (25%), and DBSCAN
          spatial hotspots (30%). Weights are configurable domain heuristics, not fixed AI outputs.
        </span>
      </div>
    </div>
  );
}
