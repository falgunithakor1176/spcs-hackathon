import api from './api';

export const getHotspots = async () => {
  const response = await api.get('/hotspots');
  return response.data;
};

export const getPredictions = async () => {
  const response = await api.get('/predictions');
  return response.data;
};
