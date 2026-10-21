import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import api from '../services/api';
import { count, money, sized, firstImage, asList, byRating, CountUp } from './parts';
import './storefront.css';

/** Live numbers and a few real products, shown beside the sign-in and register forms. */
export default function CatalogPulse() {
  const [summary, setSummary] = useState(null);
  const [picks, setPicks] = useState([]);

  useEffect(() => {
    api.get('/catalog/summary').then((r) => setSummary(r.data)).catch(() => {});
    api.get('/products').then((r) => setPicks(asList(r.data).filter((p) => firstImage(p)).sort(byRating).slice(0, 4))).catch(() => {});
  }, []);

  if (!summary) return null;
  return (
    <aside className="ac ac-box ac-pulse" aria-label="What is in the store">
      <div>
        <h2 className="ac-display" style={{ fontSize: 28 }}>What’s waiting inside</h2>
        <p className="ac-muted" style={{ margin: '8px 0 0' }}>Real stock from real stores. Sign in to see prices near you.</p>
      </div>
      <div className="ac-pulse-nums">
        <div><b><CountUp to={summary.totalProducts} /></b><span>products</span></div>
        <div><b><CountUp to={summary.totalBrands} /></b><span>brands</span></div>
        <div><b><CountUp to={summary.totalCategories} /></b><span>categories</span></div>
        <div><b><CountUp to={summary.totalStores} /></b><span>partner stores</span></div>
      </div>
      <p className="ac-muted" style={{ margin: 0, fontSize: 15 }}>
        Prices from {money(summary.priceMin)}. {count.format(summary.inStock)} items are in stock right now.
      </p>
      {picks.length > 0 && (
        <div className="ac-pulse-pics">
          {picks.map((p) => <Link key={p.id} to={`/products/${p.id}`} title={p.name}><img src={sized(firstImage(p), 240)} alt={p.name} loading="lazy" /></Link>)}
        </div>
      )}
      <Link to="/catalog" className="ac-btn ac-btn-blue ac-btn-small" style={{ justifySelf: 'start' }}>Browse everything we sell</Link>
    </aside>
  );
}
