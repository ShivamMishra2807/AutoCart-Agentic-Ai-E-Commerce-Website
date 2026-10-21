import React from 'react';
import ProductCard from '../product/ProductCard';
import { products } from '../../data/products';
import { Sparkles } from 'lucide-react';
import { Link } from 'react-router-dom';

export const FeaturedProducts = () => {
  const featured = products.filter((p) => p.featured).slice(0, 4);

  return (
    <section className="mb-12">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-2">
          <div className="p-2 bg-amber-100 text-amber-600 rounded-lg">
            <Sparkles className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-xl sm:text-2xl font-extrabold text-gray-900 tracking-tight">
              Featured Products
            </h2>
            <p className="text-xs sm:text-sm text-gray-500">Handpicked top deals selected for you</p>
          </div>
        </div>
        <Link to="/products" className="text-xs sm:text-sm font-semibold text-indigo-600 hover:text-indigo-700">
          See All &rarr;
        </Link>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6">
        {featured.map((product) => (
          <ProductCard key={product.id} product={product} />
        ))}
      </div>
    </section>
  );
};

export default FeaturedProducts;
