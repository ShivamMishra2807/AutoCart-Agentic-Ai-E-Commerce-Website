import React, { useState, useRef } from 'react';
import { Heart, Share2, Maximize2, Zap } from 'lucide-react';
import { useWishlist } from '../../hooks/useWishlist';

export const ProductImages = ({ images = [], productName = 'Product', product = null }) => {
  const [selectedImage, setSelectedImage] = useState(0);
  const [isZooming, setIsZooming] = useState(false);
  const [zoomPosition, setZoomPosition] = useState({ x: 0, y: 0 });
  const [copied, setCopied] = useState(false);
  const imageRef = useRef(null);

  const { isInWishlist, toggleWishlist } = useWishlist();
  const isWishlisted = product ? isInWishlist(product.id) : false;

  const displayImages = images && images.length > 0
    ? images
    : ['https://images.unsplash.com/photo-1560343090-f0409e92791a?w=600&q=80'];

  const handleMouseMove = (e) => {
    if (!imageRef.current) return;
    const { left, top, width, height } = imageRef.current.getBoundingClientRect();
    const x = ((e.clientX - left) / width) * 100;
    const y = ((e.clientY - top) / height) * 100;
    setZoomPosition({ x: Math.max(0, Math.min(100, x)), y: Math.max(0, Math.min(100, y)) });
  };

  const handleShare = () => {
    navigator.clipboard?.writeText(window.location.href);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="flex flex-col-reverse md:flex-row gap-4">
      {/* Thumbnails strip (Vertical on desktop like Flipkart/Amazon) */}
      {displayImages.length > 1 && (
        <div className="flex md:flex-col gap-2.5 overflow-x-auto md:overflow-y-auto max-h-[460px] pb-2 md:pb-0 scrollbar-thin">
          {displayImages.map((img, index) => (
            <button
              key={index}
              onMouseEnter={() => setSelectedImage(index)}
              onClick={() => setSelectedImage(index)}
              className={`w-16 h-16 sm:w-20 sm:h-20 rounded-xl border-2 overflow-hidden bg-white shrink-0 p-1.5 transition-all duration-200 ${
                selectedImage === index
                  ? 'border-indigo-600 ring-2 ring-indigo-200 scale-105 shadow-md'
                  : 'border-gray-200 hover:border-gray-400 opacity-75 hover:opacity-100'
              }`}
            >
              <img
                src={img}
                alt={`Thumbnail ${index + 1}`}
                className="w-full h-full object-contain"
                loading="lazy"
                onError={(e) => {
                  e.currentTarget.onerror = null;
                  e.currentTarget.src = 'https://images.unsplash.com/photo-1526170375885-4d8ecf77b99f?w=600&q=80';
                }}
              />
            </button>
          ))}
        </div>
      )}

      {/* Main Showcase Image with Zoom Lens */}
      <div className="relative flex-1 bg-white rounded-3xl border border-gray-100 p-6 flex items-center justify-center overflow-hidden min-h-[360px] sm:min-h-[460px] shadow-sm">
        {/* Badges on Image */}
        <div className="absolute top-4 left-4 z-10 flex flex-col gap-2 pointer-events-none">
          <span className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white font-extrabold text-[11px] px-2.5 py-1 rounded-lg shadow-md flex items-center gap-1">
            <Zap className="w-3 h-3 fill-white" /> Plus Assured
          </span>
          {product?.bestSeller && (
            <span className="bg-amber-500 text-white font-bold text-[10px] px-2 py-0.5 rounded shadow">
              #1 Best Seller
            </span>
          )}
        </div>

        {/* Quick Actions (Share & Wishlist) */}
        <div className="absolute top-4 right-4 z-10 flex flex-col gap-2">
          {product && (
            <button
              onClick={() => toggleWishlist(product)}
              className={`p-2.5 rounded-full shadow-md backdrop-blur-sm transition-all ${
                isWishlisted
                  ? 'bg-rose-50 text-rose-500 shadow-rose-500/20'
                  : 'bg-white/90 text-gray-500 hover:text-rose-500 hover:bg-white'
              }`}
              title={isWishlisted ? 'Saved to Wishlist' : 'Add to Wishlist'}
            >
              <Heart className={`w-5 h-5 ${isWishlisted ? 'fill-rose-500 text-rose-500' : ''}`} />
            </button>
          )}

          <button
            onClick={handleShare}
            className="p-2.5 rounded-full bg-white/90 text-gray-500 hover:text-indigo-600 hover:bg-white shadow-md backdrop-blur-sm transition-all"
            title="Share this product"
          >
            <Share2 className="w-5 h-5" />
          </button>
        </div>

        {copied && (
          <div className="absolute bottom-4 left-1/2 -translate-x-1/2 bg-gray-900 text-white text-xs font-semibold py-1.5 px-3.5 rounded-full shadow-lg z-20 animate-fade-in">
            ✓ Link copied to clipboard!
          </div>
        )}

        {/* The Image with Hover Zoom */}
        <div
          ref={imageRef}
          onMouseEnter={() => setIsZooming(true)}
          onMouseLeave={() => setIsZooming(false)}
          onMouseMove={handleMouseMove}
          className="w-full h-full max-h-[420px] flex items-center justify-center cursor-crosshair relative"
        >
          <img
            src={displayImages[selectedImage]}
            alt={productName}
            onError={(e) => {
              e.currentTarget.onerror = null;
              e.currentTarget.src = 'https://images.unsplash.com/photo-1526170375885-4d8ecf77b99f?w=600&q=80';
            }}
            className={`max-h-[420px] max-w-full object-contain transition-transform duration-200 select-none ${
              isZooming ? 'opacity-0 md:opacity-100' : 'opacity-100'
            }`}
          />

          {/* Flipkart / Amazon style Zoom Glass Window */}
          {isZooming && (
            <div
              className="hidden md:block absolute inset-0 rounded-2xl pointer-events-none bg-no-repeat bg-white border border-indigo-200 shadow-2xl z-20"
              style={{
                backgroundImage: `url(${displayImages[selectedImage]})`,
                backgroundPosition: `${zoomPosition.x}% ${zoomPosition.y}%`,
                backgroundSize: '240%',
              }}
            />
          )}
        </div>

        {/* Visual Zoom Hint */}
        <div className="absolute bottom-3 right-4 hidden md:flex items-center gap-1.5 text-[11px] text-gray-400 font-medium pointer-events-none">
          <Maximize2 className="w-3.5 h-3.5" /> Hover image to zoom in
        </div>
      </div>
    </div>
  );
};

export default ProductImages;
