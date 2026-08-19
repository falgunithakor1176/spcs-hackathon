import React, { useState } from 'react';
import { runSimulation } from '../services/simulationService';
import { FlaskConical, Play, TrendingUp, TrendingDown, Minus, AlertTriangle, Info } from 'lucide-react';

const SCENARIOS = [
  { key: 'festival',    label: 'Festival Mode',      sub: 'Navratri / Diwali / Uttarayan', color: '#FF6D00', icon: '🎉', mult: '×1.40' },
  { key: 'large_event', label: 'Large Public Event', sub: 'IPL / Political Rally / Concert', color: '#A78BFA', icon: '🏟️', mult: '×1.25' },
  { key: 'curfew',      label: 'Curfew / Heavy Deployment', sub: 'Maximum police presence', color: '#00E676', icon: '🛡️', mult: '×0.55' },
  { key: 'night_ops',   label: 'Night Operations',   sub: 'After-dark violent crime spike', color: '#00D4FF', icon: '🌙', mult: '×1.20' },
  { key: 'normal',      label: 'Normal Operations',  sub: 'Baseline — no adjustment', color: '#7A9BB5', icon: '📊', mult: '×1.00' },
];

const RISK_COLORS = { Critical: '#FF1744', High: '#FF6D00', Medium: '#FFD600', Low: '#00E676' };
const RISK_ORDER  = { Low: 0, Medium: 1, High: 2, Critical: 3 };

function RiskBadge({ level, small }) {
  const c = RISK_COLORS[level] || '#aaa';
  return (
    <span style={{
      background: `${c}18`, color: c, border: `1px solid ${c}35`,
      padding: small ? '1px 5px' : '2px 8px',
      borderRadius: 3, fontSize: small ? 8 : 10, fontFamily: 'Orbitron',
    }}>{level?.toUpperCase()}</span>
  );
}

function DeltaIcon({ orig, sim }) {
  const d = RISK_ORDER[sim] - RISK_ORDER[orig];
  if (d > 0)  return <TrendingUp  size={13} style={{ color: '#FF1744' }} />;
  if (d < 0)  return <TrendingDown size={13} style={{ color: '#00E676' }} />;
  return <Minus size={13} style={{ color: '#7A9BB5' }} />;
}

