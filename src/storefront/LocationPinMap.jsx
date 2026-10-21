import React, { useEffect, useMemo } from 'react';
import api from '../services/api';
import { MapContainer, TileLayer, Marker, useMap, useMapEvents } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import markerIcon from 'leaflet/dist/images/marker-icon.png';
import markerIcon2x from 'leaflet/dist/images/marker-icon-2x.png';
import markerShadow from 'leaflet/dist/images/marker-shadow.png';
import './storefront.css';

// Default Leaflet icon fallback
L.Icon.Default.mergeOptions({ iconUrl: markerIcon, iconRetinaUrl: markerIcon2x, shadowUrl: markerShadow });

// Custom AutoCART Branded Store Marker Icon
export const createAutoCartStoreIcon = () => {
  return L.divIcon({
    className: 'autocart-store-pin-wrapper',
    html: `
      <div style="position: relative; width: 38px; height: 48px; filter: drop-shadow(0 4px 6px rgba(0,0,0,0.35)); cursor: pointer;">
        <svg viewBox="0 0 36 46" width="38" height="48" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M18 0C8.05888 0 0 8.05888 0 18C0 30.5 18 46 18 46C18 46 36 30.5 36 18C36 8.05888 27.9411 0 18 0Z" fill="#2563EB"/>
          <circle cx="18" cy="18" r="14" fill="#1D4ED8"/>
          <path d="M11 15H25L24 25H12L11 15Z" fill="white"/>
          <path d="M14 15V12C14 9.79086 15.7909 8 18 8C20.2091 8 22 9.79086 22 12V15" stroke="white" stroke-width="2" stroke-linecap="round"/>
          <circle cx="18" cy="20" r="2" fill="#2563EB"/>
        </svg>
        <span style="position: absolute; top: -7px; left: 50%; transform: translateX(-50%); background: #F59E0B; color: #000; font-size: 9px; font-weight: 800; padding: 1px 5px; border-radius: 4px; border: 1px solid #FFF; white-space: nowrap; box-shadow: 0 1px 3px rgba(0,0,0,0.2);">
          STORE
        </span>
      </div>
    `,
    iconSize: [38, 48],
    iconAnchor: [19, 48],
    popupAnchor: [0, -44],
  });
};

const Recenter = ({ lat, lng, zoom }) => {
  const map = useMap();
  useEffect(() => {
    if (lat != null && lng != null && !isNaN(lat) && !isNaN(lng)) {
      map.setView([lat, lng], zoom || map.getZoom(), { animate: true });
    }
  }, [lat, lng, zoom, map]);
  return null;
};

const Picker = ({ onChange }) => {
  useMapEvents({
    click: (e) => {
      onChange?.(+e.latlng.lat.toFixed(6), +e.latlng.lng.toFixed(6));
    },
  });
  return null;
};

/**
 * A map with the custom AutoCART store pin.
 * Pass onChange to let sellers click or drag the pin.
 * If lat & lng are null, displays an interactive map of India ready for placement.
 */
export default function LocationPinMap({ lat, lng, onChange, height = 340, zoom = 15 }) {
  const editable = typeof onChange === 'function';
  const hasCoords =
    lat != null &&
    lng != null &&
    !isNaN(lat) &&
    !isNaN(lng) &&
    lat >= 6 &&
    lat <= 38 &&
    lng >= 68 &&
    lng <= 98;

  const centerLat = hasCoords ? lat : 20.5937;
  const centerLng = hasCoords ? lng : 78.9629;
  const activeZoom = hasCoords ? zoom : 4;
  const storeIcon = useMemo(() => createAutoCartStoreIcon(), []);

  return (
    <div className="ac-map" style={{ height, position: 'relative' }}>
      <MapContainer
        center={[centerLat, centerLng]}
        zoom={activeZoom}
        scrollWheelZoom={false}
        style={{ height: '100%', width: '100%' }}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://tile.openstreetmap.org/{z}/{x}/{y}.png"
        />

        {hasCoords && (
          <Marker
            position={[lat, lng]}
            icon={storeIcon}
            draggable={editable}
            eventHandlers={
              editable
                ? {
                    dragend: (e) => {
                      const p = e.target.getLatLng();
                      onChange(+p.lat.toFixed(6), +p.lng.toFixed(6));
                    },
                  }
                : {}
            }
          />
        )}

        {editable && <Picker onChange={onChange} />}
        {hasCoords && <Recenter lat={lat} lng={lng} zoom={zoom} />}
      </MapContainer>

      {!hasCoords && editable && (
        <div
          style={{
            position: 'absolute',
            bottom: 12,
            left: 12,
            right: 12,
            background: 'rgba(15, 23, 42, 0.85)',
            color: '#fff',
            padding: '8px 14px',
            borderRadius: 8,
            fontSize: 13,
            zIndex: 1000,
            textAlign: 'center',
            backdropFilter: 'blur(4px)',
            pointerEvents: 'none',
          }}
        >
          📍 Enter your store PIN code or click anywhere on the map to place your AutoCART store pin.
        </div>
      )}
    </div>
  );
}

/** Looks up details for a 6-digit Indian PIN code using backend location service. */
export async function lookupPincode(pincode, addressContext = '') {
  const cleanPin = (pincode || '').trim();
  if (!cleanPin || !/^[1-9]\d{5}$/.test(cleanPin)) {
    throw new Error('Please enter a valid 6-digit Indian PIN code.');
  }
  try {
    const params = { pincode: cleanPin };
    if (addressContext) {
      params.address = addressContext;
    }
    const res = await api.get('/location/pincode-lookup', { params });
    if (!res?.data || typeof res.data !== 'object') {
      throw new Error('Unable to resolve this PIN code right now. Please retry or enter the location manually.');
    }
    return res.data;
  } catch (err) {
    if (err.response) {
      const data = err.response.data;
      if (typeof data === 'object' && data?.detail) {
        throw new Error(data.detail);
      }
    }
    throw new Error('Unable to resolve this PIN code right now. Please retry or enter the location manually.');
  }
}

/** Resolves coordinates to locality and postal details using backend reverse geocode. */
export async function reverseGeocode(lat, lng) {
  if (lat == null || lng == null || isNaN(lat) || isNaN(lng)) return null;
  try {
    const res = await api.get('/location/reverse-geocode', {
      params: { lat, lng },
    });
    return res?.data || null;
  } catch {
    return null;
  }
}

/** Finds a place on the map from an address using OpenStreetMap search. */
export async function findOnMap(query) {
  try {
    const url = `https://nominatim.openstreetmap.org/search?format=json&limit=1&countrycodes=in&q=${encodeURIComponent(query)}`;
    const res = await fetch(url, { headers: { Accept: 'application/json' } });
    const rows = await res.json();
    return rows[0] ? { lat: +parseFloat(rows[0].lat).toFixed(6), lng: +parseFloat(rows[0].lon).toFixed(6) } : null;
  } catch {
    return null;
  }
}

/** High-precision geocoder with backend known database + OSM fallback. */
export async function geocodeAddress(query, pincode = '', city = '') {
  const cleanQ = (query || '').trim();
  if (!cleanQ && !pincode) return null;
  try {
    const res = await api.get('/location/geocode', {
      params: { q: cleanQ, pincode, city },
    });
    if (res?.data?.success && res.data.latitude && res.data.longitude) {
      return { lat: +res.data.latitude, lng: +res.data.longitude, area: res.data.area };
    }
  } catch (err) {
    console.debug('Backend geocode error, trying OSM fallback:', err);
  }
  return findOnMap(cleanQ + (city ? `, ${city}` : '') + (pincode ? `, ${pincode}` : ''));
}

