import React, { useCallback, useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Boxes, AlertTriangle, MessageCircleQuestion, ClipboardList, IndianRupee, LogOut, ExternalLink, Check } from 'lucide-react';
import api from '../../services/api';
import { useAuth } from '../../hooks/useAuth';
import { BrandLink } from '../../storefront/Brand';
import SalesCharts from './SalesCharts';
import HowItWorks from './HowItWorks';
import SellerOrders from './SellerOrders';
import PayoutSettings from './PayoutSettings';
import SellerProducts from './SellerProducts';
import AddProduct from './AddProduct';
import SellerAssistant from './SellerAssistant';
import EnquiryInbox from '../../storefront/EnquiryInbox';
import { money, count, sized } from '../../storefront/parts';
import '../../storefront/storefront.css';
import '../../storefront/forms.css';
import '../../storefront/pages.css';

const TONE = { warn: 'warn', info: 'info', good: 'ok', bad: 'bad' };

/** The seller's own workspace. It shows only this seller's products, orders and questions. */
export default function SellerCenter() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [data, setData] = useState(null);
  const [error, setError] = useState('');
  const [edits, setEdits] = useState({});
  const [saved, setSaved] = useState('');

  const load = useCallback(() => api.get('/seller/overview').then((r) => { setData(r.data); setError(''); })
    .catch((e) => setError(e?.response?.status === 403 ? (e.response.data.detail || 'This area is for approved sellers.') : 'We could not load your seller centre.')), []);
  useEffect(() => { document.title = 'Seller centre | AutoCart'; load(); }, [load]);

  const edit = (id, k, v) => setEdits((e) => ({ ...e, [id]: { ...e[id], [k]: v } }));
  const save = async (p) => {
    const e = edits[p.id] || {};
    try {
      await api.patch(`/seller/products/${p.id}`, { ...(e.price !== undefined ? { price: e.price } : {}), ...(e.stock !== undefined ? { stock: e.stock } : {}) });
      setEdits((x) => { const n = { ...x }; delete n[p.id]; return n; });
      setSaved(`${p.name} updated.`); window.setTimeout(() => setSaved(''), 2500);
      load();
    } catch (err) { setSaved(err?.response?.data?.detail || 'That did not save.'); }
  };

  const cards = data && [
    { href: '#products', icon: Boxes, big: data.productsCount, label: 'Products live', hint: `${data.outOfStock} out of stock`, tone: data.outOfStock ? 'warn' : '' },
    { href: '#products', icon: AlertTriangle, big: data.lowStock, label: 'Almost gone', hint: 'Ten or fewer left', tone: data.lowStock ? 'warn' : '' },
    { href: '#questions', icon: MessageCircleQuestion, big: data.openQuestions, label: 'Questions waiting', hint: 'Customers want an answer', tone: data.openQuestions ? 'warn' : '' },
    { href: '#orders', icon: ClipboardList, big: data.ordersCount, label: 'Orders with your items', hint: `${count.format(data.unitsSold)} units sold`, tone: '' },
    { href: '#orders', icon: IndianRupee, big: money(data.revenue), label: 'Your sales', hint: 'From orders not cancelled', tone: '' },
  ];

  return (
    <div className="ac ac-seller">
      <header className="ac-sc-top">
        <div className="ac-wrap ac-row-between" style={{ paddingBlock: 14 }}>
          <div className="ac-row" style={{ gap: 18 }}><BrandLink size={30} /><span className="ac-chip-status" data-tone="info">Seller centre</span></div>
          <div className="ac-row">
            <span className="ac-muted" style={{ fontSize: 14 }}>{data?.company || user?.name}</span>
            <Link to="/" className="ac-btn ac-btn-outline ac-btn-small"><ExternalLink size={15} /> View the store</Link>
            <button className="ac-btn ac-btn-outline ac-btn-small" onClick={() => { logout(); navigate('/seller/login'); }}><LogOut size={15} /> Sign out</button>
          </div>
        </div>
      </header>

      <main className="ac-wrap" style={{ paddingBlock: 36 }}>
        <h1 className="ac-display" style={{ fontSize: 'clamp(32px, 4vw, 48px)' }}>{data ? `Hello, ${user?.name?.split(' ')[0]}` : 'Your seller centre'}</h1>
        {error && <div className="ac-box" role="alert" style={{ marginTop: 20, borderColor: 'var(--coral)' }}>{error}</div>}
        {!data && !error && <div className="ac-skel" style={{ height: 180, marginTop: 24 }} />}

        {data && (
          <>
            <div className="ac-bigcards">
              {cards.map((c) => (
                <a key={c.label} href={c.href} className="ac-bigcard" data-tone={c.tone}>
                  <c.icon size={26} /><b>{c.big}</b><span>{c.label}</span><small>{c.hint}</small>
                </a>
              ))}
            </div>

            <section className="ac-box" aria-labelledby="tips-h" style={{ marginTop: 24 }}>
              <h2 id="tips-h">What to do next</h2>
              <ul className="ac-tips">{data.tips.map((t) => <li key={t.text}><span className="ac-chip-status" data-tone={TONE[t.level]}>{t.level === 'good' ? 'All good' : t.level === 'warn' ? 'Needs you' : 'Heads up'}</span> {t.text}</li>)}</ul>
            </section>

            <SalesCharts data={data} />
            <SellerAssistant />
            <AddProduct onAdded={load} />

            <SellerProducts products={data.products} onChanged={load} />

            <SellerOrders orders={data.orders} onChange={load} />
            <PayoutSettings />
          </>
        )}

        <div id="questions"><EnquiryInbox title="Questions about your products" allowDraft /></div>
      <HowItWorks />
      </main>
      <a href="#assistant" className="ac-munim-fab" aria-label="Ask Munim about your sales and profit" onClick={(e) => { e.preventDefault(); document.getElementById('assistant')?.scrollIntoView({ behavior: 'smooth', block: 'start' }); document.getElementById('sa-in')?.focus({ preventScroll: true }); }}>Ask Munim</a>
    </div>
  );
}
