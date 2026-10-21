import React from 'react';
import { Trash2 } from 'lucide-react';
import { Link } from 'react-router-dom';
import formatPrice from '../../utils/formatPrice';
import QuantitySelector from '../product/QuantitySelector';
import { useCart } from '../../hooks/useCart';

export const CartItem = ({ item }) => {
  const { updateQuantity, removeFromCart } = useCart();

  return (
    <div className="flex flex-col sm:flex-row items-center justify-between p-4 bg-white rounded-xl border border-gray-100 shadow-sm gap-4">
      {/* Product info */}
      <div className="flex items-center gap-4 w-full sm:w-auto">
        <div className="w-20 h-20 bg-gray-50 rounded-lg p-2 shrink-0 border border-gray-100 flex items-center justify-center">
          <img
            src={item.images ? item.images[0] : item.image}
            alt={item.name}
            className="max-h-full max-w-full object-contain"
          />
        </div>
        <div className="flex-1 min-w-0">
          <span className="text-[10px] font-bold text-gray-400 uppercase tracking-wider">{item.brand}</span>
          <Link to={`/products/${item.id}`} className="block text-sm font-bold text-gray-900 truncate hover:text-indigo-600">
            {item.name}
          </Link>
          <div className="text-sm font-extrabold text-gray-900 mt-1">
            {formatPrice(item.price)}
          </div>
        </div>
      </div>

      {/* Controls & Subtotal */}
      <div className="flex items-center justify-between w-full sm:w-auto gap-6 border-t sm:border-t-0 pt-3 sm:pt-0">
        <QuantitySelector
          quantity={item.quantity}
          onDecrease={() => updateQuantity(item.id, item.quantity - 1)}
          onIncrease={() => updateQuantity(item.id, item.quantity + 1)}
          max={item.stock || 99}
        />

        <div className="text-right min-w-[90px]">
          <span className="text-xs text-gray-400 block sm:hidden">Total</span>
          <span className="text-sm font-extrabold text-gray-900">
            {formatPrice(item.price * item.quantity)}
          </span>
        </div>

        <button
          onClick={() => removeFromCart(item.id)}
          className="p-2 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition"
          title="Remove item"
        >
          <Trash2 className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
};

export default CartItem;
