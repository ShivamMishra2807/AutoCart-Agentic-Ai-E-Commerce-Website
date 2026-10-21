import React, { useState, useEffect } from 'react';
import { Store, Navigation, Clock, ShieldCheck, CheckCircle2, AlertCircle, Lock, Loader2, MapPin } from 'lucide-react';
import { useLocation } from '../../context/LocationContext';
import { MumbaiStoreMap } from '../map/MumbaiStoreMap';
import api from '../../services/api';

export const NearbyStoreAvailability = ({ productId, productName }) => {
  const { location, selectedStore, updateSelectedStore } = useLocation();
  const [stores, setStores] = useState([]);
  const [loading, setLoading] = useState(true);
  const [reservingStoreId, setReservingStoreId] = useState(null);
  const [reservationSuccess, setReservationSuccess] = useState(null);
  const [reservationError, setReservationError] = useState(null);
  const [showMap, setShowMap] = useState(false);

  useEffect(() => {
    if (!productId) return;
    fetchNearbyStores();
  }, [productId, location.lat, location.lng]);

  const fetchNearbyStores = async () => {
    setLoading(true);
    try {
      const lat = location.lat || 12.9716;
      const lng = location.lng || 77.5946;
      const res = await api.get(`/stores/nearby?productId=${productId}&lat=${lat}&lng=${lng}&radius=35`);
      setStores(res.data?.stores || []);
    } catch (err) {
      console.warn('Could not fetch nearby stores', err);
      setStores([]);
    } finally {
      setLoading(false);
    }
  };

  const handleReserveStock = async (store) => {
    setReservingStoreId(store.storeId);
    setReservationError(null);
    setReservationSuccess(null);

    try {
      const res = await api.post('/orders/reserve-stock', {
        storeId: store.storeId,
        productId,
        quantity: 1,
      });

      if (res.data?.success) {
        setReservationSuccess({
          storeName: store.storeName,
          token: res.data.reservationToken,
          expiresInMinutes: res.data.expiresInMinutes || 15,
        });
      } else {
        setReservationError(res.data?.error || 'Unable to reserve stock right now.');
      }
    } catch (err) {
      setReservationError(err.response?.data?.error || 'Stock reservation request failed.');
    } finally {
      setReservingStoreId(null);
    }
  };

  if (loading) {
    return (
      <div className="p-4 bg-indigo-50/50 rounded-2xl border border-indigo-100 flex items-center justify-center gap-2 text-xs text-indigo-700">
        <Loader2 className="w-4 h-4 animate-spin text-indigo-600" />
        <span>Checking live physical inventory at nearby partner stores...</span>
      </div>
    );
  }

  if (stores.length === 0) {
    return (
      <div className="p-4 bg-gray-50 rounded-2xl border border-gray-100 text-xs text-gray-500 flex items-center gap-2">
        <Store className="w-4 h-4 text-gray-400 shrink-0" />
        <span>No physical store within 35 km has verified counter stock. Standard warehouse fulfillment available (1-2 days).</span>
      </div>
    );
  }

  const bestStore = stores[0];

  return (
    <div className="p-4 bg-gradient-to-br from-indigo-50/80 via-white to-purple-50/40 rounded-2xl border border-indigo-100 shadow-xs space-y-3">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="w-7 h-7 rounded-lg bg-indigo-600 text-white flex items-center justify-center shadow-xs">
            <Store className="w-4 h-4" />
          </div>
          <div>
            <h4 className="text-xs font-extrabold text-gray-900">Nearby Physical Store In Stock</h4>
            <p className="text-[10px] text-gray-500 font-medium">Hyperlocal 35-min delivery or instant pickup</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => setShowMap(true)}
            className="text-[10px] font-bold text-indigo-700 bg-indigo-50 hover:bg-indigo-100 border border-indigo-200 px-2.5 py-1 rounded-full transition flex items-center gap-1 shadow-2xs"
          >
            <MapPin className="w-3 h-3 text-indigo-600" />
            <span>Mumbai Map</span>
          </button>
          <span className="inline-flex items-center gap-1 text-[10px] font-extrabold text-emerald-700 bg-emerald-100 px-2.5 py-0.5 rounded-full">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></span>
            Live Verified Stock
          </span>
        </div>
      </div>

      {/* Primary Store Banner */}
      <div className="p-3 bg-white rounded-xl border border-indigo-100/80 shadow-xs text-xs space-y-2">
        <div className="flex items-start justify-between gap-2">
          <div>
            <p className="font-extrabold text-gray-900">{bestStore.storeName}</p>
            <p className="text-[11px] text-gray-500 mt-0.5">{bestStore.address}, {bestStore.city}</p>
          </div>
          <div className="text-right shrink-0">
            <span className="font-extrabold text-indigo-600 text-sm">
              {bestStore.distanceKm} km
            </span>
            <p className="text-[10px] text-gray-400">Road Distance</p>
          </div>
        </div>

        {/* Perks Badges */}
        <div className="grid grid-cols-2 gap-2 pt-1">
          <div className="flex items-center gap-1.5 p-2 rounded-lg bg-indigo-50 text-[11px] font-bold text-indigo-900">
            <Clock className="w-3.5 h-3.5 text-indigo-600" />
            <span>ETA: ~{bestStore.estimatedMinutes} mins</span>
          </div>
          <div className="flex items-center gap-1.5 p-2 rounded-lg bg-emerald-50 text-[11px] font-bold text-emerald-900">
            <ShieldCheck className="w-3.5 h-3.5 text-emerald-600" />
            <span>{bestStore.availableStock || bestStore.stock || 'In Stock'} Available</span>
          </div>
        </div>

        {/* Reserve Stock Button */}
        <div className="pt-1 flex items-center justify-between gap-3">
          <p className="text-[10px] text-gray-400 leading-tight">
            Locks store unit for 15 minutes while you complete checkout.
          </p>
          <button
            onClick={() => handleReserveStock(bestStore)}
            disabled={Boolean(reservingStoreId)}
            className="shrink-0 flex items-center gap-1 px-3 py-1.5 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white font-extrabold text-[11px] shadow-xs active:scale-95 transition cursor-pointer disabled:opacity-50"
          >
            {reservingStoreId === bestStore.storeId ? (
              <Loader2 className="w-3.5 h-3.5 animate-spin" />
            ) : (
              <Lock className="w-3.5 h-3.5 text-amber-300" />
            )}
            <span>Reserve Unit (15m Lock)</span>
          </button>
        </div>
      </div>

      {/* Reservation Notifications */}
      {reservationSuccess && (
        <div className="p-3 bg-emerald-50 border border-emerald-200 rounded-xl text-xs text-emerald-900 space-y-1">
          <p className="font-extrabold flex items-center gap-1.5 text-emerald-700">
            <CheckCircle2 className="w-4 h-4 text-emerald-600" /> Unit Reserved Successfully!
          </p>
          <p className="text-[11px]">
            1 unit held at <strong>{reservationSuccess.storeName}</strong> for{' '}
            <strong>{reservationSuccess.expiresInMinutes} minutes</strong>. Reservation token:{' '}
            <code className="font-mono bg-white px-1.5 py-0.5 rounded border border-emerald-200 text-[10px]">
              {reservationSuccess.token}
            </code>
          </p>
        </div>
      )}

      {reservationError && (
        <div className="p-3 bg-rose-50 border border-rose-200 rounded-xl text-xs text-rose-900 flex items-center gap-1.5">
          <AlertCircle className="w-4 h-4 text-rose-600 shrink-0" />
          <span>{reservationError}</span>
        </div>
      )}

      {/* Other Nearby Stores */}
      {stores.length > 1 && (
        <div className="pt-1">
          <p className="text-[10px] font-bold uppercase tracking-wider text-gray-400 mb-1.5">
            Other Nearby Hubs With Stock ({stores.length - 1})
          </p>
          <div className="space-y-1.5">
            {stores.slice(1, 3).map((st) => (
              <div
                key={st.storeId}
                className="flex items-center justify-between p-2 rounded-xl bg-white border border-gray-100 text-[11px]"
              >
                <div>
                  <span className="font-bold text-gray-800">{st.storeName}</span>
                  <span className="text-gray-400 ml-1.5 font-medium">({st.city})</span>
                </div>
                <div className="flex items-center gap-3">
                  <span className="text-gray-500 font-semibold">{st.distanceKm} km</span>
                  <span className="text-emerald-600 font-bold">~{st.estimatedMinutes}m delivery</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Interactive Mumbai Hyperlocal Stores Modal */}
      <MumbaiStoreMap
        isOpen={showMap}
        onClose={() => setShowMap(false)}
        productId={productId}
        productName={productName}
        onSelectStore={(st) => {
          updateSelectedStore(st);
          setShowMap(false);
        }}
      />
    </div>
  );
};

export default NearbyStoreAvailability;
