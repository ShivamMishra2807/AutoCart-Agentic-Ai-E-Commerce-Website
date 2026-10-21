import React, { useCallback, useEffect, useState } from 'react';
import { RefreshCw } from 'lucide-react';
import api from '../../services/api';

const FILTERS = [['', 'All'], ['OPEN', 'Open'], ['IN_PROGRESS', 'In progress'], ['WAITING_CUSTOMER', 'Waiting for customer'], ['RESOLVED', 'Resolved']];
const STATUSES = ['OPEN', 'IN_PROGRESS', 'WAITING_CUSTOMER', 'RESOLVED', 'CLOSED'];
const PRIORITIES = ['LOW', 'NORMAL', 'HIGH', 'URGENT'];
const TONE = { OPEN: 'bg-blue-100 text-blue-800', IN_PROGRESS: 'bg-indigo-100 text-indigo-800', WAITING_CUSTOMER: 'bg-amber-100 text-amber-800', RESOLVED: 'bg-green-100 text-green-800', CLOSED: 'bg-gray-100 text-gray-700' };
const PRIO = { URGENT: 'text-red-700', HIGH: 'text-orange-600', NORMAL: 'text-gray-500', LOW: 'text-gray-400' };
const nice = (s) => String(s || '').replace(/_/g, ' ').toLowerCase().replace(/^\w/, (c) => c.toUpperCase());
const when = (d) => new Date(d).toLocaleString([], { dateStyle: 'medium', timeStyle: 'short' });

