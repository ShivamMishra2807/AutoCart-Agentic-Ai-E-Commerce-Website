import React from 'react';
import formatPrice from '../../utils/formatPrice';
import { products } from '../../data/products';

export const TopProducts = () => {
  const topList = [...products].sort((a, b) => b.reviewCount - a.reviewCount).slice(0, 4);

  return (
    <div className="bg-white p-6 rounded-2xl border border-gray-100 shadow-sm space-y-4">
      <h3 className="text-base font-extrabold text-gray-900">Top Performing Products</h3>

      <div className="space-y-3">
        {topList.map((prod) => (
          <div key={prod.id} className="flex items-center gap-3 p-2.5 bg-gray-50 rounded-xl">
            <div className="w-10 h-10 bg-white rounded border p-1 shrink-0 flex items-center justify-center">
              <img src={prod.images[0]} alt={prod.name} className="max-h-full max-w-full object-contain" />
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-xs font-bold text-gray-900 truncate">{prod.name}</p>
              <p className="text-[10px] text-gray-400">{prod.brand} • {prod.category}</p>
            </div>
            <div className="text-right shrink-0">
              <p className="text-xs font-extrabold text-indigo-600">{formatPrice(prod.price)}</p>
              <p className="text-[10px] text-gray-400 font-semibold">{prod.reviewCount} Sold</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default TopProducts;
