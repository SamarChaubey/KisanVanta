import { Menu, ChevronDown } from "lucide-react";
import "../styles/TopBar.css";

export default function TopBar({ language, setLanguage, onMenuClick }) {
  return (
    <header className="topbar">
      <button className="topbar-menu-btn" onClick={onMenuClick} aria-label="Open menu">
        <Menu size={22} />
      </button>
      <div className="topbar-spacer" />
      <div className="topbar-lang">
        <select
          value={language}
          onChange={(e) => setLanguage(e.target.value)}
          aria-label="Select language"
        >
          <option value="en">English</option>
          <option value="hi">हिन्दी</option>
        </select>
        <ChevronDown size={16} className="topbar-lang-chevron" />
      </div>
    </header>
  );
}
