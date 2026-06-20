import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import { DataProvider } from './context/DataContext';
import AppLayout from './components/layout/AppLayout';
import Login from './pages/Login';
import CommandCenter from './pages/CommandCenter';
import CrimeAnalytics from './pages/CrimeAnalytics';
import CyberCrime from './pages/CyberCrime';
import PatrolRouting from './pages/PatrolRouting';
import Alerts from './pages/Alerts';
import Settings from './pages/Settings';

function ProtectedRoute({ children }) {
  const { isAuthenticated } = useAuth();
  return isAuthenticated ? <DataProvider>{children}</DataProvider> : <Navigate to="/login" replace />;
}

function AppRoutes() {
  const { isAuthenticated } = useAuth();
  return (
    <Routes>
      <Route path="/login" element={
        isAuthenticated ? <Navigate to="/command" replace /> : <Login />
      } />
      <Route path="/" element={
        <ProtectedRoute>
          <AppLayout />
        </ProtectedRoute>
      }>
        <Route index element={<Navigate to="/command" replace />} />
        <Route path="command"   element={<CommandCenter />} />
        <Route path="analytics" element={<CrimeAnalytics />} />
        <Route path="cybercrime" element={<CyberCrime />} />
        <Route path="patrol"    element={<PatrolRouting />} />
        <Route path="alerts"    element={<Alerts />} />
        <Route path="settings"  element={<Settings />} />
      </Route>
      <Route path="*" element={<Navigate to="/command" replace />} />
    </Routes>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <AppRoutes />
      </BrowserRouter>
    </AuthProvider>
  );
}
