import React, { useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Circle, useMap } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import './LocationPinMap';
import { themeColor } from './theme'; // loads the marker image fix once
import './storefront.css';

const pin = (color, big = false) => L.divIcon({
  className: 'ac-pin', html: `<span style="background:${color};${big ? 'width:34px;height:34px;' : ''}"></span>`,
  iconSize: big ? [34, 34] : [26, 26], iconAnchor: big ? [17, 34] : [13, 26], popupAnchor: [0, -26],
});
const youIcon = L.divIcon({ className: 'ac-pin', html: '<i class="ac-you"></i>', iconSize: [22, 22], iconAnchor: [11, 11] });

const Fit = ({ points }) => {
  const map = useMap();
  useEffect(() => {
    if (!points.length) return;
    map.fitBounds(L.latLngBounds(points), { padding: [40, 40], maxZoom: 14, animate: true });
  }, [points, map]);
  return null;
};

/** Real map of partner stores. Click a pin to see the store and choose it. `stores` need latitude and longitude. */
export default function StoreMap({ stores, customer, selectedId, onSelect, height = 420, radiusKm }) {
  const located = stores.filter((s) => Number.isFinite(s.latitude) && Number.isFinite(s.longitude));
  const points = [...located.map((s) => [s.latitude, s.longitude]), ...(customer ? [[customer.lat, customer.lng]] : [])];
  const center = customer ? [customer.lat, customer.lng] : [19.076, 72.8777];
  return (
    <div className="ac-map" style={{ height }}>
      <MapContainer center={center} zoom={12} scrollWheelZoom style={{ height: '100%', width: '100%' }}>
        <TileLayer attribution="&copy; OpenStreetMap contributors" url="https://tile.openstreetmap.org/{z}/{x}/{y}.png" />
        {customer && <Marker position={[customer.lat, customer.lng]} icon={youIcon}><Popup>Your location</Popup></Marker>}
        {customer && radiusKm && <Circle center={[customer.lat, customer.lng]} radius={radiusKm * 1000} pathOptions={{ color: themeColor('brand'), weight: 1, fillOpacity: 0.05 }} />}
        {located.map((s) => {
          const on = s.storeId === selectedId;
          return (
            <Marker key={s.storeId} position={[s.latitude, s.longitude]} icon={pin(on ? '#d63a17' : themeColor('brand'), on)} zIndexOffset={on ? 1000 : 0}
              eventHandlers={{ click: () => onSelect?.(s) }}>
              <Popup>
                <b>{s.storeName}</b><br />
                {s.address}<br />
                {s.distanceKm != null && <>{s.distanceKm} km away · about {s.estimatedMinutes} min<br /></>}
                {s.availableQuantity != null && s.productId ? <>{s.availableQuantity} in stock here<br /></>
                  : s.availableQuantity != null ? <>{s.availableQuantity} products in stock<br /></> : null}
                {onSelect && <button type="button" className="ac-pop-btn" onClick={() => onSelect(s, true)}>Choose this store</button>}
              </Popup>
            </Marker>
          );
        })}
        <Fit points={points} />
      </MapContainer>
    </div>
  );
}
