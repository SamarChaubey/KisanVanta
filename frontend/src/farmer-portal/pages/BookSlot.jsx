import { useState } from "react";
import { centres, timeSlots } from "../data/mockData.js";
import "../styles/BookSlot.css";

export default function BookSlot({ t, onBook }) {
  const [centre, setCentre] = useState("");
  const [date, setDate] = useState("");
  const [slot, setSlot] = useState("");
  const [error, setError] = useState("");
  const [confirmation, setConfirmation] = useState(null);

  const today = new Date().toISOString().split("T")[0];

  function handleSubmit(e) {
    e.preventDefault();
    if (!centre || !date || !slot) {
      setError("Please select a centre, date and time slot to continue.");
      return;
    }
    setError("");
    const result = { centre, date, slot };
    setConfirmation(result);
    onBook(result);
  }

  function bookAnother() {
    setConfirmation(null);
    setCentre("");
    setDate("");
    setSlot("");
  }

  if (confirmation) {
    return (
      <div className="bookslot-page">
        <div className="bookslot-confirmation">
          <div className="bookslot-confirm-badge">✓</div>
          <h1>Slot booked</h1>
          <p>
            Your procurement slot is confirmed at <strong>{confirmation.centre}</strong> on{" "}
            <strong>{confirmation.date}</strong> during <strong>{confirmation.slot}</strong>. A
            new gate entry pass has been generated on your Dashboard.
          </p>
          <button className="bookslot-submit" onClick={bookAnother}>
            Book another slot
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="bookslot-page">
      <h1>{t.bookSlot}</h1>
      <p className="bookslot-subtitle">
        Choose your nearest procurement centre and pick an available date and time.
      </p>

      <form className="bookslot-form" onSubmit={handleSubmit} noValidate>
        <label className="bookslot-field">
          <span>Procurement centre</span>
          <select value={centre} onChange={(e) => setCentre(e.target.value)}>
            <option value="">Select a centre</option>
            {centres.map((c) => (
              <option key={c} value={c}>
                {c}
              </option>
            ))}
          </select>
        </label>

        <label className="bookslot-field">
          <span>Date</span>
          <input type="date" min={today} value={date} onChange={(e) => setDate(e.target.value)} />
        </label>

        <div className="bookslot-field">
          <span>Time slot</span>
          <div className="bookslot-slots">
            {timeSlots.map((s) => (
              <button
                type="button"
                key={s}
                className={`slot-chip ${slot === s ? "slot-chip--active" : ""}`}
                onClick={() => setSlot(s)}
              >
                {s}
              </button>
            ))}
          </div>
        </div>

        {error && <p className="bookslot-error">{error}</p>}

        <button type="submit" className="bookslot-submit">
          Confirm slot
        </button>
      </form>
    </div>
  );
}
