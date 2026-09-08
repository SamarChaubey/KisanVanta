import { Check } from "lucide-react";
import GateEntryPass from "../components/GateEntryPass.jsx";
import { procurementSteps } from "../data/mockData.js";
import "../styles/MyProcurement.css";

export default function MyProcurement({ t, farmer, procurement }) {
  const currentStepIndex = 1;

  return (
    <div className="procurement-page">
      <div className="procurement-main">
        <h1>{t.myProcurement}</h1>
        <p className="procurement-subtitle">
          Track the progress of your procurement and stay updated in real time.
        </p>

        <ol className="procurement-timeline">
          {procurementSteps.map((step, i) => {
            const state =
              i < currentStepIndex ? "done" : i === currentStepIndex ? "active" : "pending";
            return (
              <li key={step.key} className={`timeline-item timeline-item--${state}`}>
                <span className="timeline-dot">
                  {state === "done" ? <Check size={13} strokeWidth={3} /> : i + 1}
                </span>
                <div className="timeline-content">
                  <p className="timeline-label">{step.label}</p>
                  <p className="timeline-detail">{step.detail}</p>
                </div>
              </li>
            );
          })}
        </ol>
      </div>

      <GateEntryPass t={t} procurement={procurement} farmer={farmer} compact />
    </div>
  );
}
