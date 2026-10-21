import React, { useEffect, useMemo, useRef, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Sparkles, ChevronLeft, ChevronRight, Store, Truck, LifeBuoy, ShoppingBag } from 'lucide-react';
import api from '../services/api';
import {
  money, count, sized, firstImage, asList, byRating, savings, firstSentence, reduceMotion, finePointer,
  tonesFor, openAssistant, useScrollProgress, CountUp, useAdd, ProductCard,
} from './parts';
import { CategoryIcon, Photo } from './Brand';
import { useCart } from '../hooks/useCart';
import './storefront.css';


/** One real deal per day, picked from the biggest discounts, with a countdown to midnight when the next one starts. */
const useCountdown = () => {
  const left = () => { const n = new Date(); const end = new Date(n); end.setHours(24, 0, 0, 0); return Math.max(0, end - n); };
  const [ms, setMs] = useState(left);
  useEffect(() => { const t = window.setInterval(() => setMs(left()), 1000); return () => window.clearInterval(t); }, []);
  const pad = (n) => String(n).padStart(2, '0');
  return [Math.floor(ms / 3600000), Math.floor(ms / 60000) % 60, Math.floor(ms / 1000) % 60].map(pad);
};

const DealOfDay = ({ p, tone }) => {
  const navigate = useNavigate();
  const { addToCart } = useCart();
  const [h, m, sec] = useCountdown();
  const save = savings(p);
  return (
    <section className="ac-sec ac-wrap" aria-labelledby="dod-h">
      <div className="ac-dod" style={{ '--tone': tone }}>
        <div className="ac-dod-copy">
          <p className="ac-dod-kicker">Deal of the day</p>
          <h2 id="dod-h" className="ac-display">{p.name}</h2>
          <div className="ac-dod-price"><b>{money(p.price)}</b><s>{money(p.originalPrice)}</s><span>Save {money(save)}</span></div>
          <div className="ac-dod-clock" role="timer" aria-label={`Deal ends in ${h} hours ${m} minutes`}>
            <div><b>{h}</b><small>hours</small></div><div><b>{m}</b><small>minutes</small></div><div><b>{sec}</b><small>seconds</small></div>
            <p>left. A new deal starts at midnight.</p>
          </div>
          <div className="ac-row" style={{ marginTop: 22 }}>
            <button className="ac-btn ac-btn-blue" onClick={() => { if (addToCart(p, 1, { buyNow: true }) !== false) navigate('/checkout'); }}>Buy now</button>
            <Link to={`/products/${p.id}`} className="ac-btn ac-btn-white">See details</Link>
          </div>
          {p.stock <= 20 && <p className="ac-dod-low">Only {p.stock} left at this price.</p>}
        </div>
        <Link to={`/products/${p.id}`} className="ac-dod-img" aria-label={p.name}><Photo p={p} w={900} eager /></Link>
      </div>
    </section>
  );
};

const Collections = ({ items }) => (
  <section className="ac-sec ac-wrap" aria-labelledby="coll-h">
    <h2 id="coll-h" className="ac-display ac-h2" style={{ marginBottom: 20 }}>Shop by what you need</h2>
    <div className="ac-collgrid">
      {items.map((c) => (
        <Link key={c.label} to={c.to} className="ac-collcard"><b>{c.label}</b><span>{c.note}</span><em>{c.count} products</em></Link>
      ))}
    </div>
  </section>
);

const Spotlight = ({ p, tone, flip }) => {
  const ref = useRef(null);
  const [added, add] = useAdd(p);
  const navigate = useNavigate();
  const { addToCart } = useCart();
  useScrollProgress(ref);
  const save = savings(p);
  return (
    <section ref={ref} className={`ac-spot ${flip ? 'ac-spot-flip' : ''}`} style={{ '--tone': tone }} aria-label={p.name}>
      <div className="ac-spot-copy">
        <p className="ac-spot-cat">{p.brand ? `${p.brand}, ${p.category}` : p.category}</p>
        <h2 className="ac-display ac-spot-name">{p.name}</h2>
        <p className="ac-spot-desc">{firstSentence(p.description)}</p>
        <div className="ac-spot-rate">{Number(p.rating || 0).toFixed(1)} <span className="ac-star">★</span> from {count.format(p.reviewCount || 0)} reviews</div>
        <div className="ac-spot-price">
          <b>{money(p.price)}</b>
          {save > 0 && <s>{money(p.originalPrice)}</s>}
          {save > 0 && <span className="ac-spot-save">Save {money(save)}</span>}
        </div>
        <div className="ac-spot-cta">
          <button className="ac-btn ac-btn-blue" onClick={() => { if (addToCart(p, 1, { buyNow: true }) !== false) navigate('/checkout'); }}>Buy now</button>
          <button className="ac-btn ac-btn-outline" onClick={add} data-added={added}>{added ? 'Added to cart' : 'Add to cart'}</button>
        </div>
      </div>
      <div className="ac-spot-media">
        <div className="ac-spot-frame"><img src={sized(firstImage(p), 1200)} alt={p.name} loading="lazy" /></div>
      </div>
    </section>
  );
};

