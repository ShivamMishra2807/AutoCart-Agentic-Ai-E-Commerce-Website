import React from 'react';
import formatPrice from '../../utils/formatPrice';

export const OrderSummary = ({ cartItems = [], subtotal, discountAmount, deliveryCharge, finalTotal }) => {
  return (
    <div className="bg-white rounded-2xl border border-gray-100 p-5 shadow-sm space-y-4">
      <h3 className="text-base font-extrabold text-gray-900 border-b pb-3">
        Order Review ({cartItems.length} items)
      </h3>

      <div className="space-y-3 max-h-60 overflow-y-auto pr-1">
        {cartItems.map((item) => (
          <div key={item.id} className="flex items-center justify-between text-xs py-1">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-gray-50 rounded border p-1 shrink-0 flex items-center justify-center">
                <img src={item.images ? item.images[0] : item.image} alt={item.name} className="max-h-full max-w-full object-contain" />
              </div>
              <div>
                <p className="font-bold text-gray-900 line-clamp-1">{item.name}</p>
                <p className="text-gray-400">Qty: {item.quantity}</p>
              </div>
            </div>
            <span className="font-extrabold text-gray-900">{formatPrice(item.price * item.quantity)}</span>
          </div>
        ))}
      </div>

      <div className="border-t pt-3 space-y-2 text-xs text-gray-600">
        <div className="flex justify-between">
          <span>Items Subtotal</span>
          <span className="font-bold text-gray-900">{formatPrice(subtotal)}</span>
        </div>
        {discountAmount > 0 && (
          <div className="flex justify-between text-emerald-600 font-bold">
            <span>Discount Applied</span>
            <span>- {formatPrice(discountAmount)}</span>
          </div>
        )}
        <div className="flex justify-between">
          <span>Delivery Fee</span>
          <span>{deliveryCharge === 0 ? 'FREE' : formatPrice(deliveryCharge)}</span>
        </div>
        <div className="border-t pt-3 flex justify-between text-sm font-extrabold text-gray-900">
          <span>Total Amount</span>
          <span className="text-indigo-600 text-base">{formatPrice(finalTotal)}</span>
        </div>
      </div>
    </div>
  );
};

export default OrderSummary;
