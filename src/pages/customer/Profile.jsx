import React, { useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Package, Heart, LifeBuoy, Store, LogOut } from 'lucide-react';
import { useAuth } from '../../hooks/useAuth';
import { money } from '../../storefront/parts';
import '../../storefront/storefront.css';
import '../../storefront/forms.css';
import '../../storefront/pages.css';

export const Profile = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  useEffect(() => { document.title = 'Your account | AutoCart'; }, []);
  if (!user) return null;
  const links = [
    { to: '/orders', icon: Package, title: 'Your orders', text: 'Track, cancel or return an order.' },
    { to: '/wishlist', icon: Heart, title: 'Wishlist', text: 'Products you saved for later.' },
    { to: '/support', icon: LifeBuoy, title: 'Help and tickets', text: 'Questions and support replies.' },
    user.role === 'SELLER' ? { to: '/seller/dashboard', icon: Store, title: 'Seller dashboard', text: 'Questions about your products.' }
      : { to: '/seller/apply', icon: Store, title: 'Sell on AutoCart', text: 'Open a store on AutoCart.' },
  ];
  return (
    <div className="ac ac-page"><div className="ac-wrap" style={{ maxWidth: 860 }}>
      <div className="ac-box ac-profile">
        <div className="ac-avatar" aria-hidden="true">{user.name?.[0]?.toUpperCase()}</div>
        <div style={{ flex: 1, minWidth: 0 }}>
          <h1 className="ac-display" style={{ fontSize: 34 }}>{user.name}</h1>
          <div className="ac-muted">{user.email}{user.phone ? ` · ${user.phone}` : ''}</div>
          <div className="ac-row" style={{ marginTop: 10 }}><span className="ac-chip-status" data-tone="info">{user.role === 'SELLER' ? 'Seller' : user.role === 'ADMIN' ? 'Administrator' : 'Customer'}</span>
            {user.ordersCount != null && <span className="ac-muted" style={{ fontSize: 14 }}>{user.ordersCount} orders · {money(user.totalSpent || 0)} spent</span>}</div>
        </div>
        <button className="ac-btn ac-btn-outline ac-btn-small" onClick={() => { logout(); navigate('/'); }}><LogOut size={16} /> Sign out</button>
      </div>
      <div className="ac-grid-2" style={{ marginTop: 20 }}>
        {links.map((l) => (
          <Link to={l.to} key={l.to} className="ac-box ac-linkcard"><l.icon size={26} color="var(--brand)" /><div><b>{l.title}</b><div className="ac-muted" style={{ fontSize: 14 }}>{l.text}</div></div></Link>
        ))}
      </div>
    </div></div>
  );
};

export default Profile;
