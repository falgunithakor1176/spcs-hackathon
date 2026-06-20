import api from './api';

export const runMLEngine = async () => {
  const response = await api.post('/ml/run');
  return response.data;
};

export const getMLStatus = async () => {
  const response = await api.get('/ml/status');
  return response.data;
};
