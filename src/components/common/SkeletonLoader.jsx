import React from 'react';

export const ProductCardSkeleton = () => {
  return (
    <div className="bg-white rounded-2xl border border-gray-100 p-4 animate-pulse flex flex-col gap-3">
      <div className="w-full h-48 bg-gray-200 rounded-xl"></div>
      <div className="h-4 bg-gray-200 rounded w-1/3"></div>
      <div className="h-5 bg-gray-200 rounded w-3/4"></div>
      <div className="h-4 bg-gray-200 rounded w-1/2"></div>
      <div className="flex justify-between items-center pt-2">
        <div className="h-6 bg-gray-200 rounded w-24"></div>
        <div className="h-8 bg-gray-200 rounded-lg w-20"></div>
      </div>
    </div>
  );
};

export const ProductGridSkeleton = ({ count = 8 }) => {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
      {Array.from({ length: count }).map((_, i) => (
        <ProductCardSkeleton key={i} />
      ))}
    </div>
  );
};

export const ProductDetailSkeleton = () => {
  return (
    <div className="max-w-7xl mx-auto px-4 py-8 animate-pulse grid grid-cols-1 md:grid-cols-2 gap-8">
      <div className="flex flex-col gap-4">
        <div className="w-full h-[400px] bg-gray-200 rounded-2xl"></div>
        <div className="flex gap-3">
          {Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="w-20 h-20 bg-gray-200 rounded-xl"></div>
          ))}
        </div>
      </div>
      <div className="flex flex-col gap-4">
        <div className="h-4 bg-gray-200 rounded w-1/4"></div>
        <div className="h-8 bg-gray-200 rounded w-3/4"></div>
        <div className="h-6 bg-gray-200 rounded w-1/3"></div>
        <div className="h-10 bg-gray-200 rounded w-1/2"></div>
        <div className="h-20 bg-gray-200 rounded-xl"></div>
        <div className="flex gap-4 pt-4">
          <div className="h-12 bg-gray-200 rounded-xl w-1/2"></div>
          <div className="h-12 bg-gray-200 rounded-xl w-1/2"></div>
        </div>
      </div>
    </div>
  );
};
