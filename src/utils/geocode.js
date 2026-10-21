/**
 * Turn GPS coordinates into a street address with free OpenStreetMap (Nominatim) search.
 * Called only when the customer asks to use their location. Returns null if the service cannot be reached.
 */
export async function reverseGeocode(lat, lng) {
  try {
    const res = await fetch(`https://nominatim.openstreetmap.org/reverse?format=jsonv2&addressdetails=1&zoom=18&lat=${lat}&lon=${lng}`, { headers: { Accept: 'application/json' } });
    if (!res.ok) return null;
    const a = (await res.json()).address || {};
    const area = a.suburb || a.neighbourhood || a.city_district || a.quarter || '';
    const line = [a.house_number, a.road, area].filter(Boolean).join(', ');
    const city = a.city || a.town || a.village || a.county || a.state_district || '';
    return { line, area, city, state: a.state || '', pincode: (a.postcode || '').replace(/\D/g, '').slice(0, 6) };
  } catch {
    return null;
  }
}
