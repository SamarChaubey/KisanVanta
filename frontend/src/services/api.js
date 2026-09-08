const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
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
  });
}

export function acceptAlternative(requestId, time) {
  return request(`/api/slot-requests/${requestId}/accept-alternative`, {
    method: 'POST',
    body: JSON.stringify(time),
  });
}
