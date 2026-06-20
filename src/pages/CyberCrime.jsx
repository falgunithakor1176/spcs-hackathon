import { useData } from '../context/DataContext';
import { AREAS, CRIME_TYPES } from '../data/mockData';
import { getCrimesByType, getCrimesByArea, getCrimesByMonth, getCrimesByHour, getCyberByType, getTotalAmountLost } from '../data/analyticsUtils';
import React, { useMemo } from 'react';
import {
  BarChart, Bar, PieChart, Pie, Cell, LineChart, Line,
  XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, AreaChart, Area
} from 'recharts';
import { Shield, DollarSign, TrendingUp, AlertTriangle, Zap } from 'lucide-react';

const COLORS = ['#FF1744','#FF6D00','#FFD600','#00D4FF','#A78BFA','#60A5FA','#34D399','#F97316','#E879F9','#FB923C'];

const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null;
  return (
    <div className="tooltip-content">
      <div style={{ color: 'var(--electric)', fontSize: 11, marginBottom: 4, fontFamily: 'Orbitron' }}>{label}</div>
      {payload.map((p, i) => (
        <div key={i} style={{ color: '#E8F4FD', fontSize: 11 }}>
          <span style={{ color: p.color }}>■ </span>{p.name}: <strong>{typeof p.value === 'number' ? p.value.toLocaleString() : p.value}</strong>
        </div>
      ))}
    </div>
  );
};

function KPI({ icon: Icon, label, value, sub, color }) {
  return (
    <div className="glass-card p-4 rounded-lg flex items-center gap-4"
      style={{ borderLeft: `3px solid ${color}` }}>
      <div className="flex items-center justify-center w-11 h-11 rounded-lg"
        style={{ background: `${color}15`, border: `1px solid ${color}25` }}>
        <Icon size={20} style={{ color }} />
      </div>
      <div>
        <div className="font-orbitron font-bold" style={{ color, fontSize: 20 }}>{value}</div>
        <div className="text-xs font-medium" style={{ color: '#E8F4FD', fontSize: 11 }}>{label}</div>
        {sub && <div style={{ color: 'var(--text-muted)', fontSize: 10 }}>{sub}</div>}
      </div>
    </div>
  );
}

