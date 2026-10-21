/**
 * One source of colour for the whole site (Sunset). To change the look, edit the colours below.
 * applyTheme() writes CSS variables on <html>. The storefront styles read --t-*, and the older Tailwind pages
 * (admin, seller dashboard) read --ix-* / --px-* through the indigo and purple scales in tailwind.config.js.
 * The choice is remembered in the browser. It runs at start-up, before the page draws, so there is no flash.
 */

const KEY = 'autocart_theme_v2';

const hex = (h) => { const n = parseInt(h.slice(1), 16); return [(n >> 16) & 255, (n >> 8) & 255, n & 255]; };
const mix = (a, b, t) => a.map((v, i) => Math.round(v + (b[i] - v) * t));
const scale = (base) => {
  const c = hex(base); const W = [255, 255, 255]; const K = [0, 0, 0];
  return { 50: mix(c, W, 0.93), 100: mix(c, W, 0.85), 200: mix(c, W, 0.7), 300: mix(c, W, 0.5), 400: mix(c, W, 0.25), 500: mix(c, W, 0.1),
    600: c, 700: mix(c, K, 0.15), 800: mix(c, K, 0.3), 900: mix(c, K, 0.45), 950: mix(c, K, 0.6) };
};

export const THEMES = {
  sunset: {
    label: 'Sunset', swatch: 'linear-gradient(135deg, #d9480f 50%, #ffd9b8 50%)', tw: '#d9480f',
    brand: '#d9480f', dark: '#b83a08', soft: '#ffeddf', ink: '#b83a08', on: '#ffffff', fog: '#fbf6f1', line: '#f0e4d8', wash: '#fff1e6',
    d1: '#ffd9b8', d2: '#ffc08a', d3: '#f7e3b0', s1: '#f06a2a', s2: '#ffd36a',
    tones: ['#ffe8d6', '#fff1d9', '#fde3d0', '#f9ecd7', '#ffe2cf', '#f6e7dc', '#fdeccd', '#ffe9dd'],
  },
};
export const DEFAULT_THEME = 'sunset';

export const getThemeKey = () => { try { const k = localStorage.getItem(KEY); return THEMES[k] ? k : DEFAULT_THEME; } catch { return DEFAULT_THEME; } };
export const getTheme = () => THEMES[getThemeKey()];
export const themeColor = (name) => getTheme()[name];

export function applyTheme(key = getThemeKey()) {
  const t = THEMES[key] || THEMES[DEFAULT_THEME];
  const root = document.documentElement;
  const set = (k, v) => root.style.setProperty(k, v);
  set('--t-brand', t.brand); set('--t-dark', t.dark); set('--t-soft', t.soft); set('--t-ink', t.ink); set('--t-on', t.on);
  set('--t-fog', t.fog); set('--t-line', t.line); set('--t-wash', t.wash); set('--t-rgb', hex(t.brand).join(', '));
  set('--t-d1', t.d1); set('--t-d2', t.d2); set('--t-d3', t.d3); set('--t-s1', t.s1); set('--t-s2', t.s2);
  const a = scale(t.tw); const b = scale(mix(hex(t.tw), [255, 255, 255], 0.18).reduce((s, v) => s + v.toString(16).padStart(2, '0'), '#'));
  Object.entries(a).forEach(([n, rgb]) => set(`--ix-${n}`, rgb.join(' ')));
  Object.entries(b).forEach(([n, rgb]) => set(`--px-${n}`, rgb.join(' ')));
  root.dataset.acTheme = key;
}

export function chooseTheme(key) {
  try { localStorage.setItem(KEY, key); } catch { /* storage may be blocked */ }
  applyTheme(key);
}

applyTheme();
