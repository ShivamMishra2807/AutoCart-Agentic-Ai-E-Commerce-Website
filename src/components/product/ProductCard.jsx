import React from 'react';
import { Heart, ShoppingBag, Check, Zap, Star } from 'lucide-react';
import { Link } from 'react-router-dom';
import formatPrice from '../../utils/formatPrice';
import { useCart } from '../../hooks/useCart';
import { useWishlist } from '../../hooks/useWishlist';
import Badge from '../common/Badge';

export const ProductCard = ({ product }) => {
  const { addToCart, cartItems } = useCart();
  const { isInWishlist, toggleWishlist } = useWishlist();

  const isCartAdded = cartItems.some((item) => item.id === product.id);
  const isWishlisted = isInWishlist(product.id);

  return (
    <div className="group relative bg-white rounded-2xl border border-gray-100 shadow-sm hover:shadow-xl hover:border-indigo-200 transition-all duration-300 flex flex-col h-full overflow-hidden">
      {/* Product Image & Badges */}
      <div className="relative w-full pt-[85%] bg-gray-50 overflow-hidden">
        <Link to={`/products/${product.id}`} className="absolute inset-0 flex items-center justify-center p-4">
          <img
            src={product.images && product.images[0] ? product.images[0] : 'https://images.unsplash.com/photo-1526170375885-4d8ecf77b99f?w=600&q=80'}
            alt={product.name}
            className="max-h-full max-w-full object-contain group-hover:scale-105 transition-transform duration-300"
            loading="lazy"
            onError={(e) => {
              e.currentTarget.onerror = null;
              e.currentTarget.src = 'https://images.unsplash.com/photo-1526170375885-4d8ecf77b99f?w=600&q=80';
            }}
          />
        </Link>

        {/* Top Badges (Discount + Assured) */}
        <div className="absolute top-3 left-3 flex flex-col gap-1.5 pointer-events-none">
          {product.discount > 0 && (
            <span className="bg-rose-500 text-white font-extrabold text-[10px] px-2 py-0.5 rounded-md shadow flex items-center gap-1 w-max">
              <Zap className="w-2.5 h-2.5 fill-white" /> {product.discount}% OFF
            </span>
          )}
          {product.bestSeller && (
            <span className="bg-amber-500 text-white font-bold text-[9px] px-1.5 py-0.5 rounded shadow w-max">
              BESTSELLER
            </span>
          )}
        </div>

        {/* Wishlist Action Button */}
        <button
          onClick={() => toggleWishlist(product)}
          className={`absolute top-3 right-3 p-2 rounded-full shadow-md transition-all z-10 ${
            isWishlisted
              ? 'bg-rose-50 text-rose-500'
              : 'bg-white/90 text-gray-400 hover:text-rose-500 hover:bg-white'
          }`}
          title={isWishlisted ? 'Remove from wishlist' : 'Add to wishlist'}
        >
          <Heart className={`w-4 h-4 ${isWishlisted ? 'fill-rose-500 text-rose-500' : ''}`} />
        </button>
      </div>

      {/* Product Details */}
      <div className="p-4 flex flex-col flex-1 justify-between">
        <div>
          {/* Brand & Stock Status */}
          <div className="flex items-center justify-between text-xs text-gray-400 font-semibold mb-1">
            <span className="uppercase tracking-wider font-bold text-indigo-600">{product.brand}</span>
            {product.stockStatus === 'Low Stock' && (
              <Badge variant="yellow">Only {product.stock} left</Badge>
            )}
            {product.stockStatus === 'Out of Stock' && (
              <Badge variant="red">Out of Stock</Badge>
            )}
          </div>

          {/* Product Name */}
          <Link
            to={`/products/${product.id}`}
            className="block text-sm font-bold text-gray-900 group-hover:text-indigo-600 line-clamp-2 leading-snug mb-2 transition-colors"
          >
            {product.name}
          </Link>

          {/* Flipkart style Rating Pill */}
          <div className="flex items-center gap-2 mb-2.5">
            <span className="inline-flex items-center gap-1 bg-emerald-600 text-white text-[11px] font-extrabold px-1.5 py-0.5 rounded">
              {product.rating || 4.2} <Star className="w-2.5 h-2.5 fill-white" />
            </span>
            <span className="text-[11px] text-gray-400">
              ({product.reviewCount ? Number(product.reviewCount).toLocaleString() : '1,200'})
            </span>
            <span className="text-[10px] font-bold text-blue-600 ml-auto flex items-center gap-0.5">
              ✦ Assured
            </span>
          </div>

          {/* Delivery Tag */}
          <div className="text-[11px] text-emerald-600 font-semibold mb-2">
            Free Delivery by <strong>Tomorrow</strong>
          </div>
        </div>

        {/* Price & Cart CTA */}
        <div className="pt-3 border-t border-gray-100 flex items-center justify-between mt-auto">
          <div>
            <div className="text-base font-extrabold text-gray-900 leading-none">
              {formatPrice(product.price)}
            </div>
            {product.originalPrice > product.price && (
              <div className="text-xs text-gray-400 line-through mt-0.5">
                {formatPrice(product.originalPrice)}
              </div>
            )}
          </div>

          <button
            disabled={product.stock === 0}
            onClick={() => addToCart(product)}
            className={`p-2.5 rounded-xl font-medium transition-all ${
              isCartAdded
                ? 'bg-emerald-50 text-emerald-600 border border-emerald-200'
                : product.stock === 0
                ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                : 'bg-indigo-600 text-white hover:bg-indigo-700 shadow-md shadow-indigo-600/20 active:scale-95'
            }`}
            title={product.stock === 0 ? 'Out of Stock' : isCartAdded ? 'Added to Cart' : 'Add to Cart'}
          >
            {isCartAdded ? <Check className="w-4 h-4 text-emerald-600" /> : <ShoppingBag className="w-4 h-4" />}
          </button>
        </div>
      </div>
    </div>
  );
};

export default ProductCard;
