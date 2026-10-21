import React from 'react';
import { categories } from '../../data/categories';
import { Link } from 'react-router-dom';
import { ArrowRight } from 'lucide-react';

export const CategorySection = () => {
  return (
    <section className="mb-12">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-xl sm:text-2xl font-extrabold text-gray-900 dark:text-white tracking-tight">
            Shop by Category
          </h2>
          <p className="text-xs sm:text-sm text-gray-500 dark:text-gray-400 mt-0.5">Explore our wide selection of top verified categories</p>
        </div>
        <Link
          to="/products"
          className="text-xs sm:text-sm font-semibold text-indigo-600 dark:text-indigo-400 hover:text-indigo-700 flex items-center gap-1 group"
        >
          View All
          <ArrowRight className="w-4 h-4 group-hover:translate-x-0.5 transition-transform" />
        </Link>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-8 gap-3 sm:gap-4">
        {categories.map((cat) => (
          <Link
            key={cat.id}
            to={`/products?category=${encodeURIComponent(cat.name)}`}
            className="group flex flex-col items-center text-center p-3 bg-white dark:bg-gray-900 rounded-2xl border border-gray-100 dark:border-gray-800 shadow-sm hover:shadow-xl hover:border-indigo-300 dark:hover:border-indigo-700 transition-all duration-300"
          >
            <div className="w-16 h-16 sm:w-20 sm:h-20 rounded-full overflow-hidden mb-3 bg-gray-50 dark:bg-gray-800 p-1 group-hover:scale-105 transition-transform ring-2 ring-indigo-50 dark:ring-indigo-950">
              <img
                src={cat.image}
                alt={cat.name}
                className="w-full h-full object-cover rounded-full"
                loading="lazy"
              />
            </div>
            <h3 className="text-xs font-bold text-gray-800 dark:text-gray-200 group-hover:text-indigo-600 dark:group-hover:text-indigo-400 line-clamp-1">
              {cat.name}
            </h3>
            <span className="text-[10px] text-gray-400 dark:text-gray-500 mt-0.5">{cat.productCount}+ items</span>
          </Link>
        ))}
      </div>
    </section>
  );
};

export default CategorySection;
