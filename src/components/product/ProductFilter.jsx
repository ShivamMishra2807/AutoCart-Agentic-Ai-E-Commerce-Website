import React from 'react';
import { Filter, RotateCcw, Star, Check } from 'lucide-react';
import { useFilter } from '../../context/FilterContext';
import { MOCK_CATEGORIES } from '../../data/mockCategories';
import { MOCK_PRODUCTS } from '../../data/mockProducts';

const ALL_BRANDS = Array.from(new Set(MOCK_PRODUCTS.map(p => p.brand)));

export const ProductFilter = ({ isMobileOpen, onCloseMobile }) => {
  const {
    selectedCategory,
    setSelectedCategory,
    selectedBrands,
    setSelectedBrands,
    priceRange,
    setPriceRange,
    minRating,
    setMinRating,
    inStockOnly,
    setInStockOnly,
    resetFilters
  } = useFilter();

  const handleBrandChange = (brand) => {
    if (selectedBrands.includes(brand)) {
      setSelectedBrands(selectedBrands.filter(b => b !== brand));
    } else {
      setSelectedBrands([...selectedBrands, brand]);
    }
  };

  const filterContent = (
    <div className="flex flex-col gap-6 p-4 sm:p-0">
      
      {/* Filter Header */}
      <div className="flex justify-between items-center pb-4 border-b border-gray-100">
        <h3 className="font-extrabold text-gray-900 text-base flex items-center gap-2">
          <Filter className="w-4 h-4 text-brand-600" /> Filters
        </h3>
        <button
          onClick={resetFilters}
          className="text-xs font-semibold text-rose-500 hover:text-rose-700 flex items-center gap-1 transition-colors"
        >
          <RotateCcw className="w-3 h-3" /> Reset All
        </button>
      </div>

      {/* Category Filter */}
      <div>
        <h4 className="text-xs font-bold text-gray-900 uppercase tracking-wider mb-3">Categories</h4>
        <div className="flex flex-col gap-1.5 max-h-48 overflow-y-auto hide-scrollbar">
          <button
            onClick={() => setSelectedCategory('all')}
            className={`text-left text-xs px-3 py-1.5 rounded-xl font-medium transition-all ${
              selectedCategory === 'all'
                ? 'bg-brand-50 text-brand-700 font-bold'
                : 'text-gray-600 hover:bg-gray-50'
            }`}
          >
            All Departments
          </button>
          {MOCK_CATEGORIES.map((cat) => (
            <button
              key={cat.id}
              onClick={() => setSelectedCategory(cat.id)}
              className={`text-left text-xs px-3 py-1.5 rounded-xl font-medium transition-all flex justify-between items-center ${
                selectedCategory === cat.id
                  ? 'bg-brand-50 text-brand-700 font-bold'
                  : 'text-gray-600 hover:bg-gray-50'
              }`}
            >
              <span>{cat.name}</span>
              <span className="text-[10px] text-gray-400 font-normal">{cat.itemCount}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Price Range Filter */}
      <div>
        <div className="flex justify-between items-center mb-2">
          <h4 className="text-xs font-bold text-gray-900 uppercase tracking-wider">Price Range</h4>
          <span className="text-xs font-bold text-brand-600">Up to ₹{priceRange[1].toLocaleString()}</span>
        </div>
        <input
          type="range"
          min="500"
          max="200000"
          step="1000"
          value={priceRange[1]}
          onChange={(e) => setPriceRange([0, Number(e.target.value)])}
          className="w-full accent-brand-600 bg-gray-200 rounded-lg h-1.5 cursor-pointer"
        />
        <div className="flex justify-between text-[11px] text-gray-400 font-medium mt-1">
          <span>₹500</span>
          <span>₹2,00,000</span>
        </div>
      </div>

      {/* Brand Checkboxes */}
      <div>
        <h4 className="text-xs font-bold text-gray-900 uppercase tracking-wider mb-3">Brands</h4>
        <div className="flex flex-col gap-2 max-h-40 overflow-y-auto hide-scrollbar">
          {ALL_BRANDS.map((brand) => {
            const isChecked = selectedBrands.includes(brand);
            return (
              <label key={brand} className="flex items-center gap-2.5 text-xs text-gray-700 font-medium cursor-pointer hover:text-brand-600">
                <input
                  type="checkbox"
                  checked={isChecked}
                  onChange={() => handleBrandChange(brand)}
                  className="rounded border-gray-300 text-brand-600 focus:ring-brand-500 w-4 h-4"
                />
                <span>{brand}</span>
              </label>
            );
          })}
        </div>
      </div>

      {/* Minimum Rating */}
      <div>
        <h4 className="text-xs font-bold text-gray-900 uppercase tracking-wider mb-3">Minimum Rating</h4>
        <div className="flex flex-col gap-1.5">
          {[4.5, 4.0, 3.5, 3.0].map((star) => (
            <button
              key={star}
              onClick={() => setMinRating(minRating === star ? 0 : star)}
              className={`flex items-center justify-between text-xs px-3 py-1.5 rounded-xl font-medium border transition-all ${
                minRating === star
                  ? 'bg-amber-50 text-amber-900 border-amber-300 font-bold'
                  : 'border-gray-100 text-gray-600 hover:bg-gray-50'
              }`}
            >
              <div className="flex items-center gap-1 text-amber-500">
                <span>{star}</span>
                <Star className="w-3.5 h-3.5 fill-amber-400" />
                <span className="text-gray-500 font-normal ml-1">& Above</span>
              </div>
              {minRating === star && <Check className="w-3.5 h-3.5 text-amber-600" />}
            </button>
          ))}
        </div>
      </div>

      {/* In Stock Only */}
      <div className="pt-2 border-t border-gray-100">
        <label className="flex items-center justify-between text-xs font-semibold text-gray-800 cursor-pointer">
          <span>In Stock Only</span>
          <input
            type="checkbox"
            checked={inStockOnly}
            onChange={(e) => setInStockOnly(e.target.checked)}
            className="rounded border-gray-300 text-brand-600 focus:ring-brand-500 w-4 h-4"
          />
        </label>
      </div>

    </div>
  );

  return (
    <>
      {/* Desktop Sidebar */}
      <aside className="hidden lg:block w-64 shrink-0 bg-white rounded-3xl p-6 border border-gray-100 shadow-sm sticky top-24 self-start">
        {filterContent}
      </aside>

      {/* Mobile Drawer Filter */}
      {isMobileOpen && (
        <div className="lg:hidden fixed inset-0 z-50 bg-black/50 backdrop-blur-sm flex justify-end">
          <div className="w-full max-w-xs bg-white h-full overflow-y-auto p-4 shadow-2xl flex flex-col justify-between">
            {filterContent}
            <button
              onClick={onCloseMobile}
              className="mt-6 w-full py-3 bg-brand-600 text-white text-xs font-bold rounded-2xl"
            >
              Apply Filters
            </button>
          </div>
        </div>
      )}
    </>
  );
};
