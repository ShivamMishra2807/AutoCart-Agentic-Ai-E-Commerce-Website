import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { Filter, SlidersHorizontal } from 'lucide-react';
import { ProductFilter } from '../components/product/ProductFilter';
import { ProductSort } from '../components/product/ProductSort';
import { ProductGrid } from '../components/product/ProductGrid';
import { Breadcrumbs } from '../components/common/Breadcrumbs';
import { ProductGridSkeleton } from '../components/common/SkeletonLoader';
import { Pagination } from '../components/common/Pagination';
import { productService } from '../services/productService';
import { useFilter } from '../context/FilterContext';

export const ProductListingPage = () => {
  const [searchParams] = useSearchParams();
  const urlCategory = searchParams.get('category');
  const urlSearch = searchParams.get('search');

  const {
    searchQuery,
    setSearchQuery,
    selectedCategory,
    setSelectedCategory,
    selectedBrands,
    priceRange,
    minRating,
    selectedSort,
    inStockOnly
  } = useFilter();

  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [isMobileFilterOpen, setIsMobileFilterOpen] = useState(false);
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 8;

  // Sync URL params to filter state on mount/change
  useEffect(() => {
    if (urlCategory) setSelectedCategory(urlCategory);
    if (urlSearch) setSearchQuery(urlSearch);
  }, [urlCategory, urlSearch]);

  // Fetch products when filters change
  useEffect(() => {
    const fetchProducts = async () => {
      setLoading(true);
      try {
        const res = await productService.getProducts({
          category: selectedCategory,
          brand: selectedBrands,
          search: searchQuery,
          maxPrice: priceRange[1],
          minRating,
          sort: selectedSort,
          inStock: inStockOnly
        });
        setProducts(res.products || []);
      } catch (err) {
        console.error("Error loading products:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchProducts();
  }, [selectedCategory, selectedBrands, searchQuery, priceRange, minRating, selectedSort, inStockOnly]);

  const totalPages = Math.ceil(products.length / itemsPerPage) || 1;
  const paginatedProducts = products.slice((currentPage - 1) * itemsPerPage, currentPage * itemsPerPage);

  const categoryTitle = selectedCategory === 'all' ? 'All Products' : selectedCategory.toUpperCase();

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
      {/* Breadcrumbs */}
      <Breadcrumbs items={[{ label: 'Catalog' }, { label: categoryTitle }]} />

      {/* Page Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 my-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-black text-gray-900 tracking-tight capitalize">
            {searchQuery ? `Search results for "${searchQuery}"` : `${categoryTitle} Store`}
          </h1>
          <p className="text-xs text-gray-500 font-medium mt-1">
            Discover premier flagship tech, apparel, and lifestyle items with verified buyer ratings.
          </p>
        </div>

        {/* Mobile Filter Toggle Button */}
        <button
          onClick={() => setIsMobileFilterOpen(true)}
          className="lg:hidden flex items-center gap-2 bg-white px-4 py-2 rounded-xl border border-gray-200 text-xs font-bold text-gray-800 shadow-xs"
        >
          <SlidersHorizontal className="w-4 h-4 text-brand-600" />
          <span>Filters & Refine</span>
        </button>
      </div>

      {/* Listing Content (Sidebar Filter + Product Grid) */}
      <div className="flex gap-8 items-start">
        <ProductFilter
          isMobileOpen={isMobileFilterOpen}
          onCloseMobile={() => setIsMobileFilterOpen(false)}
        />

        <div className="flex-1 min-w-0">
          <ProductSort totalCount={products.length} />

          {loading ? (
            <ProductGridSkeleton count={8} />
          ) : (
            <>
              <ProductGrid products={paginatedProducts} />
              {products.length > itemsPerPage && (
                <div className="mt-8 flex justify-center">
                  <Pagination
                    currentPage={currentPage}
                    totalPages={totalPages}
                    onPageChange={(p) => setCurrentPage(p)}
                  />
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
};
