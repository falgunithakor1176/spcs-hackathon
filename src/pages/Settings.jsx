import React, { useState } from 'react';
import { Settings as SettingsIcon, User, Shield, Bell, Database, Sliders, Save, ChevronRight } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

function SettingSection({ icon: Icon, title, children }) {
  return (
    <div className="glass-card p-5 rounded-lg mb-4">
      <div className="flex items-center gap-2 mb-4 pb-3"
        style={{ borderBottom: '1px solid rgba(0,212,255,0.08)' }}>
        <div className="flex items-center justify-center w-8 h-8 rounded-lg"
          style={{ background: 'rgba(0,212,255,0.1)', border: '1px solid rgba(0,212,255,0.2)' }}>
          <Icon size={15} style={{ color: 'var(--electric)' }} />
        </div>
        <span className="font-orbitron font-bold text-sm" style={{ color: '#E8F4FD', letterSpacing: '0.08em' }}>
          {title}
        </span>
      </div>
      {children}
    </div>
  );
}

function SettingRow({ label, description, children }) {
  return (
    <div className="flex items-center justify-between py-3 border-b" style={{ borderColor: 'rgba(0,212,255,0.04)' }}>
      <div>
        <div className="text-sm font-medium" style={{ color: '#E8F4FD' }}>{label}</div>
        {description && <div style={{ color: 'var(--text-muted)', fontSize: 11, marginTop: 1 }}>{description}</div>}
      </div>
      <div className="flex-shrink-0 ml-4">{children}</div>
    </div>
  );
}

function Toggle({ value, onChange }) {
  return (
    <button onClick={() => onChange(!value)}
      className="relative w-11 h-6 rounded-full transition-all"
      style={{ background: value ? 'rgba(0,212,255,0.4)' : 'rgba(0,0,0,0.4)', border: `1px solid ${value ? 'rgba(0,212,255,0.5)' : 'rgba(255,255,255,0.1)'}` }}>
      <div className="absolute top-0.5 w-5 h-5 rounded-full transition-all"
        style={{
          left: value ? '22px' : '2px',
          background: value ? 'var(--electric)' : '#4A6580',
          boxShadow: value ? '0 0 8px rgba(0,212,255,0.6)' : 'none',
        }} />
    </button>
  );
}

function RangeInput({ value, onChange, min, max, label }) {
  return (
    <div className="flex items-center gap-3">
      <input type="range" min={min} max={max} value={value}
        onChange={e => onChange(+e.target.value)}
        style={{ accentColor: 'var(--electric)', width: 120 }} />
      <span className="font-orbitron font-bold w-8" style={{ color: 'var(--electric)', fontSize: 12 }}>{value}</span>
      {label && <span style={{ color: 'var(--text-muted)', fontSize: 11 }}>{label}</span>}
    </div>
  );
}

