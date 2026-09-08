import { useState } from 'react';
import { Navigate, Route, Routes } from 'react-router-dom';
import AppLayout from './layouts/AppLayout.jsx';
import Login from './pages/Login.jsx';
import Dashboard from './pages/Dashboard.jsx';
import MyProcurement from './pages/MyProcurement.jsx';
import BookSlot from './pages/BookSlot.jsx';
import Alerts from './pages/Alerts.jsx';
import HelpSupport from './pages/HelpSupport.jsx';
import Profile from './pages/Profile.jsx';
import { translations } from './data/translations.js';
import { initialFarmer, initialProcurement, initialAlerts } from './data/mockData.js';
import { createSlotRequest } from '../services/api';

export default function FarmerPortalApp() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [language, setLanguage] = useState('en');
  const [farmer, setFarmer] = useState(initialFarmer);
  const [procurement, setProcurement] = useState(initialProcurement);
  const [alerts, setAlerts] = useState(initialAlerts);
  const t = translations[language];

  function handleBookSlot({ centre, date, slot }) {
    setProcurement(previous => ({ ...previous, centre, slotDate: date, slotTime: slot }));
    setAlerts(previous => [{ id: Date.now(), type: 'success', title: 'Slot booked', message: `Your slot at ${centre} on ${date} (${slot}) is confirmed.`, time: 'Just now' }, ...previous]);
    createSlotRequest({ farmerName: farmer.name, phone: farmer.phone.replace(/\D/g, '').slice(-10), centre, crop: 'Wheat', quantity: 50, date, time: slot }).catch(() => {});
  }

  if (!isAuthenticated) return <Routes><Route path="*" element={<Login onLogin={() => setIsAuthenticated(true)} />} /></Routes>;

  return <Routes>
    <Route element={<AppLayout t={t} language={language} setLanguage={setLanguage} alertCount={alerts.length} onLogout={() => setIsAuthenticated(false)} />}>
      <Route path="/" element={<Navigate to="/dashboard" replace />} />
      <Route path="/dashboard" element={<Dashboard t={t} farmer={farmer} procurement={procurement} alerts={alerts} />} />
      <Route path="/procurement" element={<MyProcurement t={t} farmer={farmer} procurement={procurement} />} />
      <Route path="/book-slot" element={<BookSlot t={t} onBook={handleBookSlot} />} />
      <Route path="/alerts" element={<Alerts t={t} alerts={alerts} onDismiss={id => setAlerts(previous => previous.filter(alert => alert.id !== id))} />} />
      <Route path="/help" element={<HelpSupport t={t} />} />
      <Route path="/profile" element={<Profile t={t} farmer={farmer} setFarmer={setFarmer} />} />
      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Route>
  </Routes>;
}