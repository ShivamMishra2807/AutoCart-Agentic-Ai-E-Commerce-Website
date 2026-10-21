import React from 'react';
import { ArrowUpDown } from 'lucide-react';
import { useFilter } from '../../context/FilterContext';

export const ProductSort = ({ totalCount }) => {
  const { selectedSort, setSelectedSort } = useFilter();

  return (
    <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3 bg-white p-4 rounded-2xl border border-gray-100 shadow-xs mb-6">
      <div className="text-xs sm:text-sm text-gray-500 font-medium">
        Showing <span className="font-extrabold text-gray-900">{totalCount}</span> products
      </div>

      <div className="flex items-center gap-2 self-end sm:self-auto">
        <label htmlFor="sort-select" className="text-xs font-semibold text-gray-500 flex items-center gap-1">
          <ArrowUpDown className="w-3.5 h-3.5 text-gray-400" /> Sort By:
        </label>
        <select
          id="sort-select"
          value={selectedSort}
          onChange={(e) => setSelectedSort(e.target.value)}
          className="bg-gray-50 border border-gray-200 text-xs font-bold text-gray-800 rounded-xl px-3 py-1.5 focus:border-brand-500 focus:ring-0 cursor-pointer"
        >
          <option value="relevance">Relevance</option>
          <option value="price-low">Price: Low to High</option>
          <option value="price-high">Price: High to Low</option>
          <option value="rating">Highest Rated</option>
          <option value="popularity">Most Popular</option>
          <option value="newest">Newest Arrivals</option>
        </select>
      </div>
    </div>
  );
};
