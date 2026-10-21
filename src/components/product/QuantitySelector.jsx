import React from 'react';
import { Plus, Minus } from 'lucide-react';

export const QuantitySelector = ({ quantity = 1, onDecrease, onIncrease, min = 1, max = 99 }) => {
  return (
    <div className="inline-flex items-center rounded-lg border border-gray-200 bg-white shadow-sm">
      <button
        type="button"
        disabled={quantity <= min}
        onClick={onDecrease}
        className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-50 disabled:opacity-30 rounded-l-lg transition"
      >
        <Minus className="w-3.5 h-3.5" />
      </button>
      <span className="w-10 text-center text-sm font-bold text-gray-900 select-none">
        {quantity}
      </span>
      <button
        type="button"
        disabled={quantity >= max}
        onClick={onIncrease}
        className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-50 disabled:opacity-30 rounded-r-lg transition"
      >
        <Plus className="w-3.5 h-3.5" />
      </button>
    </div>
  );
};

export default QuantitySelector;
