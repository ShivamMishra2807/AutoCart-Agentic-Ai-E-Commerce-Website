import React, { useEffect, useState } from 'react';
import { UserPlus, PackagePlus, ShoppingBag, Wallet } from 'lucide-react';
import api from '../../services/api';

const STEPS = [
  { icon: UserPlus, t: 'Join free', d: 'Upload your PAN and masked Aadhaar. We read them for you and an admin approves you.' },
  { icon: PackagePlus, t: 'List your products', d: 'Add items and stock. Nearby shoppers see your store and what is in stock.' },
  { icon: ShoppingBag, t: 'Get orders', d: 'Customers buy for delivery or pick up in your store. You pack and hand over.' },
  { icon: Wallet, t: 'Keep your earnings', d: 'You pay a small commission only when something sells. No joining, listing or monthly fee.' },
];

/** Explains how selling on AutoCart works and exactly what it costs. The rates come from the server, so they never drift from what is charged. */
export default function HowItWorks({ compact = false }) {
  const [terms, setTerms] = useState(null);
  useEffect(() => { api.get('/commission').then((r) => setTerms(r.data)).catch(() => {}); }, []);
  return (
    <section id="how" className="ac-box" aria-labelledby="how-h" style={{ marginTop: compact ? 0 : 24 }}>
      <h2 id="how-h">How selling on AutoCart works</h2>
      <ol className="ac-steps4">
        {STEPS.map((s, i) => <li key={s.t}><span><s.icon size={20} /></span><b>{i + 1}. {s.t}</b><p>{s.d}</p></li>)}
      </ol>
      {terms && (
        <>
          <h3 style={{ marginTop: 18 }}>What it costs</h3>
          <p className="ac-muted">Joining ₹{terms.joiningFee} · Listing ₹{terms.listingFee} · Monthly ₹{terms.monthlyFee}. Commission is charged only on a sale, as a share of the item price:</p>
          <div className="ac-ratechips">{terms.rates.map((r) => <span key={r.category}>{r.category} <b>{r.percent}%</b></span>)}</div>
          <p className="ac-muted" style={{ fontSize: 14, marginTop: 8 }}>Online payments also carry the payment provider charge (about {terms.paymentFeePercent}%), passed on at cost. {terms.note}</p>
        </>
      )}
    </section>
  );
}
