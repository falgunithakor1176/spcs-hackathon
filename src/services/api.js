import axios from 'axios';

const api = axios.create({
  baseURL: '/api',
});

// Intercept requests to add the auth token
api.interceptors.request.use(
  (config) => {
    const token = sessionStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Intercept responses to handle token expiration/refresh (simplified for now)
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    // In a real app, you'd try to refresh the token here if error.response.status === 401
    // and a refresh_token is available.
    return Promise.reject(error);
  }
);

export default api;
