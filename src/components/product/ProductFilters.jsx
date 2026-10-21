import React from 'react';
import { Filter, RotateCcw } from 'lucide-react';
import { categories } from '../../data/categories';

export const ProductFilters = ({ filters = {}, onFilterChange, onResetFilters }) => {
  const brandsList = ['boAt', 'Noise', 'HP', 'OnePlus', 'Sony', 'Allen Solly', 'Biba', 'Puma', 'Prestige', 'Mamaearth'];

  const handleCategoryClick = (catName) => {
    onFilterChange({ category: filters.category === catName ? 'All' : catName });
  };

  const handleBrandToggle = (brandName) => {
    const currentBrands = filters.brand || [];
    const updated = currentBrands.includes(brandName)
      ? currentBrands.filter((b) => b !== brandName)
      : [...currentBrands, brandName];
    onFilterChange({ brand: updated });
  };

  return (
    <div className="bg-white rounded-2xl border border-gray-100 p-5 shadow-sm space-y-6">
      <div className="flex items-center justify-between border-b pb-4">
        <div className="flex items-center gap-2 font-bold text-gray-900">
          <Filter className="w-4 h-4 text-indigo-600" />
          <span>Filter Products</span>
        </div>
        <button
          onClick={onResetFilters}
          className="text-xs text-indigo-600 hover:text-indigo-700 font-semibold flex items-center gap-1"
        >
          <RotateCcw className="w-3 h-3" />
          Reset
        </button>
      </div>

      {/* Category Filter */}
      <div>
        <h4 className="text-xs font-bold text-gray-900 uppercase tracking-wider mb-3">Categories</h4>
        <div className="space-y-1.5 max-h-48 overflow-y-auto pr-1">
          <button
            onClick={() => onFilterChange({ category: 'All' })}
            className={`w-full text-left px-3 py-1.5 text-xs font-medium rounded-lg transition-colors ${
              !filters.category || filters.category === 'All'
                ? 'bg-indigo-50 text-indigo-700 font-bold'
                : 'text-gray-600 hover:bg-gray-50'
            }`}
          >
            All Categories
          </button>
          {categories.map((cat) => (
            <button
              key={cat.id}
              onClick={() => handleCategoryClick(cat.name)}
              className={`w-full text-left px-3 py-1.5 text-xs font-medium rounded-lg transition-colors ${
                filters.category === cat.name
                  ? 'bg-indigo-50 text-indigo-700 font-bold'
                  : 'text-gray-600 hover:bg-gray-50'
              }`}
            >
              {cat.name}
            </button>
          ))}
        </div>
      </div>

      {/* Price Range Filter */}
      <div>
        <h4 className="text-xs font-bold text-gray-900 uppercase tracking-wider mb-3">Price Range (₹)</h4>
        <div className="grid grid-cols-2 gap-2">
          <input
            type="number"
            placeholder="Min"
            value={filters.minPrice || ''}
            onChange={(e) => onFilterChange({ minPrice: e.target.value })}
            className="w-full text-xs px-3 py-2 border rounded-lg focus:ring-1 focus:ring-indigo-500 focus:outline-none"
          />
          <input
            type="number"
            placeholder="Max"
            value={filters.maxPrice || ''}
            onChange={(e) => onFilterChange({ maxPrice: e.target.value })}
            className="w-full text-xs px-3 py-2 border rounded-lg focus:ring-1 focus:ring-indigo-500 focus:outline-none"
          />
        </div>
      </div>

      {/* Brands Filter */}
      <div>
        <h4 className="text-xs font-bold text-gray-900 uppercase tracking-wider mb-3">Popular Brands</h4>
        <div className="space-y-2 max-h-40 overflow-y-auto pr-1">
          {brandsList.map((b) => (
            <label key={b} className="flex items-center gap-2 text-xs text-gray-700 cursor-pointer hover:text-gray-900">
              <input
                type="checkbox"
                checked={(filters.brand || []).includes(b)}
                onChange={() => handleBrandToggle(b)}
                className="rounded text-indigo-600 focus:ring-indigo-500 w-3.5 h-3.5"
              />
              <span>{b}</span>
            </label>
          ))}
        </div>
      </div>

      {/* Minimum Rating */}
      <div>
        <h4 className="text-xs font-bold text-gray-900 uppercase tracking-wider mb-3">Customer Rating</h4>
        <div className="space-y-1.5">
          {[4, 3, 2].map((stars) => (
            <button
              key={stars}
              onClick={() => onFilterChange({ rating: filters.rating === stars ? null : stars })}
              className={`w-full text-left px-3 py-1.5 text-xs font-medium rounded-lg transition-colors ${
                filters.rating === stars
                  ? 'bg-indigo-50 text-indigo-700 font-bold'
                  : 'text-gray-600 hover:bg-gray-50'
              }`}
            >
              ★ {stars} Stars & Above
            </button>
          ))}
        </div>
      </div>

      {/* In Stock Checkbox */}
      <div className="pt-2 border-t">
        <label className="flex items-center gap-2 text-xs font-semibold text-gray-800 cursor-pointer">
          <input
            type="checkbox"
            checked={!!filters.inStockOnly}
            onChange={(e) => onFilterChange({ inStockOnly: e.target.checked })}
            className="rounded text-indigo-600 focus:ring-indigo-500 w-4 h-4"
          />
          <span>In Stock Only</span>
        </label>
      </div>
    </div>
  );
};

export default ProductFilters;
