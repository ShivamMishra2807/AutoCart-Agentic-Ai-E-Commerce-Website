import React, { useEffect } from 'react';
import { Link, Navigate, useLocation } from 'react-router-dom';
import { CheckCircle2 } from 'lucide-react';
import { money } from '../../storefront/parts';
import '../../storefront/storefront.css';
import '../../storefront/forms.css';
import '../../storefront/pages.css';

export const OrderSuccess = () => {
  const { state } = useLocation();
  const order = state?.order;
  useEffect(() => { document.title = 'Order placed | AutoCart'; }, []);
  if (!order) return <Navigate to="/orders" replace />;
  const paid = order.paymentStatus === 'Paid';
  return (
    <div className="ac ac-page"><div className="ac-wrap" style={{ maxWidth: 620, textAlign: 'center', padding: '40px 0' }}>
      <CheckCircle2 size={64} color="var(--ok)" className="ac-pop" />
      <h1 className="ac-display" style={{ marginTop: 16 }}>{paid ? 'Payment received' : 'Order placed'}</h1>
      <p className="ac-sub" style={{ margin: '12px auto' }}>Thank you. Your order <b>{order.id}</b> is {paid ? 'paid and confirmed' : 'confirmed'}.</p>
      <div className="ac-box" style={{ textAlign: 'left', marginTop: 24 }}>
        <dl className="ac-sum">
          <div><dt>Total</dt><dd>{money(order.totalAmount)}</dd></div>
          <div><dt>Payment</dt><dd>{order.paymentMethod}</dd></div>
          <div><dt>Payment status</dt><dd>{order.paymentStatus}{!paid ? ' (you pay on receipt)' : ''}</dd></div>
          {order.shippingAddress?.storeName && <div><dt>Store</dt><dd>{order.shippingAddress.storeName}</dd></div>}
        </dl>
      </div>
      <div className="ac-row" style={{ justifyContent: 'center', marginTop: 24 }}>
        <Link to={`/orders/${order.id}`} className="ac-btn ac-btn-blue">Track this order</Link>
        <Link to="/catalog" className="ac-btn ac-btn-outline">Keep shopping</Link>
      </div>
    </div></div>
  );
};

export default OrderSuccess;
