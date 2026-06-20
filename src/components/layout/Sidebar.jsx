import React, { useState } from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import {
  LayoutDashboard, Map, BarChart3, Shield, Truck,
  Bell, Settings, LogOut, ChevronRight, Activity
} from 'lucide-react';
import { useAuth } from '../../context/AuthContext';

const NAV_ITEMS = [
  { to: '/command',    icon: LayoutDashboard, label: 'Command Center', shortLabel: 'CMD'  },
  { to: '/analytics',  icon: BarChart3,        label: 'Crime Analytics', shortLabel: 'ANA'  },
  { to: '/cybercrime', icon: Shield,           label: 'Cyber Intelligence', shortLabel: 'CYB' },
  { to: '/patrol',     icon: Truck,            label: 'Patrol Routing', shortLabel: 'PAT'  },
  { to: '/alerts',     icon: Bell,             label: 'Alert Center',  shortLabel: 'ALT'  },
  { to: '/settings',   icon: Settings,         label: 'Settings',      shortLabel: 'SET'  },
];

export default function Sidebar() {
  const { logout, user } = useAuth();
  const [hovered, setHovered] = useState(null);
  const location = useLocation();

  return (
    <aside className="relative z-40 flex flex-col items-center w-14 min-h-screen py-3 border-r border-electric/10"
      style={{ background: 'linear-gradient(180deg, #060d1a 0%, #081120 100%)' }}>

      {/* Logo */}
      <div className="flex items-center justify-center w-10 h-10 mb-4 rounded-lg border border-electric/20"
        style={{ background: 'rgba(0,212,255,0.08)', boxShadow: '0 0 15px rgba(0,212,255,0.1)' }}>
        <Activity size={18} className="text-electric" />
      </div>

      {/* Top divider */}
      <div className="w-8 h-px mb-4" style={{ background: 'linear-gradient(90deg, transparent, rgba(0,212,255,0.3), transparent)' }} />

      {/* Nav Items */}
      <nav className="flex flex-col gap-1 flex-1">
        {NAV_ITEMS.map(({ to, icon: Icon, label }) => (
          <NavLink
            key={to}
            to={to}
            onMouseEnter={() => setHovered(to)}
            onMouseLeave={() => setHovered(null)}
            className={({ isActive }) =>
              `nav-item relative ${isActive ? 'active' : ''}`
            }
          >
            <Icon size={18} />
            {/* Tooltip */}
            {hovered === to && (
              <div className="absolute left-14 z-50 flex items-center gap-2 px-3 py-1.5 rounded-md pointer-events-none animate-fade-in"
                style={{
                  background: 'rgba(8,17,32,0.98)',
                  border: '1px solid rgba(0,212,255,0.2)',
                  boxShadow: '0 4px 20px rgba(0,0,0,0.5)',
                  whiteSpace: 'nowrap',
                }}>
                <ChevronRight size={10} className="text-electric" />
                <span className="text-xs font-medium text-white">{label}</span>
              </div>
            )}
          </NavLink>
        ))}
      </nav>

      {/* Bottom divider */}
      <div className="w-8 h-px mb-3" style={{ background: 'linear-gradient(90deg, transparent, rgba(0,212,255,0.2), transparent)' }} />

      {/* User Avatar + Logout */}
      <div className="flex flex-col items-center gap-2">
        <div
          title={`${user?.name} | ${user?.role}`}
          className="flex items-center justify-center w-9 h-9 rounded-full text-xs font-bold cursor-default"
          style={{ background: 'rgba(0,102,255,0.3)', border: '1px solid rgba(0,212,255,0.25)', color: '#00D4FF' }}>
          {user?.name?.split(' ').slice(-1)[0]?.[0] || 'U'}
        </div>
        <button
          onClick={logout}
          onMouseEnter={() => setHovered('logout')}
          onMouseLeave={() => setHovered(null)}
          className="nav-item relative"
          title="Logout"
        >
          <LogOut size={16} />
          {hovered === 'logout' && (
            <div className="absolute left-14 z-50 px-3 py-1.5 rounded-md pointer-events-none"
              style={{ background: 'rgba(8,17,32,0.98)', border: '1px solid rgba(255,23,68,0.2)', whiteSpace: 'nowrap' }}>
              <span className="text-xs text-red-400">Logout</span>
            </div>
          )}
        </button>
      </div>
    </aside>
  );
}
