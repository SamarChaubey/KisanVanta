import { X, Info, AlertTriangle, CheckCircle2 } from "lucide-react";
import "../styles/Alerts.css";

const ICONS = {
  info: Info,
  warning: AlertTriangle,
  success: CheckCircle2,
};

export default function Alerts({ t, alerts, onDismiss }) {
  return (
    <div className="alerts-page">
      <h1>{t.alerts}</h1>
      <p className="alerts-subtitle">Stay updated on your procurement, slots and payments.</p>

      {alerts.length === 0 ? (
        <div className="alerts-empty">You're all caught up. No new alerts right now.</div>
      ) : (
        <ul className="alerts-list">
          {alerts.map((a) => {
            const Icon = ICONS[a.type] || Info;
            return (
              <li key={a.id} className={`alert-item alert-item--${a.type}`}>
                <span className="alert-icon">
                  <Icon size={18} />
                </span>
                <div className="alert-body">
                  <div className="alert-top">
                    <p className="alert-title">{a.title}</p>
                    <span className="alert-time">{a.time}</span>
                  </div>
                  <p className="alert-message">{a.message}</p>
                </div>
                <button
                  className="alert-dismiss"
                  onClick={() => onDismiss(a.id)}
                  aria-label={`Dismiss alert: ${a.title}`}
                >
                  <X size={16} />
                </button>
              </li>
            );
          })}
        </ul>
      )}
    </div>
  );
}
