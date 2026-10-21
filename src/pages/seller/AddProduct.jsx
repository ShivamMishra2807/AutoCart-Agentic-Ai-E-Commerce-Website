import React, { useEffect, useState } from 'react';
import { ImagePlus, Plus } from 'lucide-react';
import api from '../../services/api';

const CATS = ['Electronics', 'Fashion', 'Home & Kitchen', 'Beauty & Personal Care', 'Sports & Fitness', 'Books & Stationery', 'Grocery & Gourmet', 'Toys & Baby Care'];
const EMPTY = { name: '', category: CATS[0], brand: '', price: '', stock: '', description: '', autoRestock: false, reorderLevel: '5', restockQty: '20' };

/** List a new product with a photo. It starts with no rating or reviews; those have to be earned from real buyers. */
export default function AddProduct({ onAdded }) {
  const [f, setF] = useState(EMPTY);
  const [photo, setPhoto] = useState(null);
  const [preview, setPreview] = useState('');
  const [msg, setMsg] = useState('');
  const [errs, setErrs] = useState({});
  const set = (k) => (e) => { const v = e.target.value; setF((x) => ({ ...x, [k]: v })); }; // read the value now, not later inside the updater
  useEffect(() => { if (!photo) { setPreview(''); return undefined; } const u = URL.createObjectURL(photo); setPreview(u); return () => URL.revokeObjectURL(u); }, [photo]);

  const submit = async (e) => {
    e.preventDefault(); setErrs({}); setMsg('');
    const body = new FormData();
    Object.entries(f).forEach(([k, v]) => body.append(k, v));
    if (photo) body.append('image', photo);
    try {
      const { data } = await api.post('/seller/products', body);
      setMsg(`${data.name} is now live in the store.`); setF(EMPTY); setPhoto(null); onAdded?.();
    } catch (err) {
      setErrs(err?.response?.data?.errors || {}); setMsg(err?.response?.data?.detail || 'That did not save.');
    }
  };
  const field = (k, label, props = {}) => (
    <div><label htmlFor={`ap-${k}`}>{label}</label>
      <input id={`ap-${k}`} className="ac-input" value={f[k]} onChange={set(k)} aria-invalid={!!errs[k]} {...props} />
      {errs[k] && <small role="alert" style={{ color: 'var(--coral)' }}>{errs[k]}</small>}</div>
  );
  return (
    <details className="ac-box" style={{ marginTop: 24 }}>
      <summary style={{ cursor: 'pointer', fontWeight: 700 }}><Plus size={16} style={{ verticalAlign: '-3px' }} /> Add a product</summary>
      <form onSubmit={submit} style={{ display: 'grid', gap: 12, marginTop: 14, maxWidth: 620 }}>
        <div>
          <label htmlFor="ap-image">Product photo</label>
          <label className="ac-dropzone" htmlFor="ap-image">
            {preview ? <img src={preview} alt="Preview of your photo" /> : <span><ImagePlus size={26} /><b>Choose a photo</b><small>JPG, PNG or WebP, up to 5 MB. A clear photo on a plain background sells best.</small></span>}
          </label>
          <input id="ap-image" type="file" accept="image/*" hidden onChange={(e) => setPhoto(e.target.files?.[0] || null)} />
          {errs.image && <small role="alert" style={{ color: 'var(--coral)' }}>{errs.image}</small>}
        </div>
        {field('name', 'Product name')}
        <div><label htmlFor="ap-category">Category</label>
          <select id="ap-category" className="ac-input" value={f.category} onChange={set('category')}>{CATS.map((c) => <option key={c}>{c}</option>)}</select></div>
        {field('brand', 'Brand (optional)')}
        {field('price', 'Price (₹)', { inputMode: 'decimal' })}
        {field('stock', 'Units in stock', { inputMode: 'numeric' })}
        <div><label htmlFor="ap-description">Description (optional)</label>
          <textarea id="ap-description" className="ac-input" rows={3} value={f.description} onChange={set('description')} /></div>
        <label className="ac-switch"><input type="checkbox" checked={f.autoRestock} onChange={(e) => setF((x) => ({ ...x, autoRestock: e.target.checked }))} /><span>Auto-restock after sales</span></label>
        {f.autoRestock && (
          <p className="ac-muted">After a sale, if stock is at or below <input className="ac-input ac-mini-input" value={f.reorderLevel} onChange={set('reorderLevel')} aria-label="Reorder level" /> units, add <input className="ac-input ac-mini-input" value={f.restockQty} onChange={set('restockQty')} aria-label="Units to add" /> units. Use this only if your supplier reliably tops you up.</p>
        )}
        <button className="ac-btn ac-btn-blue" style={{ justifySelf: 'start' }}>Add product</button>
        {msg && <p role="status">{msg}</p>}
      </form>
    </details>
  );
}
