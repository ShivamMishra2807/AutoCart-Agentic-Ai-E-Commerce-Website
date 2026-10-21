import React, { useEffect, useMemo, useRef, useState } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { ChevronDown, X, Search, Check } from 'lucide-react';
import api from '../services/api';
import { money, count, asList, tonesFor, ProductCard } from './parts';
import './storefront.css';
import './forms.css';
import './pages.css';

const PAGE = 24;
const COLLECTIONS = [
  { key: 'all', label: 'Everything', set: {} },
  { key: 'under', label: 'Under ₹999', set: { max: '999' } },
  { key: 'top', label: 'Top rated', set: { rating: '4.5' } },
  { key: 'deal', label: '50% off or more', set: { deal: '50' } },
  { key: 'low', label: 'Almost gone', set: { low: '1' } },
];
const SORTS = [['popular', 'Most reviewed'], ['rating', 'Top rated'], ['discount', 'Biggest discount'], ['low', 'Price, low to high'], ['high', 'Price, high to low']];
const PRICE_PRESETS = [['Under ₹500', '', 500], ['₹500 to ₹1,000', 500, 1000], ['₹1,000 to ₹5,000', 1000, 5000], ['Over ₹5,000', 5000, '']];

/** A pill that opens a small menu. Closes on outside click or Escape, so nothing sits on the page until you ask for it. */
function Pill({ label, active, children }) {
  const [open, setOpen] = useState(false);
  const box = useRef(null);
  useEffect(() => {
    if (!open) return undefined;
    const away = (e) => { if (box.current && !box.current.contains(e.target)) setOpen(false); };
    const esc = (e) => { if (e.key === 'Escape') setOpen(false); };
    document.addEventListener('mousedown', away); document.addEventListener('keydown', esc);
    return () => { document.removeEventListener('mousedown', away); document.removeEventListener('keydown', esc); };
  }, [open]);
  return (
    <div className="ac-pillwrap" ref={box}>
      <button className="ac-pill" data-on={!!active} aria-expanded={open} aria-haspopup="true" onClick={() => setOpen((o) => !o)}>{label}<ChevronDown size={15} /></button>
      {open && <>
        <div className="ac-pillback" onClick={() => setOpen(false)} aria-hidden="true" />
        <div className="ac-pillmenu" role="group" aria-label={label}>{children(() => setOpen(false))}</div>
      </>}
    </div>
  );
}

