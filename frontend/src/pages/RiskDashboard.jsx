import { useEffect, useRef, useState } from 'react';
import {
  Bar,
  BarChart,
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';

import { getCentreRisks, getRiskHistory } from '../services/api';
import './RiskDashboard.css';

const REFRESH_MS = 15000;

function RiskDashboard() {
  const [mode, setMode] = useState('admin');
  const [risks, setRisks] = useState([]);
  const [centreId, setCentreId] = useState('');
  const [history, setHistory] = useState([]);
  const [error, setError] = useState('');
  const [updatedAt, setUpdatedAt] = useState(null);
  const [refreshing, setRefreshing] = useState(false);
  const centreIdRef = useRef('');

  async function refreshRisks() {
    setRefreshing(true);
    try {
      const nextRisks = await getCentreRisks();
      setRisks(nextRisks);
      const nextCentreId = centreIdRef.current || nextRisks[0]?.centreId || '';
      setCentreId(nextCentreId);
      centreIdRef.current = nextCentreId;
      await refreshHistory(nextCentreId);
      setUpdatedAt(new Date());
      setError('');
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setRefreshing(false);
    }
  }

  async function refreshHistory(selectedCentreId) {
    if (!selectedCentreId) {
      setHistory([]);
      return;
    }
    try {
      const snapshots = await getRiskHistory(selectedCentreId);
      setHistory([...snapshots].reverse());
    } catch (requestError) {
      setError(requestError.message);
    }
  }

  useEffect(() => {
    refreshRisks();
    const interval = window.setInterval(refreshRisks, REFRESH_MS);
    return () => window.clearInterval(interval);
  }, []);

  useEffect(() => {
    centreIdRef.current = centreId;
    refreshHistory(centreId);
  }, [centreId]);

  const selectedRisk = risks.find((risk) => risk.centreId === centreId);
  const combinedData = risks.map((risk) => ({
    name: risk.centreName,
    riskScore: risk.riskScore,
    queueHours: risk.queueHours || 0,
    storageUtilization: risk.storageUtilization || 0,
  }));
  const historyData = history.map((snapshot) => ({
    time: new Date(snapshot.createdAt).toLocaleTimeString([], {
      hour: '2-digit',
      minute: '2-digit',
    }),
    riskScore: snapshot.riskScore,
    queueHours: snapshot.queueHours || 0,
    storageUtilization: snapshot.storageUtilization || 0,
  }));

  return (
    <section className="risk-dashboard">
      <header className="risk-header">
        <div>
          <p className="eyebrow">KisanVanta operations</p>
          <h2>Procurement risk radar</h2>
          <p className="risk-subtitle">
            Current database status and forecast pressure, refreshed every minute.
          </p>
        </div>
        <div className="mode-switch" role="group" aria-label="Dashboard mode">
          <button className={mode === 'admin' ? 'active' : ''} onClick={() => setMode('admin')}>
            Admin overview
          </button>
          <button className={mode === 'pco' ? 'active' : ''} onClick={() => setMode('pco')}>
            Centre view
          </button>
        </div>
      </header>

      {error && <p className="risk-error" role="alert">{error}</p>}

      {mode === 'pco' && (
        <label className="centre-picker">
          Centre
          <select value={centreId} onChange={(event) => setCentreId(event.target.value)}>
            {risks.map((risk) => (
              <option key={risk.centreId} value={risk.centreId}>{risk.centreName}</option>
            ))}
          </select>
        </label>
      )}

      {mode === 'admin' ? (
        <div className="chart-panel">
          <div className="panel-heading">
            <div>
              <span className="panel-kicker">All open centres</span>
              <h3>Combined risk comparison</h3>
            </div>
            <div className="panel-actions">
              <span className="updated-label">
                {updatedAt ? `Checked ${updatedAt.toLocaleTimeString()}` : 'Loading'}
              </span>
              <button type="button" className="refresh-button" onClick={refreshRisks} disabled={refreshing}>
                {refreshing ? 'Refreshing...' : 'Refresh'}
              </button>
            </div>
          </div>
          <ResponsiveContainer width="100%" height={340}>
            <BarChart data={combinedData} margin={{ top: 12, right: 20, left: 0, bottom: 48 }}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} />
              <XAxis dataKey="name" angle={-18} textAnchor="end" interval={0} />
              <YAxis domain={[0, 100]} unit="%" />
              <Tooltip formatter={(value) => [`${value}%`, 'Risk score']} />
              <Bar dataKey="riskScore" fill="#e36b3d" radius={[5, 5, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      ) : (
        <>
          <div className="risk-summary">
            <div><span>Risk score</span><strong>{selectedRisk?.riskScore ?? '--'}%</strong></div>
            <div><span>Risk level</span><strong>{selectedRisk?.riskLevel ?? '--'}</strong></div>
            <div><span>Queue estimate</span><strong>{selectedRisk?.queueHours ?? '--'} hrs</strong></div>
            <div><span>Storage used</span><strong>{selectedRisk?.storageUtilization ?? '--'}%</strong></div>
          </div>
          <div className="chart-panel">
            <div className="panel-heading">
              <div>
                <span className="panel-kicker">Centre history</span>
                <h3>{selectedRisk?.centreName || 'Select a centre'}</h3>
              </div>
            </div>
            <ResponsiveContainer width="100%" height={340}>
              <LineChart data={historyData} margin={{ top: 12, right: 20, left: 0, bottom: 12 }}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} />
                <XAxis dataKey="time" />
                <YAxis domain={[0, 100]} unit="%" />
                <Tooltip />
                <Line type="monotone" dataKey="riskScore" name="Risk score" stroke="#e36b3d" strokeWidth={3} dot={false} />
                <Line type="monotone" dataKey="storageUtilization" name="Storage %" stroke="#2d7f73" strokeWidth={2} dot={false} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </>
      )}
    </section>
  );
}

export default RiskDashboard;