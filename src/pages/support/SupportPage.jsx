import React, { useCallback, useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import api from '../../services/api';
import { useAuth } from '../../hooks/useAuth';
import { openAssistant } from '../../storefront/parts';
import '../../storefront/storefront.css';
import '../../storefront/forms.css';

const TONE = { OPEN: 'info', IN_PROGRESS: 'info', WAITING_CUSTOMER: 'warn', RESOLVED: 'ok', CLOSED: 'ok' };
const nice = (s) => String(s || '').replace(/_/g, ' ').toLowerCase().replace(/^\w/, (c) => c.toUpperCase());
const when = (d) => new Date(d).toLocaleString([], { dateStyle: 'medium', timeStyle: 'short' });

export default function SupportPage() {
  const { user } = useAuth();
  const [tickets, setTickets] = useState([]);
  const [open, setOpen] = useState(null);
  const [reply, setReply] = useState('');
  const [creating, setCreating] = useState(false);
  const [form, setForm] = useState({ subject: '', orderId: '', message: '', consent: false });
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);

  const load = useCallback(() => api.get('/support/tickets').then((r) => setTickets(r.data)).catch(() => setError('We could not load your tickets.')), []);
  useEffect(() => { document.title = 'Help and tickets | AutoCart'; if (user) load(); }, [user, load]);

  const show = async (id) => { setError(''); try { setOpen((await api.get(`/support/tickets/${id}`)).data); } catch { setError('Could not open that ticket.'); } };
  const send = async (e) => {
    e.preventDefault(); if (!reply.trim()) return;
    setBusy(true);
    try { setOpen((await api.post(`/support/tickets/${open.id}/messages`, { body: reply })).data); setReply(''); load(); } catch { setError('Your message did not send. Try again.'); }
    setBusy(false);
  };
  const create = async (e) => {
    e.preventDefault(); setBusy(true); setError('');
    try { const { data } = await api.post('/support/tickets', { ...form, consent: form.consent === true }); setCreating(false); setForm({ subject: '', orderId: '', message: '', consent: false }); await load(); setOpen(data); }
    catch (err) { setError(err?.response?.data?.detail || 'We could not create the ticket.'); }
    setBusy(false);
  };

  if (!user) {
    return <div className="ac ac-page"><div className="ac-wrap" style={{ maxWidth: 720 }}>
      <h1 className="ac-display">Help and tickets</h1>
      <p className="ac-sub">Sign in to see your support tickets, or ask the assistant a quick question.</p>
      <div className="ac-row" style={{ marginTop: 24 }}><Link to="/login" state={{ from: '/support' }} className="ac-btn ac-btn-blue">Sign in</Link><button className="ac-btn ac-btn-outline" onClick={openAssistant}>Ask the assistant</button></div>
    </div></div>;
  }

  return (
    <div className="ac ac-page"><div className="ac-wrap" style={{ maxWidth: 1000 }}>
      <div className="ac-row-between"><div><h1 className="ac-display">Help and tickets</h1><p className="ac-sub">A real person reads every ticket. You can also ask the assistant first.</p></div>
        <div className="ac-row"><button className="ac-btn ac-btn-outline ac-btn-small" onClick={openAssistant}>Ask the assistant</button><button className="ac-btn ac-btn-blue ac-btn-small" onClick={() => { setCreating(true); setOpen(null); }}>New ticket</button></div></div>
      {error && <div className="ac-box" role="alert" style={{ marginTop: 16, borderColor: 'var(--coral)' }}>{error}</div>}

      <div style={{ display: 'grid', gridTemplateColumns: 'minmax(0, 340px) minmax(0, 1fr)', gap: 20, marginTop: 28 }} className="ac-split">
        <div className="ac-box" style={{ padding: 8 }}>
          {tickets.length === 0 && <p className="ac-muted" style={{ padding: 16 }}>No tickets yet. If something goes wrong with an order, open one and we will help.</p>}
          {tickets.map((t) => (
            <button key={t.id} onClick={() => { setCreating(false); show(t.id); }} className="ac-act" style={{ width: '100%', textAlign: 'left', borderRadius: 16, margin: '4px 0', display: 'block', color: 'var(--ink)', background: open?.id === t.id ? 'var(--brand-soft)' : '#fff' }}>
              <b style={{ display: 'block' }}>{t.subject}</b>
              <span className="ac-chip-status" data-tone={TONE[t.status]}>{nice(t.status)}</span> <span className="ac-muted" style={{ fontSize: 14 }}>{t.id}</span>
            </button>
          ))}
        </div>

        <div>
          {creating && (
            <form className="ac-box" onSubmit={create}>
              <h2>Open a ticket</h2>
              <div className="ac-field" style={{ marginTop: 14 }}><label htmlFor="t-s">What is this about?</label><input id="t-s" className="ac-input" value={form.subject} onChange={(e) => setForm({ ...form, subject: e.target.value })} required /></div>
              <div className="ac-field" style={{ marginTop: 14 }}><label htmlFor="t-o">Order number (if any)</label><input id="t-o" className="ac-input" placeholder="ORD-2026-1234" value={form.orderId} onChange={(e) => setForm({ ...form, orderId: e.target.value })} /></div>
              <div className="ac-field" style={{ marginTop: 14 }}><label htmlFor="t-m">Tell us what happened</label><textarea id="t-m" className="ac-textarea" value={form.message} onChange={(e) => setForm({ ...form, message: e.target.value })} required /></div>
              <p className="ac-muted" style={{ fontSize: 14 }}>We will save your name and email ({user.email}), the subject, order number and message.</p>
              <label className="ac-check"><input type="checkbox" checked={form.consent} onChange={(e) => setForm({ ...form, consent: e.target.checked })} /><span>I agree that AutoCart saves these details to help with my request.</span></label>
              <div className="ac-row" style={{ marginTop: 16 }}><button className="ac-btn ac-btn-blue ac-btn-small" disabled={!form.consent || busy}>{busy ? 'Sending…' : 'Send to support'}</button><button type="button" className="ac-btn ac-btn-outline ac-btn-small" onClick={() => setCreating(false)}>Cancel</button></div>
            </form>
          )}
          {!creating && !open && <div className="ac-box ac-muted">Choose a ticket to read the conversation.</div>}
          {!creating && open && (
            <div className="ac-box">
              <div className="ac-row-between"><h2>{open.subject}</h2><span className="ac-chip-status" data-tone={TONE[open.status]}>{nice(open.status)}</span></div>
              <p className="ac-muted" style={{ margin: '4px 0 18px', fontSize: 14 }}>{open.id}{open.orderId ? ` · order ${open.orderId}` : ''} · opened {when(open.createdAt)}{open.assignedTo ? ` · handled by ${open.assignedTo}` : ''}</p>
              <div className="ac-thread">{open.messages.map((m) => (
                <div className="ac-bubble" data-from={m.author} key={m.id}><header><b>{m.author === 'support' ? `${m.authorName || 'AutoCart support'} (support)` : m.author === 'assistant' ? 'AutoCart assistant' : 'You'}</b><span>{when(m.createdAt)}</span></header><p>{m.body}</p></div>))}</div>
              {!['CLOSED'].includes(open.status) && (
                <form onSubmit={send} style={{ marginTop: 18 }}>
                  <label className="ac-sr" htmlFor="t-r">Your reply</label>
                  <textarea id="t-r" className="ac-textarea" placeholder="Write a reply" value={reply} onChange={(e) => setReply(e.target.value)} />
                  <button className="ac-btn ac-btn-blue ac-btn-small" style={{ marginTop: 10 }} disabled={!reply.trim() || busy}>Send reply</button>
                </form>
              )}
            </div>
          )}
        </div>
      </div>
      <style>{'@media (max-width: 800px) { .ac-split { grid-template-columns: minmax(0, 1fr) !important; } }'}</style>
    </div></div>
  );
}
