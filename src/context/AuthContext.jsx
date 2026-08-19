import React, { createContext, useContext, useState } from 'react';
import { login as apiLogin } from '../services/authService';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    try {
      const saved = sessionStorage.getItem('spcs_user');
      return saved ? JSON.parse(saved) : null;
    } catch (err) {
      console.error("Error parsing stored user session:", err);
      sessionStorage.removeItem('spcs_user');
      return null;
    }
  });

  const login = async (username, password) => {
    try {
      const data = await apiLogin(username, password);
      if (data && data.access_token) {
        sessionStorage.setItem('access_token', data.access_token);
        sessionStorage.setItem('refresh_token', data.refresh_token);
        sessionStorage.setItem('spcs_user', JSON.stringify(data.user));
        setUser(data.user);
        return { success: true, user: data.user };
      }
    } catch (err) {
      console.error('Login error:', err);
      return { success: false, error: 'Invalid credentials' };
    }
    return { success: false, error: 'Unknown error' };
  };

  const logout = () => {
    sessionStorage.removeItem('spcs_user');
    sessionStorage.removeItem('access_token');
    sessionStorage.removeItem('refresh_token');
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, login, logout, isAuthenticated: !!user }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}
