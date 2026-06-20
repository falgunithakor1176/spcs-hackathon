import api from './api';

export const getPatrolUnits = async () => {
  const response = await api.get('/patrols');
  return response.data;
};

export const getPatrolRoutes = async () => {
  const response = await api.get('/patrol-routes');
  return response.data;
};
