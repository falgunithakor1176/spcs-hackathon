import { useData } from '../context/DataContext';
import { AREAS, CRIME_TYPES } from '../data/mockData';
import { getCrimesByType, getCrimesByArea, getCrimesByMonth, getCrimesByHour, getCyberByType, getTotalAmountLost } from '../data/analyticsUtils';
import React, { useState } from 'react';
import { Bell, CheckCircle, Clock, Filter, AlertTriangle, Search } from 'lucide-react';

const ALERT_COLORS = {
  Critical: '#FF1744', High: '#FF6D00', Medium: '#FFD600', Low: '#00E676',
};

function getTimeAgo(ts) {
  const diff = (Date.now() - new Date(ts).getTime()) / 1000;
  if (diff < 60) return `${Math.floor(diff)}s ago`;
  if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
  return `${Math.floor(diff / 3600)}h ago`;
}

function AlertRow({ alert, onAck }) {
  const color = ALERT_COLORS[alert.type] || '#FFD600';
  return (
    <div className={`glass-card p-4 rounded-lg mb-2 transition-all ${!alert.acknowledged ? 'animate-fade-in' : 'opacity-60'}`}
      style={{
        borderLeft: `4px solid ${!alert.acknowledged ? color : '#1e293b'}`,
        background: !alert.acknowledged ? `${color}04` : undefined,
      }}>
      <div className="flex items-start gap-4">
        {/* Type indicator */}
        <div className="flex-shrink-0 flex items-center justify-center w-10 h-10 rounded-lg"
          style={{ background: `${color}15`, border: `1px solid ${color}25` }}>
          <AlertTriangle size={16} style={{ color }} />
        </div>

        <div className="flex-1 min-w-0">
          <div className="flex items-start justify-between gap-3 mb-1">
            <div>
              <span className="font-semibold text-sm mr-2" style={{ color: '#E8F4FD' }}>{alert.title}</span>
              <span style={{
                background: `${color}15`, border: `1px solid ${color}30`,
                color, fontSize: 9, padding: '1px 6px', borderRadius: 3,
                fontFamily: 'Orbitron', letterSpacing: '0.08em',
              }}>{alert.type.toUpperCase()}</span>
            </div>
            <div className="flex items-center gap-2 flex-shrink-0">
              <span style={{ color: 'var(--text-muted)', fontSize: 11 }}>{getTimeAgo(alert.timestamp)}</span>
              {!alert.acknowledged && (
                <button onClick={() => onAck(alert.id)}
                  className="flex items-center gap-1 px-2 py-1 rounded btn-ghost">
                  <CheckCircle size={11} />
                  <span style={{ fontSize: 9, fontFamily: 'Orbitron' }}>ACK</span>
                </button>
              )}
              {alert.acknowledged && (
                <div className="flex items-center gap-1" style={{ color: '#00E676' }}>
                  <CheckCircle size={11} />
                  <span style={{ fontSize: 9 }}>Acknowledged</span>
                </div>
              )}
            </div>
          </div>
          <div className="text-sm mb-2" style={{ color: 'var(--text-secondary)' }}>{alert.message}</div>
          <div className="flex items-center gap-4" style={{ color: 'var(--text-muted)', fontSize: 11 }}>
            <span>📍 {alert.area}</span>
            <span>🆔 {alert.id}</span>
            {alert.assigned_to && <span>👮 {alert.assigned_to}</span>}
            <span>{new Date(alert.timestamp).toLocaleString('en-IN')}</span>
          </div>
        </div>
      </div>
    </div>
  );
}

