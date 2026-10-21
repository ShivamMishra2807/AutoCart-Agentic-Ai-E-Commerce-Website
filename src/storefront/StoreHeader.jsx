import React, { useEffect, useRef, useState } from 'react';
import { Link, useNavigate, useSearchParams, useLocation as useRoute } from 'react-router-dom';
import { Search, ShoppingBag, MapPin, User, LifeBuoy } from 'lucide-react';
import api from '../services/api';
import { useAuth } from '../hooks/useAuth';
import { useCart } from '../hooks/useCart';
import { useLocation } from '../context/LocationContext';
import LocationPickerModal from '../components/navbar/LocationPickerModal';
import { BrandLink, CategoryIcon } from './Brand';
import './storefront.css';

let categoryCache = null; // categories rarely change; fetch once per visit

export default function StoreHeader() {
  const navigate = useNavigate();
  const [sp] = useSearchParams();
  const route = useRoute();
  const shopping = ['/products', '/catalog'].includes(route.pathname);
  const current = shopping ? sp.get('category') || '' : null;
  const { user } = useAuth();
  const { itemCount } = useCart();
  const { location } = useLocation();
  const [categories, setCategories] = useState(categoryCache || []);
  const [query, setQuery] = useState('');
  const [scrolled, setScrolled] = useState(false);
  const [bump, setBump] = useState(false);
  const [locationOpen, setLocationOpen] = useState(false);

  useEffect(() => {
    if (categoryCache) return;
    api.get('/categories')
      .then((res) => {
        categoryCache = Array.isArray(res.data) ? res.data : res.data?.results || [];
        setCategories(categoryCache);
      })
      .catch(() => {});
  }, []);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 8);
    onScroll();
    window.addEventListener('scroll', onScroll, { passive: true });
    return () => window.removeEventListener('scroll', onScroll);
  }, []);

  const first = useRef(true);
  useEffect(() => {
    if (first.current) { first.current = false; return undefined; }
    setBump(true);
    const t = window.setTimeout(() => setBump(false), 520);
    return () => window.clearTimeout(t);
  }, [itemCount]);

  const search = (e) => {
    e.preventDefault();
    const q = query.trim();
    if (q) navigate(`/search?q=${encodeURIComponent(q)}`);
  };

  const place = location?.source === 'default' ? 'Set your location' : [location?.area, location?.city].filter(Boolean).join(', ') || 'Choose your area';
  const firstName = user?.name?.split(' ')[0];
  const isAdmin = user?.role === 'ADMIN' || user?.role === 'STAFF';

  return (
    <>
      <header className="ac-header" data-scrolled={scrolled}>
        <div className="ac-wrap ac-bar">
          <BrandLink />
          <button className="ac-where" onClick={() => setLocationOpen(true)} aria-label={`Delivering to ${place}. Change location`}>
            <MapPin size={18} /><span>{place}</span>
          </button>
          <form className="ac-search" onSubmit={search} role="search">
            <Search size={19} aria-hidden="true" />
            <label className="ac-sr" htmlFor="ac-q">Search products</label>
            <input id="ac-q" value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Search products and brands" autoComplete="off" />
          </form>
          <div className="ac-actions">
            {isAdmin && <Link to="/admin" className="ac-icon-btn"><span className="ac-label">Admin console</span></Link>}
            {user?.role === 'SELLER' && <Link to="/seller/dashboard" className="ac-icon-btn"><span className="ac-label">Seller centre</span></Link>}
            {user && <Link to="/support" className="ac-icon-btn" aria-label="Support tickets"><LifeBuoy size={20} /><span className="ac-label">Help</span></Link>}
            <Link to={user ? '/profile' : '/login'} className="ac-icon-btn" aria-label={firstName ? `Account for ${firstName}` : 'Sign in'}>
              <User size={20} /><span className="ac-label">{firstName || 'Sign in'}</span>
            </Link>
            <Link to="/cart" className={`ac-icon-btn ${bump ? 'ac-bump' : ''}`} aria-label={`Cart, ${itemCount || 0} items`}>
              <ShoppingBag size={21} />
              {itemCount > 0 && <span className="ac-count">{itemCount}</span>}
            </Link>
          </div>
        </div>
        {categories.length > 0 && (
          <nav className="ac-cats" aria-label="Categories">
            <div className="ac-wrap">
              <Link to="/catalog" data-on={current === ''} aria-current={current === '' ? 'page' : undefined}><CategoryIcon name="all" size={16} /> Everything we sell</Link>
              {categories.map((c) => <Link key={c.id} to={`/products?category=${encodeURIComponent(c.name)}`} data-on={current === c.name} aria-current={current === c.name ? 'page' : undefined}><CategoryIcon name={c.name} size={16} /> {c.name}</Link>)}
            </div>
          </nav>
        )}
      </header>
      <LocationPickerModal isOpen={locationOpen} onClose={() => setLocationOpen(false)} />
    </>
  );
}
