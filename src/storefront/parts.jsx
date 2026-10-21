import React, { useEffect, useRef, useState } from 'react';
import { Link } from 'react-router-dom';
import { Heart, Check } from 'lucide-react';
import { useCart } from '../hooks/useCart';
import { useWishlist } from '../hooks/useWishlist';
import './storefront.css';
import './forms.css';
import './fx.css';
import './pages.css';
import { reduceMotion, finePointer, useTilt } from './motion';
import { getTheme } from './theme';
import { Photo } from './Brand';

export { reduceMotion, finePointer };

// --- helpers shared by the home page, the catalogue and the support chat -----

const rupee = new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 0 });
export const money = (n) => rupee.format(Number(n) || 0);
export const count = new Intl.NumberFormat('en-IN');

// Unsplash URLs carry a width; ask for the size each spot needs.
export const sized = (url, w) => (!url ? '' : /[?&]w=\d+/.test(url) ? url.replace(/([?&]w=)\d+/, `$1${w}`) : url);
// Which product "owns" each photo. Where the catalogue reuses one photo, only the owner (lowest id) shows it.
const photoOwner = new Map();
const noteProducts = (list) => {
  list.forEach((p) => (Array.isArray(p?.images) ? p.images : []).forEach((u) => {
    const cur = photoOwner.get(u);
    if (!cur || String(p.id) < cur) photoOwner.set(u, String(p.id));
  }));
};
export const firstImage = (p, w) => {
  const urls = [...(Array.isArray(p?.images) ? p.images : []), p?.image].filter(Boolean);
  const own = urls.find((u) => !photoOwner.has(u) || photoOwner.get(u) === String(p.id));
  return own ? (w ? sized(own, w) : own) : '';
};
export const ownPhotos = (p) => [...(Array.isArray(p?.images) ? p.images : []), p?.image].filter(Boolean).filter((u) => !photoOwner.has(u) || photoOwner.get(u) === String(p.id));
export const asList = (data) => {
  const list = Array.isArray(data) ? data : data?.results || data?.products || [];
  if (list.length && Array.isArray(list[0]?.images)) noteProducts(list);
  return list;
};
export const byRating = (a, b) => (b.rating || 0) - (a.rating || 0);
export const savings = (p) => Math.max(0, (Number(p.originalPrice) || 0) - (Number(p.price) || 0));
export const firstSentence = (text = '', max = 150) => {
  const s = text.split(/(?<=[.!?])\s/)[0] || text;
  return s.length > max ? `${s.slice(0, max - 1).trimEnd()}…` : s;
};

// Flat tinted panels, one per category (in category order).
export const tonesFor = (categories) => {
  const tones = getTheme().tones;
  return categories.reduce((m, c, i) => ({ ...m, [c.name]: tones[i % tones.length] }), {});
};

// Opens the support assistant from anywhere (the layout listens for this).
export const openAssistant = () => window.dispatchEvent(new CustomEvent('autocart:open-assistant'));

// Writes --p (0..1) on the element as it moves through the viewport; CSS turns it into parallax.
export function useScrollProgress(ref) {
  useEffect(() => {
    const el = ref.current;
    if (!el || reduceMotion()) return undefined;
    let raf = 0;
    const update = () => {
      raf = 0;
      const r = el.getBoundingClientRect();
      const vh = window.innerHeight;
      el.style.setProperty('--p', Math.min(1, Math.max(0, (vh - r.top) / (vh + r.height))).toFixed(3));
    };
    const onScroll = () => { if (!raf) raf = requestAnimationFrame(update); };
    update();
    window.addEventListener('scroll', onScroll, { passive: true });
    window.addEventListener('resize', onScroll);
    return () => {
      window.removeEventListener('scroll', onScroll);
      window.removeEventListener('resize', onScroll);
      if (raf) cancelAnimationFrame(raf);
    };
  }, [ref]);
}

export const CountUp = ({ to, decimals = 0 }) => {
  const ref = useRef(null);
  const [val, setVal] = useState(to);
  useEffect(() => {
    const el = ref.current;
    if (!el || reduceMotion() || typeof IntersectionObserver === 'undefined') { setVal(to); return undefined; }
    setVal(0);
    let raf = 0;
    let settle = 0;
    const io = new IntersectionObserver(([entry]) => {
      if (!entry.isIntersecting) return;
      io.disconnect();
      settle = window.setTimeout(() => setVal(to), 1800); // never leave the number short of its real value
      const t0 = performance.now();
      const tick = (t) => {
        const k = Math.min(1, (t - t0) / 1400);
        setVal(to * (1 - (1 - k) ** 3));
        if (k < 1) raf = requestAnimationFrame(tick);
      };
      raf = requestAnimationFrame(tick);
    }, { threshold: 0.4 });
    io.observe(el);
    return () => { io.disconnect(); cancelAnimationFrame(raf); window.clearTimeout(settle); };
  }, [to]);
  return <span ref={ref}>{decimals ? val.toFixed(decimals) : count.format(Math.round(val))}</span>;
};

// --- add to cart with a short "Added" confirmation ----------------------------

export const useAdd = (p) => {
  const { addToCart } = useCart();
  const [added, setAdded] = useState(false);
  const add = () => {
    addToCart(p);
    setAdded(true);
    window.setTimeout(() => setAdded(false), 1700);
  };
  return [added, add];
};

export const ProductCard = ({ p, tone }) => {
  const { toggleWishlist, isInWishlist } = useWishlist();
  const [added, add] = useAdd(p);
  const imgRef = useRef(null);
  useTilt(imgRef, 8);
  const stock = p.stock ?? 0;
  const inStock = stock > 0 && p.stockStatus !== 'Out of Stock';
  const save = savings(p);
  const liked = isInWishlist(p.id);
  const note = !inStock ? 'Out of stock' : stock <= 10 ? `Only ${stock} left` : save > 0 ? `You save ${money(save)}` : '';

  return (
    <article className="ac-card" style={{ '--tone': tone }}>
      <div className="ac-card-img ac-tilt" ref={imgRef}>
        <Link to={`/products/${p.id}`} aria-label={`View ${p.name}`}>
          <Photo p={p} w={520} />
        </Link>
        <span className="ac-glare" aria-hidden="true" />
        {p.discount > 0 && <span className="ac-badge ac-badge-sale">{p.discount}% off</span>}
        <button className="ac-heart" data-on={liked} onClick={() => toggleWishlist(p)} aria-pressed={liked}
          aria-label={liked ? `Remove ${p.name} from wishlist` : `Save ${p.name} to wishlist`}>
          <Heart size={19} />
        </button>
      </div>
      <div className="ac-card-body">
        <div className="ac-brand">{p.brand || p.category}</div>
        <Link to={`/products/${p.id}`} className="ac-name">{p.name}</Link>
        <div className="ac-rating"><b>{Number(p.rating || 0).toFixed(1)}</b> <span className="ac-star">★</span> from {count.format(p.reviewCount || 0)} reviews</div>
        <div className="ac-price">
          <b>{money(p.price)}</b>
          {save > 0 && <s>{money(p.originalPrice)}</s>}
        </div>
        <div className="ac-note">{note}</div>
        <button className="ac-add" onClick={add} disabled={!inStock} data-added={added} aria-live="polite">
          {added ? <><Check size={18} /> Added</> : 'Add to cart'}
        </button>
      </div>
    </article>
  );
};
