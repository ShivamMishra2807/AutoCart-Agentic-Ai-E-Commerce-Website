import React, { useRef, useState } from 'react';
import { Sparkles, Send } from 'lucide-react';
import api from '../../services/api';

const START = [
  'Which of my products are low on stock?',
  'What are my best selling products?',
  'How many orders are waiting?',
  'What is my revenue so far?',
  'Which products have the best ratings?',
  'Are any customer questions waiting?',
  'What is my profit?',
];

/** Ask about your own products in plain words. Answers come from your rows in the database, shown as a small table. */
export default function SellerAssistant() {
  const [log, setLog] = useState([]);
  const [text, setText] = useState('');
  const [busy, setBusy] = useState(false);
  const end = useRef(null);

  const ask = async (q) => {
    const question = (q ?? text).trim();
    if (!question || busy) return;
    setText(''); setBusy(true);
    setLog((l) => [...l, { q: question }]);
    try {
      const { data } = await api.post('/seller/assistant', { message: question });
      setLog((l) => [...l, { a: data }]);
    } catch (e) {
      setLog((l) => [...l, { a: { answer: e?.response?.data?.detail || 'I could not answer that right now.', columns: [], rows: [] } }]);
    } finally {
      setBusy(false);
      window.setTimeout(() => end.current?.scrollIntoView({ block: 'nearest' }), 50);
    }
  };

  return (
    <section id="assistant" className="ac-box" aria-labelledby="asst-h" style={{ marginTop: 24 }}>
      <h2 id="asst-h" className="ac-row" style={{ gap: 8 }}><Sparkles size={20} /> Munim, your shop assistant</h2>
      <p className="ac-muted" style={{ marginTop: 4 }}>Ask in your own words. Munim works out the numbers from your products and orders, then explains them. Nothing is guessed.</p>
      <div className="ac-pm-presets" style={{ margin: '14px 0' }}>
        {START.map((s) => <button key={s} type="button" onClick={() => ask(s)}>{s}</button>)}
      </div>
      <div role="log" aria-live="polite" style={{ display: 'grid', gap: 12 }}>
        {log.map((m, i) => m.q
          ? <div key={i} style={{ justifySelf: 'end', background: 'var(--brand)', color: 'var(--on-brand)', padding: '10px 14px', borderRadius: 16 }}>{m.q}</div>
          : (
            <div key={i} style={{ background: 'var(--fog)', padding: 14, borderRadius: 16 }}>
              <p>{m.a.answer}</p>
              {m.a.rows?.length > 0 && (
                <table className="ac-table" style={{ marginTop: 10 }}>
                  <thead><tr>{m.a.columns.map((c) => <th key={c}>{c}</th>)}</tr></thead>
                  <tbody>{m.a.rows.map((r, j) => <tr key={j}>{r.map((v, k) => <td key={k}>{v}</td>)}</tr>)}</tbody>
                </table>
              )}
              {m.a.source && <small className="ac-muted">Source: {m.a.source}{m.a.provider && m.a.provider !== 'database' ? ' · worded by Gemini' : ''}</small>}
            </div>
          ))}
        <div ref={end} />
      </div>
      <form onSubmit={(e) => { e.preventDefault(); ask(); }} className="ac-row" style={{ marginTop: 12 }}>
        <label className="ac-sr" htmlFor="sa-in">Ask a question about your shop</label>
        <input id="sa-in" className="ac-input" style={{ flex: 1 }} value={text} onChange={(e) => setText(e.target.value)} placeholder="e.g. How many Flask units are left?" maxLength={300} />
        <button className="ac-btn ac-btn-blue" disabled={busy || !text.trim()}><Send size={16} /> Ask</button>
      </form>
    </section>
  );
}
