import React, { useEffect, useMemo, useRef, useState } from 'react';
import { createPortal } from 'react-dom';
import { Link, useNavigate, useParams } from 'react-router-dom';
import { Heart, Minus, Plus, Check, MapPin, ChevronLeft, ChevronRight } from 'lucide-react';
import api from '../services/api';
import { useAuth } from '../hooks/useAuth';
import { useCart } from '../hooks/useCart';
import { useWishlist } from '../hooks/useWishlist';
import { useLocation } from '../context/LocationContext';
import { MumbaiStoreMap } from '../components/map/MumbaiStoreMap';
import Reviews, { Stars } from './Reviews';
import { money, count, sized, firstImage, ownPhotos, asList, savings, tonesFor, ProductCard } from './parts';
import { Photo } from './Brand';
import './storefront.css';
import './forms.css';
import './pages.css';

const RECENT_KEY = 'autocart_recent';
const readRecent = () => { try { return JSON.parse(localStorage.getItem(RECENT_KEY) || '[]'); } catch { return []; } };
const writeRecent = (ids) => { try { localStorage.setItem(RECENT_KEY, JSON.stringify(ids.slice(0, 12))); } catch { /* storage may be blocked */ } };

export default function ProductPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();
  const { addToCart } = useCart();
  const { toggleWishlist, isInWishlist } = useWishlist();
  const { location } = useLocation();

  const [product, setProduct] = useState(null);
  const [all, setAll] = useState([]);
  const [categories, setCategories] = useState([]);
  const [stores, setStores] = useState(null);
  const [state, setState] = useState('loading');
  const [shot, setShot] = useState(0);
  const [qty, setQty] = useState(1);
  const [added, setAdded] = useState(false);
  const [zoom, setZoom] = useState(null);
  const [mapOpen, setMapOpen] = useState(false);
  const [showBar, setShowBar] = useState(false);
  const cta = useRef(null);

  useEffect(() => {
    let live = true;
    setState('loading'); setShot(0); setQty(1); setStores(null);
    window.scrollTo({ top: 0 });
    Promise.all([api.get(`/products/${id}`), api.get('/products'), api.get('/categories')])
      .then(([p, list, cats]) => {
        if (!live) return;
        setProduct(p.data); setAll(asList(list.data)); setCategories(asList(cats.data)); setState('ready');
        document.title = `${p.data.name} | AutoCart`;
        writeRecent([p.data.id, ...readRecent().filter((x) => x !== p.data.id)]);
      })
      .catch(() => live && setState('error'));
    return () => { live = false; };
  }, [id]);

  useEffect(() => {
    if (!product) return;
    api.get('/stores/nearby', { params: { lat: location?.lat || 19.1136, lng: location?.lng || 72.8697, radius: 40, productId: product.id } })
      .then((r) => setStores(r.data?.stores || [])).catch(() => setStores([]));
  }, [product, location?.lat, location?.lng]);

  // the buy bar slides up once the main buttons have scrolled out of view
  useEffect(() => {
    const el = cta.current;
    if (!el || typeof IntersectionObserver === 'undefined') return undefined;
    const io = new IntersectionObserver(([e]) => setShowBar(!e.isIntersecting && e.boundingClientRect.top < 0), { threshold: 0 });
    io.observe(el);
    return () => io.disconnect();
  }, [product]);

  const tones = useMemo(() => tonesFor(categories), [categories]);
  const similar = useMemo(() => (product ? all.filter((p) => p.category === product.category && p.id !== product.id && Math.abs(p.price - product.price) <= product.price * 1.5).sort((a, b) => Math.abs(a.price - product.price) - Math.abs(b.price - product.price)).slice(0, 3) : []), [all, product]);
  const related = useMemo(() => (product ? all.filter((p) => p.category === product.category && p.id !== product.id).slice(0, 4) : []), [all, product]);
  const recent = useMemo(() => readRecent().filter((x) => x !== id).map((x) => all.find((p) => p.id === x)).filter(Boolean).slice(0, 4), [all, id]);

  if (state === 'loading') return <div className="ac ac-page"><div className="ac-wrap"><div className="ac-skel" style={{ height: 560 }} /></div></div>;
  if (state === 'error' || !product) {
    return <div className="ac ac-page"><div className="ac-wrap" style={{ textAlign: 'center', padding: '60px 0' }}>
      <h1 className="ac-display">We couldn’t find that product</h1>
      <p className="ac-sub" style={{ margin: '12px auto 24px' }}>It may have been removed, or the link is wrong.</p>
      <Link to="/catalog" className="ac-btn ac-btn-blue">Browse everything we sell</Link></div></div>;
  }

  const images = ownPhotos(product);
  const stock = product.stock ?? 0;
  const inStock = stock > 0 && product.stockStatus !== 'Out of Stock';
  const save = savings(product);
  const liked = isInWishlist(product.id);
  const maxQty = Math.max(1, Math.min(stock, 20));
  const nearest = stores?.[0];
  const specs = Object.entries(product.specifications || {});
  const highlights = specs.slice(0, 4);
  const warranty = specs.find(([k]) => /warrant/i.test(k));
  const quickAnswers = [
    ['How fast can I get it?', nearest ? `From ${nearest.storeName}, about ${nearest.estimatedMinutes} minutes away (${nearest.distanceKm} km).${nearest.deliveryFee ? ` Delivery is ${money(nearest.deliveryFee)}.` : ' Delivery is free.'} Or pick it up yourself.` : 'Delivery time depends on the store. Open the map to see which stores have it.'],
    ['Can I pay when I get it?', 'Yes. Pay online, in cash on delivery, or at the store when you collect it.'],
    ['What if I do not like it?', 'Returns are accepted for 7 days after delivery. Start a return from your orders page.'],
    ['Is it covered by a warranty?', warranty ? `${warranty[0]}: ${warranty[1]}.` : 'Warranty details are listed by the seller. Check the specifications below.'],
    ['Is it in stock?', !inStock ? 'Not right now. Save it to your wishlist to find it again.' : stock <= 10 ? `Only ${stock} left, so order soon.` : `Yes, ${stock} available.`],
    ['Who sells it?', product.seller ? `${product.seller}, a seller on AutoCart.` : 'A verified seller on AutoCart.'],
  ];

  const add = () => { if (addToCart(product, qty) === false) return; setAdded(true); window.setTimeout(() => setAdded(false), 1800); };
  const buyNow = () => { if (addToCart(product, qty, { buyNow: true }) !== false) navigate('/checkout'); };
  const lens = (e) => {
    const r = e.currentTarget.getBoundingClientRect();
    setZoom({ x: ((e.clientX - r.left) / r.width) * 100, y: ((e.clientY - r.top) / r.height) * 100 });
  };
  const step = (d) => setShot((s) => (s + d + images.length) % images.length);

  return (
    <div className="ac ac-page"><div className="ac-wrap">
      <nav className="ac-crumbs" aria-label="Breadcrumb">
        <Link to="/">Home</Link><span>/</span><Link to={`/products?category=${encodeURIComponent(product.category)}`}>{product.category}</Link>
        {product.brand && <><span>/</span><Link to={`/catalog?brand=${encodeURIComponent(product.brand)}`}>{product.brand}</Link></>}
      </nav>

      <div className="ac-pp">
        <div className="ac-gallery">
          <div className="ac-gallery-main" style={{ '--tone': tones[product.category] }} onPointerMove={lens} onPointerLeave={() => setZoom(null)}
            onKeyDown={(e) => { if (e.key === 'ArrowRight') step(1); if (e.key === 'ArrowLeft') step(-1); }} tabIndex={0} aria-label={`${product.name}, photo ${shot + 1} of ${images.length}`}>
            {images.length ? <img src={sized(images[shot], 1200)} alt={product.name} style={zoom ? { transformOrigin: `${zoom.x}% ${zoom.y}%`, transform: 'scale(2)' } : undefined} /> : <Photo p={product} w={900} />}
            {product.discount > 0 && <span className="ac-badge ac-badge-sale">{product.discount}% off</span>}
            <button className="ac-heart" style={{ top: 16, right: 16, width: 46, height: 46 }} data-on={liked} aria-pressed={liked} onClick={() => toggleWishlist(product)} aria-label={liked ? 'Remove from wishlist' : 'Save to wishlist'}><Heart size={22} /></button>
            {images.length > 1 && <>
              <button className="ac-gal-arrow" style={{ left: 12 }} onClick={() => step(-1)} aria-label="Previous photo"><ChevronLeft size={20} /></button>
              <button className="ac-gal-arrow" style={{ right: 12 }} onClick={() => step(1)} aria-label="Next photo"><ChevronRight size={20} /></button>
            </>}
          </div>
          {images.length > 1 && (
            <div className="ac-thumbs">{images.map((src, i) => (
              <button key={src} data-on={i === shot} onClick={() => setShot(i)} aria-label={`Show photo ${i + 1}`}><img src={sized(src, 200)} alt="" /></button>))}</div>
          )}
        </div>

        <div className="ac-pinfo">
          {product.brand && <Link to={`/catalog?brand=${encodeURIComponent(product.brand)}`} className="ac-brand" style={{ color: 'var(--brand)', fontWeight: 700 }}>{product.brand}</Link>}
          <h1 className="ac-display ac-pname">{product.name}</h1>
          <a href="#reviews" className="ac-ratingline"><Stars value={product.rating || 0} /> <b>{Number(product.rating || 0).toFixed(1)}</b><span className="ac-muted">from {count.format(product.reviewCount || 0)} ratings</span></a>

          <div className="ac-pprice">
            <b>{money(product.price)}</b>
            {save > 0 && <s>{money(product.originalPrice)}</s>}
          </div>
          {save > 0 && <p style={{ color: 'var(--coral)', fontWeight: 700, margin: 0 }}>You save {money(save)} ({product.discount}% off)</p>}

          {product.description && <p className="ac-lead">{product.description}</p>}

          {highlights.length > 0 && (
            <div className="ac-highlights">{highlights.map(([k, v]) => <div key={k}><b>{String(v)}</b><span>{k}</span></div>)}</div>
          )}

          <div ref={cta} className="ac-buyrow">
            {inStock && (
              <div className="ac-qty" role="group" aria-label="Quantity">
                <button onClick={() => setQty((q) => Math.max(1, q - 1))} aria-label="One less" disabled={qty <= 1}><Minus size={16} /></button>
                <span aria-live="polite">{qty}</span>
                <button onClick={() => setQty((q) => Math.min(maxQty, q + 1))} aria-label="One more" disabled={qty >= maxQty}><Plus size={16} /></button>
              </div>
            )}
            <button className="ac-btn ac-btn-outline" style={{ flex: 1, minWidth: 130 }} onClick={add} disabled={!inStock}>{added ? <><Check size={18} /> Added</> : 'Add to cart'}</button>
            <button className="ac-btn ac-btn-blue" style={{ flex: 1.2, minWidth: 150 }} onClick={buyNow} disabled={!inStock}>{inStock ? `Buy now · ${money(product.price * qty)}` : 'Out of stock'}</button>
          </div>
          <p className="ac-stockline" data-ok={inStock}>{!inStock ? 'Currently out of stock' : stock <= 10 ? `Only ${stock} left` : 'In stock'}</p>

          <div className="ac-avail">
            <MapPin size={18} color="var(--brand)" />
            <div style={{ flex: 1, minWidth: 0 }}>
              {stores === null && <span className="ac-muted">Checking stores near {location?.area || 'you'}…</span>}
              {stores && stores.length > 0 && <><b>{nearest.estimatedMinutes} min from {nearest.storeName}</b><div className="ac-muted" style={{ fontSize: 14 }}>{nearest.distanceKm} km away · in stock at {stores.length} store{stores.length > 1 ? 's' : ''} near you</div></>}
              {stores && stores.length === 0 && <span className="ac-muted">Not in stock at stores near {location?.area || 'you'} right now.</span>}
            </div>
            <button className="ac-textlink" style={{ border: 0, background: 'none' }} onClick={() => setMapOpen(true)}>Map</button>
          </div>
          <p className="ac-muted" style={{ fontSize: 14, margin: '14px 0 0' }}>Pay online, in cash, or at the store. Returns accepted for 7 days after delivery.{product.seller ? ` Sold by ${product.seller}.` : ''}</p>
        </div>
      </div>

      <Reviews productId={product.id} signedIn={!!user} />

      {specs.length > 0 && (
        <section aria-labelledby="spec-h" style={{ marginTop: 56 }}>
          <h2 id="spec-h" className="ac-display" style={{ fontSize: 32, marginBottom: 18 }}>Specifications</h2>
          <div className="ac-box" style={{ padding: 8 }}><table className="ac-table"><tbody>{specs.map(([k, v]) => <tr key={k}><th style={{ width: '34%' }}>{k}</th><td>{String(v)}</td></tr>)}</tbody></table></div>
        </section>
      )}



      <section aria-labelledby="quick-h" style={{ marginTop: 56 }}>
        <h2 id="quick-h" className="ac-display" style={{ fontSize: 32, marginBottom: 18 }}>Quick answers</h2>
        <div className="ac-quick">
          {quickAnswers.map(([q, a]) => <div key={q}><b>{q}</b><p>{a}</p></div>)}
        </div>
      </section>

      {similar.length > 0 && (
        <section aria-labelledby="cmp-h" style={{ marginTop: 56 }}>
          <h2 id="cmp-h" className="ac-display" style={{ fontSize: 32, marginBottom: 18 }}>How it compares</h2>
          <div className="ac-box ac-scroll-x" style={{ padding: 8 }}>
            <table className="ac-table ac-compare">
              <thead><tr><th /> {[product, ...similar].map((p, i) => <th key={p.id} data-me={i === 0}>{i === 0 ? 'This one' : <Link to={`/products/${p.id}`} className="ac-textlink">{p.name}</Link>}</th>)}</tr></thead>
              <tbody>
                <tr><th>Price</th>{[product, ...similar].map((p) => <td key={p.id}><b>{money(p.price)}</b></td>)}</tr>
                <tr><th>Rating</th>{[product, ...similar].map((p) => <td key={p.id}>{Number(p.rating || 0).toFixed(1)} ★ ({count.format(p.reviewCount || 0)})</td>)}</tr>
                <tr><th>Discount</th>{[product, ...similar].map((p) => <td key={p.id}>{p.discount ? `${p.discount}% off` : '-'}</td>)}</tr>
                <tr><th>Brand</th>{[product, ...similar].map((p) => <td key={p.id}>{p.brand || '-'}</td>)}</tr>
                <tr><th>Availability</th>{[product, ...similar].map((p) => <td key={p.id}>{p.stock > 10 ? 'In stock' : p.stock > 0 ? `Only ${p.stock} left` : 'Out of stock'}</td>)}</tr>
              </tbody>
            </table>
          </div>
        </section>
      )}

      {related.length > 0 && (
        <section style={{ marginTop: 64 }} aria-labelledby="rel-h">
          <h2 id="rel-h" className="ac-display" style={{ fontSize: 32, marginBottom: 20 }}>More in {product.category}</h2>
          <div className="ac-grid">{related.map((p) => <ProductCard key={p.id} p={p} tone={tones[p.category]} />)}</div>
        </section>
      )}
      {recent.length > 0 && (
        <section style={{ marginTop: 64 }} aria-labelledby="rec-h">
          <h2 id="rec-h" className="ac-display" style={{ fontSize: 32, marginBottom: 20 }}>Recently viewed</h2>
          <div className="ac-grid">{recent.map((p) => <ProductCard key={p.id} p={p} tone={tones[p.category]} />)}</div>
        </section>
      )}

      {createPortal(
        <div className="ac ac-host" style={{ display: 'contents' }}>
          <div className="ac-buybar" data-show={showBar && inStock} aria-hidden={!(showBar && inStock)}>
            {images[0] && <img src={sized(images[0], 120)} alt="" />}
            <div style={{ minWidth: 0, flex: 1 }}><b className="ac-buybar-name">{product.name}</b><div className="ac-muted" style={{ fontSize: 14 }}>{money(product.price)}</div></div>
            <button className="ac-btn ac-btn-blue ac-btn-small" onClick={add} tabIndex={showBar ? 0 : -1}>{added ? 'Added' : 'Add to cart'}</button>
          </div>
        </div>, document.body)}

      {mapOpen && <MumbaiStoreMap isOpen productId={product.id} productName={product.name} onClose={() => setMapOpen(false)} />}
    </div></div>
  );
}
