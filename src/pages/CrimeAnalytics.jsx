import { useData } from '../context/DataContext';
import { AREAS, CRIME_TYPES } from '../data/mockData';
import { getCrimesByType, getCrimesByArea, getCrimesByMonth, getCrimesByHour, getCyberByType, getTotalAmountLost } from '../data/analyticsUtils';
import React, { useState, useMemo } from 'react';
import {
  AreaChart, Area, BarChart, Bar, LineChart, Line, ScatterChart, Scatter,
  XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, Legend
} from 'recharts';
import { TrendingUp, BarChart3, Filter, Download } from 'lucide-react';

const COLORS = ['#FF1744','#FF6D00','#FFD600','#00D4FF','#00E676','#A78BFA','#F97316','#60A5FA','#34D399','#E879F9'];

const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null;
  return (
    <div className="tooltip-content">
      <div style={{ color: 'var(--electric)', fontSize: 11, marginBottom: 4, fontFamily: 'Orbitron' }}>{label}</div>
      {payload.map((p, i) => (
        <div key={i} style={{ color: '#E8F4FD', fontSize: 11 }}>
          <span style={{ color: p.color }}>■ </span>{p.name}: <strong>{p.value?.toLocaleString()}</strong>
        </div>
      ))}
    </div>
  );
};

function SectionTitle({ title, subtitle }) {
  return (
    <div className="mb-4">
      <div className="font-orbitron font-bold text-sm tracking-wide" style={{ color: '#E8F4FD' }}>{title}</div>
      {subtitle && <div style={{ color: 'var(--text-muted)', fontSize: 11 }}>{subtitle}</div>}
    </div>
  );
}

function ChartCard({ title, subtitle, children, className = '' }) {
  return (
    <div className={`glass-card p-4 rounded-lg ${className}`}>
      <SectionTitle title={title} subtitle={subtitle} />
      {children}
    </div>
  );
}

