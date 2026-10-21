import React from 'react';
import { formatCurrency, calculateDiscount } from '../../utils/formatters';

export const PriceDisplay = ({ price, originalPrice, size = 'normal', layout = 'horizontal' }) => {
  const discount = calculateDiscount(originalPrice, price);

  const priceClasses = size === 'lg' 
    ? 'text-2xl sm:text-3xl font-extrabold text-gray-900' 
    : size === 'sm' 
    ? 'text-base font-bold text-gray-900' 
    : 'text-lg font-bold text-gray-900';

  const origClasses = size === 'lg'
    ? 'text-base text-gray-400 line-through font-medium'
    : 'text-xs text-gray-400 line-through font-medium';

  return (
    <div className={`flex ${layout === 'vertical' ? 'flex-col items-start' : 'items-baseline gap-2'} flex-wrap`}>
      <span className={priceClasses}>{formatCurrency(price)}</span>
      {originalPrice && originalPrice > price && (
        <span className={origClasses}>{formatCurrency(originalPrice)}</span>
      )}
      {discount > 0 && (
        <span className="text-xs font-semibold text-emerald-600 bg-emerald-50 px-1.5 py-0.5 rounded">
          {discount}% OFF
        </span>
      )}
    </div>
  );
};
