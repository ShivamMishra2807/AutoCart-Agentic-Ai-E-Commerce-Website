import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import ProductImages from '../../components/product/ProductImages';
import QuantitySelector from '../../components/product/QuantitySelector';
import RelatedProducts from '../../components/product/RelatedProducts';
import ProductQuestions from '../../storefront/ProductQuestions';
import Button from '../../components/common/Button';
import Loader from '../../components/common/Loader';
import formatPrice from '../../utils/formatPrice';
import productService from '../../services/productService';
import NearbyStoreAvailability from '../../components/product/NearbyStoreAvailability';
import { useCart } from '../../hooks/useCart';
import { useWishlist } from '../../hooks/useWishlist';
import {
  ShoppingBag,
  RotateCcw,
  Check,
  Star,
  Zap,
  Tag,
  MapPin,
  ChevronDown,
  ChevronUp,
  ThumbsUp,
  Award,
  Layers,
  PackageCheck,
  CreditCard,
  Plus
} from 'lucide-react';

export const ProductDetails = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [product, setProduct] = useState(null);
  const [allProducts, setAllProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [quantity, setQuantity] = useState(1);

  // Flipkart & Amazon feature states
  const [pincode, setPincode] = useState('110001');
  const [pincodeChecked, setPincodeChecked] = useState(true);
  const [pincodeLoading, setPincodeLoading] = useState(false);
  const [showAllOffers, setShowAllOffers] = useState(false);
  const [activeTab, setActiveTab] = useState('specifications');
  const [showStickyBar, setShowStickyBar] = useState(false);
  
  // Bundle builder state
  const [bundleIncludeAccessory, setBundleIncludeAccessory] = useState(true);

  // Reviews state with interactive "Write Review"
  const [reviews, setReviews] = useState([
    {
      id: 'rev-1',
      name: 'Aditya Verma',
      rating: 5,
      date: '20 Sep 2026',
      verified: true,
      title: 'Terrific purchase! Beyond expectations',
      comment: 'Audio quality is punchy, noise cancellation completely blocks office noise. Battery easily lasts 3-4 days on regular usage. Definitely the best in this price bracket!',
      helpful: 48,
    },
    {
      id: 'rev-2',
      name: 'Rohan Deshmukh',
      rating: 4,
      date: '12 Sep 2026',
      verified: true,
      title: 'Value for money, highly recommended',
      comment: 'Build quality feels premium. Fast connection with laptop and smartphone simultaneously. Mic clarity during calls is top notch.',
      helpful: 24,
    },
    {
      id: 'rev-3',
      name: 'Pooja Sundaram',
      rating: 5,
      date: '28 Aug 2026',
      verified: true,
      title: 'Delivered in less than 24 hours!',
      comment: 'Amazon/Flipkart grade packaging and lightning fast delivery. Product works flawlessly. 10/10 service from AutoCart!',
      helpful: 19,
    },
  ]);

  const [reviewModalOpen, setReviewModalOpen] = useState(false);
  const [newReviewRating, setNewReviewRating] = useState(5);
  const [newReviewTitle, setNewReviewTitle] = useState('');
  const [newReviewComment, setNewReviewComment] = useState('');

  const { addToCart, cartItems } = useCart();
  const { isInWishlist, toggleWishlist } = useWishlist();

  useEffect(() => {
    const fetchDetails = async () => {
      setLoading(true);
      try {
        const prod = await productService.getProductById(id);
        setProduct(prod);
        const list = await productService.getProducts();
        setAllProducts(list);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchDetails();
    window.scrollTo(0, 0);
  }, [id]);

  useEffect(() => {
    const handleScroll = () => {
      if (window.scrollY > 400) {
        setShowStickyBar(true);
      } else {
        setShowStickyBar(false);
      }
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  if (loading) return <Loader fullScreen text="Loading product details & offers..." />;
  if (!product) return <div className="text-center py-20 font-bold text-gray-800">Product not found</div>;

  const isCartAdded = cartItems.some((item) => item.id === product.id);

  const handleBuyNow = () => {
    addToCart(product, quantity);
    navigate('/checkout');
  };

  const handleCheckPincode = (e) => {
    e.preventDefault();
    if (!pincode || pincode.length !== 6) return;
    setPincodeLoading(true);
    setTimeout(() => {
      setPincodeLoading(false);
      setPincodeChecked(true);
    }, 400);
  };

  const handleAddReview = (e) => {
    e.preventDefault();
    if (!newReviewTitle || !newReviewComment) return;
    const newEntry = {
      id: `rev-${Date.now()}`,
      name: 'You (Verified Buyer)',
      rating: newReviewRating,
      date: 'Today',
      verified: true,
      title: newReviewTitle,
      comment: newReviewComment,
      helpful: 1,
    };
    setReviews([newEntry, ...reviews]);
    setNewReviewTitle('');
    setNewReviewComment('');
    setReviewModalOpen(false);
  };

  const bundleAccessory = {
    name: 'AutoCart Shield 1-Year Extended Warranty + Care',
    price: 299,
    originalPrice: 799,
  };

  const bundleTotal = bundleIncludeAccessory
    ? product.price + bundleAccessory.price
    : product.price;

  const handleAddBundleToCart = () => {
    addToCart(product, 1);
    if (bundleIncludeAccessory) {
      addToCart({
        id: `acc-${product.id}`,
        name: bundleAccessory.name,
        price: bundleAccessory.price,
        images: ['https://images.unsplash.com/photo-1584438784894-089d6a62b8fa?w=300&q=80'],
        stock: 99,
      }, 1);
    }
  };

  return (
    <div className="space-y-10 pb-16">
      {/* Breadcrumb Navigation */}
      <nav className="text-xs text-gray-500 flex items-center gap-2 flex-wrap">
        <Link to="/" className="hover:text-indigo-600 font-medium">Home</Link>
        <span>/</span>
        <Link to={`/products?category=${encodeURIComponent(product.category)}`} className="hover:text-indigo-600 font-medium">
          {product.category}
        </Link>
        <span>/</span>
        <span className="text-indigo-600 font-medium">{product.brand}</span>
        <span>/</span>
        <span className="text-gray-900 font-semibold truncate max-w-xs">{product.name}</span>
      </nav>

      {/* Product Top Grid (Flipkart/Amazon 2-column layout) */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 lg:gap-12 bg-white p-5 sm:p-8 rounded-3xl border border-gray-100 shadow-sm transition-colors">
        {/* Left Column: Image Gallery (5 cols) */}
        <div className="lg:col-span-5">
          <div className="sticky top-24">
            <ProductImages images={product.images} productName={product.name} product={product} />

            {/* Quick Action Buttons on Desktop under images (Flipkart style) */}
            <div className="grid grid-cols-2 gap-3.5 mt-5">
              <Button
                variant="primary"
                size="lg"
                fullWidth
                disabled={product.stock === 0}
                onClick={() => addToCart(product, quantity)}
                icon={isCartAdded ? Check : ShoppingBag}
                className="bg-amber-500 hover:bg-amber-600 text-white font-extrabold shadow-lg shadow-amber-500/20 active:scale-95"
              >
                {isCartAdded ? 'ADDED TO CART' : 'ADD TO CART'}
              </Button>

              <Button
                variant="secondary"
                size="lg"
                fullWidth
                disabled={product.stock === 0}
                onClick={handleBuyNow}
                className="bg-orange-600 hover:bg-orange-700 text-white font-extrabold shadow-lg shadow-orange-600/20 active:scale-95"
              >
                ⚡ BUY NOW
              </Button>
            </div>
          </div>
        </div>

        {/* Right Column: Details, Deals, Specifications & Delivery (7 cols) */}
        <div className="lg:col-span-7 space-y-6">
          {/* Brand, Title & Assured Tag */}
          <div>
            <div className="flex items-center gap-2 mb-1.5">
              <span className="text-xs uppercase tracking-wider font-extrabold text-indigo-600">
                {product.brand}
              </span>
              <span className="text-gray-300">•</span>
              <span className="text-xs text-gray-400 font-medium">SKU: {product.id}</span>
              <span className="ml-auto inline-flex items-center gap-1 bg-gradient-to-r from-blue-600 to-indigo-600 text-white text-[10px] font-extrabold px-2 py-0.5 rounded-full shadow-sm">
                ✦ Plus Assured
              </span>
            </div>

            <h1 className="text-xl sm:text-2xl font-extrabold text-gray-900 leading-snug">
              {product.name}
            </h1>

            {/* Rating & Review Counter pill */}
            <div className="flex items-center gap-3 mt-3 flex-wrap">
              <div className="flex items-center gap-1.5 bg-emerald-600 text-white text-xs font-extrabold px-2.5 py-1 rounded-lg shadow-sm">
                <span>{product.rating || 4.3}</span>
                <Star className="w-3.5 h-3.5 fill-white" />
              </div>
              <span className="text-xs font-semibold text-gray-500">
                {product.reviewCount ? Number(product.reviewCount).toLocaleString() : '12,450'} Ratings & {reviews.length} Reviews
              </span>
              <span className="text-gray-300">•</span>
              <span className="text-xs font-semibold text-indigo-600 flex items-center gap-1">
                <Award className="w-3.5 h-3.5" /> 100% Genuine Product
              </span>
            </div>
          </div>

          {/* Pricing Box (Flipkart/Amazon style) */}
          <div className="p-4 sm:p-5 bg-gradient-to-r from-gray-50 to-indigo-50/40 rounded-2xl border border-gray-100">
            <div className="text-[11px] font-bold text-emerald-600 uppercase tracking-wider mb-1 flex items-center gap-1">
              <Zap className="w-3.5 h-3.5 fill-emerald-600" /> Special Deal Price
            </div>
            <div className="flex items-baseline gap-3 flex-wrap">
              <span className="text-3xl sm:text-4xl font-black text-gray-900">
                {formatPrice(product.price)}
              </span>
              {product.originalPrice > product.price && (
                <>
                  <span className="text-sm text-gray-400 line-through">
                    {formatPrice(product.originalPrice)}
                  </span>
                  <span className="text-xs font-extrabold text-emerald-600 bg-emerald-100 px-2 py-0.5 rounded-md">
                    {product.discount}% OFF
                  </span>
                </>
              )}
            </div>
            <div className="text-[11px] text-gray-500 mt-1.5 flex items-center gap-2">
              <span>Inclusive of all taxes</span>
              <span>•</span>
              <span className="text-indigo-600 font-medium">
                EMI starts at ₹{Math.round(product.price / 12)}/month. No Cost EMI available.
              </span>
            </div>
          </div>

          {/* Flipkart / Amazon style Bank & Promotional Offers */}
          <div className="space-y-2.5">
            <div className="flex items-center justify-between">
              <span className="text-xs font-extrabold uppercase tracking-wider text-gray-700 flex items-center gap-1.5">
                <Tag className="w-4 h-4 text-emerald-600" /> Available Bank Offers & Deals
              </span>
              <button
                onClick={() => setShowAllOffers(!showAllOffers)}
                className="text-xs text-indigo-600 font-bold hover:underline flex items-center gap-0.5"
              >
                {showAllOffers ? 'View Less' : '+4 More Offers'}
                {showAllOffers ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
              </button>
            </div>

            <div className="space-y-2 text-xs">
              <div className="p-3 rounded-xl bg-emerald-50/80 border border-emerald-100 flex items-start gap-2.5 text-gray-700">
                <span className="bg-emerald-600 text-white text-[10px] font-black px-1.5 py-0.5 rounded shrink-0">BANK</span>
                <span><strong>Bank Offer:</strong> 5% Unlimited Cashback on AutoCart Axis Bank Credit Card. <span className="text-indigo-600 font-semibold cursor-pointer">T&C</span></span>
              </div>

              <div className="p-3 rounded-xl bg-gray-50 border border-gray-100 flex items-start gap-2.5 text-gray-700">
                <span className="bg-indigo-600 text-white text-[10px] font-black px-1.5 py-0.5 rounded shrink-0">DEAL</span>
                <span><strong>Special Price:</strong> Get extra 10% off up to ₹1,500 on HDFC / ICICI Bank cards.</span>
              </div>

              {showAllOffers && (
                <div className="space-y-2 animate-slide-down">
                  <div className="p-3 rounded-xl bg-gray-50 border border-gray-100 flex items-start gap-2.5 text-gray-700">
                    <span className="bg-purple-600 text-white text-[10px] font-black px-1.5 py-0.5 rounded shrink-0">COUPON</span>
                    <span><strong>Partner Offer:</strong> Apply code <strong className="font-mono text-indigo-600">WELCOME10</strong> at checkout for 10% flat discount.</span>
                  </div>
                  <div className="p-3 rounded-xl bg-gray-50 border border-gray-100 flex items-start gap-2.5 text-gray-700">
                    <span className="bg-blue-600 text-white text-[10px] font-black px-1.5 py-0.5 rounded shrink-0">EMI</span>
                    <span><strong>No Cost EMI:</strong> Avail 0% interest on credit cards for 3 or 6 months.</span>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Delivery & Pincode Checker */}
          <div className="p-4 bg-gray-50 rounded-2xl border border-gray-100 space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold text-gray-700 flex items-center gap-1.5">
                <MapPin className="w-4 h-4 text-indigo-600" /> Delivery & Services
              </span>
              <span className="text-[11px] text-emerald-600 font-bold">Fastest Dispatch</span>
            </div>

            <form onSubmit={handleCheckPincode} className="flex gap-2">
              <input
                type="text"
                maxLength={6}
                value={pincode}
                onChange={(e) => setPincode(e.target.value.replace(/\D/g, ''))}
                placeholder="Enter 6-digit Pincode"
                className="flex-1 bg-white border border-gray-200 text-xs px-3.5 py-2 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500 font-mono text-gray-900"
              />
              <button
                type="submit"
                disabled={pincodeLoading || pincode.length !== 6}
                className="bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-bold px-4 py-2 rounded-xl transition disabled:opacity-50"
              >
                {pincodeLoading ? 'Checking...' : 'Check'}
              </button>
            </form>

            {pincodeChecked && (
              <div className="space-y-1.5 text-xs text-gray-600 pt-1">
                <div className="flex items-center gap-2 text-emerald-600 font-bold">
                  <PackageCheck className="w-4 h-4 shrink-0" />
                  <span>FREE Delivery by Tomorrow, 2:00 PM</span>
                </div>
                <div className="flex items-center gap-2 text-gray-500">
                  <CreditCard className="w-4 h-4 text-gray-400 shrink-0" />
                  <span>Cash on Delivery available on this order</span>
                </div>
                <div className="flex items-center gap-2 text-gray-500">
                  <RotateCcw className="w-4 h-4 text-gray-400 shrink-0" />
                  <span>7-Day Replacement Policy (Hassle-Free)</span>
                </div>
              </div>
            )}
          </div>

          {/* Hyperlocal Physical Partner Store Stock & 35-min Delivery */}
          <NearbyStoreAvailability productId={product.id} productName={product.name} />

          {/* Key Product Highlights (Flipkart style bullets) */}
          <div className="space-y-2.5">
            <span className="text-xs font-extrabold uppercase tracking-wider text-gray-700">
              Product Highlights
            </span>
            <ul className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs text-gray-600">
              <li className="flex items-center gap-2">
                <Check className="w-4 h-4 text-emerald-500 shrink-0" />
                <span>100% Original Brand Certified</span>
              </li>
              <li className="flex items-center gap-2">
                <Check className="w-4 h-4 text-emerald-500 shrink-0" />
                <span>1 Year Manufacturer Warranty</span>
              </li>
              <li className="flex items-center gap-2">
                <Check className="w-4 h-4 text-emerald-500 shrink-0" />
                <span>Sold by: <strong>{product.seller || 'AutoCart Retail'}</strong> (4.8 ★)</span>
              </li>
              <li className="flex items-center gap-2">
                <Check className="w-4 h-4 text-emerald-500 shrink-0" />
                <span>GST Invoice Available</span>
              </li>
              {product.specifications &&
                Object.entries(product.specifications).slice(0, 4).map(([key, val]) => (
                  <li key={key} className="flex items-center gap-2">
                    <Check className="w-4 h-4 text-indigo-500 shrink-0" />
                    <span><strong>{key}:</strong> {val}</span>
                  </li>
                ))}
            </ul>
          </div>

          {/* Quantity Selector & Stock Indicator */}
          <div className="flex items-center gap-6 pt-3 border-t border-gray-100">
            <div className="flex items-center gap-3">
              <span className="text-xs font-bold text-gray-700 uppercase">Quantity:</span>
              <QuantitySelector
                quantity={quantity}
                onDecrease={() => setQuantity(Math.max(1, quantity - 1))}
                onIncrease={() => setQuantity(Math.min(product.stock || 10, quantity + 1))}
                max={product.stock || 10}
              />
            </div>
            <div className="text-xs">
              {product.stock > 0 ? (
                <span className="text-emerald-600 font-bold">
                  In Stock ({product.stock} units left)
                </span>
              ) : (
                <span className="text-rose-500 font-bold">Currently Out of Stock</span>
              )}
            </div>
          </div>

          {/* Frequently Bought Together Bundle Card */}
          <div className="p-4 bg-indigo-50/50 rounded-2xl border border-indigo-100 space-y-3">
            <div className="flex items-center gap-2 text-xs font-extrabold text-indigo-900">
              <Layers className="w-4 h-4 text-indigo-600" /> Frequently Bought Together
            </div>
            <div className="flex items-center gap-3 text-xs">
              <label className="flex items-center gap-2 cursor-pointer select-none">
                <input
                  type="checkbox"
                  checked={bundleIncludeAccessory}
                  onChange={(e) => setBundleIncludeAccessory(e.target.checked)}
                  className="rounded text-indigo-600 focus:ring-indigo-500 w-4 h-4"
                />
                <span className="text-gray-700">
                  Add <strong>{bundleAccessory.name}</strong> for{' '}
                  <strong className="text-emerald-600">₹{bundleAccessory.price}</strong>{' '}
                  <span className="line-through text-gray-400">₹{bundleAccessory.originalPrice}</span>
                </span>
              </label>
            </div>
            <div className="flex items-center justify-between pt-2 border-t border-indigo-100">
              <div className="text-xs">
                <span className="text-gray-500">Bundle Total: </span>
                <span className="font-extrabold text-sm text-gray-900">{formatPrice(bundleTotal)}</span>
              </div>
              <button
                onClick={handleAddBundleToCart}
                className="bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-bold px-3 py-1.5 rounded-lg shadow transition active:scale-95 flex items-center gap-1"
              >
                <Plus className="w-3.5 h-3.5" /> Add Bundle to Cart
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Tabs Section: Specifications, Ratings & Reviews, Q&A */}
      <div className="bg-white rounded-3xl border border-gray-100 p-6 sm:p-8 shadow-sm transition-colors space-y-6">
        <div className="flex items-center gap-6 border-b border-gray-100 pb-3 overflow-x-auto">
          <button
            onClick={() => setActiveTab('specifications')}
            className={`text-sm font-extrabold pb-2 transition-all relative ${
              activeTab === 'specifications'
                ? 'text-indigo-600'
                : 'text-gray-500 hover:text-gray-800'
            }`}
          >
            Specifications & Details
            {activeTab === 'specifications' && (
              <span className="absolute bottom-0 left-0 right-0 h-0.5 bg-indigo-600 rounded-full" />
            )}
          </button>

          <button
            onClick={() => setActiveTab('reviews')}
            className={`text-sm font-extrabold pb-2 transition-all relative flex items-center gap-1.5 ${
              activeTab === 'reviews'
                ? 'text-indigo-600'
                : 'text-gray-500 hover:text-gray-800'
            }`}
          >
            Customer Reviews ({reviews.length})
            {activeTab === 'reviews' && (
              <span className="absolute bottom-0 left-0 right-0 h-0.5 bg-indigo-600 rounded-full" />
            )}
          </button>

          <button
            onClick={() => setActiveTab('qa')}
            className={`text-sm font-extrabold pb-2 transition-all relative flex items-center gap-1.5 ${
              activeTab === 'qa'
                ? 'text-indigo-600'
                : 'text-gray-500 hover:text-gray-800'
            }`}
          >
            Questions & Answers
            {activeTab === 'qa' && (
              <span className="absolute bottom-0 left-0 right-0 h-0.5 bg-indigo-600 rounded-full" />
            )}
          </button>
        </div>

        {/* Tab 1: Specifications */}
        {activeTab === 'specifications' && (
          <div className="space-y-6 animate-fade-in">
            <h3 className="text-base font-bold text-gray-900">Technical Specifications</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3.5">
              <div className="flex justify-between p-3.5 bg-gray-50 rounded-xl text-xs">
                <span className="font-semibold text-gray-500">Brand</span>
                <span className="font-bold text-gray-900">{product.brand}</span>
              </div>
              <div className="flex justify-between p-3.5 bg-gray-50 rounded-xl text-xs">
                <span className="font-semibold text-gray-500">Category</span>
                <span className="font-bold text-gray-900">{product.category}</span>
              </div>
              <div className="flex justify-between p-3.5 bg-gray-50 rounded-xl text-xs">
                <span className="font-semibold text-gray-500">Model Name / SKU</span>
                <span className="font-bold text-gray-900">{product.slug || product.id}</span>
              </div>
              <div className="flex justify-between p-3.5 bg-gray-50 rounded-xl text-xs">
                <span className="font-semibold text-gray-500">Warranty</span>
                <span className="font-bold text-gray-900">1 Year Manufacturer Warranty</span>
              </div>
              {product.specifications &&
                Object.entries(product.specifications).map(([key, val]) => (
                  <div key={key} className="flex justify-between p-3.5 bg-gray-50 rounded-xl text-xs">
                    <span className="font-semibold text-gray-500">{key}</span>
                    <span className="font-bold text-gray-900">{val}</span>
                  </div>
                ))}
            </div>

            <div className="p-4 bg-gray-50 rounded-2xl border border-gray-100 space-y-2">
              <h4 className="text-xs font-extrabold uppercase text-gray-700">In The Box</h4>
              <p className="text-xs text-gray-600">
                1 x {product.name}, Charging / Connectivity Cable, User Manual, Warranty Card.
              </p>
            </div>
          </div>
        )}

        {/* Tab 2: Reviews */}
        {activeTab === 'reviews' && (
          <div className="space-y-8 animate-fade-in">
            <div className="grid grid-cols-1 md:grid-cols-12 gap-6 p-6 bg-gray-50 rounded-2xl border border-gray-100 items-center">
              <div className="md:col-span-4 text-center md:border-r border-gray-200 pr-4">
                <div className="text-5xl font-black text-gray-900">{product.rating || 4.3}</div>
                <div className="flex justify-center my-2 text-amber-400">
                  {[...Array(5)].map((_, i) => (
                    <Star key={i} className="w-5 h-5 fill-amber-400" />
                  ))}
                </div>
                <div className="text-xs text-gray-500 font-medium">
                  Based on {Number(product.reviewCount || 12450).toLocaleString()} Verified Buyers
                </div>
              </div>

              <div className="md:col-span-5 space-y-1.5 text-xs">
                <div className="flex items-center gap-2">
                  <span className="w-8 font-semibold text-gray-600">5 ★</span>
                  <div className="flex-1 bg-gray-200 rounded-full h-2 overflow-hidden">
                    <div className="bg-emerald-500 h-full rounded-full" style={{ width: '68%' }} />
                  </div>
                  <span className="w-8 text-right text-gray-400">68%</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="w-8 font-semibold text-gray-600">4 ★</span>
                  <div className="flex-1 bg-gray-200 rounded-full h-2 overflow-hidden">
                    <div className="bg-emerald-400 h-full rounded-full" style={{ width: '22%' }} />
                  </div>
                  <span className="w-8 text-right text-gray-400">22%</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="w-8 font-semibold text-gray-600">3 ★</span>
                  <div className="flex-1 bg-gray-200 rounded-full h-2 overflow-hidden">
                    <div className="bg-amber-400 h-full rounded-full" style={{ width: '6%' }} />
                  </div>
                  <span className="w-8 text-right text-gray-400">6%</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="w-8 font-semibold text-gray-600">2 ★</span>
                  <div className="flex-1 bg-gray-200 rounded-full h-2 overflow-hidden">
                    <div className="bg-orange-400 h-full rounded-full" style={{ width: '3%' }} />
                  </div>
                  <span className="w-8 text-right text-gray-400">3%</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="w-8 font-semibold text-gray-600">1 ★</span>
                  <div className="flex-1 bg-gray-200 rounded-full h-2 overflow-hidden">
                    <div className="bg-rose-500 h-full rounded-full" style={{ width: '1%' }} />
                  </div>
                  <span className="w-8 text-right text-gray-400">1%</span>
                </div>
              </div>

              <div className="md:col-span-3 text-center">
                <button
                  onClick={() => setReviewModalOpen(true)}
                  className="w-full bg-white border-2 border-indigo-600 text-indigo-600 hover:bg-indigo-50 text-xs font-extrabold py-2.5 px-4 rounded-xl shadow-sm transition active:scale-95"
                >
                  Write a Review
                </button>
              </div>
            </div>

            <div className="space-y-4">
              {reviews.map((rev) => (
                <div key={rev.id} className="p-4 sm:p-5 rounded-2xl bg-gray-50 border border-gray-100 space-y-2">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <span className="inline-flex items-center gap-1 bg-emerald-600 text-white text-[10px] font-extrabold px-1.5 py-0.5 rounded">
                        {rev.rating} <Star className="w-2.5 h-2.5 fill-white" />
                      </span>
                      <h4 className="text-xs font-bold text-gray-900">{rev.title}</h4>
                    </div>
                    <span className="text-[11px] text-gray-400">{rev.date}</span>
                  </div>
                  <p className="text-xs text-gray-600 leading-relaxed">{rev.comment}</p>
                  <div className="flex items-center justify-between text-[11px] text-gray-400 pt-1">
                    <span className="font-semibold text-gray-500 flex items-center gap-1">
                      {rev.name} {rev.verified && <span className="text-emerald-600 font-bold">✓ Verified Purchase</span>}
                    </span>
                    <button className="flex items-center gap-1 hover:text-indigo-600 transition">
                      <ThumbsUp className="w-3.5 h-3.5" /> Helpful ({rev.helpful})
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Tab 3: Q&A */}
        {activeTab === 'qa' && (
          <div className="space-y-4 animate-fade-in">
            <h3 className="text-base font-bold text-gray-900">Customer Questions & Answers</h3>
            <div className="space-y-3">
              <div className="p-4 bg-gray-50 rounded-xl space-y-1.5 text-xs">
                <div className="font-bold text-gray-900 flex items-center gap-2">
                  <span className="bg-indigo-600 text-white px-1.5 py-0.5 rounded text-[10px]">Q</span>
                  Is this compatible with iOS and Android devices?
                </div>
                <div className="text-gray-600 pl-6 flex items-start gap-2">
                  <span className="bg-emerald-600 text-white px-1.5 py-0.5 rounded text-[10px] shrink-0">A</span>
                  <span>Yes, it is 100% compatible with all Android, iOS, Windows, and macOS devices via Bluetooth.</span>
                </div>
              </div>

              <div className="p-4 bg-gray-50 rounded-xl space-y-1.5 text-xs">
                <div className="font-bold text-gray-900 flex items-center gap-2">
                  <span className="bg-indigo-600 text-white px-1.5 py-0.5 rounded text-[10px]">Q</span>
                  How do I claim brand warranty?
                </div>
                <div className="text-gray-600 pl-6 flex items-start gap-2">
                  <span className="bg-emerald-600 text-white px-1.5 py-0.5 rounded text-[10px] shrink-0">A</span>
                  <span>You can register the invoice on the brand’s official website or present the AutoCart invoice at any authorized service center.</span>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Related Products */}
      <ProductQuestions product={product} />
      <RelatedProducts currentProduct={product} allProducts={allProducts} />

      {/* Sticky Bottom Purchase Bar */}
      {showStickyBar && (
        <div className="fixed bottom-0 left-0 right-0 z-40 bg-white/95 backdrop-blur-md border-t border-gray-200 py-3 px-4 shadow-2xl animate-slide-up">
          <div className="max-w-7xl mx-auto flex items-center justify-between gap-4">
            <div className="flex items-center gap-3 min-w-0">
              <img
                src={product.images && product.images[0] ? product.images[0] : ''}
                alt={product.name}
                className="w-12 h-12 object-contain rounded-lg border bg-gray-50 shrink-0"
              />
              <div className="min-w-0">
                <div className="text-xs font-bold text-gray-900 truncate">{product.name}</div>
                <div className="text-sm font-extrabold text-indigo-600">
                  {formatPrice(product.price)}
                </div>
              </div>
            </div>

            <div className="flex items-center gap-3 shrink-0">
              <button
                disabled={product.stock === 0}
                onClick={() => addToCart(product, quantity)}
                className="bg-amber-500 hover:bg-amber-600 text-white text-xs font-extrabold px-4 py-2.5 rounded-xl shadow transition"
              >
                {isCartAdded ? 'ADDED' : 'ADD TO CART'}
              </button>
              <button
                disabled={product.stock === 0}
                onClick={handleBuyNow}
                className="bg-orange-600 hover:bg-orange-700 text-white text-xs font-extrabold px-5 py-2.5 rounded-xl shadow transition"
              >
                BUY NOW
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Review Modal */}
      {reviewModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-gray-900/60 backdrop-blur-sm animate-fade-in">
          <div className="bg-white rounded-3xl p-6 sm:p-8 max-w-md w-full border border-gray-100 shadow-2xl space-y-4">
            <h3 className="text-lg font-bold text-gray-900">Rate & Review Product</h3>
            <form onSubmit={handleAddReview} className="space-y-4">
              <div>
                <label className="block text-xs font-bold text-gray-700 mb-1">Your Rating</label>
                <div className="flex gap-2">
                  {[1, 2, 3, 4, 5].map((star) => (
                    <button
                      type="button"
                      key={star}
                      onClick={() => setNewReviewRating(star)}
                      className="p-1 focus:outline-none"
                    >
                      <Star
                        className={`w-6 h-6 ${
                          star <= newReviewRating
                            ? 'fill-amber-400 text-amber-400'
                            : 'text-gray-300'
                        }`}
                      />
                    </button>
                  ))}
                </div>
              </div>

              <div>
                <label className="block text-xs font-bold text-gray-700 mb-1">Headline</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Great sound quality & battery"
                  value={newReviewTitle}
                  onChange={(e) => setNewReviewTitle(e.target.value)}
                  className="w-full text-xs p-3 rounded-xl border border-gray-200 bg-white text-gray-900 focus:ring-2 focus:ring-indigo-500 outline-none"
                />
              </div>

              <div>
                <label className="block text-xs font-bold text-gray-700 mb-1">Detailed Review</label>
                <textarea
                  required
                  rows={4}
                  placeholder="What did you like or dislike about this product?"
                  value={newReviewComment}
                  onChange={(e) => setNewReviewComment(e.target.value)}
                  className="w-full text-xs p-3 rounded-xl border border-gray-200 bg-white text-gray-900 focus:ring-2 focus:ring-indigo-500 outline-none"
                />
              </div>

              <div className="flex gap-3 justify-end pt-2">
                <button
                  type="button"
                  onClick={() => setReviewModalOpen(false)}
                  className="px-4 py-2 rounded-xl text-xs font-bold text-gray-600 hover:bg-gray-100"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-5 py-2 rounded-xl text-xs font-bold bg-indigo-600 hover:bg-indigo-700 text-white shadow-md"
                >
                  Submit Review
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default ProductDetails;
