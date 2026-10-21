import React, { useEffect, useState } from 'react';
import { QrCode } from 'lucide-react';
import api from '../../services/api';

/** The seller's own UPI ID. Customers who choose "Pay now with UPI" pay straight into this account. */
export default function PayoutSettings() {
  const [upi, setUpi] = useState('');
  const [saved, setSaved] = useState('');
  const [msg, setMsg] = useState('');
  const [err, setErr] = useState('');

  useEffect(() => { api.get('/seller/payout-settings').then((r) => { setUpi(r.data.upiId || ''); setSaved(r.data.upiId || ''); }).catch(() => {}); }, []);
  const save = async (e) => {
    e.preventDefault(); setErr(''); setMsg('');
    try { const { data } = await api.put('/seller/payout-settings', { upiId: upi }); setSaved(data.upiId); setMsg(data.upiId ? 'Saved. Customers can now pay you by UPI.' : 'UPI payments are switched off.'); }
    catch (x) { setErr(x?.response?.data?.detail || 'That did not save.'); }
  };

  return (
    <section id="payments" className="ac-box" aria-labelledby="pay-h" style={{ marginTop: 24 }}>
      <h2 id="pay-h" className="ac-row" style={{ gap: 8 }}><QrCode size={20} /> Get paid by UPI</h2>
      <p className="ac-muted" style={{ marginTop: 4 }}>Add your own UPI ID so customers can scan a QR and pay you directly. You confirm each payment after you see it in your account. AutoCart never touches the money.</p>
      <form onSubmit={save} className="ac-row" style={{ marginTop: 12, flexWrap: 'wrap' }}>
        <label className="ac-sr" htmlFor="upi-id">Your UPI ID</label>
        <input id="upi-id" className="ac-input" style={{ flex: 1, minWidth: 220 }} placeholder="yourshop@okaxis" value={upi} onChange={(e) => setUpi(e.target.value)} aria-invalid={!!err} autoComplete="off" />
        <button className="ac-btn ac-btn-blue" disabled={upi.trim() === saved}>Save</button>
      </form>
      {err && <p role="alert" style={{ color: 'var(--coral)', marginTop: 8 }}>{err}</p>}
      {msg && <p role="status" style={{ marginTop: 8 }}>{msg}</p>}
      {!saved && !msg && <p className="ac-muted" style={{ marginTop: 8, fontSize: 14 }}>Until you add one, customers can still pay you by cash or card on delivery, or at your store.</p>}
    </section>
  );
}
