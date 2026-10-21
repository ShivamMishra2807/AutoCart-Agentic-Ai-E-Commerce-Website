import React, { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Minus, Plus, Trash2, ShoppingBag, Tag, Truck } from 'lucide-react';
import { useCart } from '../../hooks/useCart';
import { money, sized, firstImage } from '../../storefront/parts';
import '../../storefront/storefront.css';
import '../../storefront/forms.css';
import '../../storefront/pages.css';

export const Cart = () => {
  const { cartItems, updateQuantity, removeFromCart, clearCart, subtotal, discountAmount, deliveryCharge, finalTotal, coupon, applyCoupon, removeCoupon } = useCart();
  const navigate = useNavigate();
  const [code, setCode] = useState('');
  const [couponError, setCouponError] = useState('');
  const [busy, setBusy] = useState(false);

  useEffect(() => { document.title = 'Your cart | AutoCart'; }, []);

  const apply = async (e) => {
    e.preventDefault();
    if (!code.trim()) return;
    setBusy(true); setCouponError('');
    try { await applyCoupon(code.trim()); setCode(''); } catch (err) { setCouponError(err?.response?.data?.detail || 'That coupon could not be applied.'); }
    setBusy(false);
  };

  if (cartItems.length === 0) {
    return (
      <div className="ac ac-page"><div className="ac-wrap" style={{ maxWidth: 640, textAlign: 'center', padding: '60px 0' }}>
        <ShoppingBag size={56} color="var(--brand)" />
        <h1 className="ac-display" style={{ marginTop: 16 }}>Your cart is empty</h1>
        <p className="ac-sub" style={{ margin: '12px auto 24px' }}>Add something you like and it will wait for you here.</p>
        <Link to="/catalog" className="ac-btn ac-btn-blue">Browse everything we sell</Link>
      </div></div>
    );
  }

  const toFree = Math.max(0, 500 - subtotal);
  return (
    <div className="ac ac-page"><div className="ac-wrap">
      <div className="ac-row-between"><h1 className="ac-display">Your cart</h1><button className="ac-btn ac-btn-outline ac-btn-small" onClick={clearCart}>Empty cart</button></div>
      <div className="ac-twocol" style={{ marginTop: 28 }}>
        <div>
          {cartItems.map((it) => (
            <div className="ac-cart-row" key={it.id}>
              <Link to={`/products/${it.id}`} className="ac-cart-img"><img src={sized(firstImage(it), 240)} alt={it.name} /></Link>
              <div style={{ minWidth: 0 }}>
                <div className="ac-brand">{it.brand || it.category}</div>
                <Link to={`/products/${it.id}`} className="ac-name" style={{ minHeight: 0 }}>{it.name}</Link>
                <div className="ac-price"><b>{money(it.price)}</b></div>
                <div className="ac-row" style={{ marginTop: 10 }}>
                  <div className="ac-qty" role="group" aria-label={`Quantity for ${it.name}`}>
                    <button onClick={() => updateQuantity(it.id, it.quantity - 1)} aria-label="One less"><Minus size={16} /></button>
                    <span aria-live="polite">{it.quantity}</span>
                    <button onClick={() => updateQuantity(it.id, it.quantity + 1)} aria-label="One more" disabled={it.quantity >= 20}><Plus size={16} /></button>
                  </div>
                  <button className="ac-textlink" style={{ border: 0, background: 'none' }} onClick={() => removeFromCart(it.id)}><Trash2 size={14} /> Remove</button>
                </div>
              </div>
              <b className="ac-line-total">{money(it.price * it.quantity)}</b>
            </div>
          ))}
        </div>

        <aside className="ac-box ac-summary" aria-label="Order summary">
          <h2>Summary</h2>
          {toFree > 0 ? (
            <div style={{ margin: '12px 0 4px' }}>
              <small className="ac-muted"><Truck size={14} /> Add {money(toFree)} more for free delivery</small>
              <div className="ac-progress"><i style={{ width: `${Math.min(100, (subtotal / 500) * 100)}%` }} /></div>
            </div>
          ) : <p className="ac-chip-status" data-tone="ok" style={{ margin: '12px 0' }}><Truck size={13} /> &nbsp;Free delivery</p>}

          <dl className="ac-sum">
            <div><dt>Subtotal</dt><dd>{money(subtotal)}</dd></div>
            {discountAmount > 0 && <div><dt>Coupon {coupon?.code}</dt><dd style={{ color: 'var(--ok)' }}>-{money(discountAmount)}</dd></div>}
            <div><dt>Delivery</dt><dd>{deliveryCharge ? money(deliveryCharge) : 'Free'}</dd></div>
            <div className="ac-sum-total"><dt>Total</dt><dd>{money(finalTotal)}</dd></div>
          </dl>
          <p className="ac-muted" style={{ fontSize: 14, margin: '0 0 14px' }}>The final price is confirmed by our server when you place the order.</p>

          {coupon ? (
            <div className="ac-row-between ac-coupon-on"><span><Tag size={14} /> {coupon.code} applied</span><button className="ac-textlink" style={{ border: 0, background: 'none' }} onClick={removeCoupon}>Remove</button></div>
          ) : (
            <form onSubmit={apply} className="ac-coupon">
              <label className="ac-sr" htmlFor="coupon">Coupon code</label>
              <input id="coupon" className="ac-input" placeholder="Coupon code" value={code} onChange={(e) => setCode(e.target.value.toUpperCase())} />
              <button className="ac-btn ac-btn-outline ac-btn-small" disabled={busy || !code.trim()}>Apply</button>
            </form>
          )}
          {couponError && <div className="ac-warn" role="alert">{couponError}</div>}
          <button className="ac-btn ac-btn-blue" style={{ width: '100%', marginTop: 18 }} onClick={() => navigate('/checkout')}>Checkout</button>
        </aside>
      </div>
    </div></div>
  );
};

export default Cart;
