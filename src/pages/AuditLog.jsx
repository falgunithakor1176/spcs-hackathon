import React, { useState, useEffect, useCallback } from 'react';
import { getAuditLogs, getAuditStats } from '../services/auditService';
import { ScrollText, RefreshCw, Filter, Shield, User, Activity } from 'lucide-react';

const ACTION_COLORS = {
  LOGIN:      '#00D4FF', LOGOUT:     '#7A9BB5',
  ENGINE_RUN: '#A78BFA', EXPORT:     '#00E676',
  ACK_ALERT:  '#FFD600', SIMULATE:   '#FF6D00',
  VIEW:       '#60A5FA',
};

const ROLE_COLORS = {
  Commissioner: '#FF6D00', Admin: '#FF6D00',
  Analyst:      '#A78BFA', Officer: '#00D4FF', Cyber: '#00E676',
};

function StatCard({ label, value, color }) {
  return (
    <div className="glass-card p-4 rounded-lg" style={{ textAlign: 'center' }}>
      <div style={{ fontFamily: 'Orbitron', fontSize: 22, color, fontWeight: 700 }}>{value}</div>
      <div style={{ fontSize: 10, color: 'var(--text-muted)', marginTop: 2 }}>{label}</div>
    </div>
  );
}

export default function AuditLog() {
  const [logs,    setLogs]    = useState([]);
  const [stats,   setStats]   = useState(null);
  const [loading, setLoading] = useState(true);
  const [error,   setError]   = useState(null);
  const [filters, setFilters] = useState({ action: '', role: '' });
  const [page,    setPage]    = useState(1);
  const [total,   setTotal]   = useState(0);
  const LIMIT = 50;

  const fetchData = useCallback(async () => {
    setLoading(true); setError(null);
    try {
      const [logRes, statsRes] = await Promise.all([
        getAuditLogs({ page, limit: LIMIT, action: filters.action || undefined, role: filters.role || undefined }),
        getAuditStats(),
      ]);
      setLogs(logRes.data || []);
      setTotal(logRes.total || 0);
      setStats(statsRes);
    } catch (e) {
      setError(e.response?.data?.message || 'Failed to load audit logs. Admin access required.');
    } finally {
      setLoading(false);
    }
  }, [page, filters]);

  useEffect(() => { fetchData(); }, [fetchData]);

  const formatTs = ts => {
    if (!ts) return '—';
    return new Date(ts).toLocaleString('en-IN', { dateStyle: 'medium', timeStyle: 'short' });
  };

  return (
    <div style={{ padding: 24, height: '100%', overflowY: 'auto', background: '#060d1a' }}>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 20 }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 4 }}>
            <ScrollText size={20} style={{ color: 'var(--electric)' }} />
            <span style={{ fontFamily: 'Orbitron', fontSize: 16, color: '#E8F4FD', letterSpacing: '0.1em' }}>AUDIT LOG</span>
          </div>
          <p style={{ color: 'var(--text-muted)', fontSize: 12 }}>
            System action history · Visible to Commissioner only · {total} total entries
          </p>
        </div>
        <button onClick={fetchData} style={{
          background: 'rgba(0,212,255,0.08)', border: '1px solid rgba(0,212,255,0.2)',
          borderRadius: 6, padding: '8px 14px', cursor: 'pointer', color: 'var(--electric)',
          display: 'flex', alignItems: 'center', gap: 6, fontFamily: 'Orbitron', fontSize: 10,
        }}>
          <RefreshCw size={12} style={{ animation: loading ? 'spin 1s linear infinite' : 'none' }} />
          REFRESH
        </button>
      </div>

      {/* Stats row */}
      {stats && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(5,1fr)', gap: 10, marginBottom: 20 }}>
          <StatCard label="Total Entries" value={stats.total_entries || 0} color="var(--electric)" />
          {Object.entries(stats.by_action || {}).slice(0, 4).map(([action, count]) => (
            <StatCard key={action} label={action} value={count} color={ACTION_COLORS[action] || '#7A9BB5'} />
          ))}
        </div>
      )}

      {/* Filters */}
      <div className="glass-card p-3 rounded-lg" style={{ marginBottom: 16, display: 'flex', gap: 12, alignItems: 'center' }}>
        <Filter size={13} style={{ color: 'var(--electric)', flexShrink: 0 }} />
        <select
          value={filters.action}
          onChange={e => { setFilters(f => ({ ...f, action: e.target.value })); setPage(1); }}
          style={{ background: 'rgba(0,0,0,0.3)', border: '1px solid rgba(0,212,255,0.15)', borderRadius: 4, color: '#E8F4FD', padding: '4px 8px', fontSize: 11 }}>
          <option value="">All Actions</option>
          {['LOGIN','ENGINE_RUN','EXPORT','ACK_ALERT','SIMULATE'].map(a => <option key={a} value={a}>{a}</option>)}
        </select>
        <select
          value={filters.role}
          onChange={e => { setFilters(f => ({ ...f, role: e.target.value })); setPage(1); }}
          style={{ background: 'rgba(0,0,0,0.3)', border: '1px solid rgba(0,212,255,0.15)', borderRadius: 4, color: '#E8F4FD', padding: '4px 8px', fontSize: 11 }}>
          <option value="">All Roles</option>
          {['Commissioner','Analyst','Officer','Cyber'].map(r => <option key={r} value={r}>{r}</option>)}
        </select>
        <span style={{ marginLeft: 'auto', fontSize: 10, color: 'var(--text-muted)' }}>
          Showing {logs.length} of {total}
        </span>
      </div>

      {/* Error */}
      {error && (
        <div style={{ padding: 16, background: 'rgba(255,23,68,0.1)', border: '1px solid rgba(255,23,68,0.3)', borderRadius: 6, color: '#FF1744', fontSize: 12, marginBottom: 16 }}>
          ⚠️ {error}
        </div>
      )}

      {/* Table */}
      <div className="glass-card rounded-lg" style={{ overflow: 'hidden' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 12 }}>
          <thead>
            <tr style={{ background: 'rgba(0,0,0,0.4)' }}>
              {['#','Timestamp','User','Role','Action','Resource','Detail','IP'].map(h => (
                <th key={h} style={{ padding: '10px 12px', textAlign: 'left', color: 'var(--text-muted)', fontFamily: 'Orbitron', fontSize: 9, fontWeight: 400, letterSpacing: '0.06em', whiteSpace: 'nowrap' }}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr><td colSpan={8} style={{ padding: 30, textAlign: 'center', color: 'var(--text-muted)' }}>Loading audit logs...</td></tr>
            ) : logs.length === 0 ? (
              <tr><td colSpan={8} style={{ padding: 30, textAlign: 'center', color: 'var(--text-muted)' }}>No entries found</td></tr>
            ) : logs.map((log, i) => {
              const actionColor = ACTION_COLORS[log.action] || '#7A9BB5';
              const roleColor   = ROLE_COLORS[log.role]   || '#7A9BB5';
              return (
                <tr key={log.id} style={{ borderBottom: '1px solid rgba(255,255,255,0.03)', background: i % 2 === 0 ? 'transparent' : 'rgba(0,0,0,0.1)' }}>
                  <td style={{ padding: '7px 12px', color: 'var(--text-muted)', fontSize: 10 }}>{log.id}</td>
                  <td style={{ padding: '7px 12px', color: '#7A9BB5', fontSize: 10, whiteSpace: 'nowrap' }}>{formatTs(log.timestamp)}</td>
                  <td style={{ padding: '7px 12px', color: '#E8F4FD', fontWeight: 500 }}>{log.username}</td>
                  <td style={{ padding: '7px 12px' }}>
                    <span style={{ color: roleColor, background: `${roleColor}15`, border: `1px solid ${roleColor}30`, padding: '1px 6px', borderRadius: 3, fontSize: 9, fontFamily: 'Orbitron' }}>{log.role}</span>
                  </td>
                  <td style={{ padding: '7px 12px' }}>
                    <span style={{ color: actionColor, background: `${actionColor}12`, border: `1px solid ${actionColor}25`, padding: '1px 6px', borderRadius: 3, fontSize: 9, fontFamily: 'Orbitron' }}>{log.action}</span>
                  </td>
                  <td style={{ padding: '7px 12px', color: 'var(--text-muted)', fontSize: 10 }}>{log.resource}</td>
                  <td style={{ padding: '7px 12px', color: 'var(--text-muted)', fontSize: 10, maxWidth: 200, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{log.detail}</td>
                  <td style={{ padding: '7px 12px', color: 'var(--text-muted)', fontSize: 10 }}>{log.ip_address}</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      {total > LIMIT && (
        <div style={{ display: 'flex', justifyContent: 'center', gap: 8, marginTop: 16 }}>
          <button onClick={() => setPage(p => Math.max(1, p - 1))} disabled={page === 1}
            style={{ padding: '6px 14px', background: 'rgba(0,212,255,0.08)', border: '1px solid rgba(0,212,255,0.2)', borderRadius: 4, color: 'var(--electric)', cursor: 'pointer', fontSize: 11 }}>
            ← Prev
          </button>
          <span style={{ padding: '6px 12px', color: 'var(--text-muted)', fontSize: 11 }}>Page {page} of {Math.ceil(total / LIMIT)}</span>
          <button onClick={() => setPage(p => p + 1)} disabled={page >= Math.ceil(total / LIMIT)}
            style={{ padding: '6px 14px', background: 'rgba(0,212,255,0.08)', border: '1px solid rgba(0,212,255,0.2)', borderRadius: 4, color: 'var(--electric)', cursor: 'pointer', fontSize: 11 }}>
            Next →
          </button>
        </div>
      )}
    </div>
  );
}