export default function Alerts() {
  const { crimes, hotspots, patrols, routes, cybercrime, alerts: initialAlerts, predictions, loading } = useData();
  const [alerts, setAlerts] = useState([]);
  const [filterType, setFilterType] = useState('all');
  const [filterAck, setFilterAck] = useState('all');
  const [search, setSearch] = useState('');

  React.useEffect(() => {
    if (initialAlerts) setAlerts(initialAlerts);
  }, [initialAlerts]);
  
  if (loading) return <div>Loading...</div>;

  const filtered = alerts.filter(a => {
    if (filterType !== 'all' && a.type !== filterType) return false;
    if (filterAck === 'unack' && a.acknowledged) return false;
    if (filterAck === 'ack' && !a.acknowledged) return false;
    if (search && !a.title.toLowerCase().includes(search.toLowerCase()) &&
        !a.message.toLowerCase().includes(search.toLowerCase()) &&
        !a.area.toLowerCase().includes(search.toLowerCase())) return false;
    return true;
  });

  const handleAck = (id) => {
    setAlerts(prev => prev.map(a => a.id === id ? { ...a, acknowledged: true } : a));
  };

  const handleAckAll = () => {
    setAlerts(prev => prev.map(a => ({ ...a, acknowledged: true })));
  };

  const unackCount = alerts.filter(a => !a.acknowledged).length;
  const byType = { Critical: 0, High: 0, Medium: 0, Low: 0 };
  alerts.forEach(a => { byType[a.type] = (byType[a.type] || 0) + 1; });

  return (
    <div className="h-full overflow-y-auto page-enter" style={{ background: '#060d1a' }}>
      <div className="p-4">

        {/* Summary Cards */}
        <div className="grid grid-cols-5 gap-3 mb-4">
          {[
            { label: 'Total Alerts', value: alerts.length, color: '#00D4FF' },
            { label: 'Unacknowledged', value: unackCount, color: '#FF1744' },
            ...Object.entries(byType).map(([type, count]) => ({
              label: type, value: count, color: ALERT_COLORS[type],
            })),
          ].map(({ label, value, color }) => (
            <div key={label} className="glass-card p-3 rounded-lg text-center"
              style={{ borderTop: `2px solid ${color}` }}>
              <div className="font-orbitron font-bold" style={{ color, fontSize: 20 }}>{value}</div>
              <div style={{ color: 'var(--text-secondary)', fontSize: 10 }}>{label}</div>
            </div>
          ))}
        </div>

        {/* Filters */}
        <div className="flex items-center gap-3 mb-4 p-3 glass-card rounded-lg">
          <div className="relative flex-1 max-w-xs">
            <Search size={13} className="absolute left-3 top-1/2 -translate-y-1/2" style={{ color: 'var(--text-muted)' }} />
            <input value={search} onChange={e => setSearch(e.target.value)}
              placeholder="Search alerts..." className="cmd-input w-full pl-9 pr-3 py-2 text-xs" />
          </div>

          <div className="flex gap-1">
            {['all', 'Critical', 'High', 'Medium', 'Low'].map(t => (
              <button key={t} onClick={() => setFilterType(t)}
                className="px-2.5 py-1 rounded text-xs transition-all"
                style={{
                  fontFamily: 'Orbitron', fontSize: 9, letterSpacing: '0.08em',
                  background: filterType === t ? `${ALERT_COLORS[t] || 'var(--electric)'}20` : 'transparent',
                  border: `1px solid ${filterType === t ? (ALERT_COLORS[t] || 'var(--electric)') + '40' : 'rgba(0,212,255,0.1)'}`,
                  color: filterType === t ? (ALERT_COLORS[t] || 'var(--electric)') : 'var(--text-muted)',
                }}>
                {t.toUpperCase()}
              </button>
            ))}
          </div>

          <select className="cmd-input px-3 py-2 text-xs" value={filterAck} onChange={e => setFilterAck(e.target.value)}>
            <option value="all">All Status</option>
            <option value="unack">Unacknowledged</option>
            <option value="ack">Acknowledged</option>
          </select>

          {unackCount > 0 && (
            <button onClick={handleAckAll} className="btn-primary px-3 py-2 text-xs flex items-center gap-1.5">
              <CheckCircle size={12} />
              ACK ALL ({unackCount})
            </button>
          )}

          <div className="ml-auto" style={{ color: 'var(--text-muted)', fontSize: 11 }}>
            Showing {filtered.length} of {alerts.length}
          </div>
        </div>

        {/* Alert List */}
        {filtered.length === 0 ? (
          <div className="text-center py-16">
            <Bell size={32} style={{ color: 'var(--text-muted)', margin: '0 auto 12px' }} />
            <div style={{ color: 'var(--text-muted)' }}>No alerts match your filters</div>
          </div>
        ) : (
          filtered.map(alert => (
            <AlertRow key={alert.id} alert={alert} onAck={handleAck} />
          ))
        )}
      </div>
    </div>
  );
}
