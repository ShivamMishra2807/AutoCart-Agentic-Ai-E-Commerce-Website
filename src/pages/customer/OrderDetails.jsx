import React, { useCallback, useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { Check, Circle } from 'lucide-react';
import api from '../../services/api';
import { useAuth } from '../../hooks/useAuth';
import OrderRouteMap from '../../storefront/OrderRouteMap';
import StoreMap from '../../storefront/StoreMap';
import UpiPay from '../../storefront/UpiPay';
import { money, sized, firstImage } from '../../storefront/parts';
import { statusTone } from './Orders';
import '../../storefront/storefront.css';
import '../../storefront/forms.css';
import '../../storefront/pages.css';

export const OrderDetails = () => {
  const { id } = useParams();
  const { user } = useAuth();
  const [order, setOrder] = useState(null);
  const [track, setTrack] = useState(null);
  const [error, setError] = useState('');
  const [note, setNote] = useState('');
  const [paying, setPaying] = useState(false);

  const load = useCallback(async () => {
    try {
      const { data } = await api.get(`/orders/${id}`);
      setOrder(data);
      api.get(`/orders/${id}/tracking`).then((r) => setTrack(r.data)).catch(() => {});
    } catch { setError('We could not find that order.'); }
  }, [id]);
  useEffect(() => { document.title = `Order ${id} | AutoCart`; load(); }, [id, load]);

  const act = async (path, label) => {
    setNote('');
    try { const { data } = await api.post(`/orders/${id}/${path}`); setNote(data.message || `${label} done.`); await load(); }
    catch (e) { setNote(e?.response?.data?.detail || `Could not ${label.toLowerCase()}.`); }
  };

  if (error) return <div className="ac ac-page"><div className="ac-wrap"><div className="ac-box" role="alert">{error} <Link to="/orders" className="ac-textlink">Back to orders</Link></div></div></div>;
  if (!order) return <div className="ac ac-page"><div className="ac-wrap"><div className="ac-skel" style={{ height: 300 }} /></div></div>;

  const isUpi = order.paymentMethod.startsWith('UPI (');
  const needsPayment = isUpi && ['Awaiting Payment', 'Failed'].includes(order.paymentStatus) && order.status !== 'Cancelled';
  const canCancel = ['Pending', 'Confirmed', 'Processing'].includes(order.status);
  const store = track?.storeLocation;
  const steps = track?.timeline?.length ? track.timeline : order.timeline || [];

  return (
    <div className="ac ac-page"><div className="ac-wrap" style={{ maxWidth: 1000 }}>
      <Link to="/orders" className="ac-textlink">All orders</Link>
      <div className="ac-row-between" style={{ margin: '8px 0 24px' }}>
        <h1 className="ac-display">Order {order.id}</h1>
        <div className="ac-row"><span className="ac-chip-status" data-tone={statusTone(order.status)}>{order.status}</span><span className="ac-chip-status" data-tone={order.paymentStatus === 'Paid' ? 'ok' : statusTone(order.paymentStatus)}>{order.paymentStatus}</span></div>
      </div>
      {note && <div className="ac-box" role="status" style={{ marginBottom: 16, borderColor: 'var(--brand)' }}>{note}</div>}

      <div className="ac-twocol">
        <div>
          <div className="ac-box">
            <h2>Where it is</h2>
            <ol className="ac-timeline">
              {steps.map((s, i) => (
                <li key={i} data-done={!!s.completed}><span>{s.completed ? <Check size={14} /> : <Circle size={10} />}</span><div><b>{s.status}</b>{s.time && <small>{s.time}</small>}</div></li>
              ))}
            </ol>
            {track && <p className="ac-muted" style={{ fontSize: 14, margin: '8px 0 0' }}>Tracking {track.trackingNumber} · about {track.estimatedDeliveryMinutes} minutes once it leaves the store.</p>}
          </div>

          {(track?.pickup && track?.customerLocation) && (
            <div className="ac-box">
              <h2>Route from the store to you</h2>
              <p className="ac-muted" style={{ margin: '4px 0 12px' }}>{track.pickup.name} packs your order and brings it to you.</p>
              <OrderRouteMap pickup={track.pickup} drop={track.customerLocation} height={300} />
            </div>
          )}

          {!(track?.pickup && track?.customerLocation) && store?.latitude != null && (
            <div className="ac-box">
              <h2>Fulfilled from</h2>
              <p className="ac-muted" style={{ margin: '4px 0 12px' }}>{store.name}, {store.address}{store.phone ? ` · ${store.phone}` : ''}</p>
              {track?.customerLocation
                ? <OrderRouteMap pickup={{ name: store.name, address: store.address, lat: store.latitude, lng: store.longitude }} drop={track.customerLocation} height={300} />
                : <StoreMap stores={[{ storeId: 'x', storeName: store.name, address: store.address, latitude: store.latitude, longitude: store.longitude }]} height={280} selectedId="x" />}
            </div>
          )}

          <div className="ac-box">
            <h2>Items</h2>
            {(order.items || []).map((i) => (
              <div className="ac-mini-line" key={i.id} style={{ padding: '12px 0' }}><img src={sized(firstImage(i), 100)} alt="" /><span><Link to={`/products/${i.id}`}>{i.name}</Link><small> × {i.quantity}</small></span><b>{money(i.price * i.quantity)}</b></div>
            ))}
          </div>
        </div>

        <aside>
          <div className="ac-box ac-summary">
            <h2>Payment</h2>
            <dl className="ac-sum">
              <div><dt>Subtotal</dt><dd>{money(order.subtotal)}</dd></div>
              {order.discountAmount > 0 && <div><dt>Discount</dt><dd>-{money(order.discountAmount)}</dd></div>}
              <div><dt>Delivery</dt><dd>{order.shippingFee ? money(order.shippingFee) : 'Free'}</dd></div>
              <div className="ac-sum-total"><dt>Total</dt><dd>{money(order.totalAmount)}</dd></div>
            </dl>
            <p className="ac-muted" style={{ fontSize: 14 }}>{order.paymentMethod}</p>
            {needsPayment && <button className="ac-btn ac-btn-blue" style={{ width: '100%' }} onClick={() => setPaying(true)}>{order.paymentStatus === 'Failed' ? 'Pay again with UPI' : 'Pay now with UPI'}</button>}
            {isUpi && order.paymentStatus === 'Verifying' && <p className="ac-muted" role="status">Waiting for the seller to confirm your UPI payment.</p>}
            {isUpi && order.paymentStatus === 'Failed' && <p className="ac-warn" role="alert">The seller could not find this payment. Check the UPI reference and try again.</p>}
            {canCancel && <button className="ac-btn ac-btn-outline ac-btn-small" style={{ width: '100%', marginTop: 10 }} onClick={() => act('cancel', 'Cancel')}>Cancel order</button>}
            {['Delivered', 'Completed'].includes(order.status) && <button className="ac-btn ac-btn-outline ac-btn-small" style={{ width: '100%', marginTop: 10 }} onClick={() => act('return', 'Return')}>Return an item</button>}
          </div>
          <div className="ac-box">
            <h2>Delivery</h2>
            <p className="ac-muted" style={{ margin: '6px 0 0' }}>{order.customerName}<br />{order.shippingAddress?.addressLine ? `${order.shippingAddress.addressLine}, ${order.shippingAddress.city} ${order.shippingAddress.pinCode}` : order.shippingAddress?.storeName ? `Pickup at ${order.shippingAddress.storeName}` : '-'}</p>
          </div>
          <div className="ac-box">
            <h2>Need help?</h2>
            <p className="ac-muted" style={{ margin: '6px 0 12px' }}>Ask us about this order and a person will reply.</p>
            <Link to="/support" className="ac-btn ac-btn-outline ac-btn-small">Open a support ticket</Link>
          </div>
        </aside>
      </div>
      {paying && <UpiPay order={order} onSubmitted={() => { setPaying(false); setNote('Thanks. The seller will confirm your payment shortly.'); load(); }} onClose={() => setPaying(false)} />}
    </div></div>
  );
};

export default OrderDetails;
