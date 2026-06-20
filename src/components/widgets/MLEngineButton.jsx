import React, { useState } from 'react';
import { Cpu, CheckCircle, AlertTriangle, Loader2, Zap, MapPin, Bell } from 'lucide-react';
import { runMLEngine } from '../../services/mlService';
import { useData } from '../../context/DataContext';

export default function MLEngineButton() {
  const [isRunning, setIsRunning] = useState(false);
  const [result, setResult] = useState(null);
  const [showToast, setShowToast] = useState(false);
  const [error, setError] = useState(null);
  const { refreshData, setRiskIndex } = useData();

  const handleRun = async () => {
    if (isRunning) return;
    setIsRunning(true);
    setResult(null);
    setError(null);

    try {
      const data = await runMLEngine();
      setResult(data.summary);
      if (data.summary.city_risk_index) {
        setRiskIndex(data.summary.city_risk_index);
      }
      setShowToast(true);

      // Automatically refresh all dashboard data (hotspots, alerts, etc.)
      await refreshData();

      // Auto-hide toast after 6 seconds
      setTimeout(() => setShowToast(false), 6000);
    } catch (err) {
      setError(err.response?.data?.message || 'ML Engine failed');
      setTimeout(() => setError(null), 5000);
    } finally {
      setIsRunning(false);
    }
  };

  return (
    <>
      {/* ML Engine Button */}
      <button
        id="ml-engine-trigger"
        onClick={handleRun}
        disabled={isRunning}
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: 8,
          padding: '8px 16px',
          borderRadius: 8,
          border: isRunning
            ? '1px solid rgba(255,193,7,0.3)'
            : '1px solid rgba(0,230,118,0.4)',
          background: isRunning
            ? 'rgba(255,193,7,0.08)'
            : 'linear-gradient(135deg, rgba(0,230,118,0.12) 0%, rgba(0,212,255,0.08) 100%)',
          color: isRunning ? '#FFC107' : '#00E676',
          cursor: isRunning ? 'not-allowed' : 'pointer',
          fontFamily: 'Orbitron, sans-serif',
          fontSize: 10,
          letterSpacing: '0.12em',
          textTransform: 'uppercase',
          transition: 'all 0.3s ease',
          opacity: isRunning ? 0.7 : 1,
          boxShadow: isRunning
            ? '0 0 15px rgba(255,193,7,0.1)'
            : '0 0 20px rgba(0,230,118,0.15)',
          whiteSpace: 'nowrap',
        }}
        onMouseEnter={(e) => {
          if (!isRunning) {
            e.target.style.boxShadow = '0 0 30px rgba(0,230,118,0.3)';
            e.target.style.borderColor = 'rgba(0,230,118,0.6)';
          }
        }}
        onMouseLeave={(e) => {
          if (!isRunning) {
            e.target.style.boxShadow = '0 0 20px rgba(0,230,118,0.15)';
            e.target.style.borderColor = 'rgba(0,230,118,0.4)';
          }
        }}
      >
        {isRunning ? (
          <Loader2 size={14} style={{ animation: 'spin 1s linear infinite' }} />
        ) : (
          <Cpu size={14} />
        )}
        {isRunning ? 'DBSCAN Running...' : 'Run ML Engine'}
      </button>

      {/* Success Toast */}
      {showToast && result && (
        <div
          style={{
            position: 'fixed',
            top: 20,
            right: 20,
            zIndex: 9999,
            background: 'linear-gradient(135deg, rgba(6,13,26,0.97) 0%, rgba(0,30,15,0.97) 100%)',
            border: '1px solid rgba(0,230,118,0.4)',
            borderRadius: 12,
            padding: '16px 20px',
            minWidth: 320,
            boxShadow: '0 8px 32px rgba(0,0,0,0.5), 0 0 40px rgba(0,230,118,0.15)',
            animation: 'slideInRight 0.4s ease-out',
          }}
        >
          {/* Header */}
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 12 }}>
            <CheckCircle size={18} style={{ color: '#00E676' }} />
            <span style={{
              color: '#00E676',
              fontFamily: 'Orbitron, sans-serif',
              fontSize: 12,
              letterSpacing: '0.08em',
            }}>
              ML Hotspot Analysis Complete
            </span>
            <button
              onClick={() => setShowToast(false)}
              style={{
                marginLeft: 'auto', background: 'none', border: 'none',
                color: '#7BA7C4', cursor: 'pointer', fontSize: 16
              }}
            >×</button>
          </div>

          {/* Metrics Grid */}
          <div style={{
            display: 'grid',
            gridTemplateColumns: '1fr 1fr 1fr',
            gap: 8,
          }}>
            <div style={{
              background: 'rgba(0,212,255,0.06)',
              border: '1px solid rgba(0,212,255,0.15)',
              borderRadius: 8,
              padding: '10px 12px',
              textAlign: 'center',
            }}>
              <MapPin size={14} style={{ color: '#00D4FF', margin: '0 auto 4px' }} />
              <div style={{ color: '#00D4FF', fontFamily: 'JetBrains Mono', fontSize: 18, fontWeight: 700 }}>
                {result.summary?.hotspots_generated || 0}
              </div>
              <div style={{ color: '#7BA7C4', fontSize: 9, marginTop: 2 }}>Hotspots</div>
            </div>

            <div style={{
              background: 'rgba(255,23,68,0.06)',
              border: '1px solid rgba(255,23,68,0.15)',
              borderRadius: 8,
              padding: '10px 12px',
              textAlign: 'center',
            }}>
              <Bell size={14} style={{ color: '#FF1744', margin: '0 auto 4px' }} />
              <div style={{ color: '#FF1744', fontFamily: 'JetBrains Mono', fontSize: 18, fontWeight: 700 }}>
                {result.summary?.alerts_generated || 0}
              </div>
              <div style={{ color: '#7BA7C4', fontSize: 9, marginTop: 2 }}>Alerts</div>
            </div>

            <div style={{
              background: 'rgba(255,214,0,0.06)',
              border: '1px solid rgba(255,214,0,0.15)',
              borderRadius: 8,
              padding: '10px 12px',
              textAlign: 'center',
            }}>
              <Zap size={14} style={{ color: '#FFD600', margin: '0 auto 4px' }} />
              <div style={{ color: '#FFD600', fontFamily: 'JetBrains Mono', fontSize: 18, fontWeight: 700 }}>
                {result.summary?.city_risk_index || 0}
              </div>
              <div style={{ color: '#7BA7C4', fontSize: 9, marginTop: 2 }}>Risk Index</div>
            </div>
          </div>

          {/* Subtext */}
          <div style={{ color: '#7BA7C4', fontSize: 10, marginTop: 10, textAlign: 'center' }}>
            {result.summary?.total_crimes_analyzed || 0} crimes analyzed • {result.summary?.crimes_clustered || 0} clustered • {result.summary?.noise_points || 0} noise
          </div>
        </div>
      )}

      {/* Error Toast */}
      {error && (
        <div
          style={{
            position: 'fixed',
            top: 20,
            right: 20,
            zIndex: 9999,
            background: 'rgba(6,13,26,0.97)',
            border: '1px solid rgba(255,23,68,0.4)',
            borderRadius: 12,
            padding: '14px 20px',
            display: 'flex',
            alignItems: 'center',
            gap: 10,
            boxShadow: '0 8px 32px rgba(0,0,0,0.5)',
            animation: 'slideInRight 0.4s ease-out',
          }}
        >
          <AlertTriangle size={16} style={{ color: '#FF1744' }} />
          <span style={{ color: '#FF1744', fontSize: 12, fontFamily: 'Orbitron' }}>{error}</span>
        </div>
      )}

      {/* Keyframe styles */}
      <style>{`
        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
        @keyframes slideInRight {
          from { transform: translateX(100%); opacity: 0; }
          to { transform: translateX(0); opacity: 1; }
        }
      `}</style>
    </>
  );
}
