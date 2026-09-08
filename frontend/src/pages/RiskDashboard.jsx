import { useEffect, useMemo, useState } from 'react';
import { Bar, BarChart, CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import { getCentreRisks, getRiskHistory, getSlotRequests } from '../services/api';
import ChatbotButton from '../components/ChatbotButton';
import './RiskDashboard.css';

const schedule = [
  ['07:00', 'Jaipur Wheat Procurement Centre', 'Wheat', 18, 'Gate open'],
  ['08:00', 'Sri Ganganagar Wheat Centre', 'Wheat', 26, 'In progress'],
  ['09:00', 'Jodhpur Bajra Procurement Centre', 'Bajra', 12, 'Quality check'],
  ['10:00', 'Jaipur Wheat Procurement Centre', 'Mustard', 21, 'Waiting'],
  ['11:00', 'Karnal Paddy Procurement Centre', 'Paddy', 15, 'Scheduled'],
  ['12:00', 'Amritsar Paddy Procurement Centre', 'Paddy', 9, 'Scheduled'],
];
const updates = [
  ['Minimum Support Price notice', 'Government circular - 08 Sep 2026', 'Review updated crop prices before confirming today\'s lots.'],
  ['e-Mandi operating hours', 'Department update - 07 Sep 2026', 'Extended receiving hours apply to selected centres.'],
  ['Quality grading advisory', 'Food procurement board - 05 Sep 2026', 'Use the revised moisture checklist at intake.'],
];
const lifecycle = ['Request', 'Gate entry', 'Quality', 'Weighing', 'Procurement', 'Storage / lifting'];

function AdminLogin({ onLogin }) {
  const [role, setRole] = useState('officer');
  const [user, setUser] = useState('');
  const [password, setPassword] = useState('');
  return <main className="admin-login"><section className="admin-login-card"><div className="admin-mark">KV</div><p className="admin-kicker">KisanVanta operations</p><h1>Officer and admin login</h1><p>Sign in to manage procurement centres, requests and daily operations.</p><label>Access type<select value={role} onChange={event => setRole(event.target.value)}><option value="officer">Procurement officer</option><option value="admin">System administrator</option></select></label><label>User ID<input value={user} onChange={event => setUser(event.target.value)} placeholder="Enter user ID" /></label><label>Password<input type="password" value={password} onChange={event => setPassword(event.target.value)} placeholder="Enter password" /></label><button className="admin-primary" onClick={() => onLogin(role)}>Sign in</button><small>For authorised government procurement staff only.</small></section></main>;
}

function Metric({ label, value, note, tone = '' }) { return <div className="admin-metric"><span>{label}</span><strong className={tone}>{value}</strong><small>{note}</small></div>; }
function Status({ children, tone = '' }) { return <span className={`admin-status ${tone}`}>{children}</span>; }
function Tab({ active, children, onClick }) { return <button className={`admin-tab ${active ? 'active' : ''}`} onClick={onClick}>{children}</button>; }

function RiskGraphs({ risks, history, selectedRisk, onSelect, refreshing, onRefresh, mode }) {
  const combinedData = risks.map(risk => ({ name: risk.centreName, riskScore: risk.riskScore, storage: risk.storageUtilization || 0 }));
  const historyData = history.map(snapshot => ({ time: new Date(snapshot.createdAt).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }), risk: snapshot.riskScore, storage: snapshot.storageUtilization || 0 }));
  return <div className="admin-graphs"><section className="admin-panel graph-panel"><div className="admin-panel-head"><div><span className="admin-kicker">Risk and capacity</span><h2>{mode === 'admin' ? 'Centre risk comparison' : selectedRisk?.centreName || 'Centre history'}</h2></div><button className="admin-outline" onClick={onRefresh} disabled={refreshing}>{refreshing ? 'Refreshing' : 'Refresh data'}</button></div>{mode === 'admin' ? <ResponsiveContainer width="100%" height={300}><BarChart data={combinedData} margin={{ top: 10, right: 10, left: 0, bottom: 65 }}><CartesianGrid stroke="#dfe3df" vertical={false} /><XAxis dataKey="name" angle={-20} textAnchor="end" interval={0} tick={{ fontSize: 10 }} /><YAxis domain={[0, 100]} unit="%" tick={{ fontSize: 10 }} /><Tooltip /><Bar dataKey="riskScore" name="Risk score" fill="#1c6b3a" /></BarChart></ResponsiveContainer> : <ResponsiveContainer width="100%" height={300}><LineChart data={historyData}><CartesianGrid stroke="#dfe3df" vertical={false} /><XAxis dataKey="time" tick={{ fontSize: 10 }} /><YAxis domain={[0, 100]} unit="%" tick={{ fontSize: 10 }} /><Tooltip /><Line dataKey="risk" name="Risk score" stroke="#1c6b3a" strokeWidth={2} /><Line dataKey="storage" name="Storage" stroke="#1a7dc0" strokeWidth={2} /></LineChart></ResponsiveContainer>}</section><section className="admin-panel risk-list"><div className="admin-panel-head"><div><span className="admin-kicker">Live register</span><h2>Centre health</h2></div></div>{risks.slice(0, 8).map(risk => <button className={`risk-row ${selectedRisk?.centreId === risk.centreId ? 'selected' : ''}`} key={risk.centreId} onClick={() => onSelect(risk.centreId)}><span><b>{risk.centreName}</b><small>{risk.forecast || 'No forecast available'}</small></span><Status tone={risk.riskLevel}>{risk.riskScore}% - {risk.riskLevel}</Status></button>)}</section></div>;
}