export default function Catalog() {
  const [params, setParams] = useSearchParams();
  const [products, setProducts] = useState([]);
  const [categories, setCategories] = useState([]);
  const [summary, setSummary] = useState(null);
  const [state, setState] = useState('loading');
  const [view, setView] = useState('cards');
  const [page, setPage] = useState(1);
  const [brandQ, setBrandQ] = useState('');

  const q = params.get('q') || '';
  const category = params.get('category') || '';
  const brands = (params.get('brand') || '').split(',').filter(Boolean);
  const min = Number(params.get('min')) || 0;
  const max = Number(params.get('max')) || 0;
  const rating = Number(params.get('rating')) || 0;
  const deal = Number(params.get('deal')) || 0;
  const inStock = params.get('stock') === '1';
  const low = params.get('low') === '1';
  const sort = params.get('sort') || 'popular';

  const put = (changes) => {
    const next = new URLSearchParams(params);
    Object.entries(changes).forEach(([k, v]) => { if (v === '' || v == null || v === false || v === 0) next.delete(k); else next.set(k, String(v)); });
    setParams(next, { replace: true });
    setPage(1);
  };
  const clearAll = () => { setParams({}, { replace: true }); setPage(1); };

  useEffect(() => {
    Promise.all([api.get('/products'), api.get('/categories'), api.get('/catalog/summary')])
      .then(([p, c, s]) => { setProducts(asList(p.data)); setCategories(asList(c.data)); setSummary(s.data); setState('ready'); })
      .catch(() => setState('error'));
  }, []);
  useEffect(() => { document.title = `${category || (q ? `“${q}”` : 'Shop')} | AutoCart`; }, [category, q]);

  const tones = useMemo(() => tonesFor(categories), [categories]);
  const brandList = useMemo(() => {
    const pool = category ? products.filter((p) => p.category === category) : products;
    const m = pool.reduce((acc, p) => (p.brand ? { ...acc, [p.brand]: (acc[p.brand] || 0) + 1 } : acc), {});
    return Object.entries(m).sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]));
  }, [products, category]);

  const rows = useMemo(() => {
    const needle = q.trim().toLowerCase();
    const list = products.filter((p) => (
      (!needle || `${p.name} ${p.brand} ${p.category} ${p.description}`.toLowerCase().includes(needle))
      && (!category || p.category === category) && (!brands.length || brands.includes(p.brand))
      && (!min || p.price >= min) && (!max || p.price <= max) && (!rating || (p.rating || 0) >= rating)
      && (!deal || (p.discount || 0) >= deal) && (!inStock || (p.stock ?? 0) > 0) && (!low || ((p.stock ?? 0) > 0 && p.stock <= 10))
    ));
    const by = {
      popular: (a, b) => (b.reviewCount || 0) - (a.reviewCount || 0), rating: (a, b) => (b.rating || 0) - (a.rating || 0),
      low: (a, b) => a.price - b.price, high: (a, b) => b.price - a.price, discount: (a, b) => (b.discount || 0) - (a.discount || 0),
    };
    return [...list].sort(by[sort] || by.popular);
  }, [products, q, category, brands.join(','), min, max, rating, deal, inStock, low, sort]);

  const pages = Math.max(1, Math.ceil(rows.length / PAGE));
  const shown = rows.slice((page - 1) * PAGE, page * PAGE);

  const chips = [
    q && { k: 'q', label: `“${q}”`, off: { q: '' } },
    ...brands.map((b) => ({ k: `b-${b}`, label: b, off: { brand: brands.filter((x) => x !== b).join(',') } })),
    min && { k: 'min', label: `From ${money(min)}`, off: { min: '' } }, max && { k: 'max', label: `Up to ${money(max)}`, off: { max: '' } },
    rating && { k: 'r', label: `${rating}★ and up`, off: { rating: '' } }, deal && { k: 'd', label: `${deal}% off or more`, off: { deal: '' } },
    inStock && { k: 's', label: 'In stock', off: { stock: '' } }, low && { k: 'l', label: 'Almost gone', off: { low: '' } },
  ].filter(Boolean);
  const anyFilter = chips.length > 0 || !!category;
  const activeCollection = COLLECTIONS.find((c) => c.key !== 'all' && Object.entries(c.set).every(([k, v]) => params.get(k) === v))?.key || (!anyFilter ? 'all' : '');
  const pickCollection = (c) => put({ q: '', category: '', brand: '', min: '', max: '', rating: '', deal: '', low: '', stock: '', ...c.set });
  const shownBrands = brandList.filter(([b]) => b.toLowerCase().includes(brandQ.toLowerCase()));

  return (
    <div className="ac ac-page ac-shop-page"><div className="ac-wrap">
      <nav className="ac-crumbs" aria-label="Breadcrumb"><Link to="/">Home</Link><span>/</span><span>Shop</span>{category && <><span>/</span><span>{category}</span></>}</nav>
      <div className="ac-shophead">
        <div>
          <h1 className="ac-display">{q ? `Results for “${q}”` : category || 'Everything we sell'}</h1>
          {summary && <p className="ac-sub" style={{ marginTop: 10 }}>{count.format(rows.length)} products{!q && !category ? `, from ${money(summary.priceMin)} to ${money(summary.priceMax)}, from ${summary.totalStores} nearby stores` : ''}.</p>}
        </div>
        <form className="ac-search ac-shopsearch" role="search" onSubmit={(e) => e.preventDefault()}>
          <Search size={18} aria-hidden="true" /><label className="ac-sr" htmlFor="shop-q">Search the shop</label>
          <input id="shop-q" value={q} onChange={(e) => put({ q: e.target.value })} placeholder="Search by name, brand or keyword" />
        </form>
      </div>

      <div className="ac-colls" role="group" aria-label="Quick picks">
        {COLLECTIONS.map((c) => <button key={c.key} data-on={activeCollection === c.key} onClick={() => pickCollection(c)}>{c.label}</button>)}
      </div>

      <div className="ac-pillbar" role="toolbar" aria-label="Filter and sort">
        <Pill label={min || max ? `${min ? money(min) : '₹0'} to ${max ? money(max) : 'any'}` : 'Price'} active={!!(min || max)}>{(close) => (
          <div>
            <div className="ac-pm-presets">{PRICE_PRESETS.map(([l, a, b]) => <button key={l} data-on={(min || '') === a && (max || '') === b} onClick={() => { put({ min: a, max: b }); close(); }}>{l}</button>)}</div>
            <div className="ac-prange" style={{ marginTop: 12 }}>
              <label className="ac-sr" htmlFor="pmin">Minimum price</label><input id="pmin" className="ac-input" inputMode="numeric" placeholder="Min ₹" value={min || ''} onChange={(e) => put({ min: e.target.value.replace(/\D/g, '') })} />
              <span>to</span>
              <label className="ac-sr" htmlFor="pmax">Maximum price</label><input id="pmax" className="ac-input" inputMode="numeric" placeholder="Max ₹" value={max || ''} onChange={(e) => put({ max: e.target.value.replace(/\D/g, '') })} />
            </div>
          </div>
        )}</Pill>
        <Pill label={brands.length ? `Brand · ${brands.length}` : 'Brand'} active={brands.length > 0}>{() => (
          <div>
            <label className="ac-sr" htmlFor="brand-q">Find a brand</label>
            <input id="brand-q" className="ac-input" style={{ minHeight: 42, marginBottom: 8 }} placeholder="Find a brand" value={brandQ} onChange={(e) => setBrandQ(e.target.value)} />
            <div className="ac-pm-scroll">{shownBrands.map(([b, n]) => (
              <label key={b} className="ac-check ac-fbrand"><input type="checkbox" checked={brands.includes(b)} onChange={() => put({ brand: (brands.includes(b) ? brands.filter((x) => x !== b) : [...brands, b]).join(',') })} /><span>{b}</span><em>{n}</em></label>))}
              {shownBrands.length === 0 && <p className="ac-muted" style={{ margin: 6 }}>No brand matches.</p>}</div>
          </div>
        )}</Pill>
        <Pill label={rating ? `${rating}★ and up` : 'Rating'} active={!!rating}>{(close) => (
          <div className="ac-pm-list">{[[0, 'Any rating'], [4, '4★ and up'], [4.5, '4.5★ and up']].map(([v, l]) => (
            <button key={v} data-on={rating === v} onClick={() => { put({ rating: v }); close(); }}>{l}{rating === v && <Check size={16} />}</button>))}</div>
        )}</Pill>
        <Pill label="More" active={inStock || !!deal}>{() => (
          <div>
            <label className="ac-check ac-fbrand"><input type="checkbox" checked={inStock} onChange={(e) => put({ stock: e.target.checked ? '1' : '' })} /><span>In stock only</span></label>
            <label className="ac-check ac-fbrand"><input type="checkbox" checked={!!deal} onChange={(e) => put({ deal: e.target.checked ? '30' : '' })} /><span>30% off or more</span></label>
          </div>
        )}</Pill>

        <div className="ac-pillbar-end">
          <label className="ac-sr" htmlFor="sortby">Sort by</label>
          <select id="sortby" className="ac-pill ac-pill-select" value={sort} onChange={(e) => put({ sort: e.target.value === 'popular' ? '' : e.target.value })}>{SORTS.map(([v, l]) => <option key={v} value={v}>{l}</option>)}</select>
          <div className="ac-seg ac-seg-sm" role="group" aria-label="View">
            <button data-on={view === 'cards'} onClick={() => setView('cards')} aria-pressed={view === 'cards'}>Cards</button>
            <button data-on={view === 'table'} onClick={() => setView('table')} aria-pressed={view === 'table'}>Details</button>
          </div>
        </div>
      </div>

      {(chips.length > 0 || category) && (
        <div className="ac-chiprow" aria-label="Active filters">
          {category && <button className="ac-fchip" onClick={() => put({ category: '', brand: '' })}>{category} <X size={14} /></button>}
          {chips.map((c) => <button key={c.k} className="ac-fchip" onClick={() => put(c.off)}>{c.label} <X size={14} /></button>)}
          <button className="ac-textlink" style={{ border: 0, background: 'none' }} onClick={clearAll}>Clear all</button>
        </div>
      )}

      {state === 'loading' && <div className="ac-grid">{[0, 1, 2, 3].map((i) => <div key={i} className="ac-skel" style={{ height: 380 }} />)}</div>}
      {state === 'error' && <div className="ac-error" role="alert"><h2 className="ac-display">We can’t load the shop right now.</h2><p>Make sure the backend is running, then refresh.</p></div>}
      {state === 'ready' && rows.length === 0 && (
        <div className="ac-box" style={{ textAlign: 'center', padding: 48 }}>
          <h2 className="ac-display" style={{ fontSize: 28 }}>Nothing matches those filters</h2>
          <p className="ac-muted">Try removing one, or pick a quick pick above.</p>
          <button className="ac-btn ac-btn-blue ac-btn-small" onClick={clearAll}>Clear all filters</button>
        </div>
      )}
      {state === 'ready' && rows.length > 0 && view === 'cards' && <div className="ac-grid">{shown.map((p) => <ProductCard key={p.id} p={p} tone={tones[p.category]} />)}</div>}
      {state === 'ready' && rows.length > 0 && view === 'table' && (
        <div className="ac-scroll-x ac-box" style={{ padding: 0 }}>
          <table className="ac-table">
            <thead><tr><th>Product</th><th>Brand</th><th>Category</th><th>Price</th><th>MRP</th><th>Off</th><th>Rating</th><th>Reviews</th><th>Stock</th><th>Seller</th></tr></thead>
            <tbody>{shown.map((p) => (
              <tr key={p.id}>
                <td><Link to={`/products/${p.id}`} className="ac-textlink">{p.name}</Link></td><td>{p.brand}</td><td>{p.category}</td><td>{money(p.price)}</td><td>{money(p.originalPrice)}</td>
                <td>{p.discount ? `${p.discount}%` : '-'}</td><td>{Number(p.rating || 0).toFixed(1)}</td><td>{count.format(p.reviewCount || 0)}</td><td>{p.stock > 0 ? p.stock : 'Out'}</td><td>{p.seller || '-'}</td>
              </tr>))}</tbody>
          </table>
        </div>
      )}
      {pages > 1 && (
        <nav className="ac-row" style={{ justifyContent: 'center', marginTop: 40 }} aria-label="Pages">
          <button className="ac-btn ac-btn-small ac-btn-outline" disabled={page === 1} onClick={() => { setPage(page - 1); window.scrollTo({ top: 0 }); }}>Previous</button>
          <span className="ac-muted">Page {page} of {pages}</span>
          <button className="ac-btn ac-btn-small ac-btn-outline" disabled={page === pages} onClick={() => { setPage(page + 1); window.scrollTo({ top: 0 }); }}>Next</button>
        </nav>
      )}
    </div></div>
  );
}
