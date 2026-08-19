import React, { useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import { Radio, MapPin, Wifi, Clock, AlertTriangle } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';

const PAGE_TITLES = {
  '/command':    { title: 'COMMAND CENTER',        sub: 'Live Operations Dashboard' },
  '/analytics':  { title: 'CRIME ANALYTICS',       sub: 'Pattern Analysis & Trends' },
  '/cybercrime': { title: 'CYBER INTELLIGENCE',     sub: 'Digital Crime Monitoring' },
  '/patrol':     { title: 'PATROL MANAGEMENT',      sub: 'Route Optimization & Tracking' },
  '/alerts':     { title: 'ALERT CENTER',           sub: 'Real-time Incident Notifications' },
  '/settings':   { title: 'SYSTEM SETTINGS',        sub: 'Platform Configuration' },
};

const THREAT_CONFIG = {
  NORMAL:   { label: 'NORMAL',   color: '#00BFA5', bg: 'rgba(0,191,165,0.1)',   border: 'rgba(0,191,165,0.25)',   pulse: false },
  ELEVATED: { label: 'ELEVATED', color: '#FFD600', bg: 'rgba(255,214,0,0.1)',   border: 'rgba(255,214,0,0.3)',    pulse: false },
  HIGH:     { label: 'HIGH',     color: '#FF6D00', bg: 'rgba(255,109,0,0.12)',  border: 'rgba(255,109,0,0.35)',   pulse: true  },
  CRITICAL: { label: 'CRITICAL', color: '#FF1744', bg: 'rgba(255,23,68,0.15)',  border: 'rgba(255,23,68,0.4)',    pulse: true  },
};

function LiveClock() {
  const [time, setTime] = useState(new Date());
  useEffect(() => {
    const t = setInterval(() => setTime(new Date()), 1000);
    return () => clearInterval(t);
  }, []);
  return (
    <div className="flex items-center gap-2 text-xs font-mono-code">
      <Clock size={12} style={{ color: 'var(--electric)' }} />
      <span style={{ color: 'var(--text-secondary)' }}>
        {time.toLocaleDateString('en-IN', { day:'2-digit', month:'short', year:'numeric' })}
      </span>
      <span className="font-semibold" style={{ color: 'var(--electric)', fontFamily: 'JetBrains Mono' }}>
        {time.toLocaleTimeString('en-IN', { hour12: false })}
      </span>
    </div>
  );
}

function ThreatBadge({ level = 'HIGH' }) {
  const config = THREAT_CONFIG[level] || THREAT_CONFIG.HIGH;
  const [blink, setBlink] = useState(true);
  useEffect(() => {
    if (!config.pulse) return;
    const t = setInterval(() => setBlink(b => !b), 700);
    return () => clearInterval(t);
  }, [config.pulse]);

  return (
    <div className="flex items-center gap-2 px-3 py-1.5 rounded"
      style={{ background: config.bg, border: `1px solid ${config.border}` }}>
      <div className="relative flex items-center justify-center">
        {config.pulse && (
          <div className="absolute w-4 h-4 rounded-full"
            style={{ background: config.bg, border: `1px solid ${config.color}`, animation: 'pulseRing 1.5s ease-out infinite' }} />
        )}
        <div className="w-2 h-2 rounded-full" style={{
          background: config.color,
          boxShadow: `0 0 6px ${config.color}`,
          opacity: config.pulse ? (blink ? 1 : 0.4) : 1,
        }} />
      </div>
      <div>
        <div className="text-xs font-orbitron font-bold" style={{ color: config.color, fontSize: '9px', letterSpacing: '0.12em' }}>
          THREAT LEVEL
        </div>
        <div className="font-orbitron font-bold" style={{ color: config.color, fontSize: '11px', letterSpacing: '0.08em' }}>
          {config.label}
        </div>
      </div>
    </div>
  );
}

import { useData } from '../../context/DataContext';

export default function TopHeader() {
  const { user } = useAuth();
  const location = useLocation();
  const { crimes, patrols, riskIndex } = useData() || {};
  
  const pageInfo = PAGE_TITLES[location.pathname] || PAGE_TITLES['/command'];

  // Dynamic threat level thresholds:
  // Risk > 80: CRITICAL, Risk > 60: HIGH, Risk > 40: ELEVATED (Medium), Else NORMAL (Low)
  let threatLevel = 'NORMAL';
  if (riskIndex > 80) {
    threatLevel = 'CRITICAL';
  } else if (riskIndex > 60) {
    threatLevel = 'HIGH';
  } else if (riskIndex > 40) {
    threatLevel = 'ELEVATED';
  } else {
    threatLevel = 'NORMAL';
  }

  const now = new Date();
  const last24h = new Date(now.getTime() - 24 * 3600000);
  const crimes_today = crimes?.filter(c => new Date(c.timestamp) > last24h).length || 0;
  const active_patrols = patrols?.filter(p => p.status === 'On Patrol').length || 0;

  return (
    <header className="flex-shrink-0 flex items-center justify-between px-4 border-b"
      style={{
        height: '56px',
        background: 'linear-gradient(90deg, #060d1a 0%, #081120 50%, #060d1a 100%)',
        borderColor: 'rgba(0,212,255,0.08)',
        boxShadow: '0 1px 0 rgba(0,212,255,0.05), 0 4px 20px rgba(0,0,0,0.5)',
      }}>

      {/* LEFT: Brand + Page Title */}
      <div className="flex items-center gap-4">
        {/* Brand */}
        <div className="flex items-center gap-2">
          <div className="flex items-center gap-1">
            <Radio size={14} style={{ color: 'var(--electric)' }} />
            <span className="font-orbitron font-bold text-xs tracking-widest"
              style={{ color: 'var(--electric)', letterSpacing: '0.15em' }}>
              SPCS
            </span>
          </div>
          <div className="w-px h-5" style={{ background: 'rgba(0,212,255,0.15)' }} />
        </div>

        {/* Page Title */}
        <div>
          <div className="font-orbitron font-bold" style={{ fontSize: '12px', color: '#E8F4FD', letterSpacing: '0.1em' }}>
            {pageInfo.title}
          </div>
          <div className="text-xs" style={{ color: 'var(--text-muted)', fontSize: '10px' }}>
            {pageInfo.sub}
          </div>
        </div>
      </div>

      {/* CENTER: Location + Live stats ticker */}
      <div className="hidden lg:flex items-center gap-5">
        <div className="flex items-center gap-1.5">
          <MapPin size={12} style={{ color: 'var(--electric)' }} />
          <span className="text-xs font-medium" style={{ color: 'var(--text-secondary)' }}>
            Ahmedabad City, Gujarat
          </span>
        </div>

        {/* Live incident counter */}
        <div className="flex items-center gap-2 px-3 py-1 rounded"
          style={{ background: 'rgba(255,23,68,0.08)', border: '1px solid rgba(255,23,68,0.15)' }}>
          <AlertTriangle size={11} style={{ color: '#FF1744' }} />
          <span className="text-xs font-orbitron font-bold" style={{ color: '#FF1744', letterSpacing: '0.05em' }}>
            {crimes_today}
          </span>
          <span className="text-xs" style={{ color: 'var(--text-muted)', fontSize: '10px' }}>AUTO-REFRESH</span>
        </div>

        {/* Active patrol counter */}
        <div className="flex items-center gap-2 px-3 py-1 rounded"
          style={{ background: 'rgba(0,212,255,0.06)', border: '1px solid rgba(0,212,255,0.12)' }}>
          <div className="live-dot" />
          <span className="text-xs font-orbitron font-bold" style={{ color: 'var(--electric)', letterSpacing: '0.05em' }}>
            {active_patrols}
          </span>
          <span className="text-xs" style={{ color: 'var(--text-muted)', fontSize: '10px' }}>UNITS</span>
        </div>
      </div>

      {/* RIGHT: Threat Level + Clock + User */}
      <div className="flex items-center gap-3">
        <ThreatBadge level={threatLevel} />

        <div className="w-px h-8" style={{ background: 'rgba(0,212,255,0.08)' }} />

        <LiveClock />

        <div className="w-px h-8" style={{ background: 'rgba(0,212,255,0.08)' }} />

        {/* Connectivity status */}
        <div className="flex items-center gap-1.5">
          <Wifi size={13} style={{ color: '#00E676' }} />
          <span className="text-xs" style={{ color: '#00E676', fontSize: '10px', fontFamily: 'JetBrains Mono' }}>ONLINE</span>
        </div>

        {/* User badge */}
        <div className="flex items-center gap-2 pl-2 border-l border-electric/10">
          <div className="flex items-center justify-center w-7 h-7 rounded-full text-xs font-bold"
            style={{ background: 'rgba(0,102,255,0.25)', border: '1px solid rgba(0,212,255,0.2)', color: 'var(--electric)' }}>
            {user?.name?.split(' ').slice(-1)[0]?.[0] || 'U'}
          </div>
          <div className="hidden xl:block">
            <div className="text-xs font-medium" style={{ color: 'var(--text-primary)', fontSize: '11px' }}>
              {user?.name}
            </div>
            <div style={{ color: 'var(--text-muted)', fontSize: '9px' }}>{user?.role}</div>
          </div>
        </div>
      </div>
    </header>
  );
}
