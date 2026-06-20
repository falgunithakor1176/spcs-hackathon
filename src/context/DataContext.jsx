import React, { createContext, useContext, useEffect, useState, useCallback } from 'react';
import { getCrimes, getCybercrimes } from '../services/crimeService';
import { getHotspots, getPredictions } from '../services/hotspotService';
import { getPatrolUnits, getPatrolRoutes } from '../services/patrolService';
import { getAlerts } from '../services/alertService';
import { useAuth } from './AuthContext';

const DataContext = createContext(null);

export function DataProvider({ children }) {
  const { isAuthenticated, logout } = useAuth();
  const [data, setData] = useState({
    crimes: [], cybercrime: [], patrols: [], routes: [],
    hotspots: [], alerts: [], predictions: [],
    loading: true, error: null
  });
  const [riskIndex, setRiskIndex] = useState(72);

  useEffect(() => {
    if (data.hotspots && data.hotspots.length > 0) {
      const totalRisk = data.hotspots.reduce((acc, h) => acc + (h.score || 0), 0);
      const calculatedRisk = Math.min(100, Math.floor((totalRisk / 300) * 100));
      setRiskIndex(calculatedRisk);
    } else {
      setRiskIndex(0);
    }
  }, [data.hotspots]);

  const fetchAll = useCallback(async () => {
    setData(prev => ({ ...prev, loading: true }));
    try {
      const [crimes, cyber, patrols, routes, hotspots, alerts, predictions] = await Promise.all([
        getCrimes(), getCybercrimes(), getPatrolUnits(), getPatrolRoutes(),
        getHotspots(), getAlerts(), getPredictions()
      ]);
      
      setData({ crimes, cybercrime: cyber, patrols, routes, hotspots, alerts, predictions, loading: false, error: null });
    } catch (err) {
      console.error("DataContext fetch error:", err);
      setData(prev => ({ ...prev, loading: false, error: err.message }));
      if (err.response && (err.response.status === 401 || err.response.status === 422)) {
        logout(); // Force login on invalid token
      }
    }
  }, [isAuthenticated]);

  useEffect(() => {
    if (!isAuthenticated) {
      setData(prev => ({ ...prev, loading: false }));
      return;
    }
    fetchAll();
  }, [isAuthenticated, fetchAll]);

  // Expose refreshData so components (like the ML button) can trigger a re-fetch
  const refreshData = useCallback(() => {
    if (isAuthenticated) {
      return fetchAll();
    }
  }, [isAuthenticated, fetchAll]);

  // Real-time Data Polling (15 seconds)
  useEffect(() => {
    if (!isAuthenticated) return;
    const intervalId = setInterval(() => {
      refreshData();
    }, 15000);
    return () => clearInterval(intervalId);
  }, [isAuthenticated, refreshData]);

  return <DataContext.Provider value={{ ...data, refreshData, riskIndex, setRiskIndex }}>{children}</DataContext.Provider>;
}

export const useData = () => useContext(DataContext);

