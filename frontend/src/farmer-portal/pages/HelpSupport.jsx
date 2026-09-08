import { useState } from "react";
import { ChevronDown, Phone, Mail } from "lucide-react";
import { faqs } from "../data/mockData.js";
import "../styles/HelpSupport.css";

export default function HelpSupport({ t }) {
  const [openIndex, setOpenIndex] = useState(0);
  const [subject, setSubject] = useState("");
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [sent, setSent] = useState(false);

  function toggle(i) {
    setOpenIndex(openIndex === i ? -1 : i);
  }

  function handleSend(e) {
    e.preventDefault();
    if (!subject.trim() || !message.trim()) {
      setError("Please fill in both subject and message.");
      return;
    }
    setError("");
    setSent(true);
    setSubject("");
    setMessage("");
  }

  return (
    <div className="help-page">
      <h1>{t.help}</h1>
      <p className="help-subtitle">Find answers to common questions or reach our support team.</p>

      <div className="help-contact-row">
        <a href="tel:18001801551" className="help-contact-card">
          <Phone size={18} />
          <div>
            <p className="help-contact-label">Call the helpline</p>
            <p className="help-contact-value">1800-180-1551</p>
          </div>
        </a>
        <a href="mailto:support@krishivikray.gov.in" className="help-contact-card">
          <Mail size={18} />
          <div>
            <p className="help-contact-label">Email support</p>
            <p className="help-contact-value">support@krishivikray.gov.in</p>
          </div>
        </a>
      </div>

      <h2 className="help-section-title">Frequently asked questions</h2>
      <div className="faq-list">
        {faqs.map((f, i) => (
          <div className="faq-item" key={f.q}>
            <button
              className="faq-question"
              onClick={() => toggle(i)}
              aria-expanded={openIndex === i}
            >
              <span>{f.q}</span>
              <ChevronDown size={18} className={openIndex === i ? "faq-chevron faq-chevron--open" : "faq-chevron"} />
            </button>
            {openIndex === i && <p className="faq-answer">{f.a}</p>}
          </div>
        ))}
      </div>

      <h2 className="help-section-title">Still need help?</h2>
      {sent ? (
        <p className="help-sent-note">
          Your message has been sent. Our support team will get back to you within 24 hours.
        </p>
      ) : (
        <form className="help-form" onSubmit={handleSend} noValidate>
          <label className="help-field">
            <span>Subject</span>
            <input value={subject} onChange={(e) => setSubject(e.target.value)} placeholder="e.g. Unable to book a slot" />
          </label>
          <label className="help-field">
            <span>Message</span>
            <textarea
              rows={4}
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              placeholder="Describe the issue you're facing"
            />
          </label>
          {error && <p className="help-error">{error}</p>}
          <button type="submit" className="help-submit">
            Send message
          </button>
        </form>
      )}
    </div>
  );
}
