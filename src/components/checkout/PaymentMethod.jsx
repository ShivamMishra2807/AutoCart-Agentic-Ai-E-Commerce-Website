import React, { useState } from 'react';
import { PAYMENT_METHODS } from '../../utils/constants';
import { Smartphone, CreditCard, Landmark, Banknote, ShieldCheck } from 'lucide-react';
import Button from '../common/Button';

export const PaymentMethod = ({ onSelectPayment, onPlaceOrder, isSubmitting = false }) => {
  const [selected, setSelected] = useState('upi');

  const getIcon = (id) => {
    switch (id) {
      case 'upi':
        return <Smartphone className="w-5 h-5 text-indigo-600" />;
      case 'card':
        return <CreditCard className="w-5 h-5 text-indigo-600" />;
      case 'netbanking':
        return <Landmark className="w-5 h-5 text-indigo-600" />;
      case 'cod':
      default:
        return <Banknote className="w-5 h-5 text-emerald-600" />;
    }
  };

  const handleSelect = (id) => {
    setSelected(id);
    const methodObj = PAYMENT_METHODS.find((m) => m.id === id);
    onSelectPayment(methodObj ? methodObj.name : id);
  };

  return (
    <div className="bg-white rounded-2xl border border-gray-100 p-6 shadow-sm space-y-6">
      <h3 className="text-base font-extrabold text-gray-900 border-b pb-3">
        Select Payment Method
      </h3>

      <div className="space-y-3">
        {PAYMENT_METHODS.map((method) => (
          <label
            key={method.id}
            onClick={() => handleSelect(method.id)}
            className={`flex items-center justify-between p-4 rounded-xl border-2 cursor-pointer transition-all ${
              selected === method.id
                ? 'border-indigo-600 bg-indigo-50/40 ring-2 ring-indigo-100'
                : 'border-gray-200 hover:border-gray-300 bg-white'
            }`}
          >
            <div className="flex items-center gap-3">
              <input
                type="radio"
                name="paymentMethod"
                value={method.id}
                checked={selected === method.id}
                onChange={() => handleSelect(method.id)}
                className="w-4 h-4 text-indigo-600 focus:ring-indigo-500"
              />
              <div className="p-2 bg-gray-50 rounded-lg">{getIcon(method.id)}</div>
              <div>
                <p className="text-sm font-bold text-gray-900">{method.name}</p>
                {method.id === 'cod' && (
                  <p className="text-xs text-emerald-700 font-semibold mt-0.5">
                    Cash on Delivery available
                  </p>
                )}
              </div>
            </div>

            {method.badge && (
              <span className="text-[10px] font-bold uppercase px-2 py-0.5 rounded bg-emerald-100 text-emerald-800">
                {method.badge}
              </span>
            )}
          </label>
        ))}
      </div>

      <div className="p-4 bg-gray-50 rounded-xl border border-gray-200/80 text-xs text-gray-500 flex items-center gap-2">
        <ShieldCheck className="w-5 h-5 text-indigo-600 shrink-0" />
        <span>
          Payment options shown are UI demo representations. Orders will complete immediately in test mode.
        </span>
      </div>

      <Button
        variant="primary"
        size="lg"
        fullWidth
        isLoading={isSubmitting}
        onClick={onPlaceOrder}
        className="shadow-lg shadow-indigo-600/30"
      >
        Place Order & Pay Now
      </Button>
    </div>
  );
};

export default PaymentMethod;
