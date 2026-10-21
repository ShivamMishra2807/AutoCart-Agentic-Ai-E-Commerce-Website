import React from 'react';
import { Link } from 'react-router-dom';
import { ShoppingBag, Store, ShieldCheck } from 'lucide-react';

const TABS = [
  { id: 'customer', to: '/login', label: 'Customer', icon: ShoppingBag },
  { id: 'seller', to: '/seller/login', label: 'Seller', icon: Store },
  { id: 'admin', to: '/admin/login', label: 'Admin', icon: ShieldCheck },
];

/** Three separate sign-in pages, one per kind of user. This bar only links between them; it never mixes their forms. */
export default function RoleTabs({ current }) {
  return (
    <nav aria-label="Choose how you sign in" style={{ display: 'flex', gap: 6, padding: 5, background: '#f6efe8', borderRadius: 16, marginBottom: 18 }}>
      {TABS.map((t) => (
        <Link key={t.id} to={t.to} aria-current={current === t.id ? 'page' : undefined}
          style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 7, padding: '10px 8px', borderRadius: 12, fontWeight: 700, fontSize: 14,
            textDecoration: 'none', background: current === t.id ? '#fff' : 'transparent', color: current === t.id ? '#b83a08' : '#6b5a4d',
            boxShadow: current === t.id ? '0 2px 8px rgba(120,60,20,.15)' : 'none' }}>
          <t.icon size={16} /> {t.label}
        </Link>
      ))}
    </nav>
  );
}
