import React, { useState } from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard, BarChart3, Shield, Truck,
  Bell, Settings, LogOut, ChevronRight, Activity,
  FlaskConical, ScrollText, Globe
} from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { canAccess } from '../../utils/rbac';

const ALL_NAV = [
  { to: '/command',    icon: LayoutDashboard, label: 'Command Center',     key: 'command'    },
  { to: '/analytics',  icon: BarChart3,        label: 'Crime Analytics',    key: 'analytics'  },
  { to: '/cybercrime', icon: Globe,            label: 'Cyber Intelligence', key: 'cybercrime' },
  { to: '/patrol',     icon: Truck,            label: 'Patrol Routing',     key: 'patrol'     },
  { to: '/alerts',     icon: Bell,             label: 'Alert Center',       key: 'alerts'     },
  { to: '/simulation', icon: FlaskConical,     label: 'Simulation',         key: 'simulation' },
  { to: '/audit-log',  icon: ScrollText,       label: 'Audit Log',          key: 'audit'      },
  { to: '/settings',   icon: Settings,         label: 'Settings',           key: 'settings'   },
];

export default function Sidebar() {
  const { logout, user } = useAuth();
  const [hovered, setHovered] = useState(null);
  const role = user?.role || 'Officer';

  // Filter nav items by role permissions
  const navItems = ALL_NAV.filter(item => canAccess(role, item.key));

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
        {navItems.map(({ to, icon: Icon, label }) => (
          <NavLink
            key={to}
            to={to}
            onMouseEnter={() => setHovered(to)}
            onMouseLeave={() => setHovered(null)}
            className={({ isActive }) => `nav-item relative ${isActive ? 'active' : ''}`}
          >
            <Icon size={18} />
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

      {/* Role badge */}
      <div
        title={`${user?.name} | ${user?.role}`}
        style={{
          fontSize: 7, fontFamily: 'Orbitron', color: 'var(--electric)',
          background: 'rgba(0,212,255,0.08)', border: '1px solid rgba(0,212,255,0.15)',
          borderRadius: 3, padding: '2px 4px', marginBottom: 6, letterSpacing: '0.05em',
        }}>
        {role?.toUpperCase()?.slice(0, 3)}
      </div>

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
          title="Logout">
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
