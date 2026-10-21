import React from 'react';
import { Heart } from 'lucide-react';
import { useWishlist } from '../../context/WishlistContext';

export const WishlistButton = ({ product, className = '', size = 'md' }) => {
  const { isInWishlist, toggleWishlist } = useWishlist();
  const saved = isInWishlist(product.id);

  const iconSize = size === 'lg' ? 'w-6 h-6' : size === 'sm' ? 'w-4 h-4' : 'w-5 h-5';

  return (
    <button
      onClick={(e) => {
        e.preventDefault();
        e.stopPropagation();
        toggleWishlist(product);
      }}
      className={`p-2 rounded-full transition-all duration-200 ${
        saved
          ? 'bg-rose-50 text-rose-600 border border-rose-200 shadow-sm'
          : 'bg-white/80 hover:bg-white text-gray-400 hover:text-rose-500 border border-gray-100 shadow-sm'
      } ${className}`}
      title={saved ? 'Remove from Wishlist' : 'Add to Wishlist'}
    >
      <Heart className={`${iconSize} ${saved ? 'fill-rose-600 text-rose-600' : ''}`} />
    </button>
  );
};
