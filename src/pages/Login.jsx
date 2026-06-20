import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Radio, Eye, EyeOff, Shield, Lock, User, AlertCircle } from 'lucide-react';

const DEMO_ACCOUNTS = [
  { role: 'Admin',   username: 'commissioner', password: 'admin123',   color: '#FF1744' },
  { role: 'Analyst', username: 'analyst',      password: 'analyst123', color: '#00D4FF' },
  { role: 'Officer', username: 'officer',      password: 'officer123', color: '#00E676' },
  { role: 'Cyber',   username: 'cyber',        password: 'cyber123',   color: '#A78BFA' },
];

export default function Login() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [showPass, setShowPass] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    await new Promise(r => setTimeout(r, 600)); // simulate auth delay
    const result = await login(username, password);
    if (result.success) {
      navigate('/command');
    } else {
      setError('Invalid credentials. Access denied.');
    }
    setLoading(false);
  };

  const quickLogin = (acc) => {
    setUsername(acc.username);
    setPassword(acc.password);
  };

  return (
    <div className="relative min-h-screen w-full flex items-center justify-center overflow-hidden"
      style={{ background: 'radial-gradient(ellipse at 20% 50%, #0d1f3c 0%, #060d1a 50%, #030810 100%)' }}>

      {/* Background grid */}
      <div className="absolute inset-0 grid-bg opacity-40" />

      {/* Animated scan line */}
      <div className="scan-container absolute inset-0 pointer-events-none">
        <div className="scan-line" />
      </div>

      {/* Decorative circles */}
      <div className="absolute top-1/4 left-1/4 w-96 h-96 rounded-full pointer-events-none"
        style={{ background: 'radial-gradient(circle, rgba(0,212,255,0.04) 0%, transparent 70%)' }} />
      <div className="absolute bottom-1/4 right-1/4 w-80 h-80 rounded-full pointer-events-none"
        style={{ background: 'radial-gradient(circle, rgba(0,102,255,0.05) 0%, transparent 70%)' }} />

      <div className="relative z-10 w-full max-w-md px-4">

        {/* Logo / Brand */}
        <div className="text-center mb-8 animate-fade-in">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl mb-4 mx-auto"
            style={{
              background: 'linear-gradient(135deg, rgba(0,102,255,0.2), rgba(0,212,255,0.1))',
              border: '1px solid rgba(0,212,255,0.25)',
              boxShadow: '0 0 40px rgba(0,212,255,0.15)',
            }}>
            <Shield size={28} style={{ color: '#00D4FF' }} />
          </div>
          <div className="font-orbitron font-bold text-2xl tracking-widest mb-1 glow-text-blue">
            S P C S
          </div>
          <div className="font-orbitron text-xs tracking-widest mb-1" style={{ color: 'rgba(0,212,255,0.6)', fontSize: 10 }}>
            SMART POLICING COMMAND SYSTEM
          </div>
          <div style={{ color: 'var(--text-muted)', fontSize: 11 }}>
            Ahmedabad City Police Department
          </div>
        </div>

        {/* Login Card */}
        <div className="glass-card hud-corner hud-corner-tl hud-corner-tr hud-corner-br hud-corner-bl p-8 rounded-xl"
          style={{ boxShadow: '0 0 60px rgba(0,212,255,0.08), 0 20px 60px rgba(0,0,0,0.6)' }}>

          {/* Authorized Personnel Only */}
          <div className="flex items-center justify-center gap-2 mb-6 py-2 rounded"
            style={{ background: 'rgba(255,23,68,0.06)', border: '1px solid rgba(255,23,68,0.15)' }}>
            <Lock size={11} style={{ color: '#FF1744' }} />
            <span style={{ color: '#FF1744', fontSize: 10, fontFamily: 'Orbitron', letterSpacing: '0.12em' }}>
              AUTHORIZED PERSONNEL ONLY
            </span>
          </div>

          <form onSubmit={handleLogin} className="space-y-4">
            {/* Username */}
            <div>
              <label className="section-header mb-2 block">BADGE / USERNAME</label>
              <div className="relative">
                <User size={14} className="absolute left-3 top-1/2 -translate-y-1/2"
                  style={{ color: 'var(--text-muted)' }} />
                <input
                  type="text"
                  value={username}
                  onChange={e => setUsername(e.target.value)}
                  placeholder="Enter username"
                  className="cmd-input w-full pl-9 pr-4 py-3"
                  required
                />
              </div>
            </div>

            {/* Password */}
            <div>
              <label className="section-header mb-2 block">PASSWORD / ACCESS CODE</label>
              <div className="relative">
                <Lock size={14} className="absolute left-3 top-1/2 -translate-y-1/2"
                  style={{ color: 'var(--text-muted)' }} />
                <input
                  type={showPass ? 'text' : 'password'}
                  value={password}
                  onChange={e => setPassword(e.target.value)}
                  placeholder="Enter password"
                  className="cmd-input w-full pl-9 pr-10 py-3"
                  required
                />
                <button type="button" onClick={() => setShowPass(s => !s)}
                  className="absolute right-3 top-1/2 -translate-y-1/2"
                  style={{ color: 'var(--text-muted)', background: 'none', border: 'none', cursor: 'pointer' }}>
                  {showPass ? <EyeOff size={14} /> : <Eye size={14} />}
                </button>
              </div>
            </div>

            {/* Error */}
            {error && (
              <div className="flex items-center gap-2 p-3 rounded"
                style={{ background: 'rgba(255,23,68,0.08)', border: '1px solid rgba(255,23,68,0.2)' }}>
                <AlertCircle size={13} style={{ color: '#FF1744' }} />
                <span style={{ color: '#FF1744', fontSize: 12 }}>{error}</span>
              </div>
            )}

            {/* Submit */}
            <button
              type="submit"
              disabled={loading}
              className="btn-primary w-full py-3 mt-2 flex items-center justify-center gap-2"
              style={{ borderRadius: 6 }}>
              {loading ? (
                <>
                  <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  <span>AUTHENTICATING...</span>
                </>
              ) : (
                <>
                  <Radio size={14} />
                  <span>ACCESS COMMAND SYSTEM</span>
                </>
              )}
            </button>
          </form>

          {/* Demo Accounts */}
          <div className="mt-6 pt-4 border-t border-electric/08">
            <div className="section-header mb-3 text-center">DEMO ACCESS</div>
            <div className="grid grid-cols-2 gap-2">
              {DEMO_ACCOUNTS.map(acc => (
                <button
                  key={acc.username}
                  onClick={() => quickLogin(acc)}
                  className="py-2 px-3 rounded text-left transition-all hover:scale-[1.02]"
                  style={{
                    background: `${acc.color}08`,
                    border: `1px solid ${acc.color}20`,
                    cursor: 'pointer',
                  }}>
                  <div style={{ color: acc.color, fontSize: 10, fontFamily: 'Orbitron', fontWeight: 700 }}>{acc.role}</div>
                  <div style={{ color: 'var(--text-muted)', fontSize: 9 }}>{acc.username}</div>
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="text-center mt-6" style={{ color: 'var(--text-muted)', fontSize: 10 }}>
          Smart Policing Command System v1.0 • Ahmedabad Police Department<br />
          <span style={{ color: 'rgba(0,212,255,0.3)' }}>All access is monitored and logged</span>
        </div>
      </div>
    </div>
  );
}
