import React from 'react';
import { Star } from 'lucide-react';

export const Rating = ({ rating = 0, reviewCount, size = 'sm', showBadge = true }) => {
  const iconSize = size === 'lg' ? 'w-5 h-5' : size === 'md' ? 'w-4 h-4' : 'w-3.5 h-3.5';

  return (
    <div className="flex items-center gap-1.5">
      <div className="flex items-center gap-1 bg-emerald-600 text-white text-xs font-semibold px-2 py-0.5 rounded">
        <span>{rating.toFixed(1)}</span>
        <Star className={`${iconSize} fill-white text-white`} />
      </div>
      {reviewCount !== undefined && (
        <span className="text-xs text-gray-500 font-medium">
          ({reviewCount.toLocaleString()})
        </span>
      )}
    </div>
  );
};
