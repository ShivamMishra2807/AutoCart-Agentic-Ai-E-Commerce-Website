import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { PackageSearch } from 'lucide-react';
import orderService from '../../services/orderService';
import { money, sized, firstImage } from '../../storefront/parts';
import '../../storefront/storefront.css';
import '../../storefront/forms.css';
import '../../storefront/pages.css';

export const statusTone = (s) => (['Delivered', 'Completed', 'Picked up'].includes(s) ? 'ok' : ['Cancelled', 'Failed'].includes(s) ? 'bad' : ['Pending', 'Awaiting Payment'].includes(s) ? 'warn' : 'info');

export const Orders = () => {
  const [orders, setOrders] = useState(null);
  const [error, setError] = useState('');
  useEffect(() => {
    document.title = 'Your orders | AutoCart';
    orderService.getUserOrders().then(setOrders).catch(() => setError('We could not load your orders.'));
  }, []);

  return (
    <div className="ac ac-page"><div className="ac-wrap" style={{ maxWidth: 900 }}>
      <h1 className="ac-display">Your orders</h1>
      {error && <div className="ac-box" role="alert" style={{ marginTop: 20, borderColor: 'var(--coral)' }}>{error}</div>}
      {!orders && !error && <div className="ac-skel" style={{ height: 160, marginTop: 24 }} />}
      {orders && orders.length === 0 && (
        <div className="ac-box" style={{ marginTop: 24, textAlign: 'center', padding: 48 }}>
          <PackageSearch size={44} color="var(--brand)" />
          <h2 style={{ marginTop: 12 }}>No orders yet</h2>
          <p className="ac-muted">When you place an order it shows up here, with live tracking.</p>
          <Link to="/catalog" className="ac-btn ac-btn-blue ac-btn-small">Start shopping</Link>
        </div>
      )}
      {orders?.map((o) => (
        <Link to={`/orders/${o.id}`} key={o.id} className="ac-box ac-order-card" style={{ display: 'block', marginTop: 16 }}>
          <div className="ac-row-between">
            <div><b>Order {o.id}</b><div className="ac-muted" style={{ fontSize: 14 }}>{o.date} · {o.items?.length || 0} item{o.items?.length === 1 ? '' : 's'}</div></div>
            <div className="ac-row"><span className="ac-chip-status" data-tone={statusTone(o.status)}>{o.status}</span><span className="ac-chip-status" data-tone={statusTone(o.paymentStatus === 'Paid' ? 'Delivered' : o.paymentStatus)}>{o.paymentStatus}</span></div>
          </div>
          <div className="ac-row" style={{ margin: '14px 0', gap: 8 }}>
            {(o.items || []).slice(0, 5).map((i) => <img key={i.id} src={sized(firstImage(i), 120)} alt={i.name} className="ac-thumb" />)}
          </div>
          <div className="ac-row-between"><span className="ac-muted">{o.paymentMethod}</span><b style={{ fontSize: 18 }}>{money(o.totalAmount)}</b></div>
        </Link>
      ))}
    </div></div>
  );
};

export default Orders;
