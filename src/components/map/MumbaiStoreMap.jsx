import React, { useEffect, useMemo, useState } from 'react';
import { MapPin, Search, X, Star, Clock, Truck, Check } from 'lucide-react';
import api from '../../services/api';
import { useLocation } from '../../context/LocationContext';
import StoreMap from '../../storefront/StoreMap';
import '../../storefront/storefront.css';
import '../../storefront/forms.css';

/**
 * Store picker: a real map of partner stores with a list beside it.
 * Same props as before (isOpen, onClose, productId, productName, onSelectStore), so every place that opens it keeps working.
 */
export const MumbaiStoreMap = ({ isOpen = true, onClose, productId = null, productName = null, onSelectStore = null }) => {
  const { location, selectedStore, updateSelectedStore } = useLocation();
  const [stores, setStores] = useState([]);
  const [query, setQuery] = useState('');
  const [active, setActive] = useState(null);
  const [state, setState] = useState('loading');

  const lat = location?.lat || 19.1136;
  const lng = location?.lng || 72.8697;

  useEffect(() => {
    if (!isOpen) return undefined;
    let live = true;
    setState('loading');
    api.get('/stores/nearby', { params: { lat, lng, radius: 40, ...(productId ? { productId } : {}) } })
      .then((r) => { if (live) { const list = r.data?.stores || []; setStores(list); setActive(list[0] || null); setState('ready'); } })
      .catch(() => live && setState('error'));
    return () => { live = false; };
  }, [isOpen, lat, lng, productId]);

  const shown = useMemo(() => {
    const q = query.trim().toLowerCase();
    return stores.filter((s) => !q || `${s.storeName} ${s.address} ${s.pincode}`.toLowerCase().includes(q));
  }, [stores, query]);

  const choose = (store) => {
    updateSelectedStore(store);
    onSelectStore?.(store);
    onClose?.();
  };

  if (!isOpen) return null;
  const chosenId = selectedStore?.storeId || selectedStore?.id;

  return (
    <div className="ac ac-host" style={{ display: 'contents' }}>
      <div className="ac-sc-back" onClick={onClose} aria-hidden="true" style={{ zIndex: 90 }} />
      <div role="dialog" aria-modal="true" aria-label="Choose a store" className="ac-storepick">
        <div className="ac-row-between" style={{ padding: '18px 22px', borderBottom: '1px solid var(--line)' }}>
          <div>
            <h2 className="ac-display" style={{ fontSize: 24 }}>{productName ? `Where to get ${productName}` : 'Choose a store near you'}</h2>
            <p className="ac-muted" style={{ margin: '4px 0 0', fontSize: 14 }}>{productName ? 'Stores that have it in stock right now.' : 'Pick a store for delivery or pickup. Distances are from your location.'}</p>
          </div>
          <button className="ac-sc-x" onClick={onClose} aria-label="Close"><X size={20} /></button>
        </div>

        <div className="ac-storepick-body">
          <div className="ac-storepick-list">
            <div className="ac-search" style={{ maxWidth: 'none', margin: '0 0 12px' }}>
              <Search size={18} aria-hidden="true" />
              <label className="ac-sr" htmlFor="store-q">Search stores</label>
              <input id="store-q" value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Search by area or PIN code" />
            </div>
            {state === 'loading' && [0, 1, 2].map((i) => <div key={i} className="ac-skel" style={{ height: 86, marginBottom: 10 }} />)}
            {state === 'error' && <p className="ac-warn" role="alert">We could not load stores. Check that the backend is running.</p>}
            {state === 'ready' && shown.length === 0 && <p className="ac-muted">{productName ? 'No nearby store has this in stock right now.' : 'No stores match that search.'}</p>}
            {shown.map((s) => (
              <div key={s.storeId} className="ac-store" data-on={active?.storeId === s.storeId} onClick={() => setActive(s)}>
                <div className="ac-row-between">
                  <b>{s.storeName}</b>
                  {chosenId === s.storeId && <span className="ac-chip-status" data-tone="ok"><Check size={12} /> Chosen</span>}
                </div>
                <div className="ac-muted" style={{ fontSize: 14 }}>{s.address}</div>
                <div className="ac-row" style={{ gap: 14, fontSize: 13.5, marginTop: 6 }}>
                  <span><MapPin size={13} /> {s.distanceKm} km</span>
                  <span><Clock size={13} /> ~{s.estimatedMinutes} min</span>
                  <span><Truck size={13} /> {s.deliveryFee ? `₹${s.deliveryFee}` : 'Free delivery'}</span>
                  {s.rating ? <span><Star size={13} /> {s.rating}</span> : null}
                </div>
                {active?.storeId === s.storeId && (
                  <button className="ac-btn ac-btn-blue ac-btn-small" style={{ marginTop: 10 }} onClick={(e) => { e.stopPropagation(); choose(s); }}>Choose this store</button>
                )}
              </div>
            ))}
          </div>
          <div className="ac-storepick-map">
            <StoreMap stores={shown} customer={{ lat, lng }} selectedId={active?.storeId} height="100%" radiusKm={5}
              onSelect={(s, confirm) => (confirm ? choose(s) : setActive(s))} />
          </div>
        </div>
      </div>
    </div>
  );
};

export default MumbaiStoreMap;
