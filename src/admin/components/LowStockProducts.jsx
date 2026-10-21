import React from 'react';
import { products } from '../../data/products';
import Badge from '../../components/common/Badge';
import { AlertCircle } from 'lucide-react';
import { Link } from 'react-router-dom';

export const LowStockProducts = () => {
  const lowStock = products.filter((p) => p.stock <= 15).slice(0, 4);

  return (
    <div className="bg-white p-6 rounded-2xl border border-gray-100 shadow-sm space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-base font-extrabold text-gray-900 flex items-center gap-2">
          <AlertCircle className="w-4 h-4 text-amber-500" /> Low Inventory Alert
        </h3>
        <Link to="/admin/inventory" className="text-xs font-bold text-indigo-600 hover:underline">
          Manage Inventory &rarr;
        </Link>
      </div>

      <div className="space-y-3">
        {lowStock.map((prod) => (
          <div key={prod.id} className="flex items-center justify-between p-2.5 bg-amber-50/50 rounded-xl text-xs border border-amber-100">
            <div>
              <p className="font-bold text-gray-900 line-clamp-1">{prod.name}</p>
              <p className="text-[10px] text-gray-500">Brand: {prod.brand}</p>
            </div>
            <div className="text-right">
              <Badge variant={prod.stock === 0 ? 'red' : 'yellow'}>
                {prod.stock === 0 ? 'Out of Stock' : `${prod.stock} Left`}
              </Badge>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default LowStockProducts;
