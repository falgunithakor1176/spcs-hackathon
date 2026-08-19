import api from './api';

// Engine 2 — Physical + Cyber predictions per area
export const getEngine2Forecasts = async () => {
  const response = await api.get('/engine2/forecasts');
  return response.data?.data || {};
};

// Engine 3 — Combined risk intelligence sorted by patrol priority
export const getAreaIntelligence = async () => {
  const response = await api.get('/engine3/area-intelligence');
  return response.data?.data || [];
};

// Engine 3 — Heuristic weights + model config (for transparency panel)
export const getEngineConfig = async () => {
  const response = await api.get('/engine3/config');
  return response.data || {};
};

// Trigger Engine 2 + Engine 3 refresh (POST)
export const runEngine2 = async () => {
  const response = await api.post('/engine2/run');
  return response.data;
};

export const runEngine3 = async () => {
  const response = await api.post('/engine3/run');
  return response.data;
};
