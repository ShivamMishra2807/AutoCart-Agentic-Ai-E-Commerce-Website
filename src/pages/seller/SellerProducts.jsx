import React, { useRef, useState } from 'react';
import { Link } from 'react-router-dom';
import { Camera, Check, History, Zap } from 'lucide-react';
import api from '../../services/api';
import { sized } from '../../storefront/parts';

const REASON = { sale: 'Sold to a customer', manual: 'You changed it', 'auto-restock': 'Auto-restock rule', 'cancelled-order': 'Order cancelled' };

/** One product: photo, price, stock (manual), and an auto-restock rule (automatic). */
function Row({ p, onChanged, flash }) {
  const [price, setPrice] = useState(String(p.price));
  const [cost, setCost] = useState(p.costPrice ? String(p.costPrice) : '');
  const [stock, setStock] = useState(String(p.stock));
  const [auto, setAuto] = useState(!!p.autoRestock);
  const [level, setLevel] = useState(String(p.reorderLevel ?? 5));
  const [qty, setQty] = useState(String(p.restockQty ?? 20));
  const [open, setOpen] = useState(false);
  const [history, setHistory] = useState(null);
  const [err, setErr] = useState({});
  const file = useRef(null);

  const dirty = cost !== (p.costPrice ? String(p.costPrice) : '') || price !== String(p.price) || stock !== String(p.stock) || auto !== !!p.autoRestock || level !== String(p.reorderLevel ?? 5) || qty !== String(p.restockQty ?? 20);
  const save = async (extra = {}) => {
    setErr({});
    try {
      await api.patch(`/seller/products/${p.id}`, { price, costPrice: cost || 0, stock, autoRestock: auto, reorderLevel: level, restockQty: qty, ...extra });
      flash(`${p.name} updated.`); onChanged();
    } catch (e) { setErr(e?.response?.data?.errors || {}); flash(e?.response?.data?.detail || 'That did not save.'); }
  };
  const photo = (f) => {
    if (!f) return;
    const body = new FormData(); body.append('image', f);
    api.patch(`/seller/products/${p.id}`, body).then(() => { flash('Photo updated.'); onChanged(); })
      .catch((e) => flash(e?.response?.data?.errors?.image || e?.response?.data?.detail || 'The photo did not upload.'));
  };
  const showHistory = async () => {
    setOpen((o) => !o);
    if (!history) { try { setHistory((await api.get(`/seller/products/${p.id}/stock-log`)).data.history); } catch { setHistory([]); } }
  };
  const bump = (n) => setStock(String(Math.max(0, (parseInt(stock, 10) || 0) + n)));

  return (
    <article className="ac-prodrow">
      <div className="ac-prodrow-main">
        <div className="ac-prodcell">
          <button type="button" className="ac-photo" onClick={() => file.current?.click()} aria-label={`Change photo of ${p.name}`} title="Change photo">
            {p.image ? <img src={sized(p.image, 120)} alt="" /> : <span><Camera size={20} /><small>Add photo</small></span>}
          </button>
          <input ref={file} type="file" accept="image/*" hidden onChange={(e) => photo(e.target.files?.[0])} />
          <div style={{ minWidth: 0 }}>
            <Link to={`/products/${p.id}`} className="ac-prodname">{p.name}</Link>
            <small className="ac-muted">{Number(p.rating || 0).toFixed(1)} ★ · {p.reviewCount} reviews</small>
          </div>
        </div>
        <label className="ac-fld"><span>Price (₹)</span><input className="ac-input ac-cell-input" inputMode="decimal" value={price} onChange={(e) => setPrice(e.target.value)} aria-invalid={!!err.price} /></label>
        <label className="ac-fld"><span>Cost price (₹)</span><input className="ac-input ac-cell-input" inputMode="decimal" placeholder="for profit" value={cost} onChange={(e) => setCost(e.target.value)} aria-invalid={!!err.costPrice} /></label>
        <div className="ac-fld"><span>Stock (manual)</span>
          <div className="ac-stepper">
            <button type="button" onClick={() => bump(-1)} aria-label="One less">−</button>
            <input className="ac-input ac-cell-input" inputMode="numeric" value={stock} onChange={(e) => setStock(e.target.value)} aria-label={`Stock of ${p.name}`} aria-invalid={!!err.stock} />
            <button type="button" onClick={() => bump(1)} aria-label="One more">+</button>
            <button type="button" onClick={() => bump(10)} aria-label="Ten more">+10</button>
          </div>
          {p.stock <= 0 ? <small className="ac-warn">Out of stock</small> : p.stock <= 10 ? <small className="ac-warn">Almost gone</small> : null}
        </div>
        <label className="ac-switch" title="Automatic: AutoCart tops up your stock after a sale brings it down to your reorder level">
          <input type="checkbox" checked={auto} onChange={(e) => setAuto(e.target.checked)} /><span><Zap size={15} /> Auto-restock</span>
        </label>
        <div className="ac-row" style={{ gap: 8 }}>
          {dirty && <button className="ac-btn ac-btn-blue ac-btn-small" onClick={() => save()}>Save</button>}
          <button className="ac-btn ac-btn-soft ac-btn-small" onClick={showHistory} aria-expanded={open}><History size={15} /> History</button>
        </div>
      </div>
      {(auto || open) && (
        <div className="ac-prodrow-more">
          {auto && (
            <div className="ac-autobox">
              <b>Automatic restock</b>
              <p className="ac-muted">After a sale, if stock is at or below <input className="ac-input ac-mini-input" inputMode="numeric" value={level} onChange={(e) => setLevel(e.target.value)} aria-label="Reorder level" aria-invalid={!!err.reorderLevel} /> units,
                add <input className="ac-input ac-mini-input" inputMode="numeric" value={qty} onChange={(e) => setQty(e.target.value)} aria-label="Units to add" aria-invalid={!!err.restockQty} /> units.</p>
              <small className="ac-muted">Use this only if your supplier reliably tops you up by that amount. AutoCart adds the units to your shelf count and logs it in History.</small>
              {(err.reorderLevel || err.restockQty) && <small role="alert" style={{ color: 'var(--coral)' }}>{err.reorderLevel || err.restockQty}</small>}
            </div>
          )}
          {open && (
            <div className="ac-histbox">
              <b>Stock history</b>
              {!history ? <p className="ac-muted">Loading…</p> : history.length === 0 ? <p className="ac-muted">No changes recorded yet.</p> : (
                <ul>{history.map((h, i) => <li key={i}><span className={h.change > 0 ? 'up' : 'down'}>{h.change > 0 ? '+' : ''}{h.change}</span> <span>{REASON[h.reason] || h.reason}</span> <small className="ac-muted">now {h.stockAfter} · {new Date(h.at).toLocaleString()}</small></li>)}</ul>
              )}
            </div>
          )}
        </div>
      )}
      {err.image && <small role="alert" style={{ color: 'var(--coral)' }}>{err.image}</small>}
    </article>
  );
}

export default function SellerProducts({ products, onChanged }) {
  const [saved, setSaved] = useState('');
  const flash = (t) => { setSaved(t); window.setTimeout(() => setSaved(''), 3000); };
  return (
    <section id="products" className="ac-box" aria-labelledby="prod-h" style={{ marginTop: 24 }}>
      <div className="ac-row-between"><h2 id="prod-h">Your products</h2>{saved && <span className="ac-chip-status" data-tone="ok" role="status"><Check size={13} />&nbsp;{saved}</span>}</div>
      <p className="ac-muted" style={{ marginTop: 4 }}>Change stock by hand any time, or switch on <b>Auto-restock</b> and AutoCart tops it up for you after sales.</p>
      <div style={{ display: 'grid', gap: 12, marginTop: 14 }}>{products.map((p) => <Row key={`${p.id}-${p.stock}-${p.price}-${p.image}`} p={p} onChanged={onChanged} flash={flash} />)}</div>
    </section>
  );
}
