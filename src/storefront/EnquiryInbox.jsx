import React, { useCallback, useEffect, useState } from 'react';
import api from '../services/api';
import './storefront.css';
import './forms.css';

const when = (d) => new Date(d).toLocaleString([], { dateStyle: 'medium', timeStyle: 'short' });

/** Questions waiting for an answer. Sellers see questions about their products; admins see everything. */
export default function EnquiryInbox({ title = 'Customer enquiries', allowDraft = true }) {
  const [rows, setRows] = useState([]);
  const [filter, setFilter] = useState('OPEN');
  const [drafts, setDrafts] = useState({});
  const [publicIds, setPublicIds] = useState({});
  const [busy, setBusy] = useState('');
  const [error, setError] = useState('');
  const [notice, setNotice] = useState('');

  const load = useCallback(() => api.get('/enquiries', { params: filter ? { status: filter } : {} })
    .then((r) => { setRows(r.data); setError(''); })
    .catch((e) => setError(e?.response?.status === 401 ? 'Please sign in to see enquiries.' : 'Could not load enquiries.')), [filter]);
  useEffect(() => { load(); }, [load]);

  const draft = async (e) => {
    setBusy(`d-${e.id}`); setError('');
    try {
      const { data } = await api.post(`/enquiries/${e.id}/draft`);
      setDrafts((d) => ({ ...d, [e.id]: data.draft }));
      setNotice(data.note);
    } catch { setError('We could not suggest an answer. Write it yourself.'); }
    setBusy('');
  };

  const answer = async (e) => {
    setBusy(e.id); setError(''); setNotice('');
    try {
      await api.post(`/enquiries/${e.id}/answer`, { answer: drafts[e.id], isPublic: publicIds[e.id] !== false });
      setDrafts((d) => ({ ...d, [e.id]: '' }));
      setNotice(`Answer sent to ${e.customerName}.${publicIds[e.id] !== false && e.productId ? ' It now shows on the product page.' : ''} Find it under Answered.`);
      await load();
    } catch (err) { setError(err?.response?.data?.detail || 'The answer did not send.'); }
    setBusy('');
  };

  // The server already limits non-admins to their own products' questions, so filtering by status here is only a view choice.
  const shown = filter ? rows.filter((r) => r.status === filter) : rows;

  return (
    <section className="ac" style={{ marginTop: 32 }} aria-labelledby="enq-h">
      <div className="ac-row-between" style={{ marginBottom: 14 }}>
        <h2 id="enq-h" className="ac-display" style={{ fontSize: 26 }}>{title}</h2>
        <div className="ac-row">{[['OPEN', 'Waiting for an answer'], ['ANSWERED', 'Answered'], ['', 'All']].map(([k, n]) => (
          <button key={n} className={`ac-btn ac-btn-small ${filter === k ? 'ac-btn-blue' : 'ac-btn-outline'}`} aria-pressed={filter === k} onClick={() => setFilter(k)}>{n}</button>))}</div>
      </div>
      {error && <div className="ac-warn" role="alert">{error}</div>}
      {notice && <div className="ac-box" role="status" style={{ borderColor: 'var(--brand)', marginBottom: 12 }}>{notice}</div>}
      {shown.length === 0 && !error && <div className="ac-box ac-muted">No enquiries here. New questions from customers show up here.</div>}
      {shown.map((e) => (
        <div className="ac-box" key={e.id}>
          <div className="ac-row-between">
            <b>{e.productName || 'General question'}</b>
            <span className="ac-chip-status" data-tone={e.status === 'ANSWERED' ? 'ok' : 'warn'}>{e.status === 'ANSWERED' ? 'Answered' : 'Waiting'}</span>
          </div>
          <p className="ac-muted" style={{ margin: '4px 0 10px', fontSize: 14 }}>{e.customerName} · {e.customerEmail}{e.customerPhone ? ` · ${e.customerPhone}` : ''} · {when(e.createdAt)}</p>
          <p style={{ margin: 0, whiteSpace: 'pre-wrap' }}>{e.message}</p>
          {e.status === 'ANSWERED' ? (
            <p className="ac-bubble" data-from="support" style={{ marginTop: 12 }}><b>{e.answeredBy}:</b> {e.answer}{e.isPublic ? ' (shown on the product page)' : ''}</p>
          ) : (
            <div style={{ marginTop: 14 }}>
              <label className="ac-sr" htmlFor={`a-${e.id}`}>Your answer</label>
              <textarea id={`a-${e.id}`} className="ac-textarea" placeholder="Write your answer. The customer is emailed the answer." value={drafts[e.id] || ''} onChange={(ev) => setDrafts({ ...drafts, [e.id]: ev.target.value })} />
              <div className="ac-row-between" style={{ marginTop: 10 }}>
                {e.productId
                  ? <label className="ac-check"><input type="checkbox" checked={publicIds[e.id] !== false} onChange={(ev) => setPublicIds({ ...publicIds, [e.id]: ev.target.checked })} /><span>Show this answer on the product page (first name only)</span></label>
                  : <span />}
                <div className="ac-row">
                  {allowDraft && <button type="button" className="ac-btn ac-btn-outline ac-btn-small" disabled={busy === `d-${e.id}`} onClick={() => draft(e)}>{busy === `d-${e.id}` ? 'Thinking…' : 'Suggest an answer'}</button>}
                  <button className="ac-btn ac-btn-blue ac-btn-small" disabled={busy === e.id || !(drafts[e.id] || '').trim()} onClick={() => answer(e)}>{busy === e.id ? 'Sending…' : 'Send answer'}</button>
                </div>
              </div>
            </div>
          )}
        </div>
      ))}
    </section>
  );
}
