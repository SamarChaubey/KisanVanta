import { Routes, Route } from 'react-router-dom';
import RiskDashboard from './pages/RiskDashboard';
import FarmerPortalApp from './farmer-portal/FarmerPortalApp';

function App() {
  return <Routes>
    <Route path="/admin/*" element={<RiskDashboard />} />
    <Route path="/*" element={<FarmerPortalApp />} />
  </Routes>;
}

export default App;
