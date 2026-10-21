import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import orderService from '../../services/orderService';
import Loader from '../../components/common/Loader';
import Button from '../../components/common/Button';
import Badge from '../../components/common/Badge';
import formatPrice from '../../utils/formatPrice';
import formatDate from '../../utils/formatDate';
import { ArrowLeft, Save, Truck } from 'lucide-react';

export const OrderDetails = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [order, setOrder] = useState(null);
  const [loading, setLoading] = useState(true);
  const [newStatus, setNewStatus] = useState('');
  const [updating, setUpdating] = useState(false);

  useEffect(() => {
    const fetchOrder = async () => {
      setLoading(true);
      try {
        const data = await orderService.getOrderById(id);
        setOrder(data);
        setNewStatus(data.status);
      } finally {
        setLoading(false);
      }
    };
    fetchOrder();
  }, [id]);

  const handleStatusUpdate = async () => {
    setUpdating(true);
    await new Promise((resolve) => setTimeout(resolve, 400));
    setOrder((prev) => ({ ...prev, status: newStatus }));
    setUpdating(false);
    alert('Order status updated successfully!');
  };

  if (loading) return <Loader fullScreen text="Loading order details..." />;
  if (!order) return <div className="text-center py-20 font-bold">Order not found</div>;

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div className="flex items-center gap-3 border-b pb-4">
        <button onClick={() => navigate('/admin/orders')} className="p-2 text-gray-500 hover:bg-gray-100 rounded-lg">
          <ArrowLeft className="w-5 h-5" />
        </button>
        <div>
          <span className="text-xs text-gray-400 font-bold uppercase">Order Reference</span>
          <h1 className="text-2xl font-extrabold text-gray-900 font-mono">{order.id}</h1>
        </div>
      </div>

      {/* Status update box */}
      <div className="bg-white p-5 rounded-2xl border border-gray-100 shadow-sm flex flex-col sm:flex-row items-center justify-between gap-4">
        <div>
          <p className="text-xs font-bold text-gray-400 uppercase">Current Order Status</p>
          <div className="mt-1">
            <Badge variant="indigo" size="md">{order.status}</Badge>
          </div>
        </div>

        <div className="flex items-center gap-3 w-full sm:w-auto">
          <select
            value={newStatus}
            onChange={(e) => setNewStatus(e.target.value)}
            className="text-xs font-bold border rounded-lg px-3 py-2 bg-white text-gray-800 focus:outline-none"
          >
            <option value="Pending">Pending</option>
            <option value="Confirmed">Confirmed</option>
            <option value="Processing">Processing</option>
            <option value="Shipped">Shipped</option>
            <option value="Out for Delivery">Out for Delivery</option>
            <option value="Delivered">Delivered</option>
            <option value="Cancelled">Cancelled</option>
          </select>
          <Button variant="primary" size="sm" isLoading={updating} icon={Save} onClick={handleStatusUpdate}>
            Update Status
          </Button>
        </div>
      </div>

      {/* Order Info */}
      <div className="bg-white p-6 rounded-2xl border border-gray-100 shadow-sm space-y-4">
        <h3 className="text-base font-extrabold text-gray-900 border-b pb-3">Customer & Delivery Info</h3>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
          <div>
            <p className="font-bold text-gray-400 uppercase">Customer Name</p>
            <p className="font-bold text-gray-900 text-sm mt-0.5">{order.customerName}</p>
            <p className="text-gray-500">{order.customerEmail}</p>
            <p className="text-gray-500">{order.customerPhone}</p>
          </div>
          <div>
            <p className="font-bold text-gray-400 uppercase">Shipping Address</p>
            <p className="font-semibold text-gray-800 mt-0.5">{order.shippingAddress.addressLine}</p>
            <p className="text-gray-600">{order.shippingAddress.city}, {order.shippingAddress.state} - {order.shippingAddress.pinCode}</p>
          </div>
        </div>
      </div>

      {/* Items */}
      <div className="bg-white p-6 rounded-2xl border border-gray-100 shadow-sm space-y-4">
        <h3 className="text-base font-extrabold text-gray-900 border-b pb-3">Order Items</h3>
        <div className="space-y-3">
          {order.items.map((item) => (
            <div key={item.id} className="flex items-center justify-between text-xs py-2 border-b last:border-b-0">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-gray-50 rounded border p-1 shrink-0 flex items-center justify-center">
                  <img src={item.image || item.images?.[0]} alt={item.name} className="max-h-full max-w-full object-contain" />
                </div>
                <span className="font-bold text-gray-900">{item.name} x {item.quantity}</span>
              </div>
              <span className="font-extrabold text-gray-900">{formatPrice(item.price * item.quantity)}</span>
            </div>
          ))}
        </div>
        <div className="border-t pt-3 flex justify-between text-base font-extrabold text-gray-900">
          <span>Total Amount</span>
          <span className="text-indigo-600">{formatPrice(order.totalAmount)}</span>
        </div>
      </div>
    </div>
  );
};

export default OrderDetails;