export default function CyberCrime() {
  const { crimes, hotspots, patrols, routes, cybercrime, alerts, predictions, loading } = useData();
  if (loading) return <div>Loading...</div>;

  const byType = getCyberByType(cybercrime);
  const totalLost = getTotalAmountLost(cybercrime);

  // Monthly cybercrime trend
  const monthlyTrend = useMemo(() => {
    const months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
    const counts = Array(12).fill(0);
    const amounts = Array(12).fill(0);
    cybercrime.forEach(c => {
      counts[c.month - 1]++;
      amounts[c.month - 1] += c.amount_lost;
    });
    return months.map((m, i) => ({ month: m, reports: counts[i], amount: Math.round(amounts[i] / 1000) }));
  }, []);

  // Platform breakdown
  const byPlatform = useMemo(() => {
    const counts = {};
    cybercrime.forEach(c => { counts[c.platform] = (counts[c.platform] || 0) + 1; });
    return Object.entries(counts).map(([name, value]) => ({ name, value })).sort((a, b) => b.value - a.value);
  }, []);

  // Age group distribution
  const byAge = useMemo(() => {
    const counts = {};
    cybercrime.forEach(c => { counts[c.victim_age_group] = (counts[c.victim_age_group] || 0) + 1; });
    return Object.entries(counts).map(([name, value]) => ({ name, value })).sort((a, b) => a.name.localeCompare(b.name));
  }, []);

  // Correlation: cybercrime vs physical crime by area
  const correlation = useMemo(() => {
    const cyberByArea = {};
    cybercrime.forEach(c => { cyberByArea[c.area] = (cyberByArea[c.area] || 0) + 1; });
    const physByArea = {};
    crimes.forEach(c => { physByArea[c.area] = (physByArea[c.area] || 0) + 1; });
    return Object.keys(cyberByArea).slice(0, 8).map(area => ({
      area: area.length > 10 ? area.slice(0, 10) + '..' : area,
      cyber: cyberByArea[area] || 0,
      physical: Math.round((physByArea[area] || 0) / 10),
    }));
  }, []);

  return (
    <div className="h-full overflow-y-auto page-enter" style={{ background: '#060d1a' }}>
      <div className="p-4">

        {/* KPI Row */}
        <div className="grid grid-cols-4 gap-3 mb-4">
          <KPI icon={Shield} label="Total Reports" value={cybercrime.length.toLocaleString()}
            sub="All time" color="#A78BFA" />
          <KPI icon={DollarSign} label="Total Amount Lost"
            value={`₹${(totalLost / 100000).toFixed(1)}L`}
            sub="Estimated losses" color="#FF1744" />
          <KPI icon={AlertTriangle} label="Active Cases"
            value={cybercrime.filter(c => c.status === 'Under Investigation').length}
            sub="Under investigation" color="#FF6D00" />
          <KPI icon={Zap} label="Recovery Rate"
            value="23.4%"
            sub="Amount recovered" color="#00E676" />
        </div>

        <div className="grid grid-cols-2 gap-4 mb-4">
          {/* Fraud Type Breakdown */}
          <div className="glass-card p-4 rounded-lg">
            <div className="font-orbitron font-bold text-sm mb-1" style={{ color: '#E8F4FD' }}>Fraud Type Distribution</div>
            <div style={{ color: 'var(--text-muted)', fontSize: 11, marginBottom: 12 }}>Cases by cybercrime category</div>
            <div className="flex gap-4">
              <ResponsiveContainer width="50%" height={180}>
                <PieChart>
                  <Pie data={byType.slice(0, 7)} dataKey="value" cx="50%" cy="50%"
                    innerRadius={40} outerRadius={75} paddingAngle={2}>
                    {byType.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} opacity={0.9} />)}
                  </Pie>
                  <Tooltip content={<CustomTooltip />} />
                </PieChart>
              </ResponsiveContainer>
              <div className="flex-1 space-y-1.5">
                {byType.slice(0, 7).map((item, i) => (
                  <div key={item.name} className="flex items-center gap-2">
                    <div className="w-2 h-2 rounded-full flex-shrink-0" style={{ background: COLORS[i % COLORS.length] }} />
                    <span className="flex-1 text-xs truncate" style={{ color: 'var(--text-secondary)' }}>{item.name}</span>
                    <span className="text-xs font-bold" style={{ color: COLORS[i % COLORS.length], fontFamily: 'JetBrains Mono' }}>{item.value}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Monthly Trend */}
          <div className="glass-card p-4 rounded-lg">
            <div className="font-orbitron font-bold text-sm mb-1" style={{ color: '#E8F4FD' }}>Monthly Cybercrime Trend</div>
            <div style={{ color: 'var(--text-muted)', fontSize: 11, marginBottom: 12 }}>Report count per month</div>
            <ResponsiveContainer width="100%" height={180}>
              <AreaChart data={monthlyTrend}>
                <defs>
                  <linearGradient id="cyberGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#A78BFA" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#A78BFA" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(0,212,255,0.05)" />
                <XAxis dataKey="month" tick={{ fill: '#4A6580', fontSize: 10 }} axisLine={false} tickLine={false} />
                <YAxis tick={{ fill: '#4A6580', fontSize: 10 }} axisLine={false} tickLine={false} />
                <Tooltip content={<CustomTooltip />} />
                <Area type="monotone" dataKey="reports" name="Reports" stroke="#A78BFA" strokeWidth={2}
                  fill="url(#cyberGrad)" dot={false} />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="grid grid-cols-3 gap-4 mb-4">
          {/* Platform */}
          <div className="glass-card p-4 rounded-lg">
            <div className="font-orbitron font-bold text-sm mb-3" style={{ color: '#E8F4FD' }}>Attack Platforms</div>
            <div className="space-y-2">
              {byPlatform.map((p, i) => {
                const max = byPlatform[0]?.value || 1;
                return (
                  <div key={p.name}>
                    <div className="flex justify-between mb-0.5">
                      <span style={{ color: 'var(--text-secondary)', fontSize: 11 }}>{p.name}</span>
                      <span style={{ color: COLORS[i], fontSize: 11, fontFamily: 'JetBrains Mono' }}>{p.value}</span>
                    </div>
                    <div className="progress-track h-1.5">
                      <div className="progress-fill h-full" style={{ width: `${(p.value / max) * 100}%`, background: COLORS[i] }} />
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Victim Age */}
          <div className="glass-card p-4 rounded-lg">
            <div className="font-orbitron font-bold text-sm mb-3" style={{ color: '#E8F4FD' }}>Victim Age Groups</div>
            <ResponsiveContainer width="100%" height={180}>
              <BarChart data={byAge}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(0,212,255,0.05)" vertical={false} />
                <XAxis dataKey="name" tick={{ fill: '#4A6580', fontSize: 10 }} axisLine={false} tickLine={false} />
                <YAxis tick={{ fill: '#4A6580', fontSize: 10 }} axisLine={false} tickLine={false} />
                <Tooltip content={<CustomTooltip />} />
                <Bar dataKey="value" name="Victims" fill="#FF6D00" radius={[3, 3, 0, 0]} opacity={0.85} />
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* Correlation */}
          <div className="glass-card p-4 rounded-lg">
            <div className="font-orbitron font-bold text-sm mb-1" style={{ color: '#E8F4FD' }}>Cyber vs Physical Crime</div>
            <div style={{ color: 'var(--text-muted)', fontSize: 10, marginBottom: 10 }}>Area-wise correlation</div>
            <ResponsiveContainer width="100%" height={180}>
              <BarChart data={correlation}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(0,212,255,0.05)" vertical={false} />
                <XAxis dataKey="area" tick={{ fill: '#4A6580', fontSize: 8 }} axisLine={false} tickLine={false} angle={-30} textAnchor="end" height={40} />
                <YAxis tick={{ fill: '#4A6580', fontSize: 9 }} axisLine={false} tickLine={false} />
                <Tooltip content={<CustomTooltip />} />
                <Bar dataKey="cyber" name="Cyber" fill="#A78BFA" radius={[2, 2, 0, 0]} opacity={0.85} />
                <Bar dataKey="physical" name="Physical" fill="#FF1744" radius={[2, 2, 0, 0]} opacity={0.7} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
}