export default function Simulation() {
  const [selected,   setSelected]   = useState('festival');
  const [areaFilter, setAreaFilter] = useState('all');
  const [running,    setRunning]    = useState(false);
  const [result,     setResult]     = useState(null);
  const [error,      setError]      = useState(null);

  const handleRun = async () => {
    setRunning(true); setError(null);
    try {
      const data = await runSimulation(selected, areaFilter);
      setResult(data);
    } catch (e) {
      setError(e.response?.data?.message || e.message);
    } finally {
      setRunning(false);
    }
  };

  const escalated = result?.areas_escalated || 0;
  const reduced   = result?.areas_reduced   || 0;

  return (
    <div style={{ padding: 24, height: '100%', overflowY: 'auto', background: '#060d1a' }}>
      {/* Page header */}
      <div style={{ marginBottom: 20 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 6 }}>
          <FlaskConical size={20} style={{ color: 'var(--electric)' }} />
          <span style={{ fontFamily: 'Orbitron', fontSize: 16, color: '#E8F4FD', letterSpacing: '0.1em' }}>
            SCENARIO SIMULATION
          </span>
        </div>
        <p style={{ color: 'var(--text-muted)', fontSize: 12, maxWidth: 600 }}>
          Simulate how crime risk changes under different operational scenarios (festivals, events, curfew).
          Read-only — no live data is modified.
        </p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '320px 1fr', gap: 20 }}>
        {/* Left — controls */}
        <div>
          {/* Scenario selector */}
          <div className="glass-card p-4 rounded-lg" style={{ marginBottom: 16 }}>
            <div style={{ fontFamily: 'Orbitron', fontSize: 11, color: 'var(--electric)', marginBottom: 12, letterSpacing: '0.08em' }}>
              SELECT SCENARIO
            </div>
            {SCENARIOS.map(s => (
              <div
                key={s.key}
                onClick={() => setSelected(s.key)}
                style={{
                  padding: '10px 12px', borderRadius: 6, marginBottom: 6, cursor: 'pointer',
                  border: `1px solid ${selected === s.key ? s.color + '60' : 'rgba(255,255,255,0.05)'}`,
                  background: selected === s.key ? `${s.color}10` : 'rgba(0,0,0,0.2)',
                  transition: 'all 0.2s',
                }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                    <span style={{ fontSize: 16 }}>{s.icon}</span>
                    <div>
                      <div style={{ fontSize: 12, color: selected === s.key ? s.color : '#E8F4FD', fontWeight: 600 }}>{s.label}</div>
                      <div style={{ fontSize: 10, color: 'var(--text-muted)' }}>{s.sub}</div>
                    </div>
                  </div>
                  <span style={{
                    fontFamily: 'Orbitron', fontSize: 11, color: s.color,
                    background: `${s.color}15`, padding: '2px 6px', borderRadius: 3,
                  }}>{s.mult}</span>
                </div>
              </div>
            ))}
          </div>

          {/* Run button */}
          <button
            onClick={handleRun}
            disabled={running}
            style={{
              width: '100%', padding: '12px', borderRadius: 6, cursor: running ? 'not-allowed' : 'pointer',
              background: running ? 'rgba(0,212,255,0.08)' : 'linear-gradient(135deg,#0066FF,#00D4FF)',
              border: '1px solid rgba(0,212,255,0.3)', color: '#fff',
              fontFamily: 'Orbitron', fontSize: 12, letterSpacing: '0.1em',
              display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8,
            }}>
            <Play size={14} />
            {running ? 'SIMULATING...' : 'RUN SIMULATION'}
          </button>

          {error && (
            <div style={{ marginTop: 10, padding: 10, background: 'rgba(255,23,68,0.1)', border: '1px solid rgba(255,23,68,0.3)', borderRadius: 6, color: '#FF1744', fontSize: 11 }}>
              {error}
            </div>
          )}

          {/* Methodology note */}
          <div style={{ marginTop: 16, padding: '10px 12px', background: 'rgba(96,165,250,0.06)', border: '1px solid rgba(96,165,250,0.15)', borderRadius: 6 }}>
            <div style={{ display: 'flex', gap: 6 }}>
              <Info size={11} style={{ color: '#60A5FA', flexShrink: 0, marginTop: 2 }} />
              <span style={{ fontSize: 10, color: 'var(--text-muted)', lineHeight: 1.6 }}>
                Multipliers are domain-informed heuristics based on documented seasonal crime patterns
                in Ahmedabad (festival surge, curfew suppression). They are applied to Engine 3 scores
                and do not modify the database.
              </span>
            </div>
          </div>
        </div>

        {/* Right — results */}
        <div>
          {!result ? (
            <div className="glass-card p-8 rounded-lg" style={{ textAlign: 'center' }}>
              <FlaskConical size={40} style={{ color: 'rgba(0,212,255,0.2)', margin: '0 auto 12px' }} />
              <div style={{ color: 'var(--text-muted)', fontSize: 13 }}>Select a scenario and click Run Simulation</div>
            </div>
          ) : (
            <>
              {/* Summary cards */}
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4,1fr)', gap: 10, marginBottom: 16 }}>
                {[
                  { label: 'Scenario',       value: result.scenario_label?.split(' ')[0] || result.scenario, color: '#00D4FF' },
                  { label: 'Areas Analysed', value: result.areas?.length || 0, color: 'var(--electric)' },
                  { label: 'Escalated',      value: escalated, color: '#FF1744' },
                  { label: 'Reduced',        value: reduced,   color: '#00E676' },
                ].map(({ label, value, color }) => (
                  <div key={label} className="glass-card p-3 rounded-lg" style={{ textAlign: 'center' }}>
                    <div style={{ fontFamily: 'Orbitron', fontSize: 22, color, fontWeight: 700 }}>{value}</div>
                    <div style={{ fontSize: 10, color: 'var(--text-muted)', marginTop: 2 }}>{label}</div>
                  </div>
                ))}
              </div>

              {/* Distribution comparison */}
              <div className="glass-card p-4 rounded-lg" style={{ marginBottom: 16 }}>
                <div style={{ fontFamily: 'Orbitron', fontSize: 11, color: 'var(--electric)', marginBottom: 12 }}>RISK DISTRIBUTION — BEFORE vs AFTER</div>
                <div style={{ display: 'flex', gap: 20 }}>
                  {['Critical','High','Medium','Low'].map(level => (
                    <div key={level} style={{ flex: 1, textAlign: 'center' }}>
                      <div style={{ color: 'var(--text-muted)', fontSize: 9, marginBottom: 6, fontFamily: 'Orbitron' }}>{level.toUpperCase()}</div>
                      <div style={{ display: 'flex', alignItems: 'flex-end', justifyContent: 'center', gap: 4, height: 50 }}>
                        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                          <span style={{ fontSize: 9, color: 'var(--text-muted)', marginBottom: 2 }}>BEFORE</span>
                          <div style={{
                            width: 24, background: `${RISK_COLORS[level]}50`,
                            height: Math.max(4, ((result.original_distribution?.[level] || 0) / 27) * 50),
                            borderRadius: '3px 3px 0 0',
                          }} />
                          <span style={{ fontFamily: 'Orbitron', fontSize: 11, color: RISK_COLORS[level] }}>
                            {result.original_distribution?.[level] || 0}
                          </span>
                        </div>
                        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                          <span style={{ fontSize: 9, color: 'var(--text-muted)', marginBottom: 2 }}>AFTER</span>
                          <div style={{
                            width: 24, background: RISK_COLORS[level],
                            height: Math.max(4, ((result.simulated_distribution?.[level] || 0) / 27) * 50),
                            borderRadius: '3px 3px 0 0',
                          }} />
                          <span style={{ fontFamily: 'Orbitron', fontSize: 11, color: RISK_COLORS[level] }}>
                            {result.simulated_distribution?.[level] || 0}
                          </span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Area table */}
              <div className="glass-card rounded-lg" style={{ overflow: 'hidden' }}>
                <div style={{ padding: '12px 16px', borderBottom: '1px solid rgba(0,212,255,0.06)', fontFamily: 'Orbitron', fontSize: 11, color: 'var(--electric)' }}>
                  AREA-LEVEL SIMULATION RESULTS
                </div>
                <div style={{ overflowY: 'auto', maxHeight: 380 }}>
                  <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 11 }}>
                    <thead>
                      <tr style={{ background: 'rgba(0,0,0,0.3)' }}>
                        {['Priority','Area','Before','After','Δ Change','Score Before','Score After'].map(h => (
                          <th key={h} style={{ padding: '8px 10px', textAlign: 'left', color: 'var(--text-muted)', fontFamily: 'Orbitron', fontSize: 9, fontWeight: 400, letterSpacing: '0.06em' }}>{h}</th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {result.areas?.map((row, i) => {
                        const d = RISK_ORDER[row.simulated_risk] - RISK_ORDER[row.original_risk];
                        return (
                          <tr key={row.area} style={{ borderBottom: '1px solid rgba(255,255,255,0.03)', background: i % 2 === 0 ? 'transparent' : 'rgba(0,0,0,0.1)' }}>
                            <td style={{ padding: '7px 10px', fontFamily: 'Orbitron', fontSize: 10, color: 'var(--electric)' }}>#{row.simulated_patrol_priority}</td>
                            <td style={{ padding: '7px 10px', color: '#E8F4FD', fontWeight: 500 }}>{row.area}</td>
                            <td style={{ padding: '7px 10px' }}><RiskBadge level={row.original_risk} small /></td>
                            <td style={{ padding: '7px 10px' }}><RiskBadge level={row.simulated_risk} small /></td>
                            <td style={{ padding: '7px 10px' }}>
                              <div style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
                                <DeltaIcon orig={row.original_risk} sim={row.simulated_risk} />
                                <span style={{ fontSize: 10, color: d > 0 ? '#FF1744' : d < 0 ? '#00E676' : 'var(--text-muted)' }}>
                                  {row.change_pct > 0 ? '+' : ''}{row.change_pct}%
                                </span>
                              </div>
                            </td>
                            <td style={{ padding: '7px 10px', fontFamily: 'Orbitron', fontSize: 10, color: 'var(--text-muted)' }}>{Math.round(row.original_score * 100)}</td>
                            <td style={{ padding: '7px 10px', fontFamily: 'Orbitron', fontSize: 10, color: RISK_COLORS[row.simulated_risk] }}>{Math.round(row.simulated_score * 100)}</td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
