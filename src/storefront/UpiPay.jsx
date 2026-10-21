import React, { useEffect, useState } from 'react';
import { QRCodeSVG } from 'qrcode.react';
import { X, Smartphone, CheckCircle2, Copy } from 'lucide-react';
import api from '../services/api';
import { money } from './parts';
import './storefront.css';

/**
 * Pay the seller directly with UPI. Scan the QR (or open the UPI app on a phone), then enter the 12-digit UPI reference from your app.
 * The seller checks their account and confirms. No payment gateway is involved.
 */
export default function UpiPay({ order, onSubmitted, onClose }) {
  const [info, setInfo] = useState(null);
  const [utr, setUtr] = useState('');
  const [err, setErr] = useState('');
  const [busy, setBusy] = useState(false);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    if (order.upi) { setInfo(order.upi); return; }
    api.get(`/orders/${order.id}/upi`).then((r) => setInfo(r.data)).catch((e) => setErr(e?.response?.data?.detail || 'Could not load the payment details.'));
  }, [order]);

  const submit = async (e) => {
    e.preventDefault(); setBusy(true); setErr('');
    try { await api.post(`/orders/${order.id}/upi-reference`, { utr }); onSubmitted(); }
    catch (x) { setErr(x?.response?.data?.errors?.utr ? x.response.data.detail : x?.response?.data?.detail || 'We could not save that. Please try again.'); }
    setBusy(false);
  };
  const copy = async () => { try { await navigator.clipboard.writeText(info.upiId); setCopied(true); window.setTimeout(() => setCopied(false), 1600); } catch { /* the ID is shown on screen anyway */ } };

  return (
    <div className="ac ac-host" style={{ display: 'contents' }}>
      <div className="ac-sc-back" style={{ zIndex: 95 }} onClick={onClose} aria-hidden="true" />
      <div className="ac-rzp" role="dialog" aria-modal="true" aria-label="Pay with UPI">
        <div className="ac-rzp-head">
          <div><b>Pay with UPI</b><small>Order {order.id}</small></div>
          <button className="ac-sc-x" style={{ background: 'rgba(255,255,255,.18)', color: '#fff' }} onClick={onClose} aria-label="Close payment"><X size={18} /></button>
        </div>
        <div className="ac-rzp-body">
          {!info && !err && <p className="ac-muted">Getting the payment details…</p>}
          {info && (
            <>
              <div className="ac-rzp-amount">{money(info.amount)}</div>
              <p className="ac-muted" style={{ margin: '0 0 12px' }}>Pay <b>{info.payee}</b> directly. The amount is already filled in.</p>
              <div className="ac-upi-qr"><QRCodeSVG value={info.link} size={176} marginSize={2} title={`UPI payment of ${money(info.amount)} to ${info.payee}`} /></div>
              <p className="ac-upi-id">
                <span>{info.upiId}</span>
                <button type="button" onClick={copy} aria-label="Copy UPI ID"><Copy size={15} /> {copied ? 'Copied' : 'Copy'}</button>
              </p>
              <a href={info.link} className="ac-btn ac-btn-outline ac-btn-small ac-upi-open"><Smartphone size={16} /> Open my UPI app (on a phone)</a>
              <form onSubmit={submit} style={{ marginTop: 14 }}>
                <label htmlFor="utr" style={{ fontWeight: 700 }}>After paying, enter the 12-digit UPI reference</label>
                <input id="utr" className="ac-input" inputMode="numeric" maxLength={14} placeholder="e.g. 412345678901" value={utr} onChange={(e) => { const v = e.target.value.replace(/\D/g, ''); setUtr(v); }} aria-invalid={!!err} autoComplete="off" />
                <small className="ac-muted">Find it in your UPI app under the payment details (it may be called UTR or transaction ID).</small>
                {err && <div className="ac-warn" role="alert" style={{ marginTop: 8 }}>{err}</div>}
                <button className="ac-btn ac-btn-blue" style={{ width: '100%', marginTop: 12 }} disabled={busy || utr.length !== 12}><CheckCircle2 size={17} /> {busy ? 'Saving…' : 'I have paid'}</button>
              </form>
              <p className="ac-muted" style={{ fontSize: 14, marginTop: 10 }}>The seller checks their account and confirms. Your order is packed once they do.</p>
            </>
          )}
          {!info && err && <div className="ac-warn" role="alert">{err}</div>}
        </div>
      </div>
    </div>
  );
}
