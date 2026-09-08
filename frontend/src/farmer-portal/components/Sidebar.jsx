import { NavLink } from "react-router-dom";
import {
  LayoutGrid,
  ClipboardList,
  CalendarDays,
  Bell,
  Info,
  CircleUserRound,
  Sprout,
  LogOut,
} from "lucide-react";
import "../styles/Sidebar.css";

const NAV_ITEMS = [
  { to: "/dashboard", key: "dashboard", icon: LayoutGrid },
  { to: "/procurement", key: "myProcurement", icon: ClipboardList },
  { to: "/book-slot", key: "bookSlot", icon: CalendarDays },
  { to: "/alerts", key: "alerts", icon: Bell },
  { to: "/help", key: "help", icon: Info },
  { to: "/profile", key: "profile", icon: CircleUserRound },
];

export default function Sidebar({ t, alertCount, onLogout, mobileOpen, onCloseMobile }) {
  return (
    <>
      {mobileOpen && <div className="sidebar-scrim" onClick={onCloseMobile} />}
      <aside className={`sidebar ${mobileOpen ? "sidebar--open" : ""}`}>
        <div className="sidebar-logo" aria-label="Krishi Vikray Portal">
          <Sprout size={20} color="#ffffff" />
        </div>

        <nav className="sidebar-nav">
          <ul>
            {NAV_ITEMS.map(({ to, key, icon: Icon }) => (
              <li key={key}>
                <NavLink
                  to={to}
                  onClick={onCloseMobile}
                  className={({ isActive }) =>
                    "sidebar-nav-item" + (isActive ? " sidebar-nav-item--active" : "")
                  }
                >
                  <Icon size={18} strokeWidth={2} />
                  <span>{t[key]}</span>
                  {key === "alerts" && alertCount > 0 && (
                    <span className="sidebar-badge">{alertCount}</span>
                  )}
                </NavLink>
              </li>
            ))}
          </ul>
        </nav>

        <button className="sidebar-logout" onClick={onLogout}>
          <LogOut size={18} strokeWidth={2} />
          <span>Log out</span>
        </button>
      </aside>
    </>
  );
}