function AdminDashboard() {
  const [authenticated, setAuthenticated] = useState(false);
  const [role, setRole] = useState('officer');
  const [tab, setTab] = useState('overview');
  const [risks, setRisks] = useState([]);
  const [history, setHistory] = useState([]);
  const [requests, setRequests] = useState([]);
  const [selectedCentre, setSelectedCentre] = useState('');
  const [lookup, setLookup] = useState('');
  const [updatedAt, setUpdatedAt] = useState(null);
  const [error, setError] = useState('');
  const [refreshing, setRefreshing] = useState(false);

  async function refresh() {
    setRefreshing(true);
    try {
      const [nextRisks, nextRequests] = await Promise.all([getCentreRisks(), getSlotRequests()]);
      setRisks(nextRisks); setRequests(nextRequests); setSelectedCentre(previous => previous || nextRisks[0]?.centreId || ''); setUpdatedAt(new Date()); setError('');
    } catch (requestError) { setError(requestError.message); } finally { setRefreshing(false); }
  }
  useEffect(() => { if (authenticated) refresh(); }, [authenticated]);
  useEffect(() => { if (!selectedCentre) return; getRiskHistory(selectedCentre).then(data => setHistory([...data].reverse())).catch(() => {}); }, [selectedCentre]);

  const selectedRisk = risks.find(risk => risk.centreId === selectedCentre);
  const filteredRequests = requests.filter(request => JSON.stringify(request).toLowerCase().includes(lookup.toLowerCase()));
  const pending = requests.filter(request => ['received', 'alternative_suggested'].includes(request.status)).length;
  const highRisk = risks.filter(risk => ['high', 'critical'].includes(risk.riskLevel)).length;
  const todayLots = requests.reduce((sum, request) => sum + Number(request.quantity || 0), 0) || 286;
  if (!authenticated) return <AdminLogin onLogin={selectedRole => { setRole(selectedRole); setAuthenticated(true); }} />;

  const tabs = [['overview', 'Overview'], ['schedule', 'Booking schedule'], ['requests', 'Slot requests'], ['lookup', 'QR / ID lookup'], ['lifecycle', 'Ticket lifecycle'], ['quality', 'Quality and weighing'], ['storage', 'Storage and lifting'], ['alerts', 'Alerts and escalation'], ['updates', 'Government updates']];
  return <div className="admin-console"><header className="admin-topbar"><div className="admin-brand"><span>KV</span><div><strong>KisanVanta</strong><small>Government procurement operations</small></div></div><div className="admin-user"><span>{role === 'admin' ? 'Administrator' : 'Procurement officer'}</span><button onClick={() => setAuthenticated(false)}>Sign out</button></div></header><nav className="admin-tabs">{tabs.map(([id, label]) => <Tab key={id} active={tab === id} onClick={() => setTab(id)}>{label}</Tab>)}</nav><main className="admin-content"><div className="admin-page-head"><div><span className="admin-kicker">Daily operations - 09 September 2026</span><h1>{tabs.find(item => item[0] === tab)?.[1]}</h1><p>Use verified centre data to coordinate today&apos;s procurement work.</p></div><div className="admin-head-actions"><span className="admin-updated">{updatedAt ? `Updated ${updatedAt.toLocaleTimeString()}` : 'Not synced'}</span><button className="admin-primary small" onClick={refresh}>Refresh</button></div></div>{error && <div className="admin-error">Unable to load live data: {error}. Check that FastAPI is running on port 8000.</div>}
      {tab === 'overview' && <><div className="admin-metrics"><Metric label="Open centres" value={risks.length || '--'} note="Reporting now" tone="green" /><Metric label="Pending requests" value={pending || '--'} note="Need review" tone="amber" /><Metric label="Today\'s lots" value={todayLots} note="Across all centres" /><Metric label="High-risk centres" value={highRisk || '--'} note="Needs action" tone="red" /><Metric label="Average wait" value="2h 18m" note="Network estimate" tone="amber" /><Metric label="Storage use" value="74%" note="14,800 / 20,000 bags" tone="blue" /></div><RiskGraphs risks={risks} history={history} selectedRisk={selectedRisk} onSelect={setSelectedCentre} refreshing={refreshing} onRefresh={refresh} mode="admin" /><div className="admin-columns"><section className="admin-panel"><div className="admin-panel-head"><div><span className="admin-kicker">Today</span><h2>Procurement flow</h2></div></div><div className="flow-steps">{lifecycle.map((step, index) => <div key={step}><span>{index + 1}</span><b>{step}</b><small>{[18, 142, 91, 64, 38, 22][index]} lots</small></div>)}</div></section><section className="admin-panel"><div className="admin-panel-head"><div><span className="admin-kicker">Attention</span><h2>Alerts and escalation</h2></div><Status tone="critical">3 open</Status></div><div className="alert-line"><Status tone="critical">Critical</Status><span><b>Amer storage at 87%</b><small>Escalate to centre manager - divert arrivals</small></span></div><div className="alert-line"><Status tone="high">High</Status><span><b>Jaipur assaying queue rising</b><small>Assign reserve bay - quality lead</small></span></div></section></div></>}
      {tab === 'schedule' && <Schedule />}
      {tab === 'requests' && <RequestRegister requests={filteredRequests} lookup={lookup} setLookup={setLookup} />}
      {tab === 'lookup' && <Lookup requests={requests} />}
      {tab === 'lifecycle' && <Lifecycle />}
      {tab === 'quality' && <Quality />}
      {tab === 'storage' && <Storage risks={risks} />}
      {tab === 'alerts' && <AlertsPanel risks={risks} />}
      {tab === 'updates' && <Updates />}
    </main><ChatbotButton role="admin" /></div>;
}

