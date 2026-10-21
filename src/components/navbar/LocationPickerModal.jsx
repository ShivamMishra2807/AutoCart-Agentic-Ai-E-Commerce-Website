import React, { useState } from 'react';
import { MapPin, Navigation, X, Check, ShieldCheck, Loader2, Search } from 'lucide-react';
import { useLocation } from '../../context/LocationContext';

const POPULAR_HUBS = [
  { name: 'Andheri West (Lokhandwala)', pin: '400053', city: 'Mumbai' },
  { name: 'Thane West (Viviana)', pin: '400606', city: 'Thane' },
  { name: 'Kalyan (Khadakpada)', pin: '421301', city: 'Kalyan' },
  { name: 'Dombivli (Manpada)', pin: '421201', city: 'Dombivli' },
  { name: 'Navi Mumbai (Vashi)', pin: '400703', city: 'Navi Mumbai' },
  { name: 'Powai (Hiranandani)', pin: '400076', city: 'Mumbai' },
  { name: 'Borivali West (Shimpoli)', pin: '400092', city: 'Mumbai' },
  { name: 'Bandra West (Linking Rd)', pin: '400050', city: 'Mumbai' },
];

export const LocationPickerModal = ({ isOpen, onClose }) => {
  const { location, loading, error, requestBrowserLocation, setManualLocation } = useLocation();
  const [pinInput, setPinInput] = useState('');
  const [statusMessage, setStatusMessage] = useState('');

  if (!isOpen) return null;

  const handleManualSubmit = async (e) => {
    e?.preventDefault();
    if (!pinInput.trim()) return;
    setStatusMessage('Checking store serviceability...');
    const ok = await setManualLocation(pinInput.trim());
    if (ok) {
      setStatusMessage('Location updated successfully!');
      setTimeout(() => {
        setStatusMessage('');
        onClose();
      }, 700);
    } else {
      setStatusMessage('');
    }
  };

  const handleQuickSelect = async (pin) => {
    setStatusMessage(`Switching location to ${pin}...`);
    const ok = await setManualLocation(pin);
    if (ok) {
      setTimeout(() => {
        setStatusMessage('');
        onClose();
      }, 500);
    }
  };

  const handleBrowserGeo = () => {
    requestBrowserLocation();
    setTimeout(() => {
      onClose();
    }, 1500);
  };

  return (
    <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-xs flex items-center justify-center p-4 animate-in fade-in duration-150">
      <div className="w-full max-w-md bg-white rounded-3xl shadow-2xl border border-gray-100 overflow-hidden">
        {/* Header */}
        <div className="bg-gradient-to-r from-slate-900 to-indigo-950 text-white p-5 flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div className="w-9 h-9 rounded-xl bg-indigo-500/20 border border-indigo-400/30 flex items-center justify-center">
              <MapPin className="w-5 h-5 text-amber-300" />
            </div>
            <div>
              <h3 className="font-extrabold text-sm">Select Delivery Location</h3>
              <p className="text-[11px] text-indigo-200">Hyperlocal inventory & 35-min delivery</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-slate-300 hover:text-white hover:bg-white/10 transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Body */}
        <div className="p-5 space-y-4 text-xs">
          {/* Current Location Display */}
          <div className="p-3 bg-indigo-50/60 rounded-2xl border border-indigo-100 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
              <span className="text-gray-600 font-medium">Currently delivering to:</span>
            </div>
            <span className="font-bold text-indigo-950 truncate max-w-[200px]">
              {location.displayName || `${location.city} (${location.pincode})`}
            </span>
          </div>

          {/* Device Location Button */}
          <button
            onClick={handleBrowserGeo}
            disabled={loading}
            className="w-full flex items-center justify-center gap-2 py-3 px-4 rounded-2xl bg-indigo-600 hover:bg-indigo-700 active:scale-[0.99] text-white font-bold transition shadow-sm cursor-pointer disabled:opacity-50"
          >
            {loading ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <Navigation className="w-4 h-4 text-amber-300" />
            )}
            <span>Use My Current Device Location</span>
          </button>

          {/* Divider */}
          <div className="flex items-center gap-3">
            <div className="flex-1 h-px bg-gray-200" />
            <span className="text-[10px] font-bold uppercase tracking-wider text-gray-400">or enter PIN code</span>
            <div className="flex-1 h-px bg-gray-200" />
          </div>

          {/* Manual Input Form */}
          <form onSubmit={handleManualSubmit} className="flex gap-2">
            <div className="relative flex-1">
              <Search className="w-4 h-4 absolute left-3 top-3 text-gray-400" />
              <input
                type="text"
                placeholder="Enter 6-digit PIN (e.g. 560038) or City"
                value={pinInput}
                onChange={(e) => setPinInput(e.target.value)}
                className="w-full pl-9 pr-3 py-2.5 rounded-xl border border-gray-200 focus:outline-none focus:border-indigo-600 text-xs font-semibold"
              />
            </div>
            <button
              type="submit"
              disabled={loading || !pinInput.trim()}
              className="px-4 py-2.5 rounded-xl bg-slate-900 hover:bg-black text-white font-bold transition disabled:opacity-50 cursor-pointer"
            >
              Verify
            </button>
          </form>

          {statusMessage && (
            <p className="text-emerald-700 bg-emerald-50 border border-emerald-200 p-2 rounded-xl text-center font-bold">
              {statusMessage}
            </p>
          )}

          {error && (
            <p className="text-rose-700 bg-rose-50 border border-rose-200 p-2 rounded-xl text-center font-semibold">
              {error}
            </p>
          )}

          {/* Quick Hubs */}
          <div>
            <p className="text-[10px] font-bold uppercase tracking-wider text-gray-400 mb-2">
              Popular Partner Store Hubs
            </p>
            <div className="flex flex-wrap gap-1.5">
              {POPULAR_HUBS.map((hub) => (
                <button
                  key={hub.pin}
                  onClick={() => handleQuickSelect(hub.pin)}
                  className="px-2.5 py-1.5 rounded-xl bg-gray-50 hover:bg-indigo-50 text-gray-700 hover:text-indigo-700 border border-gray-200 hover:border-indigo-200 font-semibold text-[11px] transition"
                >
                  📍 {hub.name}
                </button>
              ))}
            </div>
          </div>

          {/* Privacy Notice */}
          <div className="pt-2 border-t border-gray-100 flex items-start gap-2 text-[10px] text-gray-400 leading-relaxed">
            <ShieldCheck className="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" />
            <p>
              Your coordinates are stored locally on your device and only sent during store searches to compute distance and 35-min delivery road ETAs.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LocationPickerModal;
