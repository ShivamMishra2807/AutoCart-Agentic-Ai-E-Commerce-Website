import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { 
  Package, 
  CheckCircle2, 
  Clock, 
  Truck, 
  MapPin, 
  ShieldCheck, 
  ChevronRight,
  ArrowLeft
} from 'lucide-react';
import { orderService } from '../services/orderService';
import { formatCurrency, formatDate } from '../utils/formatters';
import { Breadcrumbs } from '../components/common/Breadcrumbs';

export const OrderTrackingPage = () => {
  const { id } = useParams();
  const [order, setOrder] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchOrderDetails = async () => {
      setLoading(true);
      try {
        const data = await orderService.getOrderById(id);
        setOrder(data);
      } catch (err) {
        console.error("Error loading order:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchOrderDetails();
  }, [id]);

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-16 text-center animate-pulse">
        <div className="h-8 bg-gray-200 rounded w-1/3 mx-auto mb-4"></div>
        <div className="h-64 bg-gray-200 rounded-3xl max-w-2xl mx-auto"></div>
      </div>
    );
  }

  if (!order) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-16 text-center">
        <h2 className="text-2xl font-bold text-gray-900">Order Not Found</h2>
        <p className="text-gray-500 mt-2">Could not find tracking record for ID #{id}</p>
        <Link to="/dashboard?tab=orders" className="inline-block mt-4 px-6 py-2.5 bg-brand-600 text-white rounded-xl text-xs font-bold">
          View All Orders
        </Link>
      </div>
    );
  }

  const steps = [
    { title: "Order Placed", key: 0 },
    { title: "Confirmed", key: 1 },
    { title: "Packed", key: 2 },
    { title: "Shipped", key: 3 },
    { title: "Out for Delivery", key: 4 },
    { title: "Delivered", key: 5 }
  ];

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-6">
      <Breadcrumbs items={[{ label: 'Orders', link: '/dashboard?tab=orders' }, { label: `Track #${order.id}` }]} />

      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 pb-2 border-b border-gray-100">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl sm:text-3xl font-black text-gray-900 tracking-tight">Order #{order.id}</h1>
            <span className="bg-brand-50 text-brand-700 text-xs font-bold px-3 py-1 rounded-full border border-brand-200">
              {order.status}
            </span>
          </div>
          <p className="text-xs text-gray-500 font-medium mt-1">
            Placed on {formatDate(order.date)} | Estimated Delivery: <strong className="text-gray-900">{order.estimatedDelivery}</strong>
          </p>
        </div>

        <Link to="/dashboard?tab=orders" className="flex items-center gap-1 text-xs font-bold text-gray-600 hover:text-brand-600">
          <ArrowLeft className="w-4 h-4" /> Back to My Orders
        </Link>
      </div>

      {/* Visual Tracking Timeline Stepper */}
      <div className="bg-white rounded-3xl p-6 sm:p-8 border border-gray-100 shadow-sm">
        <h3 className="text-sm font-extrabold text-gray-900 uppercase tracking-wider mb-8">
          Delivery Timeline Status
        </h3>

        {/* Desktop Stepper */}
        <div className="hidden md:flex justify-between items-center relative">
          {/* Connecting Line */}
          <div className="absolute left-0 right-0 top-1/2 -translate-y-1/2 h-1 bg-gray-200 z-0">
            <div
              className="h-full bg-emerald-500 transition-all duration-700"
              style={{ width: `${(order.currentStep / (steps.length - 1)) * 100}%` }}
            />
          </div>

          {steps.map((st, idx) => {
            const isDone = idx <= order.currentStep;
            const isCurrent = idx === order.currentStep;
            return (
              <div key={st.key} className="relative z-10 flex flex-col items-center gap-2 text-center bg-white px-2">
                <div
                  className={`w-10 h-10 rounded-full flex items-center justify-center font-bold text-xs transition-all ${
                    isDone
                      ? 'bg-emerald-600 text-white shadow-md'
                      : 'bg-gray-100 text-gray-400 border border-gray-200'
                  } ${isCurrent ? 'ring-4 ring-emerald-100 scale-110' : ''}`}
                >
                  {isDone ? <CheckCircle2 className="w-5 h-5" /> : idx + 1}
                </div>
                <span className={`text-xs font-bold ${isDone ? 'text-gray-900' : 'text-gray-400'}`}>
                  {st.title}
                </span>
              </div>
            );
          })}
        </div>

        {/* Mobile Vertical Timeline */}
        <div className="md:hidden flex flex-col gap-6 relative pl-4 border-l-2 border-emerald-500 ml-2">
          {order.timeline?.map((item, index) => (
            <div key={index} className="relative pl-4">
              <div
                className={`absolute -left-[21px] top-0.5 w-4 h-4 rounded-full border-2 ${
                  item.completed ? 'bg-emerald-500 border-white' : 'bg-gray-200 border-white'
                }`}
              />
              <p className="text-xs font-bold text-gray-900">{item.title}</p>
              <p className="text-[11px] text-gray-400 font-medium">{item.date}</p>
              <p className="text-xs text-gray-600 mt-0.5">{item.description}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Order Details & Address Summary */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        
        {/* Ordered Items */}
        <div className="bg-white rounded-3xl p-6 border border-gray-100 shadow-sm space-y-4">
          <h3 className="text-sm font-extrabold text-gray-900 uppercase tracking-wider pb-2 border-b border-gray-100">
            Package Items
          </h3>
          {order.items?.map((item, i) => (
            <div key={i} className="flex items-center gap-3">
              <img src={item.image} alt="" className="w-14 h-14 object-cover rounded-xl border border-gray-100" />
              <div className="flex-1 min-w-0">
                <p className="text-xs font-bold text-gray-900 truncate">{item.title}</p>
                <p className="text-[11px] text-gray-400">Qty: {item.quantity} | {item.color || 'Standard'}</p>
              </div>
              <span className="text-xs font-bold text-gray-900">{formatCurrency(item.price * item.quantity)}</span>
            </div>
          ))}
        </div>

        {/* Delivery Address */}
        <div className="bg-white rounded-3xl p-6 border border-gray-100 shadow-sm space-y-3">
          <h3 className="text-sm font-extrabold text-gray-900 uppercase tracking-wider pb-2 border-b border-gray-100 flex items-center gap-1.5">
            <MapPin className="w-4 h-4 text-brand-600" /> Delivery Address
          </h3>
          <p className="text-xs font-bold text-gray-900">{order.shippingAddress?.fullName}</p>
          <p className="text-xs text-gray-600">{order.shippingAddress?.street}, {order.shippingAddress?.city}</p>
          <p className="text-xs text-gray-600">{order.shippingAddress?.state} - {order.shippingAddress?.pincode}</p>
          <p className="text-xs text-gray-500 font-medium">Contact: {order.shippingAddress?.phone}</p>

          <div className="pt-3 border-t border-gray-100 text-xs">
            <span className="font-semibold text-gray-500">Payment Method: </span>
            <span className="font-bold text-gray-900">{order.paymentMethod}</span>
          </div>
        </div>

      </div>
    </div>
  );
};
