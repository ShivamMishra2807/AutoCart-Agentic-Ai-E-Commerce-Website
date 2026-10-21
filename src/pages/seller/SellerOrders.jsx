import React, { useState } from 'react';
import { PackageCheck, Route } from 'lucide-react';
import api from '../../services/api';
import OrderRouteMap from '../../storefront/OrderRouteMap';
import { money } from '../../storefront/parts';

/** Orders that contain this seller's products. One click confirms packing; then the route to the customer opens on a map. */
export default function SellerOrders({ orders, onChange }) {
  const [busy, setBusy] = useState('');
  const [open, setOpen] = useState('');
  const [route, setRoute] = useState(null);
  const [err, setErr] = useState('');

  const pack = async (id) => {
    setBusy(id); setErr('');
    try { await api.post(`/seller/orders/${id}/pack`); await onChange(); await show(id); }
    catch (e) { setErr(e?.response?.data?.detail || 'Could not update that order.'); }
    setBusy('');
  };
  const payment = async (id, action) => {
    setBusy(id); setErr('');
    try { await api.post(`/orders/${id}/payment`, { action }); await onChange(); }
    catch (e) { setErr(e?.response?.data?.detail || 'Could not update that payment.'); }
    setBusy('');
  };
  const show = async (id) => {
    if (open === id) { setOpen(''); return; }
    setOpen(id); setRoute(null);
    try { setRoute((await api.get(`/seller/orders/${id}/route`)).data); }
    catch (e) { setRoute({ note: e?.response?.data?.detail || 'Could not load the route.' }); }
  };

  const todo = orders.filter((o) => o.canPack).length;
  return (
    <section id="orders" className="ac-box" aria-labelledby="ord-h" style={{ marginTop: 24 }}>
      <h2 id="ord-h">Orders to pack {todo > 0 && <span className="ac-chip-status" data-tone="warn">{todo} waiting</span>}</h2>
      {err && <p role="alert" style={{ color: 'var(--coral)' }}>{err}</p>}
      {orders.length === 0 ? <p className="ac-muted">No orders yet. When someone buys from you, it shows up here.</p> : (
        <div style={{ display: 'grid', gap: 12, marginTop: 12 }}>
          {orders.map((o) => (
            <article key={o.id} className="ac-ordercard" data-open={open === o.id}>
              <div className="ac-ordercard-top">
                <div>
                  <b>{o.id}</b> <span className="ac-chip-status" data-tone={o.status === 'Delivered' ? 'ok' : o.canPack ? 'warn' : 'info'}>{o.status}</span>
                  <p style={{ margin: '4px 0 0' }}>{o.items.map((i) => `${i.name} × ${i.quantity}`).join(', ')}</p>
                  <small className="ac-muted">{o.customerFirstName} · {o.date} · your share {money(o.yourShare)}{o.pickup ? ' · customer pickup' : ''} · {o.paymentMethod}</small>
                  {o.paymentMethod === 'UPI (Scan & Pay)' && (
                    <p style={{ margin: '6px 0 0' }}>
                      {o.paymentStatus === 'Awaiting Payment' && <span className="ac-chip-status" data-tone="warn">Waiting for the customer to pay</span>}
                      {o.paymentStatus === 'Verifying' && <span className="ac-chip-status" data-tone="warn">Check your UPI account: reference <b>{o.utr}</b></span>}
                      {o.paymentStatus === 'Paid' && <span className="ac-chip-status" data-tone="ok">Payment received</span>}
                      {o.paymentStatus === 'Failed' && <span className="ac-chip-status" data-tone="bad">Marked not received</span>}
                    </p>
                  )}
                </div>
                <div className="ac-row" style={{ gap: 8 }}>
                  {o.paymentStatus === 'Verifying' && o.paymentMethod === 'UPI (Scan & Pay)' && (
                    <>
                      <button className="ac-btn ac-btn-blue" disabled={busy === o.id} onClick={() => payment(o.id, 'received')}>Payment received</button>
                      <button className="ac-btn ac-btn-outline" disabled={busy === o.id} onClick={() => payment(o.id, 'not_received')}>Not received</button>
                    </>
                  )}
                  {o.canPack && <button className="ac-btn ac-btn-blue" disabled={busy === o.id} onClick={() => pack(o.id)}><PackageCheck size={17} /> {busy === o.id ? 'Saving…' : 'Confirm & pack'}</button>}
                  <button className="ac-btn ac-btn-outline" onClick={() => show(o.id)} aria-expanded={open === o.id}><Route size={17} /> {open === o.id ? 'Hide route' : 'View route'}</button>
                </div>
              </div>
              {open === o.id && (
                <div style={{ marginTop: 14 }}>
                  {!route && <div className="ac-skel" style={{ height: 200 }} />}
                  {route?.pickup && route?.drop && <OrderRouteMap pickup={route.pickup} drop={route.drop} />}
                  {route && !(route.pickup && route.drop) && <p className="ac-muted" role="status">{route.note || 'No map location is available for this order.'}</p>}
                </div>
              )}
            </article>
          ))}
        </div>
      )}
    </section>
  );
}
