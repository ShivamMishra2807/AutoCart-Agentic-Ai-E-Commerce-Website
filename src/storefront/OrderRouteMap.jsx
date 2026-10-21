import React, { useEffect, useState } from 'react';
import { MapContainer, Marker, Polyline, Popup, TileLayer, useMap } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import markerIcon from 'leaflet/dist/images/marker-icon.png';
import markerIcon2x from 'leaflet/dist/images/marker-icon-2x.png';
import markerShadow from 'leaflet/dist/images/marker-shadow.png';
import './storefront.css';

L.Icon.Default.mergeOptions({ iconUrl: markerIcon, iconRetinaUrl: markerIcon2x, shadowUrl: markerShadow });

const Fit = ({ points }) => {
  const map = useMap();
  useEffect(() => { map.fitBounds(points, { padding: [40, 40] }); }, [points, map]);
  return null;
};

/**
 * The road route from the store to the customer, on OpenStreetMap.
 * The route comes from the free public OSRM service; if it cannot be reached we draw a straight line and say so.
 */
export default function OrderRouteMap({ pickup, drop, height = 340 }) {
  const [route, setRoute] = useState(null); // { line, km, minutes } | { failed: true }
  const a = [pickup.lat, pickup.lng];
  const b = [drop.lat, drop.lng];

  useEffect(() => {
    let live = true;
    fetch(`https://router.project-osrm.org/route/v1/driving/${pickup.lng},${pickup.lat};${drop.lng},${drop.lat}?overview=full&geometries=geojson`)
      .then((r) => r.json())
      .then((d) => {
        const r = d?.routes?.[0];
        if (!live) return;
        setRoute(r ? { line: r.geometry.coordinates.map(([lng, lat]) => [lat, lng]), km: r.distance / 1000, minutes: Math.round(r.duration / 60) } : { failed: true });
      })
      .catch(() => live && setRoute({ failed: true }));
    return () => { live = false; };
  }, [pickup.lat, pickup.lng, drop.lat, drop.lng]);

  const line = route?.line || [a, b];
  const directions = `https://www.openstreetmap.org/directions?engine=fossgis_osrm_car&route=${pickup.lat}%2C${pickup.lng}%3B${drop.lat}%2C${drop.lng}`;
  return (
    <div>
      <div className="ac-map" style={{ height }}>
        <MapContainer center={a} zoom={13} scrollWheelZoom={false} style={{ height: '100%', width: '100%' }}>
          <TileLayer attribution="&copy; OpenStreetMap contributors" url="https://tile.openstreetmap.org/{z}/{x}/{y}.png" />
          <Polyline positions={line} pathOptions={{ color: '#d9480f', weight: 5, dashArray: route?.line ? undefined : '8 8' }} />
          <Marker position={a}><Popup><b>Pickup</b><br />{pickup.name}</Popup></Marker>
          <Marker position={b}><Popup><b>Deliver to</b><br />{drop.name}</Popup></Marker>
          <Fit points={[a, b]} />
        </MapContainer>
      </div>
      <p style={{ margin: '10px 0 0', fontWeight: 600 }} role="status">
        {route?.km ? `${route.km.toFixed(1)} km by road, about ${route.minutes} min.` : route?.failed ? 'Straight-line view only (the road routing service did not respond).' : 'Finding the best road route…'}
        {' '}<a href={directions} target="_blank" rel="noreferrer">Open turn-by-turn directions</a>
      </p>
      <p className="ac-muted" style={{ fontSize: 14, margin: '4px 0 0' }}>From {pickup.name}{pickup.address ? `, ${pickup.address}` : ''} to {drop.address || drop.name}.</p>
    </div>
  );
}
