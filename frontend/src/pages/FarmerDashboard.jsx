import { useState } from 'react';

import { acceptAlternative, createSlotRequest } from '../services/api';

function FarmerDashboard() {
  const [form, setForm] = useState({
    farmerId: '',
    centreId: '',
    crop: 'wheat',
    quantity: 50,
    requestedDate: '2026-09-10',
    preferredTime: '11:00',
  });
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');

  function updateField(event) {
    setForm({ ...form, [event.target.name]: event.target.value });
  }

  async function submitRequest(event) {
    event.preventDefault();
    setError('');
    try {
      setResult(await createSlotRequest(form));
    } catch (requestError) {
      setError(requestError.message);
    }
  }

  async function acceptSuggestedSlot() {
    setError('');
    try {
      setResult(
        await acceptAlternative(result.requestId, result.suggestedSlot),
      );
    } catch (requestError) {
      setError(requestError.message);
    }
  }

  return (
    <main>
      <h1>KisanVanta</h1>
      <form onSubmit={submitRequest}>
        <label>
          Farmer ID
          <input name="farmerId" value={form.farmerId} onChange={updateField} required />
        </label>
        <label>
          Centre
          <input name="centreId" value={form.centreId} onChange={updateField} required />
        </label>
        <label>
          Date
          <input name="requestedDate" type="date" value={form.requestedDate} onChange={updateField} required />
        </label>
        <label>
          Time
          <input name="preferredTime" type="time" value={form.preferredTime} onChange={updateField} required />
        </label>
        <button type="submit">Request slot</button>
      </form>
      {error && <p role="alert">{error}</p>}
      {result?.status === 'confirmed' && <p>Slot confirmed for {result.slot.time}.</p>}
      {result?.status === 'alternative_suggested' && (
        <section>
          <p>Suggested slot: {result.suggested_slot.time}</p>
          <button type="button" onClick={acceptSuggestedSlot}>
            Accept suggested slot
          </button>
        </section>
      )}
      {result?.status === 'unavailable' && <p>{result.message}</p>}
    </main>
  );
}

export default FarmerDashboard;
