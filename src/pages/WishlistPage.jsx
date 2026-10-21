import React from 'react';
import { Link } from 'react-router-dom';
import { Heart, ShoppingBag, Trash2 } from 'lucide-react';
import { useWishlist } from '../context/WishlistContext';
import { ProductCard } from '../components/product/ProductCard';
import { Breadcrumbs } from '../components/common/Breadcrumbs';

export const WishlistPage = () => {
  const { wishlistItems, wishlistCount, removeFromWishlist, moveToCart } = useWishlist();

  if (wishlistCount === 0) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-16 text-center flex flex-col items-center justify-center gap-4 min-h-[60vh]">
        <div className="w-20 h-20 rounded-full bg-rose-50 text-rose-500 flex items-center justify-center shadow-inner">
          <Heart className="w-10 h-10" />
        </div>
        <h2 className="text-2xl sm:text-3xl font-black text-gray-900 tracking-tight">Your Wishlist is Empty</h2>
        <p className="text-xs sm:text-sm text-gray-500 max-w-md">
          Save your favorite flagship items here for later price drops or quick purchase anytime!
        </p>
        <Link
          to="/products"
          className="mt-2 px-8 py-3.5 bg-brand-600 hover:bg-brand-700 text-white rounded-2xl font-extrabold text-xs shadow-lg shadow-brand-500/20 transition-all hover:scale-105"
        >
          Discover Products
        </Link>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-6">
      <Breadcrumbs items={[{ label: 'Saved Wishlist' }]} />

      <div className="flex justify-between items-center pb-2 border-b border-gray-100">
        <div>
          <h1 className="text-2xl sm:text-3xl font-black text-gray-900 tracking-tight">
            My Wishlist ({wishlistCount} {wishlistCount === 1 ? 'Item' : 'Items'})
          </h1>
          <p className="text-xs text-gray-500 font-medium mt-0.5">
            Your saved shortlist. Move items to cart whenever you are ready to buy.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 xl:grid-cols-4 gap-6">
        {wishlistItems.map((product) => (
          <div key={product.id} className="relative flex flex-col">
            <ProductCard product={product} />
            <div className="flex gap-2 mt-2">
              <button
                onClick={() => moveToCart(product)}
                className="flex-1 py-2 bg-brand-600 hover:bg-brand-700 text-white rounded-xl text-xs font-bold flex items-center justify-center gap-1.5 transition-colors shadow-sm"
              >
                <ShoppingBag className="w-3.5 h-3.5" /> Move to Cart
              </button>
              <button
                onClick={() => removeFromWishlist(product.id)}
                className="p-2 bg-gray-100 hover:bg-rose-50 text-gray-500 hover:text-rose-600 rounded-xl transition-colors"
                title="Remove from wishlist"
              >
                <Trash2 className="w-4 h-4" />
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
