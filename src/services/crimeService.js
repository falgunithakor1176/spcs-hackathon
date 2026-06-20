import api from './api';

export const getCrimes = async () => {
  const response = await api.get('/crimes');
  return response.data;
};

export const getCybercrimes = async () => {
  const response = await api.get('/cybercrime');
  return response.data;
};
