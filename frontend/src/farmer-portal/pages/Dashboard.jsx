import GateEntryPass from "../components/GateEntryPass.jsx";
import "../styles/Dashboard.css";

export default function Dashboard({ t, farmer, procurement, alerts }) {
  const unread = alerts.length;

  return (
    <div className="dashboard">
      <div className="dashboard-main">
        <h1 className="dashboard-greeting">
          {t.namaste}, {farmer.name}!
        </h1>

        <div className="dashboard-info-rows">
          <p>
            <span className="info-label">{t.slot}:</span>{" "}
            <span className="info-value">
              {procurement.slotDate}, {procurement.slotTime}
            </span>
          </p>
          <p>
            <span className="info-label">{t.centre}:</span>{" "}
            <span className="info-value">{procurement.centre}</span>
          </p>
          <p>
            <span className="info-label">{t.lotId}:</span>{" "}
            <span className="info-value">{procurement.lotId}</span>
          </p>
          <p>
            <span className="info-label">{t.value}:</span>{" "}
            <span className="info-value">₹{procurement.value}</span>
          </p>
        </div>

        <div className="dashboard-alerts-box">
          <h2>{t.alerts}</h2>
          {unread === 0 ? (
            <p>
              {t.noAlerts}: {procurement.lotId}
            </p>
          ) : (
            <ul className="dashboard-alerts-list">
              {alerts.slice(0, 2).map((a) => (
                <li key={a.id}>
                  <strong>{a.title}.</strong> {a.message}
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>

      <GateEntryPass t={t} procurement={procurement} farmer={farmer} />
    </div>
  );
}
