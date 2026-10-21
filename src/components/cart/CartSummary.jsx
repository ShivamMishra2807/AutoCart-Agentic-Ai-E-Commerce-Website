import React from 'react';
import formatPrice from '../../utils/formatPrice';
import Button from '../common/Button';
import CouponBox from './CouponBox';
import { ArrowRight, ShieldCheck, Truck } from 'lucide-react';
import { Link } from 'react-router-dom';

export const CartSummary = ({
  subtotal,
  discountAmount,
  deliveryCharge,
  finalTotal,
  coupon,
  onApplyCoupon,
  onRemoveCoupon,
  checkoutDisabled = false,
}) => {
  return (
    <div className="bg-white rounded-2xl border border-gray-100 p-6 shadow-sm space-y-6">
      <h3 className="text-base font-extrabold text-gray-900 border-b pb-4">
        Order Summary
      </h3>

      {/* Coupon section */}
      <CouponBox
        coupon={coupon}
        discountAmount={discountAmount}
        onApplyCoupon={onApplyCoupon}
        onRemoveCoupon={onRemoveCoupon}
      />

      {/* Price breakdown */}
      <div className="space-y-3 text-sm text-gray-600 pt-2">
        <div className="flex justify-between">
          <span>Bag Subtotal</span>
          <span className="font-semibold text-gray-900">{formatPrice(subtotal)}</span>
        </div>

        {discountAmount > 0 && (
          <div className="flex justify-between text-emerald-600 font-medium">
            <span>Coupon Discount</span>
            <span>- {formatPrice(discountAmount)}</span>
          </div>
        )}

        <div className="flex justify-between items-center">
          <span className="flex items-center gap-1.5">
            <Truck className="w-4 h-4 text-gray-400" /> Delivery Fee
          </span>
          <span className="font-semibold">
            {deliveryCharge === 0 ? (
              <span className="text-emerald-600 font-bold uppercase text-xs bg-emerald-50 px-2 py-0.5 rounded">
                FREE
              </span>
            ) : (
              formatPrice(deliveryCharge)
            )}
          </span>
        </div>

        <div className="border-t pt-4 flex justify-between items-center text-base font-extrabold text-gray-900">
          <span>Final Total</span>
          <span className="text-lg text-indigo-600">{formatPrice(finalTotal)}</span>
        </div>
      </div>

      {/* Checkout CTA */}
      <Link to="/checkout">
        <Button
          variant="primary"
          size="lg"
          fullWidth
          disabled={checkoutDisabled || subtotal === 0}
          className="shadow-lg shadow-indigo-600/25 mt-2"
        >
          Proceed to Checkout <ArrowRight className="w-4 h-4 ml-1" />
        </Button>
      </Link>

      <div className="flex items-center justify-center gap-2 text-xs text-gray-400 font-medium pt-2">
        <ShieldCheck className="w-4 h-4 text-indigo-500" />
        <span>100% Safe & Secure Payments</span>
      </div>
    </div>
  );
};

export default CartSummary;
