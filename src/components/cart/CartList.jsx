import React from 'react';
import CartItem from './CartItem';
import Button from '../common/Button';
import { Trash2 } from 'lucide-react';

export const CartList = ({ cartItems, onClearCart }) => {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between px-1">
        <h2 className="text-lg font-bold text-gray-900">
          Shopping Cart ({cartItems.length} {cartItems.length === 1 ? 'item' : 'items'})
        </h2>
        {cartItems.length > 0 && (
          <button
            onClick={onClearCart}
            className="text-xs text-red-600 hover:text-red-700 font-semibold flex items-center gap-1"
          >
            <Trash2 className="w-3.5 h-3.5" />
            Clear Cart
          </button>
        )}
      </div>

      <div className="space-y-3">
        {cartItems.map((item) => (
          <CartItem key={item.id} item={item} />
        ))}
      </div>
    </div>
  );
};

export default CartList;
