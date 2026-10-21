import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  MapPin, 
  CreditCard, 
  Truck, 
  CheckCircle2, 
  ShieldCheck, 
  Plus, 
  Smartphone, 
  Building, 
  Banknote,
  Lock,
  ArrowRight
} from 'lucide-react';
import { useCart } from '../context/CartContext';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../context/ToastContext';
import { orderService } from '../services/orderService';
import { formatCurrency } from '../utils/formatters';
import { Breadcrumbs } from '../components/common/Breadcrumbs';

export const CheckoutPage = () => {
  const navigate = useNavigate();
  const { cartItems, grandTotal, subtotal, deliveryFee, couponDiscountAmount, clearCart } = useCart();
  const { user } = useAuth();
  const { addToast } = useToast();

  const [selectedAddressIndex, setSelectedAddressIndex] = useState(0);
  const [shippingMethod, setShippingMethod] = useState('standard'); // 'standard' | 'express'
  const [paymentMethod, setPaymentMethod] = useState('upi'); // 'upi' | 'card' | 'netbanking' | 'cod'
  const [upiId, setUpiId] = useState('');
  const [isPlacingOrder, setIsPlacingOrder] = useState(false);

  // Address list
  const addresses = [
    {
      id: 1,
      name: user?.name || "Shivam Sharma",
      type: "Home",
      street: "42 Tech Park Avenue, Sector 62",
      city: "Noida",
      state: "Uttar Pradesh",
      pincode: "201301",
      phone: "+91 98765 43210"
    },
    {
      id: 2,
      name: user?.name || "Shivam Sharma",
      type: "Office",
      street: "Suite 404, Cyber Towers, DLF Phase 3",
      city: "Gurugram",
      state: "Haryana",
      pincode: "122002",
      phone: "+91 98765 43210"
    }
  ];

  const handlePlaceOrder = async () => {
    if (cartItems.length === 0) {
      addToast('Your cart is empty', 'error');
      return;
    }

    setIsPlacingOrder(true);
    try {
      const order = await orderService.placeOrder({
        totalAmount: grandTotal,
        shippingAddress: addresses[selectedAddressIndex],
        paymentMethod: paymentMethod.toUpperCase(),
        items: cartItems
      });

      clearCart();
      addToast('Order placed successfully! Redirecting to tracking...', 'success');
      navigate(`/orders/track/${order.id}`);
    } catch (err) {
      addToast(err.message || 'Failed to place order', 'error');
    } finally {
      setIsPlacingOrder(false);
    }
  };

  if (cartItems.length === 0) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-16 text-center">
        <h2 className="text-2xl font-bold text-gray-900">Your Cart is Empty</h2>
        <button onClick={() => navigate('/products')} className="mt-4 px-6 py-2.5 bg-brand-600 text-white font-bold text-xs rounded-xl">
          Return to Shop
        </button>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-6">
      <Breadcrumbs items={[{ label: 'Cart', link: '/cart' }, { label: 'Checkout' }]} />

      <h1 className="text-2xl sm:text-3xl font-black text-gray-900 tracking-tight">Checkout</h1>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
        
        {/* Left Column: Multi-Step Checkout Form */}
        <div className="lg:col-span-8 flex flex-col gap-6">
          
          {/* Step 1: Shipping Address Selection */}
          <div className="bg-white rounded-3xl p-6 border border-gray-100 shadow-sm">
            <h3 className="text-base font-extrabold text-gray-900 flex items-center gap-2 mb-4">
              <MapPin className="w-5 h-5 text-brand-600" /> 1. Select Delivery Address
            </h3>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {addresses.map((addr, idx) => (
                <div
                  key={addr.id}
                  onClick={() => setSelectedAddressIndex(idx)}
                  className={`p-4 rounded-2xl border-2 cursor-pointer transition-all ${
                    selectedAddressIndex === idx
                      ? 'border-brand-600 bg-brand-50/40 shadow-xs'
                      : 'border-gray-100 hover:border-gray-300'
                  }`}
                >
                  <div className="flex justify-between items-center mb-2">
                    <span className="text-xs font-bold bg-gray-200 text-gray-800 px-2 py-0.5 rounded-md">{addr.type}</span>
                    {selectedAddressIndex === idx && <CheckCircle2 className="w-4 h-4 text-brand-600" />}
                  </div>
                  <p className="text-xs font-bold text-gray-900">{addr.name}</p>
                  <p className="text-xs text-gray-600 mt-1">{addr.street}, {addr.city}</p>
                  <p className="text-xs text-gray-600">{addr.state} - {addr.pincode}</p>
                  <p className="text-[11px] text-gray-400 mt-2 font-medium">Mobile: {addr.phone}</p>
                </div>
              ))}
            </div>
          </div>

          {/* Step 2: Delivery Shipping Speed */}
          <div className="bg-white rounded-3xl p-6 border border-gray-100 shadow-sm">
            <h3 className="text-base font-extrabold text-gray-900 flex items-center gap-2 mb-4">
              <Truck className="w-5 h-5 text-brand-600" /> 2. Delivery Options
            </h3>

            <div className="flex flex-col sm:flex-row gap-4">
              <div
                onClick={() => setShippingMethod('standard')}
                className={`flex-1 p-4 rounded-2xl border-2 cursor-pointer transition-all ${
                  shippingMethod === 'standard' ? 'border-brand-600 bg-brand-50/40' : 'border-gray-100'
                }`}
              >
                <div className="flex justify-between font-bold text-xs text-gray-900 mb-1">
                  <span>Standard Shipping</span>
                  <span className="text-emerald-600">FREE</span>
                </div>
                <p className="text-xs text-gray-500">Delivered in 2-3 business days</p>
              </div>

              <div
                onClick={() => setShippingMethod('express')}
                className={`flex-1 p-4 rounded-2xl border-2 cursor-pointer transition-all ${
                  shippingMethod === 'express' ? 'border-brand-600 bg-brand-50/40' : 'border-gray-100'
                }`}
              >
                <div className="flex justify-between font-bold text-xs text-gray-900 mb-1">
                  <span>Express Next-Day</span>
                  <span>₹149</span>
                </div>
                <p className="text-xs text-gray-500">Guaranteed delivery by tomorrow 2 PM</p>
              </div>
            </div>
          </div>

          {/* Step 3: Payment Method Selector */}
          <div className="bg-white rounded-3xl p-6 border border-gray-100 shadow-sm">
            <h3 className="text-base font-extrabold text-gray-900 flex items-center gap-2 mb-4">
              <CreditCard className="w-5 h-5 text-brand-600" /> 3. Payment Method
            </h3>

            <div className="space-y-3">
              {/* UPI Option */}
              <div
                onClick={() => setPaymentMethod('upi')}
                className={`p-4 rounded-2xl border-2 cursor-pointer transition-all ${
                  paymentMethod === 'upi' ? 'border-brand-600 bg-brand-50/40' : 'border-gray-100'
                }`}
              >
                <div className="flex items-center gap-3 font-bold text-xs text-gray-900">
                  <Smartphone className="w-5 h-5 text-indigo-600" />
                  <span>UPI (GPay / PhonePe / Paytm / BHIM)</span>
                </div>
                {paymentMethod === 'upi' && (
                  <div className="mt-3 pt-3 border-t border-brand-200">
                    <input
                      type="text"
                      placeholder="Enter UPI ID (e.g. name@okicici)"
                      value={upiId}
                      onChange={(e) => setUpiId(e.target.value)}
                      className="w-full max-w-sm px-4 py-2 bg-white border border-gray-300 rounded-xl text-xs"
                    />
                  </div>
                )}
              </div>

              {/* Credit / Debit Card Option */}
              <div
                onClick={() => setPaymentMethod('card')}
                className={`p-4 rounded-2xl border-2 cursor-pointer transition-all ${
                  paymentMethod === 'card' ? 'border-brand-600 bg-brand-50/40' : 'border-gray-100'
                }`}
              >
                <div className="flex items-center gap-3 font-bold text-xs text-gray-900">
                  <CreditCard className="w-5 h-5 text-brand-600" />
                  <span>Credit / Debit Card (Visa, Mastercard, RuPay)</span>
                </div>
                {paymentMethod === 'card' && (
                  <div className="mt-3 pt-3 border-t border-brand-200 grid grid-cols-2 gap-3 max-w-md">
                    <input type="text" placeholder="Card Number" className="col-span-2 px-3 py-2 border rounded-xl text-xs bg-white" />
                    <input type="text" placeholder="MM / YY" className="px-3 py-2 border rounded-xl text-xs bg-white" />
                    <input type="password" placeholder="CVV" className="px-3 py-2 border rounded-xl text-xs bg-white" />
                  </div>
                )}
              </div>

              {/* Net Banking */}
              <div
                onClick={() => setPaymentMethod('netbanking')}
                className={`p-4 rounded-2xl border-2 cursor-pointer transition-all ${
                  paymentMethod === 'netbanking' ? 'border-brand-600 bg-brand-50/40' : 'border-gray-100'
                }`}
              >
                <div className="flex items-center gap-3 font-bold text-xs text-gray-900">
                  <Building className="w-5 h-5 text-emerald-600" />
                  <span>Net Banking (HDFC, SBI, ICICI, Axis)</span>
                </div>
              </div>

              {/* Cash On Delivery */}
              <div
                onClick={() => setPaymentMethod('cod')}
                className={`p-4 rounded-2xl border-2 cursor-pointer transition-all ${
                  paymentMethod === 'cod' ? 'border-brand-600 bg-brand-50/40' : 'border-gray-100'
                }`}
              >
                <div className="flex items-center gap-3 font-bold text-xs text-gray-900">
                  <Banknote className="w-5 h-5 text-amber-600" />
                  <span>Cash on Delivery (Pay upon doorstep arrival)</span>
                </div>
              </div>
            </div>
          </div>

        </div>

        {/* Right Column: Order Summary & Place Order CTA */}
        <div className="lg:col-span-4 flex flex-col gap-4">
          <div className="bg-white rounded-3xl p-6 border border-gray-100 shadow-sm flex flex-col gap-4">
            <h3 className="text-base font-extrabold text-gray-900 border-b border-gray-100 pb-3">
              Order Items ({cartItems.length})
            </h3>

            <div className="space-y-3 max-h-60 overflow-y-auto hide-scrollbar">
              {cartItems.map((item) => (
                <div key={item.itemKey} className="flex items-center gap-3">
                  <img src={item.images?.[0]} alt="" className="w-12 h-12 object-cover rounded-lg border border-gray-100" />
                  <div className="flex-1 min-w-0">
                    <p className="text-xs font-bold text-gray-900 truncate">{item.title}</p>
                    <p className="text-[11px] text-gray-400">Qty: {item.quantity}</p>
                  </div>
                  <span className="text-xs font-bold text-gray-900">{formatCurrency(item.price * item.quantity)}</span>
                </div>
              ))}
            </div>

            <div className="pt-3 border-t border-gray-100 flex justify-between items-baseline">
              <span className="text-sm font-extrabold text-gray-900">Amount Payable</span>
              <span className="text-xl font-black text-brand-600">{formatCurrency(grandTotal)}</span>
            </div>

            <button
              onClick={handlePlaceOrder}
              disabled={isPlacingOrder}
              className="mt-2 w-full py-4 bg-brand-600 hover:bg-brand-700 disabled:opacity-50 text-white rounded-2xl font-extrabold text-sm flex items-center justify-center gap-2 shadow-lg shadow-brand-500/20 transition-all hover:scale-[1.02]"
            >
              <Lock className="w-4 h-4 text-amber-300" />
              <span>{isPlacingOrder ? 'Processing Order...' : 'Place Order Now'}</span>
            </button>

            <div className="flex items-center justify-center gap-1.5 text-[11px] text-gray-400 font-medium pt-1">
              <ShieldCheck className="w-4 h-4 text-emerald-500" /> 100% Buyer Protection Guarantee
            </div>
          </div>
        </div>

      </div>
    </div>
  );
};
