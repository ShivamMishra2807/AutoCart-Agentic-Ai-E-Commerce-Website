import React from 'react';
import { Star } from 'lucide-react';

export const ProductRating = ({ rating = 0, reviewCount, showCount = true, size = 'sm' }) => {
  const stars = Array.from({ length: 5 }, (_, i) => i + 1);
  const sizeClasses = size === 'lg' ? 'w-5 h-5' : size === 'md' ? 'w-4 h-4' : 'w-3.5 h-3.5';

  return (
    <div className="flex items-center gap-1.5">
      <div className="flex items-center gap-0.5">
        {stars.map((star) => (
          <Star
            key={star}
            className={`${sizeClasses} ${
              star <= Math.floor(rating)
                ? 'text-amber-400 fill-amber-400'
                : star - rating < 1
                ? 'text-amber-400 fill-amber-200'
                : 'text-gray-300'
            }`}
          />
        ))}
      </div>
      <span className="text-xs font-semibold text-gray-700">{rating.toFixed(1)}</span>
      {showCount && reviewCount !== undefined && (
        <span className="text-xs text-gray-400">({reviewCount.toLocaleString('en-IN')})</span>
      )}
    </div>
  );
};

export default ProductRating;
