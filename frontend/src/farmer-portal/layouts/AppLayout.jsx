import { useState } from "react";
import { Outlet } from "react-router-dom";
import Sidebar from "../components/Sidebar.jsx";
import TopBar from "../components/TopBar.jsx";
import "../styles/AppLayout.css";
import ChatbotButton from "../../components/ChatbotButton.jsx";

export default function AppLayout({ t, language, setLanguage, alertCount, onLogout }) {
  const [mobileOpen, setMobileOpen] = useState(false);

  return (
    <div className="app-shell">
      <Sidebar
        t={t}
        alertCount={alertCount}
        onLogout={onLogout}
        mobileOpen={mobileOpen}
        onCloseMobile={() => setMobileOpen(false)}
      />
      <div className="app-main">
        <TopBar
          language={language}
          setLanguage={setLanguage}
          onMenuClick={() => setMobileOpen(true)}
        />
        <main className="app-content">
          <Outlet />
        </main>
        <ChatbotButton role="farmer" language={language} />
      </div>
    </div>
  );
}
