import React from 'react';
import { TrendingUp, TrendingDown, Minus } from 'lucide-react';

export default function StatCard({ icon: Icon, label, value, sub, trend, trendValue, color = '#00D4FF', accentColor }) {
  const accent = accentColor || color;
  const TrendIcon = trend === 'up' ? TrendingUp : trend === 'down' ? TrendingDown : Minus;
  const trendColor = trend === 'up' ? '#FF1744' : trend === 'down' ? '#00E676' : '#7BA7C4';

  return (
    <div className="glass-card hud-corner hud-corner-tl hud-corner-br p-4 rounded-lg flex-1 min-w-0 relative overflow-hidden"
      style={{ animation: 'fadeIn 0.4s ease-out both' }}>

      {/* Background glow accent */}
      <div className="absolute inset-0 pointer-events-none" style={{
        background: `radial-gradient(ellipse at top right, ${accent}08 0%, transparent 65%)`,
      }} />

      {/* Top row: icon + trend */}
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center justify-center w-9 h-9 rounded-lg"
          style={{ background: `${accent}15`, border: `1px solid ${accent}25` }}>
          {Icon && <Icon size={16} style={{ color: accent }} />}
        </div>
        {trend && (
          <div className="flex items-center gap-1"
            style={{ background: `${trendColor}12`, border: `1px solid ${trendColor}25`, padding: '2px 6px', borderRadius: 4 }}>
            <TrendIcon size={10} style={{ color: trendColor }} />
            <span style={{ color: trendColor, fontSize: 10, fontFamily: 'JetBrains Mono' }}>{trendValue}</span>
          </div>
        )}
      </div>

      {/* Value */}
      <div className="font-orbitron font-bold mb-1"
        style={{ fontSize: 24, color: accent, lineHeight: 1, textShadow: `0 0 20px ${accent}40` }}>
        {value}
      </div>

      {/* Label */}
      <div className="text-xs font-medium mb-0.5" style={{ color: '#E8F4FD', fontSize: 11 }}>
        {label}
      </div>

      {/* Sub */}
      {sub && (
        <div style={{ color: 'var(--text-muted)', fontSize: 10 }}>{sub}</div>
      )}
    </div>
  );
}
