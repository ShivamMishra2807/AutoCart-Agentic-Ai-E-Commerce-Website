import React from 'react';
import ProductCard from '../product/ProductCard';
import { products } from '../../data/products';
import { Sparkle } from 'lucide-react';
import { Link } from 'react-router-dom';

export const NewArrivals = () => {
  const newArrivals = products.filter((p) => p.newArrival).slice(0, 4);

  return (
    <section className="mb-12">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-2">
          <div className="p-2 bg-emerald-100 text-emerald-600 rounded-lg">
            <Sparkle className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-xl sm:text-2xl font-extrabold text-gray-900 tracking-tight">
              New Arrivals
            </h2>
            <p className="text-xs sm:text-sm text-gray-500">Freshly catalogued premium items</p>
          </div>
        </div>
        <Link to="/products?sortBy=newest" className="text-xs sm:text-sm font-semibold text-indigo-600 hover:text-indigo-700">
          View All &rarr;
        </Link>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6">
        {newArrivals.map((product) => (
          <ProductCard key={product.id} product={product} />
        ))}
      </div>
    </section>
  );
};

export default NewArrivals;
