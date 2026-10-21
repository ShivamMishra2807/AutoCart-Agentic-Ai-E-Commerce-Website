import React from 'react';
import ProductCard from './ProductCard';

export const RelatedProducts = ({ currentProduct, allProducts = [] }) => {
  const related = allProducts
    .filter((p) => p.category === currentProduct.category && p.id !== currentProduct.id)
    .slice(0, 4);

  if (related.length === 0) return null;

  return (
    <section className="mt-16 pt-8 border-t border-gray-200">
      <h3 className="text-xl font-extrabold text-gray-900 mb-6">
        Similar Products You Might Like
      </h3>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        {related.map((prod) => (
          <ProductCard key={prod.id} product={prod} />
        ))}
      </div>
    </section>
  );
};

export default RelatedProducts;
