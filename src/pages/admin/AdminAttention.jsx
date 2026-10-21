import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { ClipboardCheck, LifeBuoy, HelpCircle, CreditCard, PackageX } from 'lucide-react';
import api from '../../services/api';

const LEVEL = { bad: 'bg-red-50 text-red-800 border-red-200', warn: 'bg-amber-50 text-amber-900 border-amber-200', info: 'bg-blue-50 text-blue-900 border-blue-200', good: 'bg-green-50 text-green-900 border-green-200' };

const RISK = { Incomplete: 'bg-gray-50 text-gray-700 border-gray-300', Low: 'bg-green-50 text-green-900 border-green-200', Medium: 'bg-amber-50 text-amber-900 border-amber-200', High: 'bg-red-50 text-red-800 border-red-200' };

/** The first thing an admin sees: what needs a decision right now, as big cards and a plain-language briefing. */
export default function AdminAttention() {
  const [d, setD] = useState(null);
  useEffect(() => { api.get('/admin/overview').then((r) => setD(r.data)).catch(() => setD(null)); }, []);
  if (!d) return null;
  const c = d.cards;
  const tiles = [
    { to: '/admin/ai-seller-onboarding', icon: ClipboardCheck, n: c.applications, label: 'Seller applications to review', hot: c.applications > 0 },
    { to: '/admin/support', icon: LifeBuoy, n: c.openTickets, label: c.overdueTickets ? `Support tickets (${c.overdueTickets} overdue)` : 'Open support tickets', hot: c.overdueTickets > 0 },
    { to: '/admin/enquiries', icon: HelpCircle, n: c.openEnquiries, label: 'Customer questions unanswered', hot: c.openEnquiries > 0 },
    { to: '/admin/payments', icon: CreditCard, n: c.awaitingPayment, label: 'Orders waiting for payment', hot: c.awaitingPayment > 0 },
    { to: '/admin/inventory', icon: PackageX, n: c.outOfStock + c.lowStock, label: 'Products low or out of stock', hot: c.outOfStock > 0 },
  ];
  return (
    <section aria-label="Needs your attention" className="space-y-4">
      <h2 className="text-lg font-extrabold text-gray-900">Needs your attention</h2>
      <div className="grid grid-cols-2 lg:grid-cols-5 gap-3">
        {tiles.map((t) => (
          <Link key={t.label} to={t.to} className={`group rounded-2xl border p-5 transition hover:-translate-y-1 hover:shadow-lg ${t.hot ? 'bg-white border-indigo-300 ring-1 ring-indigo-100' : 'bg-white border-gray-200'}`}>
            <t.icon className={`w-6 h-6 ${t.hot ? 'text-indigo-600' : 'text-gray-400'}`} />
            <div className="mt-3 text-4xl font-extrabold text-gray-900 tabular-nums">{t.n}</div>
            <div className="text-sm text-gray-600 mt-1">{t.label}</div>
          </Link>
        ))}
      </div>
      {d.applications?.length > 0 && (
        <div className="rounded-2xl border border-gray-200 bg-white p-5">
          <h3 className="font-bold text-gray-900 mb-1">New sellers waiting for you</h3>
          <p className="text-sm text-gray-600 mb-3">Risk is worked out from how well their documents match what they typed. Lower is safer. You always make the final decision.</p>
          <ul className="divide-y divide-gray-100">
            {d.applications.map((a) => (
              <li key={a.id}>
                <Link to="/admin/ai-seller-onboarding" className="flex flex-wrap items-center gap-3 py-3 hover:bg-gray-50 rounded-xl px-2">
                  <div className="min-w-0 flex-1">
                    <div className="font-bold text-gray-900">{a.company}</div>
                    <div className="text-sm text-gray-600">{a.applicant} · {a.city} · {a.documents} document{a.documents === 1 ? '' : 's'} · sent {a.submitted}</div>
                    {a.reasons.length > 0 && <div className="text-xs text-amber-800 mt-0.5">Check: {a.reasons.join(' · ')}</div>}
                  </div>
                  <span className={`rounded-full px-3 py-1 text-sm font-bold border ${RISK[a.documents < 2 ? 'Incomplete' : a.riskCategory] || RISK.Medium}`} title={`Trust score ${a.trustScore}/100`}>
                    {a.documents < 2 ? 'Incomplete' : `${a.riskCategory} risk`} · {a.riskScore}/100
                  </span>
                </Link>
              </li>
            ))}
          </ul>
        </div>
      )}
      <div className="rounded-2xl border border-gray-200 bg-white p-5">
        <h3 className="font-bold text-gray-900 mb-3">Today's briefing</h3>
        <ul className="space-y-2">
          {d.briefing.map((b) => (
            <li key={b.text} className={`rounded-xl border px-4 py-2.5 text-sm ${LEVEL[b.level]}`}>
              {b.text} {b.link && <Link to={b.link} className="font-bold underline ml-1">Open</Link>}
            </li>
          ))}
        </ul>
      </div>
    </section>
  );
}
