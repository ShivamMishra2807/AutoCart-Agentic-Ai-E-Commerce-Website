import React from 'react';
import { useNavigate } from 'react-router-dom';
import { LogOut } from 'lucide-react';
import { useAuth } from '../../hooks/useAuth';
import { BrandLink } from '../../storefront/Brand';
import '../../storefront/storefront.css';
import '../../storefront/forms.css';
import '../../storefront/pages.css';

/** The frame for the seller sign-up flow: seller branding only. No customer shop header, cart or shopper account menu. */
export default function SellerShell({ children }) {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  return (
    <div className="ac ac-seller">
      <header className="ac-sc-top">
        <div className="ac-wrap ac-row-between" style={{ paddingBlock: 14 }}>
          <div className="ac-row" style={{ gap: 18 }}><BrandLink size={30} /><span className="ac-chip-status" data-tone="info">Seller application</span></div>
          <div className="ac-row">
            {user && <span className="ac-muted" style={{ fontSize: 14 }}>{user.name} · {user.email}</span>}
            {user
              ? <button className="ac-btn ac-btn-outline ac-btn-small" onClick={() => { logout(); navigate('/seller/login'); }}><LogOut size={15} /> Sign out</button>
              : <button className="ac-btn ac-btn-outline ac-btn-small" onClick={() => navigate('/seller/login')}>Seller sign in</button>}
          </div>
        </div>
      </header>
      {children}
    </div>
  );
}
