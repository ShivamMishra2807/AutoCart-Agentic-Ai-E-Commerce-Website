import React from 'react';
import { useSearchParams } from 'react-router-dom';
import ProductGrid from '../../components/product/ProductGrid';
import useProducts from '../../hooks/useProducts';

export const SearchResults = () => {
  const [searchParams] = useSearchParams();
  const query = searchParams.get('q') || '';

  const { products, loading, resetFilters } = useProducts({
    search: query,
  });

  return (
    <div className="space-y-6">
      <div className="border-b pb-4">
        <h1 className="text-2xl font-extrabold text-gray-900 tracking-tight">
          Search Results for "{query}"
        </h1>
        <p className="text-xs text-gray-500 mt-1">
          Found <span className="font-bold">{products.length}</span> matching items
        </p>
      </div>

      <ProductGrid products={products} loading={loading} onResetFilters={resetFilters} />
    </div>
  );
};

export default SearchResults;
