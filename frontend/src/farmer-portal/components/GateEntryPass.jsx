import { BadgeCheck } from "lucide-react";
import "../styles/GateEntryPass.css";

/*
  Note: the QR code image from the original design is not available as an
  asset. It is reproduced here as a generated placeholder QR-style pattern.
  Replace `QrPlaceholder` with a real QR code (e.g. from a `qrcode` npm
  package) wired to the actual token/lot ID when integrating with a backend.
*/
function QrPlaceholder({ seed = "A-45" }) {
  const cells = [];
  let s = 0;
  for (let i = 0; i < seed.length; i++) s += seed.charCodeAt(i);
  for (let i = 0; i < 49; i++) {
    s = (s * 9301 + 49297) % 233280;
    cells.push(s / 233280 > 0.52);
  }
  return (
    <div className="qr-placeholder" role="img" aria-label={`QR code for token ${seed}`}>
      <div className="qr-grid">
        {cells.map((filled, i) => (
          <span key={i} className={filled ? "qr-cell qr-cell--on" : "qr-cell"} />
        ))}
      </div>
    </div>
  );
}

export default function GateEntryPass({ t, procurement, farmer, compact = false }) {
  return (
    <div className="gate-pass-card">
      <div className="gate-pass-header">
        <span>{t.gateEntryPass}</span>
        <BadgeCheck size={22} strokeWidth={2} color="#ffffff" />
      </div>
      <div className="gate-pass-body">
        <div className="gate-pass-token">TOKEN #{procurement.token}</div>
        <QrPlaceholder seed={procurement.token} />

        {!compact && (
          <div className="gate-pass-grid">
            <div className="gate-pass-field">
              <span className="gate-pass-label">{t.farmerName}</span>
              <span className="gate-pass-value">{farmer.name}</span>
            </div>
            <div className="gate-pass-field">
              <span className="gate-pass-label">{t.tractorNumber}</span>
              <span className="gate-pass-value">{farmer.tractorNumber}</span>
            </div>
            <div className="gate-pass-field">
              <span className="gate-pass-label">{t.typeOfCrop}</span>
              <span className="gate-pass-value">{procurement.typeOfCrop}</span>
            </div>
            <div className="gate-pass-field">
              <span className="gate-pass-label">{t.grossWeight}</span>
              <span className="gate-pass-value">{procurement.grossWeight}</span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
