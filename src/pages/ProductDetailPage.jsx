import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { 
  ShoppingBag, 
  Heart, 
  Truck, 
  ShieldCheck, 
  Zap, 
  Check, 
  Star, 
  Share2, 
  Plus, 
  Minus,
  Sparkles,
  ChevronRight,
  ArrowRight
} from 'lucide-react';
import { productService } from '../services/productService';
import { useCart } from '../context/CartContext';
import { useWishlist } from '../context/WishlistContext';
import { Rating } from '../components/common/Rating';
import { PriceDisplay } from '../components/common/PriceDisplay';
import { Breadcrumbs } from '../components/common/Breadcrumbs';
import { ProductDetailSkeleton } from '../components/common/SkeletonLoader';
import { ProductSection } from '../components/home/ProductSection';
import { useToast } from '../context/ToastContext';

export const ProductDetailPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { addToCart } = useCart();
  const { isInWishlist, toggleWishlist } = useWishlist();
  const { addToast } = useToast();

  const [product, setProduct] = useState(null);
  const [loading, setLoading] = useState(true);
  const [selectedImage, setSelectedImage] = useState('');
  const [selectedColor, setSelectedColor] = useState('');
  const [selectedSize, setSelectedSize] = useState('');
  const [quantity, setQuantity] = useState(1);
  const [pincode, setPincode] = useState('201301');
  const [pincodeChecked, setPincodeChecked] = useState(false);
  const [activeTab, setActiveTab] = useState('specs'); // 'specs' | 'reviews'
  const [relatedProducts, setRelatedProducts] = useState([]);

  useEffect(() => {
    const fetchProductData = async () => {
      setLoading(true);
      try {
        const prod = await productService.getProductById(id);
        setProduct(prod);
        setSelectedImage(prod.images?.[0] || '');
        setSelectedColor(prod.colors?.[0] || '');
        setSelectedSize(prod.sizes?.[0] || '');

        // Fetch related products in category
        const relRes = await productService.getProducts({ category: prod.category });
        setRelatedProducts(relRes.products.filter(p => p.id !== id).slice(0, 4));
      } catch (err) {
        console.error("Error fetching PDP:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchProductData();
  }, [id]);

  if (loading) return <ProductDetailSkeleton />;
  if (!product) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-16 text-center">
        <h2 className="text-2xl font-bold text-gray-900">Product Not Found</h2>
        <p className="text-gray-500 mt-2">The requested product could not be located in our catalog.</p>
        <Link to="/products" className="inline-block mt-4 px-6 py-2.5 bg-brand-600 text-white rounded-xl font-bold text-xs">
          Back to Shop
        </Link>
      </div>
    );
  }

  const isSaved = isInWishlist(product.id);

  const handleBuyNow = () => {
    addToCart(product, quantity, selectedColor, selectedSize);
    navigate('/checkout');
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-12">
      {/* Breadcrumbs */}
      <Breadcrumbs items={[{ label: 'Store', link: '/products' }, { label: product.category, link: `/products?category=${product.category}` }, { label: product.title }]} />

      {/* Main PDP Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 lg:gap-12 items-start">
        
        {/* Left Column: Image Gallery */}
        <div className="lg:col-span-6 flex flex-col-reverse sm:flex-row gap-4">
          
          {/* Thumbnails list */}
          <div className="flex sm:flex-col gap-3 overflow-x-auto hide-scrollbar sm:w-20 shrink-0">
            {product.images?.map((img, idx) => (
              <button
                key={idx}
                onClick={() => setSelectedImage(img)}
                className={`w-16 h-16 sm:w-20 sm:h-20 rounded-2xl border-2 overflow-hidden bg-gray-50 transition-all shrink-0 ${
                  selectedImage === img ? 'border-brand-600 shadow-md' : 'border-gray-100 hover:border-gray-300'
                }`}
              >
                <img src={img} alt="" className="w-full h-full object-cover" />
              </button>
            ))}
          </div>

          {/* Main Hero Image Zoom View */}
          <div className="flex-1 relative aspect-square rounded-3xl overflow-hidden bg-gray-50 border border-gray-100 group shadow-md">
            <img
              src={selectedImage}
              alt={product.title}
              className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500 cursor-zoom-in"
            />
            <div className="absolute top-4 right-4 flex gap-2">
              <button
                onClick={() => {
                  navigator.clipboard.writeText(window.location.href);
                  addToast('Link copied to clipboard!', 'info');
                }}
                className="p-2.5 rounded-full bg-white/80 backdrop-blur-md shadow-md text-gray-600 hover:text-brand-600"
                title="Share product link"
              >
                <Share2 className="w-4 h-4" />
              </button>
            </div>
          </div>

        </div>

        {/* Right Column: Product Specs, Buying Actions & Offers */}
        <div className="lg:col-span-6 flex flex-col gap-6">
          
          {/* Brand & Title */}
          <div>
            <span className="text-xs font-bold text-brand-600 uppercase tracking-widest block mb-1">
              {product.brand} Official Store
            </span>
            <h1 className="text-2xl sm:text-3xl font-extrabold text-gray-900 tracking-tight leading-snug">
              {product.title}
            </h1>

            {/* Rating Summary */}
            <div className="flex items-center gap-4 mt-3">
              <Rating rating={product.rating} reviewCount={product.reviewCount} size="md" />
              <span className="text-xs font-semibold text-emerald-600 bg-emerald-50 px-2 py-0.5 rounded-md">
                Verified Customer Choice
              </span>
            </div>
          </div>

          {/* Price Block */}
          <div className="bg-gray-50/80 rounded-2xl p-4 border border-gray-100 flex items-center justify-between">
            <PriceDisplay price={product.price} originalPrice={product.originalPrice} size="lg" />
            <div className="text-right">
              <span className="text-[11px] text-gray-400 block font-medium">Inclusive of all taxes</span>
              <span className="text-xs font-bold text-emerald-600">Free Shipping Eligible</span>
            </div>
          </div>

          {/* Bank Offers & Coupon Tag */}
          <div className="bg-amber-50/60 border border-amber-200/70 rounded-2xl p-4 flex items-start gap-3">
            <Sparkles className="w-5 h-5 text-amber-600 shrink-0 mt-0.5" />
            <div className="text-xs text-amber-950">
              <p className="font-bold">Available Bank Offers & Coupons:</p>
              <p className="mt-0.5 text-amber-900">• Get 10% Instant Cashback up to ₹1,500 on HDFC Credit Cards</p>
              <p className="mt-0.5 text-amber-900">• Use Code <strong>AURASAVE10</strong> for extra 10% flat off at checkout</p>
            </div>
          </div>

          {/* Variant Selector: Color */}
          {product.colors && product.colors.length > 0 && (
            <div>
              <label className="text-xs font-bold text-gray-800 uppercase tracking-wider block mb-2">
                Color Option: <span className="text-brand-600 font-semibold ml-1">{selectedColor}</span>
              </label>
              <div className="flex flex-wrap gap-2">
                {product.colors.map((color) => (
                  <button
                    key={color}
                    onClick={() => setSelectedColor(color)}
                    className={`px-3.5 py-2 rounded-xl text-xs font-semibold border transition-all ${
                      selectedColor === color
                        ? 'bg-brand-600 text-white border-brand-600 shadow-sm'
                        : 'bg-white border-gray-200 text-gray-700 hover:border-gray-300'
                    }`}
                  >
                    {color}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Variant Selector: Size */}
          {product.sizes && product.sizes.length > 0 && (
            <div>
              <label className="text-xs font-bold text-gray-800 uppercase tracking-wider block mb-2">
                Size / Variant: <span className="text-brand-600 font-semibold ml-1">{selectedSize}</span>
              </label>
              <div className="flex flex-wrap gap-2">
                {product.sizes.map((sz) => (
                  <button
                    key={sz}
                    onClick={() => setSelectedSize(sz)}
                    className={`px-3.5 py-2 rounded-xl text-xs font-semibold border transition-all ${
                      selectedSize === sz
                        ? 'bg-brand-600 text-white border-brand-600 shadow-sm'
                        : 'bg-white border-gray-200 text-gray-700 hover:border-gray-300'
                    }`}
                  >
                    {sz}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Quantity Selector */}
          <div>
            <label className="text-xs font-bold text-gray-800 uppercase tracking-wider block mb-2">Quantity</label>
            <div className="flex items-center gap-3 bg-gray-100 p-1.5 rounded-2xl w-fit border border-gray-200">
              <button
                onClick={() => setQuantity(Math.max(1, quantity - 1))}
                className="w-8 h-8 rounded-xl bg-white text-gray-700 hover:bg-gray-200 flex items-center justify-center text-xs font-bold shadow-2xs"
              >
                <Minus className="w-3.5 h-3.5" />
              </button>
              <span className="w-8 text-center text-sm font-extrabold text-gray-900">{quantity}</span>
              <button
                onClick={() => setQuantity(quantity + 1)}
                className="w-8 h-8 rounded-xl bg-white text-gray-700 hover:bg-gray-200 flex items-center justify-center text-xs font-bold shadow-2xs"
              >
                <Plus className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>

          {/* Delivery Pincode Checker */}
          <div className="bg-white rounded-2xl p-4 border border-gray-200">
            <div className="flex justify-between items-center mb-2">
              <span className="text-xs font-bold text-gray-900 flex items-center gap-1.5">
                <Truck className="w-4 h-4 text-emerald-600" /> Delivery Availability
              </span>
              {pincodeChecked && (
                <span className="text-xs text-emerald-600 font-bold flex items-center gap-1">
                  <Check className="w-3.5 h-3.5" /> Serviceable Location
                </span>
              )}
            </div>

            <div className="flex gap-2">
              <input
                type="text"
                placeholder="Enter Pincode"
                value={pincode}
                onChange={(e) => setPincode(e.target.value)}
                className="px-3 py-2 bg-gray-50 border border-gray-300 rounded-xl text-xs font-bold"
              />
              <button
                onClick={() => {
                  if (pincode.length >= 6) {
                    setPincodeChecked(true);
                    addToast(`Delivery available for ${pincode}! Expected by tomorrow.`, 'success');
                  }
                }}
                className="px-4 py-2 bg-gray-900 text-white rounded-xl text-xs font-bold"
              >
                Check
              </button>
            </div>
            <p className="text-[11px] text-gray-400 mt-2">Guaranteed Express Delivery by {product.deliveryDate}</p>
          </div>

          {/* Action CTAs: Add to Cart, Buy Now, Wishlist */}
          <div className="flex flex-col sm:flex-row gap-3 pt-2">
            <button
              onClick={() => addToCart(product, quantity, selectedColor, selectedSize)}
              className="flex-1 py-4 bg-brand-600 hover:bg-brand-700 text-white rounded-2xl font-extrabold text-sm flex items-center justify-center gap-2 shadow-lg shadow-brand-500/20 transition-all hover:scale-[1.01]"
            >
              <ShoppingBag className="w-5 h-5" />
              <span>Add to Cart</span>
            </button>

            <button
              onClick={handleBuyNow}
              className="flex-1 py-4 bg-gray-900 hover:bg-black text-white rounded-2xl font-extrabold text-sm flex items-center justify-center gap-2 shadow-lg transition-all hover:scale-[1.01]"
            >
              <Zap className="w-5 h-5 text-amber-400 fill-amber-400" />
              <span>Buy Now</span>
            </button>

            <button
              onClick={() => toggleWishlist(product)}
              className={`p-4 rounded-2xl border transition-all ${
                isSaved ? 'bg-rose-50 border-rose-200 text-rose-600' : 'bg-white border-gray-200 text-gray-500 hover:text-rose-500'
              }`}
              title="Save to Wishlist"
            >
              <Heart className={`w-5 h-5 ${isSaved ? 'fill-rose-600' : ''}`} />
            </button>
          </div>

        </div>

      </div>

      {/* Tabs: Specifications & Description & Reviews */}
      <div className="bg-white rounded-3xl p-6 sm:p-8 border border-gray-100 shadow-sm">
        <div className="flex gap-6 border-b border-gray-100 pb-4 mb-6">
          <button
            onClick={() => setActiveTab('specs')}
            className={`text-sm font-extrabold pb-2 border-b-2 transition-all ${
              activeTab === 'specs' ? 'border-brand-600 text-brand-600' : 'border-transparent text-gray-500 hover:text-gray-900'
            }`}
          >
            Product Overview & Specifications
          </button>
          <button
            onClick={() => setActiveTab('reviews')}
            className={`text-sm font-extrabold pb-2 border-b-2 transition-all ${
              activeTab === 'reviews' ? 'border-brand-600 text-brand-600' : 'border-transparent text-gray-500 hover:text-gray-900'
            }`}
          >
            Ratings & Customer Reviews ({product.reviewCount})
          </button>
        </div>

        {activeTab === 'specs' ? (
          <div className="space-y-6">
            <div>
              <h3 className="text-sm font-bold text-gray-900 mb-2">Description</h3>
              <p className="text-xs text-gray-600 leading-relaxed max-w-3xl">{product.description}</p>
            </div>

            {product.highlights && (
              <div>
                <h3 className="text-sm font-bold text-gray-900 mb-2">Highlights</h3>
                <ul className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs text-gray-600">
                  {product.highlights.map((h, i) => (
                    <li key={i} className="flex items-center gap-2">
                      <Check className="w-4 h-4 text-emerald-500 shrink-0" />
                      <span>{h}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {product.specifications && (
              <div>
                <h3 className="text-sm font-bold text-gray-900 mb-3">Detailed Specs</h3>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-x-8 gap-y-3 bg-gray-50 p-4 rounded-2xl border border-gray-100">
                  {Object.entries(product.specifications).map(([key, val]) => (
                    <div key={key} className="flex justify-between text-xs py-1 border-b border-gray-200/50">
                      <span className="font-semibold text-gray-500">{key}</span>
                      <span className="font-bold text-gray-900">{val}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        ) : (
          <div className="space-y-6">
            <div className="flex flex-col sm:flex-row items-center gap-8 bg-gray-50 p-6 rounded-2xl">
              <div className="text-center">
                <span className="text-4xl font-black text-gray-900">{product.rating}</span>
                <Rating rating={product.rating} size="lg" />
                <span className="text-xs text-gray-400 mt-1 block">{product.reviewCount} Reviews</span>
              </div>
              <div className="flex-1 space-y-1.5 w-full">
                {[5, 4, 3, 2, 1].map((star) => (
                  <div key={star} className="flex items-center gap-3 text-xs">
                    <span className="w-4 font-semibold text-gray-600">{star}★</span>
                    <div className="flex-1 bg-gray-200 rounded-full h-2 overflow-hidden">
                      <div
                        className="bg-amber-400 h-full rounded-full"
                        style={{ width: `${star === 5 ? 80 : star === 4 ? 15 : 5}%` }}
                      />
                    </div>
                    <span className="w-8 text-right font-medium text-gray-400">
                      {star === 5 ? '80%' : star === 4 ? '15%' : '5%'}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Frequently Bought Together Widget */}
      {relatedProducts.length > 0 && (
        <ProductSection
          title="Frequently Bought Together"
          subtitle="Customers who viewed this item also bought these top recommendations"
          products={relatedProducts}
        />
      )}
    </div>
  );
};
