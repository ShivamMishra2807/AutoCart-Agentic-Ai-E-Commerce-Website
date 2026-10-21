import React from 'react';

export const SortDropdown = ({ value = 'popularity', onChange }) => {
  return (
    <div className="flex items-center gap-2">
      <label className="text-xs font-semibold text-gray-500 whitespace-nowrap hidden sm:inline">Sort By:</label>
      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="text-xs font-semibold bg-white border border-gray-200 rounded-lg px-3 py-2 text-gray-700 focus:outline-none focus:ring-1 focus:ring-indigo-500 shadow-sm cursor-pointer"
      >
        <option value="popularity">Popularity (Most Popular)</option>
        <option value="price_low_high">Price: Low to High</option>
        <option value="price_high_low">Price: High to Low</option>
        <option value="rating">Highest Rated</option>
        <option value="newest">Newest Arrivals</option>
      </select>
    </div>
  );
};

export default SortDropdown;
