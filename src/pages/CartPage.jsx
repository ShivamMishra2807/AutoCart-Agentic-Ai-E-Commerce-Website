import React from 'react';
import { Link } from 'react-router-dom';
import { ShoppingBag, ArrowLeft, Trash2 } from 'lucide-react';
import { useCart } from '../context/CartContext';
import { CartItem } from '../components/cart/CartItem';
import { CartSummary } from '../components/cart/CartSummary';
import { CouponBox } from '../components/cart/CouponBox';
import { Breadcrumbs } from '../components/common/Breadcrumbs';

export const CartPage = () => {
  const { cartItems, totalItemsCount, clearCart } = useCart();

  if (cartItems.length === 0) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-16 text-center flex flex-col items-center justify-center gap-4 min-h-[60vh]">
        <div className="w-20 h-20 rounded-full bg-brand-50 text-brand-600 flex items-center justify-center shadow-inner">
          <ShoppingBag className="w-10 h-10" />
        </div>
        <h2 className="text-2xl sm:text-3xl font-black text-gray-900 tracking-tight">Your Cart is Empty</h2>
        <p className="text-xs sm:text-sm text-gray-500 max-w-md">
          Looks like you haven't added any items to your cart yet. Explore our flagship catalog and discover amazing daily offers!
        </p>
        <Link
          to="/products"
          className="mt-2 px-8 py-3.5 bg-brand-600 hover:bg-brand-700 text-white rounded-2xl font-extrabold text-xs shadow-lg shadow-brand-500/20 transition-all hover:scale-105"
        >
          Explore Catalog & Shop Now
        </Link>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-6">
      <Breadcrumbs items={[{ label: 'Shopping Cart' }]} />

      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 pb-2 border-b border-gray-100">
        <div>
          <h1 className="text-2xl sm:text-3xl font-black text-gray-900 tracking-tight">
            Shopping Cart ({totalItemsCount} {totalItemsCount === 1 ? 'Item' : 'Items'})
          </h1>
          <p className="text-xs text-gray-500 font-medium mt-0.5">
            Review item quantities, apply promo codes, and proceed to secure checkout.
          </p>
        </div>

        <button
          onClick={clearCart}
          className="text-xs font-bold text-rose-500 hover:text-rose-700 flex items-center gap-1 transition-colors"
        >
          <Trash2 className="w-3.5 h-3.5" /> Clear Cart
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
        {/* Left Column: Cart Items List */}
        <div className="lg:col-span-8 flex flex-col gap-4">
          {cartItems.map((item) => (
            <CartItem key={item.itemKey} item={item} />
          ))}

          <div className="pt-4 flex justify-between items-center">
            <Link to="/products" className="flex items-center gap-2 text-xs font-bold text-brand-600 hover:underline">
              <ArrowLeft className="w-4 h-4" /> Continue Shopping
            </Link>
          </div>
        </div>

        {/* Right Column: Coupon Box & Price Summary */}
        <div className="lg:col-span-4 flex flex-col gap-4">
          <CouponBox />
          <CartSummary />
        </div>
      </div>
    </div>
  );
};
