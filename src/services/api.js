import axios from 'axios';

const api = axios.create({
  baseURL: '/api',
});

// ─── Request interceptor: attach current access token ────────────────────────
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

// ─── Response interceptor: auto-refresh access token on 401 ──────────────────
let _isRefreshing = false;
let _failedQueue = [];

function processQueue(error, token = null) {
  _failedQueue.forEach(({ resolve, reject }) => {
    if (error) reject(error);
    else resolve(token);
  });
  _failedQueue = [];
}

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // Only attempt refresh on 401/422 and only once per request
    if (
      error.response &&
      (error.response.status === 401 || error.response.status === 422) &&
      !originalRequest._retry
    ) {
      const refreshToken = sessionStorage.getItem('refresh_token');

      // No refresh token — give up
      if (!refreshToken) {
        return Promise.reject(error);
      }

      if (_isRefreshing) {
        // Queue this request until refresh is done
        return new Promise((resolve, reject) => {
          _failedQueue.push({ resolve, reject });
        }).then((newToken) => {
          originalRequest.headers.Authorization = `Bearer ${newToken}`;
          return api(originalRequest);
        });
      }

      originalRequest._retry = true;
      _isRefreshing = true;

      try {
        // Call /auth/refresh with the refresh token
        const refreshResponse = await axios.post('/api/auth/refresh', null, {
          headers: { Authorization: `Bearer ${refreshToken}` },
        });

        const newAccessToken = refreshResponse.data.access_token;
        sessionStorage.setItem('access_token', newAccessToken);

        processQueue(null, newAccessToken);

        // Retry the original failed request with the new token
        originalRequest.headers.Authorization = `Bearer ${newAccessToken}`;
        return api(originalRequest);
      } catch (refreshError) {
        // Refresh token also expired — clear session so user can log in again
        processQueue(refreshError, null);
        sessionStorage.removeItem('access_token');
        sessionStorage.removeItem('refresh_token');
        sessionStorage.removeItem('spcs_user');
        // Reload to the login page
        window.location.href = '/';
        return Promise.reject(refreshError);
      } finally {
        _isRefreshing = false;
      }
    }

    return Promise.reject(error);
  }
);

export default api;
