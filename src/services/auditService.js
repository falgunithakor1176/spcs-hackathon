import api from './api';

export const getAuditLogs = async ({ page = 1, limit = 100, action, role, username } = {}) => {
  const params = { page, limit };
  if (action)   params.action   = action;
  if (role)     params.role     = role;
  if (username) params.username = username;
  const res = await api.get('/audit/logs', { params });
  return res.data;
};

export const getAuditStats = async () => {
  const res = await api.get('/audit/stats');
  return res.data;
};
