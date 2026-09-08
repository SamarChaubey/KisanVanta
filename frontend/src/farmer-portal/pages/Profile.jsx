import { useState } from "react";
import { Pencil } from "lucide-react";
import "../styles/Profile.css";

export default function Profile({ t, farmer, setFarmer }) {
  const [editing, setEditing] = useState(false);
  const [draft, setDraft] = useState(farmer);

  function startEdit() {
    setDraft(farmer);
    setEditing(true);
  }

  function handleChange(field, value) {
    setDraft((d) => ({ ...d, [field]: value }));
  }

  function handleSave(e) {
    e.preventDefault();
    setFarmer(draft);
    setEditing(false);
  }

  const initials = farmer.name
    .split(" ")
    .map((p) => p[0])
    .join("")
    .slice(0, 2)
    .toUpperCase();

  return (
    <div className="profile-page">
      <h1>{t.profile}</h1>
      <p className="profile-subtitle">View and update your registered farmer details.</p>

      <div className="profile-card">
        <div className="profile-header">
          <div className="profile-avatar">{initials}</div>
          <div>
            <p className="profile-name">{farmer.name}</p>
            <p className="profile-id">Farmer ID: {farmer.farmerId}</p>
          </div>
          {!editing && (
            <button className="profile-edit-btn" onClick={startEdit}>
              <Pencil size={15} />
              Edit
            </button>
          )}
        </div>

        {editing ? (
          <form className="profile-form" onSubmit={handleSave}>
            <label className="profile-field">
              <span>Full name</span>
              <input value={draft.name} onChange={(e) => handleChange("name", e.target.value)} />
            </label>
            <label className="profile-field">
              <span>Phone number</span>
              <input value={draft.phone} onChange={(e) => handleChange("phone", e.target.value)} />
            </label>
            <label className="profile-field">
              <span>Village / address</span>
              <input value={draft.village} onChange={(e) => handleChange("village", e.target.value)} />
            </label>
            <label className="profile-field">
              <span>Tractor number</span>
              <input
                value={draft.tractorNumber}
                onChange={(e) => handleChange("tractorNumber", e.target.value)}
              />
            </label>
            <div className="profile-form-actions">
              <button type="button" className="profile-cancel-btn" onClick={() => setEditing(false)}>
                Cancel
              </button>
              <button type="submit" className="profile-save-btn">
                Save changes
              </button>
            </div>
          </form>
        ) : (
          <dl className="profile-details">
            <div>
              <dt>Phone number</dt>
              <dd>{farmer.phone}</dd>
            </div>
            <div>
              <dt>Village / address</dt>
              <dd>{farmer.village}</dd>
            </div>
            <div>
              <dt>Tractor number</dt>
              <dd>{farmer.tractorNumber}</dd>
            </div>
            <div>
              <dt>Linked bank account</dt>
              <dd>{farmer.bankAccount}</dd>
            </div>
          </dl>
        )}
      </div>
    </div>
  );
}
