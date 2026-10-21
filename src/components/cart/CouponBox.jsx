import React, { useState } from 'react';
import { Tag, Check, X } from 'lucide-react';

export const CouponBox = ({ coupon, discountAmount, onApplyCoupon, onRemoveCoupon }) => {
  const [code, setCode] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleApply = async (e) => {
    e.preventDefault();
    if (!code.trim()) return;
    setError('');
    setLoading(true);
    try {
      await onApplyCoupon(code);
      setCode('');
    } catch (err) {
      setError(err.message || 'Invalid coupon code');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-gray-50 rounded-xl p-4 border border-gray-200/80 space-y-3">
      <div className="flex items-center gap-2 text-xs font-bold text-gray-700 uppercase tracking-wider">
        <Tag className="w-4 h-4 text-indigo-600" />
        <span>Apply Discount Coupon</span>
      </div>

      {coupon ? (
        <div className="flex items-center justify-between p-3 bg-emerald-50 border border-emerald-200 rounded-lg text-xs font-semibold text-emerald-800">
          <div className="flex items-center gap-2">
            <Check className="w-4 h-4 text-emerald-600" />
            <div>
              <p className="font-bold">{coupon.code} Applied</p>
              <p className="text-[10px] text-emerald-600 font-normal">{coupon.description}</p>
            </div>
          </div>
          <button
            onClick={onRemoveCoupon}
            className="p-1 text-gray-400 hover:text-red-600 rounded"
            title="Remove coupon"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      ) : (
        <form onSubmit={handleApply} className="flex gap-2">
          <input
            type="text"
            value={code}
            onChange={(e) => setCode(e.target.value.toUpperCase())}
            placeholder="Enter promo code (e.g. WELCOME10)"
            className="flex-1 text-xs px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-1 focus:ring-indigo-500 uppercase font-mono"
          />
          <button
            type="submit"
            disabled={loading || !code.trim()}
            className="bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 text-white text-xs font-bold px-4 py-2 rounded-lg transition shrink-0"
          >
            {loading ? '...' : 'Apply'}
          </button>
        </form>
      )}

      {error && <p className="text-xs text-red-600">{error}</p>}
    </div>
  );
};

export default CouponBox;
