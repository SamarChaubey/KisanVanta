import { useState } from 'react';
import { askAdminQuestion } from '../services/api';
import './ChatbotButton.css';

export default function ChatbotButton({ role = 'farmer', language = 'en' }) {
  const [open, setOpen] = useState(false);
  const [question, setQuestion] = useState('');
  const [answer, setAnswer] = useState('');
  const [loading, setLoading] = useState(false);

  async function ask(event) {
    event.preventDefault();
    if (!question.trim()) return;
    setLoading(true);
    try {
      const result = await askAdminQuestion(question, language);
      setAnswer(result.answer);
    } catch (error) {
      setAnswer(role === 'admin' ? 'The operations assistant is unavailable right now.' : 'Please contact the help desk for assistance.');
    } finally {
      setLoading(false);
    }
  }

  return <>
    <button className="chatbot-launcher" onClick={() => setOpen(previous => !previous)} aria-label="Open AI assistant">
      <span>✦</span>{role === 'admin' ? 'Ask operations' : 'Help assistant'}
    </button>
    {open && <section className="chatbot-panel" aria-label="AI assistant">
      <div className="chatbot-header"><strong>{role === 'admin' ? 'Operations assistant' : 'KisanVanta help'}</strong><button onClick={() => setOpen(false)} aria-label="Close assistant">×</button></div>
      <p>{role === 'admin' ? 'Ask about queues, risk, storage, lifting or today\'s procurement.' : 'Ask a question about your slot, gate pass or procurement.'}</p>
      {answer && <div className="chatbot-answer">{answer}</div>}
      <form onSubmit={ask}><input value={question} onChange={event => setQuestion(event.target.value)} placeholder="Type your question" /><button type="submit" disabled={loading}>{loading ? '...' : 'Ask'}</button></form>
    </section>}
  </>;
}