export default function SupportInbox() {
  const [filter, setFilter] = useState('OPEN');
  const [tickets, setTickets] = useState([]);
  const [summary, setSummary] = useState(null);
  const [open, setOpen] = useState(null);
  const [reply, setReply] = useState('');
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);

  const load = useCallback(async () => {
    try {
      const [t, s] = await Promise.all([api.get('/support/tickets', { params: filter ? { status: filter } : {} }), api.get('/support/summary')]);
      setTickets(t.data); setSummary(s.data); setError('');
    } catch (e) { setError(e?.response?.status === 403 ? 'Only the support team can see this.' : 'Could not load tickets.'); }
  }, [filter]);
  useEffect(() => { load(); }, [load]);

  const show = async (id) => { try { setOpen((await api.get(`/support/tickets/${id}`)).data); } catch { setError('Could not open that ticket.'); } };
  const patch = async (body) => { try { setOpen((await api.patch(`/support/tickets/${open.id}`, body)).data); load(); } catch { setError('That change did not save.'); } };
  const send = async (e) => {
    e.preventDefault(); if (!reply.trim()) return; setBusy(true);
    try { setOpen((await api.post(`/support/tickets/${open.id}/messages`, { body: reply })).data); setReply(''); load(); } catch { setError('Reply did not send.'); }
    setBusy(false);
  };

  return (
    <div className="space-y-5">
      <div className="flex items-start justify-between gap-3 flex-wrap">
        <div><h1 className="text-2xl font-extrabold text-gray-900">Support inbox</h1><p className="text-gray-600 text-sm mt-1">Every ticket includes the chat that came before it, so customers never repeat themselves.</p></div>
        <button onClick={load} className="inline-flex items-center gap-2 px-3 py-2 rounded-xl border border-gray-200 text-sm font-semibold hover:bg-gray-50"><RefreshCw className="w-4 h-4" /> Refresh</button>
      </div>
      {error && <div role="alert" className="px-4 py-3 rounded-xl bg-red-50 text-red-800 text-sm">{error}</div>}

      {summary && (
        <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
          {[['Open', summary.open], ['In progress', summary.inProgress], ['Waiting for customer', summary.waitingCustomer], ['Overdue', summary.overdue], ['Chat rating', summary.averageRating ? `${summary.averageRating} / 5` : 'No ratings yet']].map(([k, v]) => (
            <div key={k} className={`bg-white rounded-2xl border p-4 ${k === 'Overdue' && v > 0 ? 'border-red-300' : 'border-gray-200'}`}><div className="text-2xl font-extrabold text-gray-900">{v}</div><div className="text-sm text-gray-500">{k}</div></div>))}
        </div>
      )}

      <div className="flex gap-2 flex-wrap">{FILTERS.map(([k, n]) => (
        <button key={k || 'all'} aria-pressed={filter === k} onClick={() => { setFilter(k); setOpen(null); }}
          className={`px-4 py-2 rounded-full text-sm font-semibold border ${filter === k ? 'bg-indigo-600 text-white border-indigo-600' : 'bg-white border-gray-200 text-gray-700 hover:border-indigo-600'}`}>{n}</button>))}</div>

      <div className="grid lg:grid-cols-[340px_1fr] gap-5 items-start">
        <div className="bg-white rounded-2xl border border-gray-200 divide-y divide-gray-100 overflow-hidden">
          {tickets.length === 0 && <p className="p-5 text-sm text-gray-500">No tickets here.</p>}
          {tickets.map((t) => (
            <button key={t.id} onClick={() => show(t.id)} className={`w-full text-left p-4 hover:bg-gray-50 ${open?.id === t.id ? 'bg-indigo-50' : ''}`}>
              <div className="flex justify-between gap-2"><b className="truncate text-gray-900">{t.subject}</b><span className={`text-xs font-bold ${PRIO[t.priority]}`}>{nice(t.priority)}</span></div>
              <div className="text-sm text-gray-500 truncate">{t.customerName || t.customerEmail}{t.orderId ? ` · ${t.orderId}` : ''}</div>
              <div className="flex items-center gap-2 mt-1"><span className={`px-2 py-0.5 rounded-full text-xs font-bold ${TONE[t.status]}`}>{nice(t.status)}</span>{t.overdue && <span className="text-xs font-bold text-red-700">Overdue</span>}</div>
            </button>))}
        </div>

        <div className="min-w-0">
          {!open && <div className="bg-white rounded-2xl border border-dashed border-gray-300 p-10 text-center text-gray-500">Choose a ticket to read it and reply.</div>}
          {open && (
            <div className="bg-white rounded-2xl border border-gray-200 p-5 space-y-4">
              <div><h2 className="text-lg font-bold text-gray-900">{open.subject}</h2>
                <p className="text-sm text-gray-500">{open.id} · {open.customerName} ({open.customerEmail}){open.orderId ? ` · order ${open.orderId}` : ''} · due {open.dueAt ? when(open.dueAt) : '-'}</p></div>
              <div className="flex gap-3 flex-wrap">
                <label className="text-sm font-semibold text-gray-700">Status <select value={open.status} onChange={(e) => patch({ status: e.target.value })} className="ml-1 rounded-lg border border-gray-300 p-1.5 text-sm">{STATUSES.map((s) => <option key={s} value={s}>{nice(s)}</option>)}</select></label>
                <label className="text-sm font-semibold text-gray-700">Priority <select value={open.priority} onChange={(e) => patch({ priority: e.target.value })} className="ml-1 rounded-lg border border-gray-300 p-1.5 text-sm">{PRIORITIES.map((s) => <option key={s} value={s}>{nice(s)}</option>)}</select></label>
              </div>
              {open.collectedDetails && Object.values(open.collectedDetails).some(Boolean) && (
                <p className="text-sm text-gray-600 bg-gray-50 rounded-xl p-3">Details the customer agreed to share: {Object.entries(open.collectedDetails).filter(([, v]) => v).map(([k, v]) => `${k}: ${v}`).join(' · ')}</p>)}
              <div className="space-y-3">{open.messages.map((m) => (
                <div key={m.id} className={`rounded-2xl p-3.5 text-sm ${m.author === 'support' ? 'bg-indigo-50' : 'bg-gray-50'}`}>
                  <div className="flex justify-between text-xs text-gray-500 mb-1"><b>{m.author === 'assistant' ? 'AutoCart assistant (chat before the ticket)' : m.authorName || m.author}</b><span>{when(m.createdAt)}</span></div>
                  <p className="whitespace-pre-wrap break-words m-0">{m.body}</p></div>))}</div>
              <form onSubmit={send} className="space-y-2">
                <label htmlFor="reply" className="sr-only">Reply to the customer</label>
                <textarea id="reply" value={reply} onChange={(e) => setReply(e.target.value)} rows={3} placeholder="Write a reply. The customer sees it in their tickets." className="w-full rounded-xl border border-gray-300 p-3 text-sm" />
                <button disabled={busy || !reply.trim()} className="px-4 py-2 rounded-xl bg-indigo-600 text-white font-semibold text-sm disabled:opacity-50">Send reply</button>
              </form>
            </div>)}
        </div>
      </div>
    </div>
  );
}
