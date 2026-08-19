import api from './api';

/**
 * Generate a dynamic road-following route from a patrol unit to a hotspot using OSRM on the backend.
 * @param {string} patrolId - Vehicle ID (e.g. 'AHD-PCR-001')
 * @param {string} hotspotId - Hotspot ID (e.g. 'HS-ML-001')
 */
export const generateDynamicRoute = async (patrolId, hotspotId) => {
  const response = await api.post('/routes/generate', {
    patrol_id: patrolId,
    hotspot_id: hotspotId
  });
  return response.data;
};
