const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
const NODE_API_BASE_URL = import.meta.env.VITE_NODE_API_BASE_URL || 'http://localhost:3001';

async function request(path, options = {}, baseUrl = API_BASE_URL) {
  const response = await fetch(`${baseUrl}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.detail || 'Request failed');
  }

  return response.json();
}

export function createSlotRequest(slotRequest) {
  return request('/api/slot-requests', {
    method: 'POST',
    body: JSON.stringify(slotRequest),
  }, NODE_API_BASE_URL);
}

export function acceptAlternative(requestId, time) {
  return request(`/api/slot-requests/${requestId}/accept-alternative`, {
    method: 'POST',
    body: JSON.stringify(time),
  });
}

export function getCentreRisks() {
  return request('/centres/risk');
}

export function getCentreRisk(centreId) {
  return request(`/centres/${centreId}/risk`);
}

export function getRiskHistory(centreId) {
  const query = centreId ? `?centreId=${encodeURIComponent(centreId)}` : '';
  return request(`/centres/risk/history${query}`);
}
