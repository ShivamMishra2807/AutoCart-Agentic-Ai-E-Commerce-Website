import React from 'react';
import { useNavigate } from 'react-router-dom';
import { MOCK_CATEGORIES } from '../../data/mockCategories';
import { useFilter } from '../../context/FilterContext';
import { ArrowRight } from 'lucide-react';

export const TopCategories = () => {
  const navigate = useNavigate();
  const { setSelectedCategory } = useFilter();

  const handleCategorySelect = (catId) => {
    setSelectedCategory(catId);
    navigate(`/products?category=${catId}`);
  };

  return (
    <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="flex justify-between items-end mb-6">
        <div>
          <h2 className="text-xl sm:text-2xl font-extrabold text-gray-900 tracking-tight">
            Explore Top Categories
          </h2>
          <p className="text-xs sm:text-sm text-gray-500 font-medium mt-1">
            Browse through our wide range of premium curated departments
          </p>
        </div>

        <button
          onClick={() => {
            setSelectedCategory('all');
            navigate('/products');
          }}
          className="flex items-center gap-1 text-xs sm:text-sm font-bold text-brand-600 hover:text-brand-700 transition-colors"
        >
          <span>View All</span>
          <ArrowRight className="w-4 h-4" />
        </button>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-9 gap-4">
        {MOCK_CATEGORIES.map((cat) => (
          <div
            key={cat.id}
            onClick={() => handleCategorySelect(cat.id)}
            className="group bg-white rounded-2xl p-3 border border-gray-100 shadow-sm hover:shadow-md hover:border-brand-300 transition-all cursor-pointer flex flex-col items-center text-center"
          >
            <div className="w-14 h-14 sm:w-16 sm:h-16 rounded-full overflow-hidden mb-2 bg-gray-100 border border-gray-100 group-hover:scale-105 transition-transform">
              <img src={cat.image} alt={cat.name} className="w-full h-full object-cover" />
            </div>
            <h3 className="text-xs font-bold text-gray-800 group-hover:text-brand-600 transition-colors line-clamp-1">
              {cat.name}
            </h3>
            <span className="text-[10px] text-gray-400 font-medium">
              {cat.itemCount}+ Items
            </span>
          </div>
        ))}
      </div>
    </section>
  );
};
