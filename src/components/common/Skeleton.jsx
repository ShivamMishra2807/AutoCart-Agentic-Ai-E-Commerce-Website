import React from 'react';

export const Skeleton = ({ className = '' }) => {
  return <div className={`animate-pulse bg-gray-200 rounded ${className}`} />;
};

export const ProductCardSkeleton = () => {
  return (
    <div className="bg-white rounded-xl p-4 border border-gray-100 shadow-sm space-y-3">
      <Skeleton className="h-44 w-full rounded-lg" />
      <Skeleton className="h-4 w-3/4" />
      <Skeleton className="h-3 w-1/2" />
      <div className="flex justify-between items-center pt-2">
        <Skeleton className="h-6 w-20" />
        <Skeleton className="h-8 w-24 rounded-lg" />
      </div>
    </div>
  );
};

export default Skeleton;
