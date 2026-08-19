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


/**
 * Returns the most recent 30-day and preceding 30-day date boundaries
 * anchored to the LATEST TIMESTAMP in the dataset — not the server clock.
 * This is necessary because the seeded dataset ends in mid-2025 while
 * the server clock may be in 2026, which would produce empty windows.
 */
function getDataAwareWindow(records) {
  if (!records || records.length === 0) {
    const now = new Date();
    return {
      latestDate:    now,
      current30dStart: new Date(now.getTime() - 30 * 86400000),
      prev30dStart:    new Date(now.getTime() - 60 * 86400000),
      prev30dEnd:      new Date(now.getTime() - 30 * 86400000),
    };
  }
  const latestDate = new Date(Math.max(...records.map(c => new Date(c.timestamp).getTime())));
  return {
    latestDate,
    current30dStart: new Date(latestDate.getTime() - 30 * 86400000),
    prev30dStart:    new Date(latestDate.getTime() - 60 * 86400000),
    prev30dEnd:      new Date(latestDate.getTime() - 30 * 86400000),
  };
}

/**
 * Compute a percentage-change string between two counts.
 * Returns null if previous is 0 (no basis for comparison).
 */
function computeTrendPct(current, previous) {
  if (previous === 0) return null;
  const pct = ((current - previous) / previous) * 100;
  return pct >= 0 ? `+${pct.toFixed(1)}%` : `${pct.toFixed(1)}%`;
}

export function getDashboardStats(crimes, cybercrime, patrols, hotspots, riskIndex) {
  if (!crimes || !cybercrime || !patrols || !hotspots) {
    return {
      total_crimes: 0, crimes_30d: 0, crimes_prev_30d: 0, crimes_trend: null,
      active_hotspots: 0, high_risk_areas: 0,
      active_patrols: 0, total_patrols: 0, responding_patrols: 0,
      cybercrime_reports: 0, cyber_30d: 0, cyber_prev_30d: 0, cyber_trend: null,
      critical_alerts: 0, risk_index: 0,
    };
  }

  // --- Crime trend (data-aware window) ---
  const crimeWindow  = getDataAwareWindow(crimes);
  const crimes_30d   = crimes.filter(c => {
    const t = new Date(c.timestamp);
    return t >= crimeWindow.current30dStart && t <= crimeWindow.latestDate;
  }).length;
  const crimes_prev  = crimes.filter(c => {
    const t = new Date(c.timestamp);
    return t >= crimeWindow.prev30dStart && t < crimeWindow.current30dStart;
  }).length;
  const crimes_trend = computeTrendPct(crimes_30d, crimes_prev);

  // --- Cyber trend (data-aware window) ---
  const cyberWindow  = getDataAwareWindow(cybercrime);
  const cyber_30d    = cybercrime.filter(c => {
    const t = new Date(c.timestamp);
    return t >= cyberWindow.current30dStart && t <= cyberWindow.latestDate;
  }).length;
  const cyber_prev   = cybercrime.filter(c => {
    const t = new Date(c.timestamp);
    return t >= cyberWindow.prev30dStart && t < cyberWindow.current30dStart;
  }).length;
  const cyber_trend  = computeTrendPct(cyber_30d, cyber_prev);

  // --- Patrol operational counts ---
  const active_patrols     = patrols.filter(p => p.status === 'On Patrol').length;
  const responding_patrols = patrols.filter(p => p.status === 'Responding').length;
  const total_patrols      = patrols.length;

  return {
    total_crimes:      crimes.length,
    crimes_30d,
    crimes_prev_30d:   crimes_prev,
    crimes_trend,                           // e.g. "+4.2%" or "-1.8%" or null
    active_hotspots:   hotspots.length,
    high_risk_areas:   hotspots.filter(h => h.risk === 'Critical' || h.risk === 'High').length,
    active_patrols,
    total_patrols,
    responding_patrols,                     // Real operational count
    cybercrime_reports: cybercrime.length,
    cyber_30d,
    cyber_prev_30d:    cyber_prev,
    cyber_trend,                            // e.g. "+12.5%" or null
    critical_alerts:   crimes.filter(c => c.severity === 'Critical').length,
    risk_index:        riskIndex,
  };
}

