import api from './api';

export const runSimulation = async (scenario, area = 'all') => {
  const res = await api.post('/simulate', { scenario, area });
  return res.data;
};

export const getScenarios = async () => {
  const res = await api.get('/simulate/scenarios');
  return res.data?.scenarios || [];
};
