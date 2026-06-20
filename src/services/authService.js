import api from './api';

export const login = async (username, password) => {
  const response = await api.post('/auth/login', { username, password });
  return response.data;
};

export const getMe = async () => {
  const response = await api.get('/auth/me');
  return response.data.user;
};

export const refreshToken = async (refresh_token) => {
  const response = await api.post('/auth/refresh', null, {
    headers: { Authorization: `Bearer ${refresh_token}` }
  });
  return response.data;
};
