import { useData } from '../../context/DataContext';
import { AREAS, CRIME_TYPES } from '../../data/mockData';
import { getCrimesByType, getCrimesByArea, getCrimesByMonth, getCrimesByHour, getCyberByType, getTotalAmountLost } from '../../data/analyticsUtils';
import React, { useState, useEffect } from 'react';
import { Brain, Bell, TrendingUp, MapPin, Users, Zap, ChevronRight } from 'lucide-react';

const RISK_COLORS = {
  Critical: '#FF1744', High: '#FF6D00', Medium: '#FFD600', Low: '#00E676',
};
const ALERT_COLORS = {
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
        <span className="text-xs px-1.5 py-0.5 rounded"
          style={{ background: 'rgba(0,212,255,0.1)', color: 'var(--electric)', fontSize: 10 }}>
          {count}
        </span>
      )}
    </div>
  );
}

function AIIntelligenceCard({ pred, index }) {
  const color = RISK_COLORS[pred.risk_level] || '#FF6D00';
  return (
    <div className="intel-card p-2.5 mb-2 rounded"
      style={{ animation: `fadeIn 0.4s ease-out ${index * 0.08}s both` }}>
      {/* Header */}
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-1.5">
          <MapPin size={10} style={{ color }} />
          <span className="text-xs font-semibold" style={{ color: '#E8F4FD' }}>{pred.area}</span>
        </div>
        <span className="font-orbitron font-bold text-xs" style={{ color }}>{pred.score}/100</span>
      </div>

      {/* Risk bar */}
      <div className="progress-track h-1.5 mb-2">
        <div className="progress-fill h-full" style={{
          width: `${pred.score}%`,
          background: `linear-gradient(90deg, ${color}60, ${color})`,
          boxShadow: `0 0 6px ${color}40`,
        }} />
      </div>

      {/* Details */}
      <div className="grid grid-cols-2 gap-1 mb-2">
        <div className="text-center p-1 rounded" style={{ background: 'rgba(0,0,0,0.2)' }}>
          <div className="font-orbitron font-bold" style={{ color, fontSize: 13 }}>{pred.predicted_crimes}</div>
          <div style={{ color: 'var(--text-muted)', fontSize: 9 }}>PREDICTED</div>
        </div>
        <div className="text-center p-1 rounded" style={{ background: 'rgba(0,0,0,0.2)' }}>
          <div className="font-orbitron font-bold" style={{ color: 'var(--electric)', fontSize: 13 }}>{pred.confidence}%</div>
          <div style={{ color: 'var(--text-muted)', fontSize: 9 }}>CONFIDENCE</div>
        </div>
      </div>

      {/* Recommendation */}
      <div className="flex items-center gap-1.5 p-1.5 rounded"
        style={{ background: 'rgba(0,102,255,0.08)', border: '1px solid rgba(0,102,255,0.15)' }}>
        <Users size={9} style={{ color: '#60A5FA', flexShrink: 0 }} />
        <span style={{ color: '#60A5FA', fontSize: 9 }}>{pred.deployment}</span>
      </div>
    </div>
  );
}

function AlertItem({ alert, index }) {
  const color = ALERT_COLORS[alert.type] || '#FFD600';
  const timeAgo = getTimeAgo(alert.timestamp);

  return (
    <div className={`data-row flex gap-2 py-2 px-1 rounded-sm ${!alert.acknowledged ? 'border-l-2' : ''}`}
      style={{
        borderLeftColor: !alert.acknowledged ? color : 'transparent',
        animation: `fadeIn 0.3s ease-out ${index * 0.04}s both`,
      }}>
      {/* Type dot */}
      <div className="flex-shrink-0 mt-1">
        <div className="w-1.5 h-1.5 rounded-full"
          style={{ background: color, boxShadow: `0 0 4px ${color}`, opacity: alert.acknowledged ? 0.5 : 1 }} />
      </div>

      <div className="flex-1 min-w-0">
        <div className="flex items-center justify-between gap-1 mb-0.5">
          <span className="text-xs font-medium truncate"
            style={{ color: alert.acknowledged ? 'var(--text-secondary)' : '#E8F4FD', fontSize: 11 }}>
            {alert.title}
          </span>
          <span style={{ color, background: `${color}15`, border: `1px solid ${color}30`,
            padding: '1px 4px', borderRadius: 2, fontSize: 8, fontFamily: 'Orbitron', flexShrink: 0 }}>
            {alert.type.toUpperCase()}
          </span>
        </div>
        <div className="text-xs truncate mb-0.5" style={{ color: 'var(--text-muted)', fontSize: 10 }}>
          {alert.message}
        </div>
        <div className="flex items-center justify-between">
          <span style={{ color: 'var(--text-muted)', fontSize: 9 }}>📍 {alert.area}</span>
          <span style={{ color: 'var(--text-muted)', fontSize: 9 }}>{timeAgo}</span>
        </div>
      </div>
    </div>
  );
}

