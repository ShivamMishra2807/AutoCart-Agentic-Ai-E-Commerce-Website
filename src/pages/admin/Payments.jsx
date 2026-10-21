import React, { useCallback, useEffect, useState } from 'react';
import { RefreshCw, Wallet } from 'lucide-react';
import api from '../../services/api';

const rupee = new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 0 });
const HOW = {
  'Cash on Delivery': 'Customer pays cash when it arrives.',
  'UPI or Card on Delivery': 'Customer pays by UPI or card when it arrives.',
  'Pay at Store': 'Customer pays at the store when collecting.',
  'UPI (Scan & Pay)': 'Customer pays the seller directly by UPI. The seller confirms the money arrived.',
};

/** How customers pay, and UPI payments waiting for a seller to confirm. There is no payment gateway to set up. */
export default function Payments() {
  const [data, setData] = useState(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const [note, setNote] = useState('');

  const load = useCallback(async () => {
    setBusy(true); setError('');
    try { setData((await api.get('/payments/status')).data); }
    catch (e) { setError(e?.response?.status === 403 ? 'Only administrators can see this.' : 'Could not load payments.'); }
    setBusy(false);
  }, []);
  useEffect(() => { load(); }, [load]);

  const decide = async (orderId, action) => {
    setNote('');
    try { await api.post(`/orders/${orderId}/payment`, { action }); setNote(action === 'received' ? `Order ${orderId} marked as paid.` : `Order ${orderId} marked as not received.`); load(); }
    catch (e) { setNote(e?.response?.data?.detail || 'That did not work.'); }
  };

  return (
    <div className="space-y-5">
      <div className="flex items-start justify-between gap-3 flex-wrap">
        <div>
          <h1 className="text-2xl font-extrabold text-gray-900">Payments</h1>
          <p className="text-gray-600 text-sm mt-1">No payment gateway is used. Customers pay on delivery, at the store, or by UPI straight to the seller.</p>
        </div>
        <button onClick={load} disabled={busy} className="inline-flex items-center gap-2 px-3 py-2 rounded-xl border border-gray-200 text-sm font-semibold hover:bg-gray-50"><RefreshCw className={`w-4 h-4 ${busy ? 'animate-spin' : ''}`} /> Refresh</button>
      </div>
      {error && <div role="alert" className="px-4 py-3 rounded-xl bg-red-50 text-red-800 text-sm">{error}</div>}
      {note && <div role="status" className="px-4 py-3 rounded-xl bg-green-50 text-green-800 text-sm font-semibold">{note}</div>}

      {data && (
        <>
          <section className="bg-white rounded-2xl border border-gray-200 p-5">
            <h2 className="font-bold text-gray-900 mb-3">How customers are paying</h2>
            {data.methods.length === 0 ? <p className="text-sm text-gray-500">No orders yet.</p> : (
              <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-3">
                {data.methods.map((m) => (
                  <div key={m.method} className="rounded-xl border border-gray-200 p-4">
                    <div className="font-bold text-gray-900">{m.method}</div>
                    <div className="text-3xl font-extrabold tabular-nums mt-1">{m.orders}<span className="text-base font-semibold text-gray-500"> orders</span></div>
                    <div className="text-sm text-gray-600">{rupee.format(m.amount)} · {m.paid} marked paid</div>
                    <div className="text-xs text-gray-500 mt-2">{HOW[m.method] || ''}</div>
                  </div>
                ))}
              </div>
            )}
          </section>

          <section className="bg-white rounded-2xl border border-gray-200 p-5">
            <h2 className="font-bold text-gray-900 flex items-center gap-2"><Wallet className="w-5 h-5" /> UPI payments waiting for confirmation ({data.waiting.length})</h2>
            <p className="text-sm text-gray-600 mt-1 mb-3">The seller normally confirms these. You can confirm too if the seller is away, after checking the reference in the seller&apos;s account.</p>
            {data.waiting.length === 0 ? <p className="text-sm text-gray-500">Nothing is waiting.</p> : (
              <div className="overflow-x-auto"><table className="w-full text-sm">
                <thead><tr className="text-left text-gray-500"><th className="py-2 pr-4">Order</th><th className="pr-4">Customer</th><th className="pr-4">Seller</th><th className="pr-4">Amount</th><th className="pr-4">UPI reference</th><th /></tr></thead>
                <tbody>{data.waiting.map((w) => (
                  <tr key={w.orderId} className="border-t border-gray-100">
                    <td className="py-2 pr-4 font-semibold">{w.orderId}</td><td className="pr-4">{w.customer}</td><td className="pr-4">{w.seller}</td>
                    <td className="pr-4">{rupee.format(w.amount)}</td><td className="pr-4 font-mono">{w.utr}</td>
                    <td className="whitespace-nowrap">
                      <button onClick={() => decide(w.orderId, 'received')} className="px-3 py-1.5 rounded-lg bg-green-600 text-white font-semibold mr-2">Received</button>
                      <button onClick={() => decide(w.orderId, 'not_received')} className="px-3 py-1.5 rounded-lg border border-gray-300 font-semibold">Not received</button>
                    </td>
                  </tr>))}</tbody>
              </table></div>
            )}
          </section>
        </>
      )}
    </div>
  );
}
