import React, { createContext, useContext, useState, useEffect } from 'react';
import api from '../services/api';
import { reverseGeocode } from '../utils/geocode';

const LocationContext = createContext();

const DEFAULT_LOCATION = {
  lat: 19.1136,
  lng: 72.8697,
  city: 'Mumbai',
  area: 'Andheri East',
  pincode: '400069',
  displayName: 'Andheri East, Mumbai (400069)',
  source: 'default', // 'browser' | 'manual' | 'default'
  permissionStatus: 'prompt', // 'prompt' | 'granted' | 'denied'
};

export const LocationProvider = ({ children }) => {
  const [location, setLocation] = useState(() => {
    try {
      const saved = localStorage.getItem('autocart_customer_location');
      return saved ? JSON.parse(saved) : DEFAULT_LOCATION;
    } catch {
      return DEFAULT_LOCATION;
    }
  });
  const [selectedStore, setSelectedStore] = useState(() => {
    try {
      const saved = localStorage.getItem('autocart_selected_store');
      return saved ? JSON.parse(saved) : null;
    } catch {
      return null;
    }
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const saveLocation = (loc) => {
    setLocation(loc);
    // Invalidate stale store selections across the app
    setSelectedStore(null);
    try {
      localStorage.setItem('autocart_customer_location', JSON.stringify(loc));
      localStorage.removeItem('autocart_selected_store');
    } catch (e) {
      console.warn('Could not persist location', e);
    }
    // Synchronize to backend profile and Sathi session memory
    if (loc?.pincode) {
      api.post('/auth/address', {
        addressLine: loc.line || loc.area || 'Customer Location',
        city: loc.city || 'Mumbai',
        state: loc.state || 'Maharashtra',
        pinCode: loc.pincode,
        lat: loc.lat,
        lng: loc.lng,
      }).catch(() => {});
    }
  };

  const updateSelectedStore = (store) => {
    setSelectedStore(store);
    try {
      if (store) {
        localStorage.setItem('autocart_selected_store', JSON.stringify(store));
      } else {
        localStorage.removeItem('autocart_selected_store');
      }
    } catch (e) {
      console.warn('Could not persist selected store', e);
    }
  };

  /**
   * Requests coordinates via the browser Geolocation API
   */
  const requestBrowserLocation = () => {
    if (!navigator.geolocation) {
      setError('Geolocation is not supported by your browser.');
      return;
    }

    setLoading(true);
    setError(null);

    navigator.geolocation.getCurrentPosition(
      async (pos) => {
        const lat = pos.coords.latitude;
        const lng = pos.coords.longitude;

        // Look up the street address for these coordinates, and the nearest store for the serviceability message.
        const [place, near] = await Promise.all([
          reverseGeocode(lat, lng),
          api.get(`/stores/nearby?lat=${lat}&lng=${lng}&radius=35`).then((r) => (r.data?.stores || [])[0]).catch(() => null),
        ]);
        const area = place?.area || near?.address?.split(',')[0] || 'Current location';
        const city = place?.city || near?.city || 'Mumbai';
        saveLocation({
          lat, lng, city, area, line: place?.line || '', state: place?.state || '', pincode: place?.pincode || near?.pincode || '',
          displayName: [place?.line || area, city, place?.pincode].filter(Boolean).join(', '),
          source: 'browser', permissionStatus: 'granted',
        });
        setLoading(false);
      },
      (err) => {
        setLoading(false);
        const reason = err.code === 1 ? 'Permission denied by user' : 'Position unavailable or timed out';
        setError(reason);
        setLocation((prev) => ({ ...prev, permissionStatus: 'denied' }));
      },
      { timeout: 10000, enableHighAccuracy: true }
    );
  };

  /**
   * Sets location manually via Indian PIN code or city name
   */
  const setManualLocation = async (pinOrCity) => {
    if (!pinOrCity?.trim()) return false;
    setLoading(true);
    setError(null);

    try {
      const res = await api.get(`/stores/nearby?pinCode=${encodeURIComponent(pinOrCity.trim())}&radius=50`);
      const custLoc = res.data?.customerLocation || {};
      const nearest = (res.data?.stores || [])[0];

      const newLoc = {
        lat: custLoc.lat || 19.0760,
        lng: custLoc.lng || 72.8777,
        city: nearest?.city || pinOrCity,
        area: nearest?.address?.split(',')[0] || pinOrCity,
        pincode: custLoc.pinCode || '',
        displayName: `${pinOrCity.toUpperCase()} (Serviceable)`,
        source: 'manual',
        permissionStatus: 'prompt',
      };
      saveLocation(newLoc);
      return true;
    } catch (err) {
      setError('Could not verify serviceability for this PIN/city.');
      return false;
    } finally {
      setLoading(false);
    }
  };

  return (
    <LocationContext.Provider
      value={{
        location,
        selectedStore,
        updateSelectedStore,
        loading,
        error,
        requestBrowserLocation,
        setManualLocation,
      }}
    >
      {children}
    </LocationContext.Provider>
  );
};

export const useLocation = () => {
  const context = useContext(LocationContext);
  if (!context) {
    throw new Error('useLocation must be used within a LocationProvider');
  }
  return context;
};

export default LocationContext;