function getTimeAgo(ts) {
  const diff = (Date.now() - new Date(ts).getTime()) / 1000;
  if (diff < 60) return `${Math.floor(diff)}s ago`;
  if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
  return `${Math.floor(diff / 3600)}h ago`;
}

function RiskScoreTicker({ hotspots }) {
  if (!hotspots || hotspots.length === 0) return <div className="text-sm text-gray-500 italic">No active hotspots</div>;

  // Sort hotspots by score descending
  const sorted = [...hotspots].sort((a, b) => b.score - a.score).slice(0, 5);

  return (
    <div className="space-y-1.5">
      {sorted.map(hs => {
        const color = hs.score >= 80 ? '#FF1744' : hs.score >= 50 ? '#FF6D00' : hs.score >= 25 ? '#FFD600' : '#00E676';
        return (
          <div key={hs.id} className="flex items-center gap-2">
            <span className="text-xs w-20 truncate" style={{ color: 'var(--text-secondary)', fontSize: 10 }}>{hs.name}</span>
            <div className="flex-1 progress-track h-1">
              <div className="progress-fill h-full transition-all duration-1000"
                style={{ width: `${hs.score}%`, background: `linear-gradient(90deg, ${color}50, ${color})` }} />
            </div>
            <span className="font-orbitron font-bold w-6 text-right" style={{ color, fontSize: 11 }}>{hs.score}</span>
            <span style={{ color: hs.trend.startsWith('+') ? '#FF1744' : hs.trend.startsWith('-') ? '#00E676' : 'var(--text-muted)', fontSize: 9, width: 20, textAlign: 'right', fontFamily: 'JetBrains Mono' }}>
              {hs.trend}
            </span>
          </div>
        );
      })}
    </div>
  );
}

export default function RightPanel() {
  const { crimes, hotspots, patrols, routes, cybercrime, alerts, predictions, loading } = useData();
  if (loading) return <div>Loading...</div>;

  return (
    <div className="flex flex-col h-full overflow-hidden panel-surface animate-slide-in-right"
      style={{ width: 290, borderLeft: '1px solid rgba(0,212,255,0.06)' }}>

      {/* AI Intelligence Panel */}
      <div className="flex-shrink-0 p-3 border-b" style={{ borderColor: 'rgba(0,212,255,0.05)' }}>
        <SectionHeader icon={Brain} title="AI Intelligence" />

        {/* Decorative scan effect */}
        <div className="scan-container rounded mb-2" style={{ height: 2 }}>
          <div style={{
            height: '100%',
            background: 'linear-gradient(90deg, transparent, var(--electric), transparent)',
            animation: 'scanHoriz 3s linear infinite',
          }} />
        </div>

        <div className="overflow-y-auto" style={{ maxHeight: 220 }}>
          {predictions.slice(0, 4).map((pred, i) => (
            <AIIntelligenceCard key={pred.area} pred={pred} index={i} />
          ))}
        </div>

        <button className="w-full mt-2 py-1.5 rounded flex items-center justify-center gap-1.5 btn-ghost">
          <ChevronRight size={11} />
          <span style={{ fontSize: 10, fontFamily: 'Orbitron' }}>VIEW ALL PREDICTIONS</span>
        </button>
      </div>

      {/* Live Risk Scores */}
      <div className="flex-shrink-0 p-3 border-b" style={{ borderColor: 'rgba(0,212,255,0.05)' }}>
        <SectionHeader icon={TrendingUp} title="Live Risk Scores" />
        <RiskScoreTicker hotspots={hotspots} />
      </div>

      {/* Alert Feed */}
      <div className="flex-1 overflow-y-auto p-3">
        <SectionHeader icon={Bell} title="Alert Feed"
          count={alerts.filter(a => !a.acknowledged).length} />
        <div className="space-y-0.5">
          {alerts.slice(0, 20).map((alert, i) => (
            <AlertItem key={alert.id} alert={alert} index={i} />
          ))}
        </div>
      </div>
    </div>
  );
}