function Schedule() { return <section className="admin-panel"><div className="admin-panel-head"><div><span className="admin-kicker">09 September 2026</span><h2>Booking schedule</h2></div><button className="admin-outline">Print schedule</button></div><p className="admin-help">Arrivals planned by hour. Use this view at the gate and coordinate centre teams.</p><div className="schedule-table"><div className="table-head"><span>Time</span><span>Centre</span><span>Crop</span><span>Lots</span><span>State</span></div>{schedule.map(row => <div className="table-row" key={`${row[0]}-${row[1]}`}><span><b>{row[0]}</b></span><span>{row[1]}</span><span>{row[2]}</span><span>{row[3]}</span><Status tone={row[4] === 'Waiting' ? 'amber' : 'green'}>{row[4]}</Status></div>)}</div></section>; }
function RequestRegister({ requests, lookup, setLookup }) { return <section className="admin-panel"><div className="admin-panel-head"><div><span className="admin-kicker">Intake control</span><h2>Slot requests</h2></div><input className="admin-search" value={lookup} onChange={event => setLookup(event.target.value)} placeholder="Search farmer, centre or ID" /></div><div className="schedule-table"><div className="table-head"><span>Request</span><span>Farmer</span><span>Centre</span><span>Preferred</span><span>Status</span></div>{requests.length ? requests.map(request => <div className="table-row" key={String(request._id)}><span><b>{String(request._id).slice(-8)}</b></span><span>{request.farmerId}</span><span>{request.centreId}</span><span>{request.requestedDate}<small>{request.preferredTime}</small></span><Status tone={request.status === 'confirmed' ? 'green' : 'amber'}>{request.status}</Status></div>) : <p className="admin-empty">No requests match this search.</p>}</div></section>; }
function Lookup({ requests }) { const [value, setValue] = useState(''); const result = requests.find(item => JSON.stringify(item).toLowerCase().includes(value.toLowerCase()) && value); return <section className="admin-panel lookup-panel"><span className="admin-kicker">Gate and help desk</span><h2>QR / ID lookup</h2><p className="admin-help">Scan a gate pass with a QR reader or enter a request, farmer or lot ID.</p><div className="lookup-box"><input value={value} onChange={event => setValue(event.target.value)} placeholder="Enter ID or scan code" /><button className="admin-primary">Search record</button></div>{result ? <div className="lookup-result"><Status tone="green">Record found</Status><h3>Request {String(result._id).slice(-8)}</h3><p>Farmer ID: {result.farmerId} - Centre ID: {result.centreId}</p><p>Status: <b>{result.status}</b> - Preferred: {result.requestedDate} at {result.preferredTime}</p></div> : <div className="lookup-placeholder">Lookup results will appear here.</div>}</section>; }
function Lifecycle() { return <section className="admin-panel"><span className="admin-kicker">Lot control</span><h2>Procurement lifecycle</h2><p className="admin-help">Track each lot from request to storage or lifting. Officers update the current stage at the centre.</p><div className="lifecycle-board">{lifecycle.map((stage, index) => <div className="lifecycle-column" key={stage}><h3><span>{index + 1}</span>{stage}</h3><div className="lifecycle-card"><b>{[18, 142, 91, 64, 38, 22][index]} lots</b><small>{['New requests', 'Verified arrivals', 'Awaiting grading', 'On weighbridge', 'Payment queue', 'Ready for dispatch'][index]}</small></div></div>)}</div></section>; }
function Quality() { return <div className="admin-two-column"><section className="admin-panel"><span className="admin-kicker">Quality desk</span><h2>Quality checks</h2><div className="admin-metrics compact"><Metric label="Awaiting check" value="91" note="lots" tone="amber" /><Metric label="Accepted today" value="64" note="lots" tone="green" /><Metric label="Held for review" value="7" note="lots" tone="red" /></div><div className="check-row"><b>Wheat - Lot KVF102537</b><Status tone="amber">Moisture review</Status></div><div className="check-row"><b>Mustard - Lot KVF102529</b><Status tone="green">Grade A</Status></div></section><section className="admin-panel"><span className="admin-kicker">Weighbridge</span><h2>Weighing desk</h2><div className="weigh-card"><b>4 of 5 weighbridges active</b><strong>64 lots</strong><small>Current queue - estimated wait 42 min</small><button className="admin-outline">View weighbridge status</button></div></section></div>; }
function Storage({ risks }) { return <div className="admin-two-column"><section className="admin-panel"><span className="admin-kicker">Post-procurement</span><h2>Storage and lifting</h2>{risks.slice(0, 6).map(risk => <div className="storage-row" key={risk.centreId}><span><b>{risk.centreName}</b><small>{risk.liftingGap ? `${risk.liftingGap} bags/day lifting gap` : 'Lifting on plan'}</small></span><strong>{risk.storageUtilization || 0}%</strong><div className="storage-bar"><i style={{ width: `${risk.storageUtilization || 0}%` }} /></div></div>)}</section><section className="admin-panel"><span className="admin-kicker">Action queue</span><h2>Recommended actions</h2><div className="action-item"><b>Divert arrivals from Amer</b><small>Owner: Centre manager - Priority: immediate</small><button className="admin-outline">Escalate</button></div><div className="action-item"><b>Confirm evening dispatch</b><small>Owner: Logistics lead - Priority: today</small><button className="admin-outline">Assign</button></div></section></div>; }
function AlertsPanel({ risks }) { return <section className="admin-panel"><div className="admin-panel-head"><div><span className="admin-kicker">Control room</span><h2>Alerts and escalation</h2></div><button className="admin-primary small">Acknowledge all</button></div>{risks.slice(0, 5).map((risk, index) => <div className="escalation-row" key={risk.centreId}><Status tone={risk.riskLevel}>{risk.riskLevel}</Status><span><b>{risk.centreName}</b><small>{risk.forecast || 'Centre requires review'}</small></span><span><b>{index < 2 ? 'Centre manager' : 'Procurement officer'}</b><small>Owner</small></span><button className="admin-outline">Escalate</button></div>)}</section>; }
function Updates() { return <div className="admin-two-column"><section className="admin-panel"><span className="admin-kicker">Official notices</span><h2>Government updates</h2>{updates.map(update => <article className="update-item" key={update[0]}><b>{update[0]}</b><small>{update[1]}</small><p>{update[2]}</p></article>)}</section><section className="admin-panel"><span className="admin-kicker">Today</span><h2>Procurement brief</h2><p className="admin-help">Review official notices before the first gate opening and confirm that centre teams have acknowledged changes.</p><button className="admin-primary">Mark brief as read</button></section></div>; }

export default AdminDashboard;
