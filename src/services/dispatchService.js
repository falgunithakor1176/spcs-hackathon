import api from './api';

/**
 * Fetch list of hotspots with their nearest available patrol recommendations.
 */
export const getDispatchRecommendations = async () => {
  const response = await api.get('/dispatch/recommendations');
  return response.data;
};

/**
 * Trigger dynamic dispatch transaction.
 * @param {string} hotspotId - Hotspot ID (e.g. 'HS-ML-001')
 * @param {string} patrolId - Vehicle ID (e.g. 'AHD-PCR-004')
 */
export const executeDispatch = async (hotspotId, patrolId) => {
  const response = await api.post('/dispatch', {
    hotspot_id: hotspotId,
    patrol_id: patrolId
  });
  return response.data;
};

// ─── Phase 7C: Simulated GPS Tracking ────────────────────────────────────────

/**
 * Fetch all currently active (non-arrived) dispatches with route geometry.
 * Used to resume simulations after browser refresh.
 */
export const getActiveDispatches = async () => {
  const response = await api.get('/dispatch/active');
  return response.data;
};

/**
 * Update simulated patrol position along the OSRM route.
 * The backend reads the actual coordinate from stored route geometry.
 * @param {string} patrolId - Vehicle ID
 * @param {number} stepIndex - Current index along route_geometry array
 */
export const updatePatrolPosition = async (patrolId, stepIndex) => {
  const response = await api.post('/dispatch/update-position', {
    patrol_id: patrolId,
    step_index: stepIndex
  });
  return response.data;
};

/**
 * Notify backend that simulated patrol has reached the final waypoint.
 * Triggers: patrol → Standby, alert → acknowledged, audit log entry.
 * @param {string} patrolId - Vehicle ID
 */
export const notifyArrival = async (patrolId) => {
  const response = await api.post('/dispatch/arrive', {
    patrol_id: patrolId
  });
  return response.data;
};
