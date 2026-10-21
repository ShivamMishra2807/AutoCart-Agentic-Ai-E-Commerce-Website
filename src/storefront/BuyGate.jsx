import React, { useEffect, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { ShoppingBag, ShieldAlert, X } from 'lucide-react';
import { useAuth } from '../hooks/useAuth';
import './storefront.css';

/**
 * Only customer accounts can buy. When anyone else tries (add to cart or Buy now), this explains why:
 * a visitor is offered the customer sign-in; a seller or admin is told buying is for customers.
 * Cart code fires the 'autocart:buy-blocked' event; nothing here touches the cart itself.
 */
export default function BuyGate() {
  const [open, setOpen] = useState(null); // { role }
  const { logout } = useAuth();
  const navigate = useNavigate();
  const here = useLocation();

  useEffect(() => {
    const on = (e) => {
      if (!e.detail?.role) { navigate('/login', { state: { from: here, customerOnly: true } }); return; }  // a visitor: straight to the customer sign-in
      setOpen({ role: e.detail.role });
    };
    const resume = () => navigate('/checkout');  // signed in after pressing Buy now: carry on to checkout
    window.addEventListener('autocart:buy-blocked', on);
    window.addEventListener('autocart:resume-buy', resume);
    return () => { window.removeEventListener('autocart:buy-blocked', on); window.removeEventListener('autocart:resume-buy', resume); };
  }, [navigate, here]);
  useEffect(() => {
    if (!open) return undefined;
    const esc = (e) => { if (e.key === 'Escape') setOpen(null); };
    window.addEventListener('keydown', esc);
    return () => window.removeEventListener('keydown', esc);
  }, [open]);
  if (!open) return null;

  const guest = !open.role;
  const go = (path) => { setOpen(null); navigate(path, { state: { from: here, customerOnly: true } }); };
  return (
    <>
      <div className="ac-sc-back" style={{ zIndex: 120 }} onClick={() => setOpen(null)} aria-hidden="true" />
      <div role="dialog" aria-modal="true" aria-label={guest ? 'Sign in to buy' : 'Buying is for customers'} className="ac-gate">
        <button className="ac-sc-x" onClick={() => setOpen(null)} aria-label="Close" style={{ position: 'absolute', top: 14, right: 14 }}><X size={18} /></button>
        <span className="ac-gate-ico">{guest ? <ShoppingBag size={26} /> : <ShieldAlert size={26} />}</span>
        {guest ? (
          <>
            <h2>Sign in to buy</h2>
            <p className="ac-muted">Use your customer account to add items and check out. It only takes a moment.</p>
            <button className="ac-btn ac-btn-blue" onClick={() => go('/login')}>Sign in as a customer</button>
            <button className="ac-btn ac-btn-outline" onClick={() => go('/register')}>Create a customer account</button>
          </>
        ) : (
          <>
            <h2>Buying is for customer accounts</h2>
            <p className="ac-muted">You are signed in as {open.role === 'SELLER' ? 'a seller' : 'an administrator'}. Seller and admin accounts cannot place orders. To shop, sign out and use a customer account.</p>
            <button className="ac-btn ac-btn-blue" onClick={() => { logout(); go('/login'); }}>Sign out and shop as a customer</button>
            <button className="ac-btn ac-btn-outline" onClick={() => setOpen(null)}>Stay here</button>
          </>
        )}
      </div>
    </>
  );
}
