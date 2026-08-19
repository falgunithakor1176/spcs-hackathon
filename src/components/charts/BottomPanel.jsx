import { useData } from '../../context/DataContext';
import { AREAS, CRIME_TYPES } from '../../data/mockData';
import { getCrimesByType, getCrimesByArea, getCrimesByMonth, getCrimesByHour, getCyberByType, getTotalAmountLost } from '../../data/analyticsUtils';
import React, { useState } from 'react';
import {
  AreaChart, Area, BarChart, Bar, PieChart, Pie, Cell,
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend
} from 'recharts';



const CYBER_COLORS = ['#FF1744','#FF6D00','#FFD600','#00D4FF','#60A5FA','#A78BFA'];
const CRIME_COLORS_ARR = ['#FF1744','#FF6D00','#FFD600','#60A5FA','#34D399','#E879F9'];

const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null;
  return (
    <div className="tooltip-content">
      <div style={{ color: 'var(--electric)', fontSize: 11, marginBottom: 4, fontFamily: 'Orbitron' }}>{label}</div>
      {payload.map((p, i) => (
        <div key={i} style={{ color: '#E8F4FD', fontSize: 11 }}>
          <span style={{ color: p.color }}>■ </span>
          {p.name}: <strong>{p.value?.toLocaleString()}</strong>
        </div>
      ))}
    </div>
  );
};

export default function BottomPanel() {
  const { crimes, hotspots, patrols, routes, cybercrime, alerts, predictions, loading } = useData();
  if (loading) return <div>Loading...</div>;

  const crimesByMonth = getCrimesByMonth(crimes);
  const crimesByHour = getCrimesByHour(crimes);
  const cyberByType = getCyberByType(cybercrime).slice(0, 6);
  const crimesByType = getCrimesByType(crimes).slice(0, 6);

  const [activeTab, setActiveTab] = useState('trend');

  const tabs = [
    { id: 'trend',  label: 'Crime Trend' },
    { id: 'hourly', label: 'Hourly Pattern' },
    { id: 'cyber',  label: 'Cybercrime' },
    { id: 'types',  label: 'Crime Types' },
  ];

  return (
    <div className="bottom-panel flex flex-col" style={{ height: 220 }}>
      {/* Tab Header */}
      <div className="flex items-center gap-1 px-4 pt-2 pb-0 border-b border-electric/5">
        {tabs.map(tab => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className="px-3 py-1.5 text-xs rounded-t font-medium transition-all"
            style={{
              fontFamily: 'Orbitron, monospace',
              fontSize: 9,
              letterSpacing: '0.08em',
              color: activeTab === tab.id ? 'var(--electric)' : 'var(--text-muted)',
              borderBottom: activeTab === tab.id ? '2px solid var(--electric)' : '2px solid transparent',
              background: activeTab === tab.id ? 'rgba(0,212,255,0.05)' : 'transparent',
            }}
          >
            {tab.label.toUpperCase()}
          </button>
        ))}

        {/* Right side — live indicator */}
        <div className="ml-auto flex items-center gap-2">
          <div className="live-dot" />
          <span style={{ color: '#00E676', fontSize: 9, fontFamily: 'JetBrains Mono' }}>AUTO-REFRESH</span>
        </div>
      </div>

      {/* Chart Area */}
      <div className="flex-1 px-4 py-2">
        {activeTab === 'trend' && (
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={crimesByMonth} margin={{ top: 5, right: 20, bottom: 0, left: 0 }}>
              <defs>
                <linearGradient id="crimeGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#FF1744" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="#FF1744" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(0,212,255,0.05)" />
              <XAxis dataKey="month" tick={{ fill: '#4A6580', fontSize: 10 }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fill: '#4A6580', fontSize: 10 }} axisLine={false} tickLine={false} />
              <Tooltip content={<CustomTooltip />} />
              <Area type="monotone" dataKey="crimes" name="Crimes" stroke="#FF1744" strokeWidth={2}
                fill="url(#crimeGrad)" dot={false} activeDot={{ r: 4, fill: '#FF1744' }} />
            </AreaChart>
          </ResponsiveContainer>
        )}

        {activeTab === 'hourly' && (
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={crimesByHour.filter((_, i) => i % 2 === 0)} margin={{ top: 5, right: 20, bottom: 0, left: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(0,212,255,0.05)" vertical={false} />
              <XAxis dataKey="hour" tick={{ fill: '#4A6580', fontSize: 9 }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fill: '#4A6580', fontSize: 9 }} axisLine={false} tickLine={false} />
              <Tooltip content={<CustomTooltip />} />
              <Bar dataKey="count" name="Incidents" fill="#00D4FF" radius={[2, 2, 0, 0]} opacity={0.8} />
            </BarChart>
          </ResponsiveContainer>
        )}

        {activeTab === 'cyber' && (
          <div className="flex items-center gap-4 h-full">
            <ResponsiveContainer width="40%" height="100%">
              <PieChart>
                <Pie data={cyberByType} dataKey="value" nameKey="name" cx="50%" cy="50%" innerRadius={30} outerRadius={60} paddingAngle={3}>
                  {cyberByType.map((entry, i) => (
                    <Cell key={i} fill={CYBER_COLORS[i % CYBER_COLORS.length]} opacity={0.85} />
                  ))}
                </Pie>
                <Tooltip content={<CustomTooltip />} />
              </PieChart>
            </ResponsiveContainer>
            <div className="flex-1 space-y-1">
              {cyberByType.map((item, i) => (
                <div key={item.name} className="flex items-center gap-2">
                  <div className="w-2 h-2 rounded-full flex-shrink-0"
                    style={{ background: CYBER_COLORS[i % CYBER_COLORS.length] }} />
                  <span className="text-xs flex-1 truncate" style={{ color: 'var(--text-secondary)', fontSize: 10 }}>{item.name}</span>
                  <span className="text-xs font-bold font-mono-code"
                    style={{ color: CYBER_COLORS[i % CYBER_COLORS.length] }}>{item.value}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab === 'types' && (
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={crimesByType} layout="vertical" margin={{ top: 5, right: 20, bottom: 0, left: 60 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(0,212,255,0.05)" horizontal={false} />
              <XAxis type="number" tick={{ fill: '#4A6580', fontSize: 9 }} axisLine={false} tickLine={false} />
              <YAxis type="category" dataKey="name" tick={{ fill: '#94A3B8', fontSize: 10 }} axisLine={false} tickLine={false} width={60} />
              <Tooltip content={<CustomTooltip />} />
              <Bar dataKey="value" name="Count" radius={[0, 2, 2, 0]} opacity={0.85}>
                {crimesByType.map((_, i) => (
                  <Cell key={i} fill={CRIME_COLORS_ARR[i % CRIME_COLORS_ARR.length]} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        )}
      </div>
    </div>
  );
}