export default function Settings() {
  const { user } = useAuth();
  const [saved, setSaved] = useState(false);
  const [settings, setSettings] = useState({
    alertNotifications: true,
    emailAlerts: false,
    smsAlerts: false,
    autoRefresh: true,
    refreshInterval: 30,
    mapClustering: true,
    showPatrolRoutes: true,
    dbscanEpsilon: 0.5,
    dbscanMinSamples: 5,
    riskThresholdCritical: 80,
    riskThresholdHigh: 60,
    riskThresholdMedium: 40,
    dataRetentionDays: 365,
    auditLogs: true,
    twoFactorAuth: false,
    sessionTimeout: 60,
  });

  const update = (key, value) => setSettings(prev => ({ ...prev, [key]: value }));
  const handleSave = () => {
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  };

  if (user?.role !== 'Admin') {
    return (
      <div className="flex items-center justify-center h-full page-enter" style={{ background: '#060d1a' }}>
        <div className="text-center">
          <Shield size={48} style={{ color: 'rgba(255,23,68,0.4)', margin: '0 auto 16px' }} />
          <div className="font-orbitron font-bold text-lg mb-2" style={{ color: '#FF1744' }}>ACCESS DENIED</div>
          <div style={{ color: 'var(--text-muted)' }}>Admin privileges required to access Settings.</div>
        </div>
      </div>
    );
  }

  return (
    <div className="h-full overflow-y-auto page-enter" style={{ background: '#060d1a' }}>
      <div className="p-4 max-w-3xl mx-auto">

        <SettingSection icon={User} title="USER PROFILE">
          <SettingRow label="Display Name" description="Your name shown in the command center">
            <input defaultValue={user.name} className="cmd-input px-3 py-1.5 text-sm w-48" />
          </SettingRow>
          <SettingRow label="Badge Number" description="Law enforcement badge identifier">
            <input defaultValue={user.badge} className="cmd-input px-3 py-1.5 text-sm w-48" readOnly
              style={{ opacity: 0.6 }} />
          </SettingRow>
          <SettingRow label="Role" description="System access role">
            <span className="badge-active px-2 py-1 rounded text-xs">{user.role}</span>
          </SettingRow>
        </SettingSection>

        <SettingSection icon={Bell} title="ALERT CONFIGURATION">
          <SettingRow label="Dashboard Notifications" description="Show alerts in the notification panel">
            <Toggle value={settings.alertNotifications} onChange={v => update('alertNotifications', v)} />
          </SettingRow>
          <SettingRow label="Email Alerts" description="Send critical alerts via email">
            <Toggle value={settings.emailAlerts} onChange={v => update('emailAlerts', v)} />
          </SettingRow>
          <SettingRow label="SMS Alerts" description="Send alerts via SMS (requires integration)">
            <Toggle value={settings.smsAlerts} onChange={v => update('smsAlerts', v)} />
          </SettingRow>
          <SettingRow label="Auto-Refresh Interval" description="Dashboard data refresh frequency">
            <RangeInput value={settings.refreshInterval} onChange={v => update('refreshInterval', v)} min={10} max={120} label="sec" />
          </SettingRow>
        </SettingSection>

        <SettingSection icon={Sliders} title="AI / ML THRESHOLDS">
          <SettingRow label="Critical Risk Threshold" description="Score above this = Critical zone">
            <RangeInput value={settings.riskThresholdCritical} onChange={v => update('riskThresholdCritical', v)} min={60} max={100} label="/100" />
          </SettingRow>
          <SettingRow label="High Risk Threshold" description="Score above this = High risk zone">
            <RangeInput value={settings.riskThresholdHigh} onChange={v => update('riskThresholdHigh', v)} min={40} max={80} label="/100" />
          </SettingRow>
          <SettingRow label="DBSCAN Epsilon (km)" description="Max distance between crime cluster points">
            <RangeInput value={settings.dbscanEpsilon * 10} onChange={v => update('dbscanEpsilon', v / 10)} min={1} max={20} label="× 0.1 km" />
          </SettingRow>
          <SettingRow label="DBSCAN Min Samples" description="Minimum crimes to form a cluster">
            <RangeInput value={settings.dbscanMinSamples} onChange={v => update('dbscanMinSamples', v)} min={2} max={20} />
          </SettingRow>
        </SettingSection>

        <SettingSection icon={SettingsIcon} title="MAP SETTINGS">
          <SettingRow label="Marker Clustering" description="Group nearby crime markers on map">
            <Toggle value={settings.mapClustering} onChange={v => update('mapClustering', v)} />
          </SettingRow>
          <SettingRow label="Show Patrol Routes" description="Display patrol routes on map by default">
            <Toggle value={settings.showPatrolRoutes} onChange={v => update('showPatrolRoutes', v)} />
          </SettingRow>
        </SettingSection>

        <SettingSection icon={Shield} title="SECURITY">
          <SettingRow label="Two-Factor Authentication" description="Require OTP for login">
            <Toggle value={settings.twoFactorAuth} onChange={v => update('twoFactorAuth', v)} />
          </SettingRow>
          <SettingRow label="Audit Logs" description="Log all user actions for compliance">
            <Toggle value={settings.auditLogs} onChange={v => update('auditLogs', v)} />
          </SettingRow>
          <SettingRow label="Session Timeout" description="Auto-logout after inactivity">
            <RangeInput value={settings.sessionTimeout} onChange={v => update('sessionTimeout', v)} min={15} max={480} label="min" />
          </SettingRow>
        </SettingSection>

        <SettingSection icon={Database} title="DATA MANAGEMENT">
          <SettingRow label="Data Retention" description="Keep crime records for this many days">
            <RangeInput value={settings.dataRetentionDays} onChange={v => update('dataRetentionDays', v)} min={90} max={1825} label="days" />
          </SettingRow>
        </SettingSection>

        {/* Save Button */}
        <div className="flex justify-end gap-3 pb-4">
          <button className="btn-ghost px-6 py-2.5">RESET DEFAULTS</button>
          <button onClick={handleSave} className="btn-primary px-6 py-2.5 flex items-center gap-2"
            style={{ borderRadius: 6 }}>
            <Save size={14} />
            {saved ? '✓ SAVED!' : 'SAVE SETTINGS'}
          </button>
        </div>
      </div>
    </div>
  );
}
