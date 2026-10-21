import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import ProductGrid from '../../components/product/ProductGrid';
import ProductFilters from '../../components/product/ProductFilters';
import SortDropdown from '../../components/product/SortDropdown';
import Pagination from '../../components/common/Pagination';
import useProducts from '../../hooks/useProducts';
import { Filter, X, LayoutGrid, List } from 'lucide-react';

export const Products = () => {
  const [searchParams] = useSearchParams();
  const categoryParam = searchParams.get('category') || 'All';
  const sortParam = searchParams.get('sortBy') || 'popularity';

  const [mobileFilterOpen, setMobileFilterOpen] = useState(false);
  const [viewMode, setViewMode] = useState('grid');
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 12;

  const { products, loading, filters, updateFilters, resetFilters } = useProducts({
    category: categoryParam,
    sortBy: sortParam,
  });

  useEffect(() => {
    if (categoryParam) {
      updateFilters({ category: categoryParam });
    }
  }, [categoryParam]);

  const totalPages = Math.ceil(products.length / itemsPerPage);
  const paginatedProducts = products.slice(
    (currentPage - 1) * itemsPerPage,
    currentPage * itemsPerPage
  );

  return (
    <div className="space-y-6">
      {/* Header with Title & View Toggles */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between border-b border-gray-200 pb-4 gap-4">
        <div>
          <h1 className="text-2xl font-extrabold text-gray-900 tracking-tight">
            {filters.category && filters.category !== 'All' ? filters.category : 'All Products & Categories'}
          </h1>
          <p className="text-xs text-gray-500 mt-1">
            Showing <span className="font-semibold text-indigo-600">{products.length}</span> verified items
          </p>
        </div>

        <div className="flex items-center gap-3 justify-between sm:justify-end">
          {/* Mobile Filter Button */}
          <button
            onClick={() => setMobileFilterOpen(true)}
            className="lg:hidden flex items-center gap-2 text-xs font-bold px-3 py-2 border border-gray-200 rounded-xl bg-white text-gray-700 shadow-sm"
          >
            <Filter className="w-4 h-4 text-indigo-600" /> Filter
          </button>

          {/* View Mode Toggle (Grid vs List) */}
          <div className="hidden sm:flex items-center border border-gray-200 rounded-xl p-1 bg-white shadow-sm">
            <button
              onClick={() => setViewMode('grid')}
              className={`p-1.5 rounded-lg transition ${
                viewMode === 'grid'
                  ? 'bg-indigo-600 text-white shadow'
                  : 'text-gray-500 hover:text-gray-900'
              }`}
              title="Grid View"
            >
              <LayoutGrid className="w-4 h-4" />
            </button>
            <button
              onClick={() => setViewMode('list')}
              className={`p-1.5 rounded-lg transition ${
                viewMode === 'list'
                  ? 'bg-indigo-600 text-white shadow'
                  : 'text-gray-500 hover:text-gray-900'
              }`}
              title="List View"
            >
              <List className="w-4 h-4" />
            </button>
          </div>

          {/* Sort Dropdown */}
          <SortDropdown
            value={filters.sortBy || 'popularity'}
            onChange={(val) => updateFilters({ sortBy: val })}
          />
        </div>
      </div>

      {/* Main Grid + Filter Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
        {/* Desktop Filters */}
        <div className="hidden lg:block lg:col-span-1">
          <ProductFilters
            filters={filters}
            onFilterChange={updateFilters}
            onResetFilters={resetFilters}
          />
        </div>

        {/* Product Grid */}
        <div className="lg:col-span-3">
          <ProductGrid
            products={paginatedProducts}
            loading={loading}
            onResetFilters={resetFilters}
          />
          <Pagination
            currentPage={currentPage}
            totalPages={totalPages}
            onPageChange={setCurrentPage}
          />
        </div>
      </div>

      {/* Mobile Drawer Filter */}
      {mobileFilterOpen && (
        <div className="fixed inset-0 z-50 overflow-y-auto bg-gray-900/50 backdrop-blur-sm lg:hidden flex justify-end">
          <div className="w-full max-w-xs bg-white min-h-screen p-5 shadow-2xl space-y-4">
            <div className="flex items-center justify-between border-b border-gray-100 pb-3">
              <h3 className="font-bold text-gray-900 text-sm">Filter Catalogue</h3>
              <button onClick={() => setMobileFilterOpen(false)} className="p-1 text-gray-400">
                <X className="w-5 h-5" />
              </button>
            </div>
            <ProductFilters
              filters={filters}
              onFilterChange={(newF) => {
                updateFilters(newF);
                setMobileFilterOpen(false);
              }}
              onResetFilters={() => {
                resetFilters();
                setMobileFilterOpen(false);
              }}
            />
          </div>
        </div>
      )}
    </div>
  );
};

export default Products;
