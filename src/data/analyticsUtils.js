export function getCrimesByType(crimes) {
  if (!crimes) return [];
  const counts = {};
  crimes.forEach(c => { counts[c.crime_type] = (counts[c.crime_type] || 0) + 1; });
  return Object.entries(counts).map(([name, value]) => ({ name, value })).sort((a, b) => b.value - a.value);
}

export function getCrimesByArea(crimes) {
  if (!crimes) return [];
  const counts = {};
  crimes.forEach(c => { counts[c.area] = (counts[c.area] || 0) + 1; });
  return Object.entries(counts).map(([name, value]) => ({ name, value })).sort((a, b) => b.value - a.value).slice(0, 10);
}

export function getCrimesByMonth(crimes) {
  if (!crimes) return [];
  const months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
  const counts = Array(12).fill(0);
  crimes.forEach(c => { counts[(c.month || new Date(c.timestamp).getMonth() + 1) - 1]++; });
  return months.map((month, i) => ({ month, crimes: counts[i] }));
}

export function getCrimesByHour(crimes) {
  if (!crimes) return [];
  const counts = Array(24).fill(0);
  crimes.forEach(c => counts[c.hour !== undefined ? c.hour : new Date(c.timestamp).getHours()]++);
  return counts.map((count, hour) => ({ hour: `${String(hour).padStart(2,'0')}:00`, count }));
}

export function getCyberByType(cybercrime) {
  if (!cybercrime) return [];
  const counts = {};
  cybercrime.forEach(c => { counts[c.fraud_type] = (counts[c.fraud_type] || 0) + 1; });
  return Object.entries(counts).map(([name, value]) => ({ name, value })).sort((a, b) => b.value - a.value);
}

export function getTotalAmountLost(cybercrime) {
  if (!cybercrime) return 0;
  return cybercrime.reduce((sum, c) => sum + (c.amount_lost || 0), 0);
}

export function getDashboardStats(crimes, cybercrime, patrols, hotspots, riskIndex) {
  if (!crimes || !cybercrime || !patrols || !hotspots) {
    return {
      total_crimes: 0, crimes_today: 0, active_hotspots: 0, high_risk_areas: 0,
      active_patrols: 0, total_patrols: 0, cybercrime_reports: 0, cyber_today: 0,
      critical_alerts: 0, risk_index: 0, threat_level: 'LOADING'
    };
  }

  const now = new Date();
  const last24h = new Date(now.getTime() - 24 * 3600000);
  const recent = crimes.filter(c => new Date(c.timestamp) > last24h);
  return {
    total_crimes:      crimes.length,
    crimes_today:      recent.length,
    active_hotspots:   hotspots.length,
    high_risk_areas:   hotspots.filter(h => h.risk === 'Critical' || h.risk === 'High').length,
    active_patrols:    patrols.filter(p => p.status === 'On Patrol').length,
    total_patrols:     patrols.length,
    cybercrime_reports:cybercrime.length,
    cyber_today:       Math.floor(cybercrime.length * 0.04),
    critical_alerts:   recent.filter(c => c.severity === 'Critical').length,
    risk_index:        riskIndex,
    threat_level:      'HIGH',
  };
}
