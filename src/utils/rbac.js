/**
 * rbac.js — Role-Based Access Control
 * Defines what each role can access in SPCS.
 *
 * Roles (from backend DEMO_ACCOUNTS):
 *   Commissioner (Admin) — full access
 *   Analyst              — read-only analytics
 *   Officer              — operations only
 *   Cyber                — cyber intelligence only
 */

export const ROLE_PERMISSIONS = {
  Commissioner: {
    pages: ['command', 'analytics', 'cybercrime', 'patrol', 'alerts', 'simulation', 'audit', 'settings'],
    canRunEngines: true,
    canExport: true,
    canAcknowledgeAlerts: true,
    canViewAuditLog: true,
    canSimulate: true,
  },
  Admin: {  // alias
    pages: ['command', 'analytics', 'cybercrime', 'patrol', 'alerts', 'simulation', 'audit', 'settings'],
    canRunEngines: true,
    canExport: true,
    canAcknowledgeAlerts: true,
    canViewAuditLog: true,
    canSimulate: true,
  },
  Analyst: {
    pages: ['command', 'analytics', 'cybercrime', 'simulation', 'settings'],
    canRunEngines: false,
    canExport: true,
    canAcknowledgeAlerts: false,
    canViewAuditLog: false,
    canSimulate: true,
  },
  Officer: {
    pages: ['command', 'patrol', 'alerts', 'settings'],
    canRunEngines: false,
    canExport: false,
    canAcknowledgeAlerts: true,
    canViewAuditLog: false,
    canSimulate: false,
  },
  Cyber: {
    pages: ['command', 'cybercrime', 'analytics', 'simulation', 'settings'],
    canRunEngines: false,
    canExport: true,
    canAcknowledgeAlerts: false,
    canViewAuditLog: false,
    canSimulate: true,
  },
};

/**
 * Check if a role can access a page or feature.
 * @param {string} role    - User's role
 * @param {string} feature - Page key or permission key
 * @returns {boolean}
 */
export function canAccess(role, feature) {
  const perms = ROLE_PERMISSIONS[role] || ROLE_PERMISSIONS['Officer'];
  if (Array.isArray(perms.pages) && perms.pages.includes(feature)) return true;
  if (perms[feature] !== undefined) return perms[feature];
  return false;
}

/** Nav items with role visibility */
export const NAV_ITEMS = [
  { key: 'command',    label: 'Command Center', icon: 'LayoutDashboard', path: '/'            },
  { key: 'analytics',  label: 'Analytics',       icon: 'BarChart3',       path: '/analytics'   },
  { key: 'cybercrime', label: 'Cybercrime',       icon: 'Globe',           path: '/cybercrime'  },
  { key: 'patrol',     label: 'Patrol Routing',   icon: 'Truck',           path: '/patrol'      },
  { key: 'alerts',     label: 'Alerts',           icon: 'Bell',            path: '/alerts'      },
  { key: 'simulation', label: 'Simulation',       icon: 'FlaskConical',    path: '/simulation'  },
  { key: 'audit',      label: 'Audit Log',        icon: 'ScrollText',      path: '/audit-log'   },
  { key: 'settings',   label: 'Settings',         icon: 'Settings',        path: '/settings'    },
];