const Rail = ({ id, title, sub, items, tones, to }) => {
  const track = useRef(null);
  const nudge = (dir) => track.current?.scrollBy({ left: dir * 640, behavior: reduceMotion() ? 'auto' : 'smooth' });
  if (!items.length) return null;
  return (
    <section className="ac-sec" id={id} aria-labelledby={`${id}-h`}>
      <div className="ac-wrap">
        <div className="ac-head">
          <div>
            <h2 className="ac-display ac-h2" id={`${id}-h`}>{title}</h2>
            {sub && <p className="ac-sub">{sub}</p>}
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 22 }}>
            <Link to={to} className="ac-textlink">See all</Link>
            <div className="ac-arrows">
              <button className="ac-arrow" onClick={() => nudge(-1)} aria-label={`Scroll ${title} back`}><ChevronLeft size={20} /></button>
              <button className="ac-arrow" onClick={() => nudge(1)} aria-label={`Scroll ${title} forward`}><ChevronRight size={20} /></button>
            </div>
          </div>
        </div>
        <div className="ac-rail" ref={track} tabIndex={0} aria-label={title}>
          {items.map((p) => <ProductCard key={p.id} p={p} tone={tones[p.category]} />)}
        </div>
      </div>
    </section>
  );
};

export default function Home() {
  const heroRef = useRef(null);
  const rootRef = useRef(null);
  const [products, setProducts] = useState([]);
  const [categories, setCategories] = useState([]);
  const [state, setState] = useState('loading'); // loading | ready | error

  const load = async () => {
    setState('loading');
    try {
      const [prodRes, catRes] = await Promise.all([api.get('/products'), api.get('/categories')]);
      setProducts(asList(prodRes.data));
      setCategories(asList(catRes.data));
      setState('ready');
    } catch {
      setState('error');
    }
  };
  useEffect(() => { load(); }, []);

  useEffect(() => {
    const prev = document.title;
    document.title = 'AutoCart: find your next favourite thing';
    return () => { document.title = prev; };
  }, []);

  // Hero parallax: pointer position becomes --mx/--my in -1..1 (fine pointers only).
  useEffect(() => {
    const el = heroRef.current;
    if (!el || reduceMotion() || !finePointer()) return undefined;
    let raf = 0;
    const onMove = (e) => {
      if (raf) return;
      raf = requestAnimationFrame(() => {
        raf = 0;
        const r = el.getBoundingClientRect();
        el.style.setProperty('--mx', (((e.clientX - r.left) / r.width) * 2 - 1).toFixed(3));
        el.style.setProperty('--my', (((e.clientY - r.top) / r.height) * 2 - 1).toFixed(3));
      });
    };
    const onLeave = () => { el.style.setProperty('--mx', 0); el.style.setProperty('--my', 0); };
    el.addEventListener('pointermove', onMove);
    el.addEventListener('pointerleave', onLeave);
    return () => { el.removeEventListener('pointermove', onMove); el.removeEventListener('pointerleave', onLeave); if (raf) cancelAnimationFrame(raf); };
  }, [state]);

  // Scroll reveal: sections ease in as they come into view. Content is only hidden once the observer is running,
  // and never with reduced motion. Cards inside the sideways rails are left alone so they never stay invisible.
  useEffect(() => {
    const root = rootRef.current;
    if (state !== 'ready' || !root || reduceMotion() || typeof IntersectionObserver === 'undefined') return undefined;
    const els = [...root.querySelectorAll('.ac-head, .ac-tile, .ac-card, .ac-spot, .ac-nums, .ac-sell, .ac-perk')].filter((el) => !el.closest('.ac-rail'));
    const io = new IntersectionObserver((entries) => entries.forEach((en) => {
      if (en.isIntersecting) { en.target.dataset.in = 'true'; io.unobserve(en.target); }
    }), { rootMargin: '0px 0px -6% 0px', threshold: 0.08 });
    els.forEach((el, i) => { el.classList.add('ac-rv'); el.style.setProperty('--i', String(i % 4)); io.observe(el); });
    root.classList.add('ac-armed');
    return () => { io.disconnect(); root.classList.remove('ac-armed'); els.forEach((el) => el.classList.remove('ac-rv')); };
  }, [state, products.length]);

  // Everything shown comes from the live API. A product appears only once on the page.
  const view = useMemo(() => {
    const tones = tonesFor(categories);
    const counts = products.reduce((m, p) => ({ ...m, [p.category]: (m[p.category] || 0) + 1 }), {});
    const withImage = products.filter((p) => firstImage(p));
    const used = new Set();
    const take = (list, n) => {
      const picked = list.filter((p) => !used.has(p.id)).slice(0, n);
      picked.forEach((p) => used.add(p.id));
      return picked;
    };
    const topIn = (name) => withImage.filter((p) => p.category === name && (p.stock ?? 0) > 0).sort(byRating)[0];
    const fan = ['Electronics', 'Home & Kitchen', 'Sports & Fitness'].map(topIn).filter(Boolean);
    const [center, left, right] = fan.length === 3 ? fan : take([...withImage].sort(byRating), 3);
    [center, left, right].filter(Boolean).forEach((p) => used.add(p.id));

    const dealPool = withImage.filter((p) => (p.discount || 0) >= 30 && (p.stock ?? 0) > 0 && !used.has(p.id)).sort((a, b) => String(a.id).localeCompare(String(b.id)));
    const today = new Date();
    const dayNumber = today.getFullYear() * 400 + today.getMonth() * 32 + today.getDate();
    const dealOfDay = dealPool.length ? dealPool[dayNumber % dealPool.length] : null;
    if (dealOfDay) used.add(dealOfDay.id);
    const inCount = (f) => products.filter(f).length;
    const collections = [
      { label: 'Under ₹999', note: 'Everyday finds', to: '/catalog?max=999', count: inCount((p) => p.price <= 999) },
      { label: 'Top rated', note: '4.5 stars and up', to: '/catalog?rating=4.5&sort=rating', count: inCount((p) => (p.rating || 0) >= 4.5) },
      { label: 'Half price or less', note: '50% off or more', to: '/catalog?deal=50&sort=discount', count: inCount((p) => (p.discount || 0) >= 50) },
      { label: 'Almost gone', note: 'Ten or fewer left', to: '/catalog?low=1', count: inCount((p) => (p.stock ?? 0) > 0 && p.stock <= 10) },
    ].filter((c) => c.count > 0);
    const spot1 = take(withImage.filter((p) => p.category === 'Electronics' && (p.stock ?? 0) > 0).sort((a, b) => b.price - a.price), 1)[0];
    const spot2 = take(withImage.filter((p) => p.category === 'Fashion' && (p.stock ?? 0) > 0).sort((a, b) => b.discount - a.discount), 1)[0];
    const deals = take([...products].filter((p) => p.discount > 0).sort((a, b) => b.discount - a.discount), 10);
    const loved = take(products.filter((p) => p.bestSeller).sort((a, b) => (b.reviewCount || 0) - (a.reviewCount || 0)), 8);

    const brandCount = products.reduce((m, p) => (p.brand ? { ...m, [p.brand]: (m[p.brand] || 0) + 1 } : m), {});
    const brands = Object.keys(brandCount);
    const ticker = [...brands].sort((a, b) => brandCount[b] - brandCount[a]).slice(0, 14);
    const avg = products.length ? products.reduce((s, p) => s + (p.rating || 0), 0) / products.length : 0;
    return { tones, counts, dealOfDay, collections, center, left, right, spot1, spot2, deals, loved, ticker, brandTotal: brands.length, avg };
  }, [products, categories]);

  const { center } = view;

  return (
    <div className="ac ac-home" ref={rootRef}>
      <main>
        {/* Hero: the one orchestrated moment */}
        <section className="ac-hero ac-wrap" ref={heroRef} aria-labelledby="ac-hero-h">
          <h1 className="ac-display" id="ac-hero-h">
            <span className="ac-line"><span style={{ '--d': 80 }}>Find your next</span></span>
            <span className="ac-line"><span style={{ '--d': 220 }}>favourite thing.</span></span>
          </h1>
          <p className="ac-hero-sub ac-rise" style={{ '--d': 520 }}>
            {state === 'ready'
              ? `${products.length} products from stores around Mumbai. See what’s in stock near you, then get it delivered or pick it up.`
              : 'Products from stores around Mumbai. See what’s in stock near you.'}
          </p>
          <div className="ac-hero-cta ac-rise" style={{ '--d': 680 }}>
            <Link to="/products" className="ac-btn ac-btn-blue">Shop all products</Link>
            <button className="ac-btn ac-btn-soft" onClick={openAssistant}><Sparkles size={19} /> Ask Saathi</button>
          </div>

          {state === 'ready' && center ? (
            <div className="ac-stage" aria-label="Top rated picks">
              <span className="ac-disc ac-px ac-d1" style={{ '--d': 600 }} />
              <span className="ac-disc ac-px ac-d2" style={{ '--d': 760 }} />
              <span className="ac-disc ac-px ac-d3" style={{ '--d': 880 }} />
              {view.left && <Link to={`/products/${view.left.id}`} className="ac-fan ac-fan-l ac-px" style={{ '--d': 900 }} aria-label={view.left.name}><img src={sized(firstImage(view.left), 600)} alt={view.left.name} /></Link>}
              {view.right && <Link to={`/products/${view.right.id}`} className="ac-fan ac-fan-r ac-px" style={{ '--d': 980 }} aria-label={view.right.name}><img src={sized(firstImage(view.right), 600)} alt={view.right.name} /></Link>}
              <Link to={`/products/${center.id}`} className="ac-fan ac-fan-c ac-px" style={{ '--d': 760 }} aria-label={center.name}><img src={sized(firstImage(center), 800)} alt={center.name} loading="eager" /></Link>

              <div className="ac-chip ac-c1 ac-px" style={{ '--d': 1250 }}>
                <div className="ac-chip-in"><b>{Number(center.rating || 0).toFixed(1)} <span className="ac-star">★</span></b><small>{count.format(center.reviewCount || 0)} reviews</small></div>
              </div>
              {savings(center) > 0 && (
                <div className="ac-chip ac-c3 ac-px" style={{ '--d': 1400 }}>
                  <div className="ac-chip-in"><b>Save {money(savings(center))}</b><small>on this one</small></div>
                </div>
              )}
              <div className="ac-chip ac-c2 ac-px" style={{ '--d': 1550 }}>
                <div className="ac-chip-in">
                  <small>{center.brand || center.category}</small>
                  <b>{center.name.length > 28 ? `${center.name.slice(0, 27)}…` : center.name}</b>
                  <small>{money(center.price)}</small>
                </div>
              </div>
            </div>
          ) : state === 'loading' ? (
            <div className="ac-stage-skel ac-skel" style={{ maxWidth: 760, margin: '28px auto 0' }} aria-busy="true" />
          ) : null}
        </section>

        {state === 'error' && (
          <div className="ac-error" role="alert">
            <h2 className="ac-display">We can’t load the store right now.</h2>
            <p>Make sure the backend is running on port 8000, then try again.</p>
            <button className="ac-btn ac-btn-blue" onClick={load}>Try again</button>
          </div>
        )}

        {state === 'ready' && (
          <>
            {view.ticker.length > 0 && (
              <div className="ac-marq" aria-label="Brands in the catalogue">
                <div className="ac-marq-track">
                  {[...view.ticker, ...view.ticker].map((b, i) => <span key={`${b}-${i}`} aria-hidden={i >= view.ticker.length}>{b}</span>)}
                </div>
              </div>
            )}

            <section className="ac-wrap ac-perks" aria-label="Why shop here">
              <div className="ac-perk"><Store size={22} /><div><b>Live stock from real stores</b><span>See what is on the shelf near you before you order.</span></div></div>
              <div className="ac-perk"><Truck size={22} /><div><b>Delivery or in-store pickup</b><span>A clear delivery time and fee up front. Or collect it yourself.</span></div></div>
              <div className="ac-perk"><LifeBuoy size={22} /><div><b>Real people when you need them</b><span>Ask the assistant, send a question, or open a ticket.</span></div></div>
            </section>

            <section className="ac-wrap" aria-labelledby="how-shop-h" style={{ marginBlock: 40 }}>
              <h2 id="how-shop-h" className="ac-display" style={{ fontSize: 'clamp(26px, 3.4vw, 38px)' }}>How AutoCart works</h2>
              <ol className="ac-steps4">
                <li><span><Store size={20} /></span><b>1. Find it nearby</b><p>Search or ask Saathi. We show what is really in stock in stores around you.</p></li>
                <li><span><ShoppingBag size={20} /></span><b>2. Order in a minute</b><p>Buy now or add to cart. Pay on delivery, at the store, or online.</p></li>
                <li><span><Truck size={20} /></span><b>3. Delivered or picked up</b><p>The store packs it. You get it at home, or collect it yourself.</p></li>
                <li><span><LifeBuoy size={20} /></span><b>4. Help if anything is off</b><p>Return an item, track an order, or talk to a person from the chat.</p></li>
              </ol>
            </section>

            {view.dealOfDay && <DealOfDay p={view.dealOfDay} tone={view.tones[view.dealOfDay.category]} />}
            <Collections items={view.collections} />

            <section className="ac-sec" id="categories" aria-labelledby="cat-h">
              <div className="ac-wrap">
                <div className="ac-head">
                  <h2 className="ac-display ac-h2" id="cat-h">Shop by category</h2>
                  <Link to="/catalog" className="ac-textlink">Everything we sell</Link>
                </div>
                <div className="ac-bento">
                  {categories.slice(0, 8).map((c, i) => (
                    <Link key={c.id} to={`/products?category=${encodeURIComponent(c.name)}`}
                      className={`ac-tile ${i === 0 ? 'ac-tile-big' : ''} ${i === 7 ? 'ac-tile-wide' : ''}`} style={{ '--tone': view.tones[c.name] }}>
                      <span className="ac-tile-ico"><CategoryIcon name={c.name} size={i === 0 ? 28 : 22} /></span>
                      <b>{c.name}</b>
                      <small>{view.counts[c.name] || 0} products</small>
                      <span className="ac-tile-img"><img src={sized(c.image, i === 0 ? 800 : 420)} alt="" loading="lazy" /></span>
                    </Link>
                  ))}
                </div>
              </div>
            </section>

            {view.spot1 && <div className="ac-sec ac-wrap"><Spotlight p={view.spot1} tone={view.tones[view.spot1.category]} /></div>}
            <Rail id="deals" title="Today’s best deals" sub="The biggest discounts in the catalogue right now." items={view.deals} tones={view.tones} to="/catalog" />
            {view.spot2 && <div className="ac-sec ac-wrap"><Spotlight p={view.spot2} tone={view.tones[view.spot2.category]} flip /></div>}

            {view.loved.length > 0 && (
              <section className="ac-sec" id="loved" aria-labelledby="loved-h">
                <div className="ac-wrap">
                  <div className="ac-head">
                    <div>
                      <h2 className="ac-display ac-h2" id="loved-h">Most loved</h2>
                      <p className="ac-sub">Best sellers, ranked by how many people reviewed them.</p>
                    </div>
                    <Link to="/catalog" className="ac-textlink">See all</Link>
                  </div>
                  <div className="ac-grid">
                    {view.loved.map((p) => <ProductCard key={p.id} p={p} tone={view.tones[p.category]} />)}
                  </div>
                </div>
              </section>
            )}

            <section className="ac-sec ac-wrap" aria-label="AutoCart in numbers">
              <div className="ac-nums">
                <div><div className="ac-num"><CountUp to={products.length} /></div><div className="ac-num-label">products in the catalogue</div></div>
                <div><div className="ac-num"><CountUp to={view.brandTotal} /></div><div className="ac-num-label">brands to choose from</div></div>
                <div><div className="ac-num"><CountUp to={view.avg} decimals={1} /></div><div className="ac-num-label">average customer rating</div></div>
              </div>
            </section>

            <section className="ac-sec ac-wrap" aria-labelledby="sell-h">
              <div className="ac-sell">
                <div>
                  <h2 className="ac-display" id="sell-h">Own a shop? Sell on AutoCart.</h2>
                  <p>Fill in your business details and upload your documents. Our team reviews every application before a store goes live.</p>
                </div>
                <Link to="/seller/apply" className="ac-btn ac-btn-white">Apply to sell</Link>
              </div>
            </section>
          </>
        )}
      </main>
    </div>
  );
}
