import React, { createContext, useContext, useEffect, useState, useCallback } from 'react';
import { getCrimes, getCybercrimes } from '../services/crimeService';
import { getHotspots, getPredictions } from '../services/hotspotService';
import { getPatrolUnits, getPatrolRoutes } from '../services/patrolService';
import { getAlerts } from '../services/alertService';
import { getAreaIntelligence, getEngine2Forecasts, getEngineConfig } from '../services/forecastService';
import { useAuth } from './AuthContext';

const DataContext = createContext(null);

export function DataProvider({ children }) {
  const { isAuthenticated, logout } = useAuth();
  const [data, setData] = useState({
    crimes: [], cybercrime: [], patrols: [], routes: [],
    hotspots: [], alerts: [], predictions: [],
    areaIntelligence: [], forecasts: {}, engineConfig: {},
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
    
    const handleAuthError = (err) => {
      // Token refresh is handled automatically by the axios interceptor in api.js.
      // We no longer call logout() here — a 401 during a background poll should not
      // kick the user out. The interceptor will refresh the token and retry silently.
      // Only log for debugging purposes.
      if (err.response && err.response.status !== 401 && err.response.status !== 422) {
        console.error("API Fetch Error:", err);
      }
      return [];
    };

    try {
      const [crimes, cyber, patrols, routes, hotspots, alerts, predictions,
             areaIntelligence, forecasts, engineConfig] = await Promise.all([
        getCrimes().catch(handleAuthError),
        getCybercrimes().catch(handleAuthError),
        getPatrolUnits().catch(handleAuthError),
        getPatrolRoutes().catch(handleAuthError),
        getHotspots().catch(handleAuthError),
        getAlerts().catch(handleAuthError),
        getPredictions().catch(handleAuthError),
        getAreaIntelligence().catch(() => []),
        getEngine2Forecasts().catch(() => ({})),
        getEngineConfig().catch(() => ({})),
      ]);
      setData({
        crimes, cybercrime: cyber, patrols, routes, hotspots, alerts, predictions,
        areaIntelligence, forecasts, engineConfig,
        loading: false, error: null
      });
    } catch (err) {
      console.error("DataContext fetch error:", err);
      setData(prev => ({ ...prev, loading: false, error: err.message }));
    }
  }, [isAuthenticated, logout]);

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