export default function CrimeAnalytics() {
  const { crimes, hotspots, patrols, routes, cybercrime, alerts, predictions, loading } = useData();
  if (loading) return <div>Loading...</div>;

  const [yearFilter, setYearFilter] = useState('all');
  const [typeFilter, setTypeFilter] = useState('all');

  const filtered = useMemo(() => {
    let d = crimes;
    if (yearFilter !== 'all') d = d.filter(c => c.year === +yearFilter);
    if (typeFilter !== 'all') d = d.filter(c => c.crime_type === typeFilter);
    return d;
  }, [yearFilter, typeFilter]);

  const byType = getCrimesByType(filtered).slice(0, 10);
  const byArea = getCrimesByArea(filtered);
  const byMonth = getCrimesByMonth(filtered);
  const byHour = getCrimesByHour(filtered);

  const severityData = useMemo(() => {
    const counts = { Critical: 0, High: 0, Medium: 0, Low: 0 };
    filtered.forEach(c => { counts[c.severity] = (counts[c.severity] || 0) + 1; });
    return Object.entries(counts).map(([name, value]) => ({ name, value }));
  }, [filtered]);

  const sevColors = { Critical: '#FF1744', High: '#FF6D00', Medium: '#FFD600', Low: '#00E676' };

  return (
    <div className="h-full overflow-y-auto page-enter" style={{ background: '#060d1a' }}>
      <div className="p-4">

        {/* Filters */}
        <div className="flex items-center gap-3 mb-4 p-3 glass-card rounded-lg">
          <Filter size={14} style={{ color: 'var(--electric)' }} />
          <span className="section-header">FILTERS</span>
          <select className="cmd-input px-3 py-1.5 text-xs"
            value={yearFilter} onChange={e => setYearFilter(e.target.value)}>
            <option value="all">All Years</option>
            <option value="2023">2023</option>
            <option value="2024">2024</option>
            <option value="2025">2025</option>
          </select>
          <select className="cmd-input px-3 py-1.5 text-xs"
            value={typeFilter} onChange={e => setTypeFilter(e.target.value)}>
            <option value="all">All Crime Types</option>
            {CRIME_TYPES.map(t => <option key={t} value={t}>{t}</option>)}
          </select>
          <div className="ml-auto flex items-center gap-2">
            <span style={{ color: 'var(--electric)', fontSize: 12, fontFamily: 'Orbitron' }}>
              {filtered.length.toLocaleString()}
            </span>
            <span style={{ color: 'var(--text-muted)', fontSize: 11 }}>records</span>
          </div>
        </div>

        {/* Grid of charts */}
        <div className="grid grid-cols-2 gap-4 mb-4">
          <ChartCard title="Monthly Crime Trend" subtitle="Incidents reported per month">
            <ResponsiveContainer width="100%" height={200}>
              <AreaChart data={byMonth}>
                <defs>
                  <linearGradient id="areaGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#FF1744" stopOpacity={0.35} />
                    <stop offset="95%" stopColor="#FF1744" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(0,212,255,0.05)" />
                <XAxis dataKey="month" tick={{ fill: '#4A6580', fontSize: 10 }} axisLine={false} tickLine={false} />
                <YAxis tick={{ fill: '#4A6580', fontSize: 10 }} axisLine={false} tickLine={false} />
                <Tooltip content={<CustomTooltip />} />
                <Area type="monotone" dataKey="crimes" name="Crimes" stroke="#FF1744" strokeWidth={2}
                  fill="url(#areaGrad)" dot={false} activeDot={{ r: 4 }} />
              </AreaChart>
            </ResponsiveContainer>
          </ChartCard>

          <ChartCard title="Hourly Crime Pattern" subtitle="Crime distribution by hour of day">
            <ResponsiveContainer width="100%" height={200}>
              <BarChart data={byHour.filter((_, i) => i % 3 === 0)}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(0,212,255,0.05)" vertical={false} />
                <XAxis dataKey="hour" tick={{ fill: '#4A6580', fontSize: 9 }} axisLine={false} tickLine={false} />
                <YAxis tick={{ fill: '#4A6580', fontSize: 10 }} axisLine={false} tickLine={false} />
                <Tooltip content={<CustomTooltip />} />
                <Bar dataKey="count" name="Incidents" fill="#00D4FF" radius={[2, 2, 0, 0]} opacity={0.8} />
              </BarChart>
            </ResponsiveContainer>
          </ChartCard>
        </div>

        <div className="grid grid-cols-3 gap-4 mb-4">
          <div className="col-span-2">
            <ChartCard title="Crimes by Area" subtitle="Top 10 areas by incident count">
              <ResponsiveContainer width="100%" height={220}>
                <BarChart data={byArea} layout="vertical">
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(0,212,255,0.05)" horizontal={false} />
                  <XAxis type="number" tick={{ fill: '#4A6580', fontSize: 10 }} axisLine={false} tickLine={false} />
                  <YAxis type="category" dataKey="name" tick={{ fill: '#94A3B8', fontSize: 10 }} axisLine={false} tickLine={false} width={80} />
                  <Tooltip content={<CustomTooltip />} />
                  <Bar dataKey="value" name="Crimes" radius={[0, 2, 2, 0]} opacity={0.85}>
                    {byArea.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </ChartCard>
          </div>

          <ChartCard title="Severity Distribution" subtitle="Risk level breakdown">
            <ResponsiveContainer width="100%" height={140}>
              <PieChart>
                <Pie data={severityData} dataKey="value" nameKey="name" cx="50%" cy="50%"
                  innerRadius={35} outerRadius={65} paddingAngle={3}>
                  {severityData.map((entry) => (
                    <Cell key={entry.name} fill={sevColors[entry.name]} opacity={0.85} />
                  ))}
                </Pie>
                <Tooltip content={<CustomTooltip />} />
              </PieChart>
            </ResponsiveContainer>
            <div className="space-y-1 mt-2">
              {severityData.map(({ name, value }) => (
                <div key={name} className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <div className="w-2 h-2 rounded-full" style={{ background: sevColors[name] }} />
                    <span style={{ color: 'var(--text-secondary)', fontSize: 11 }}>{name}</span>
                  </div>
                  <span style={{ color: sevColors[name], fontSize: 11, fontFamily: 'JetBrains Mono' }}>
                    {value.toLocaleString()}
                  </span>
                </div>
              ))}
            </div>
          </ChartCard>
        </div>

        {/* Crime by type */}
        <ChartCard title="Crime Type Analysis" subtitle="Incident count by crime category">
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={byType}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(0,212,255,0.05)" vertical={false} />
              <XAxis dataKey="name" tick={{ fill: '#94A3B8', fontSize: 10 }} axisLine={false} tickLine={false} angle={-20} textAnchor="end" height={50} />
              <YAxis tick={{ fill: '#4A6580', fontSize: 10 }} axisLine={false} tickLine={false} />
              <Tooltip content={<CustomTooltip />} />
              <Bar dataKey="value" name="Crimes" radius={[3, 3, 0, 0]} opacity={0.85}>
                {byType.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>
      </div>
    </div>
  );
}
