import React, { createContext, useContext, useState, useEffect } from 'react';

const FilterContext = createContext(null);

export const FilterProvider = ({ children }) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [selectedBrands, setSelectedBrands] = useState([]);
  const [priceRange, setPriceRange] = useState([0, 200000]);
  const [minRating, setMinRating] = useState(0);
  const [selectedSort, setSelectedSort] = useState('relevance');
  const [inStockOnly, setInStockOnly] = useState(false);
  const [flashDealsOnly, setFlashDealsOnly] = useState(false);

  // Search History State
  const [searchHistory, setSearchHistory] = useState(() => {
    try {
      const stored = localStorage.getItem('auracart_search_history');
      return stored ? JSON.parse(stored) : ['Sony Headphones', 'iPhone 15', 'Gaming Laptop', 'Nike Shoes'];
    } catch {
      return ['Sony Headphones', 'iPhone 15'];
    }
  });

  useEffect(() => {
    localStorage.setItem('auracart_search_history', JSON.stringify(searchHistory));
  }, [searchHistory]);

  const addSearchTerm = (term) => {
    if (!term || !term.trim()) return;
    const clean = term.trim();
    setSearchHistory(prev => [clean, ...prev.filter(t => t.toLowerCase() !== clean.toLowerCase())].slice(0, 8));
  };

  const clearSearchHistory = () => {
    setSearchHistory([]);
    localStorage.removeItem('auracart_search_history');
  };

  const removeSearchHistoryItem = (item) => {
    setSearchHistory(prev => prev.filter(i => i !== item));
  };

  const resetFilters = () => {
    setSearchQuery('');
    setSelectedCategory('all');
    setSelectedBrands([]);
    setPriceRange([0, 200000]);
    setMinRating(0);
    setSelectedSort('relevance');
    setInStockOnly(false);
    setFlashDealsOnly(false);
  };

  return (
    <FilterContext.Provider
      value={{
        searchQuery,
        setSearchQuery,
        selectedCategory,
        setSelectedCategory,
        selectedBrands,
        setSelectedBrands,
        priceRange,
        setPriceRange,
        minRating,
        setMinRating,
        selectedSort,
        setSelectedSort,
        inStockOnly,
        setInStockOnly,
        flashDealsOnly,
        setFlashDealsOnly,
        searchHistory,
        addSearchTerm,
        clearSearchHistory,
        removeSearchHistoryItem,
        resetFilters
      }}
    >
      {children}
    </FilterContext.Provider>
  );
};

export const useFilter = () => {
  const context = useContext(FilterContext);
  if (!context) throw new Error("useFilter must be used within FilterProvider");
  return context;
};
