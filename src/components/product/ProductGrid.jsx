import React from 'react';
import ProductCard from './ProductCard';
import { ProductCardSkeleton } from '../common/Skeleton';
import EmptyState from '../common/EmptyState';
import { PackageSearch } from 'lucide-react';

export const ProductGrid = ({ products = [], loading = false, onResetFilters }) => {
  if (loading) {
    return (
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 sm:gap-6">
        {Array.from({ length: 8 }).map((_, index) => (
          <ProductCardSkeleton key={index} />
        ))}
      </div>
    );
  }

  if (products.length === 0) {
    return (
      <EmptyState
        icon={PackageSearch}
        title="No products found"
        description="Try clearing filters or searching with different keywords."
        actionText="Clear All Filters"
        onAction={onResetFilters}
        className="py-16"
      />
    );
  }

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 sm:gap-6">
      {products.map((product) => (
        <ProductCard key={product.id} product={product} />
      ))}
    </div>
  );
};

export default ProductGrid;
