import React, { useState, useRef, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { 
  Search, 
  MapPin, 
  ShoppingBag, 
  Heart, 
  User, 
  Package, 
  LogOut, 
  Menu, 
  X, 
  ChevronDown, 
  History, 
  Sparkles,
  Bot,
  Trash2
} from 'lucide-react';
import { useCart } from '../../context/CartContext';
import { useWishlist } from '../../context/WishlistContext';
import { useAuth } from '../../context/AuthContext';
import { useFilter } from '../../context/FilterContext';
import { MOCK_PRODUCTS } from '../../data/mockProducts';

export const Navbar = ({ onOpenAIAssistant }) => {
  const navigate = useNavigate();
  const { totalItemsCount, grandTotal } = useCart();
  const { wishlistCount } = useWishlist();
  const { user, isAuthenticated, logout } = useAuth();
  const { 
    searchQuery, 
    setSearchQuery, 
    searchHistory, 
    addSearchTerm, 
    clearSearchHistory,
    removeSearchHistoryItem
  } = useFilter();

  const [isSearchOpen, setIsSearchOpen] = useState(false);
  const [isAccountMenuOpen, setIsAccountMenuOpen] = useState(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [selectedLocation, setSelectedLocation] = useState('Noida 201301');
  const [isLocationModalOpen, setIsLocationModalOpen] = useState(false);

  const searchRef = useRef(null);

  // Close search suggestions when clicking outside
  useEffect(() => {
    const handleClickOutside = (e) => {
      if (searchRef.current && !searchRef.current.contains(e.target)) {
        setIsSearchOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Filter matching suggestions
  const matchingProducts = searchQuery.trim()
    ? MOCK_PRODUCTS.filter(p => p.title.toLowerCase().includes(searchQuery.toLowerCase()) || p.brand.toLowerCase().includes(searchQuery.toLowerCase())).slice(0, 5)
    : [];

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      addSearchTerm(searchQuery);
      setIsSearchOpen(false);
      navigate(`/products?search=${encodeURIComponent(searchQuery)}`);
    }
  };

  const handleSuggestionClick = (term) => {
    setSearchQuery(term);
    addSearchTerm(term);
    setIsSearchOpen(false);
    navigate(`/products?search=${encodeURIComponent(term)}`);
  };

  return (
    <header className="sticky top-0 z-40 bg-white/95 backdrop-blur-md border-b border-gray-100 shadow-sm transition-all">
      {/* Top Banner Notice */}
      <div className="bg-gradient-to-r from-brand-700 via-brand-600 to-indigo-800 text-white text-xs font-medium py-1.5 px-4 text-center flex items-center justify-center gap-2">
        <Sparkles className="w-3.5 h-3.5 text-amber-300 animate-pulse" />
        <span>⚡ Super Summer Fest: Extra 10% OFF with code <strong>AURASAVE10</strong> | Free Delivery above ₹999</span>
      </div>

      {/* Main Header Container */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-18 flex items-center justify-between gap-4">
        
        {/* Brand Logo & Mobile Toggle */}
        <div className="flex items-center gap-3">
          <button 
            onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
            className="md:hidden p-2 rounded-xl hover:bg-gray-100 text-gray-700"
            aria-label="Toggle Navigation"
          >
            {isMobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
          </button>

          <Link to="/" className="flex items-center gap-2 group">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-brand-600 to-indigo-700 flex items-center justify-center text-white shadow-md shadow-brand-500/20 group-hover:scale-105 transition-transform">
              <ShoppingBag className="w-5 h-5" />
            </div>
            <div className="flex flex-col">
              <span className="text-xl font-extrabold tracking-tight bg-gradient-to-r from-brand-700 via-indigo-600 to-purple-600 bg-clip-text text-transparent">
                AuraCart
              </span>
              <span className="text-[10px] font-semibold text-gray-400 -mt-1 tracking-widest uppercase">E-STORE</span>
            </div>
          </Link>
        </div>

        {/* Location Selector (Desktop) */}
        <button
          onClick={() => setIsLocationModalOpen(true)}
          className="hidden lg:flex items-center gap-2 px-3 py-1.5 rounded-xl border border-gray-200 hover:border-brand-300 hover:bg-gray-50 text-xs text-gray-700 transition-all"
        >
          <MapPin className="w-4 h-4 text-brand-600 shrink-0" />
          <div className="text-left leading-tight">
            <p className="text-[10px] text-gray-400 font-medium">Deliver to</p>
            <p className="font-semibold text-gray-900 truncate max-w-[100px]">{selectedLocation}</p>
          </div>
          <ChevronDown className="w-3.5 h-3.5 text-gray-400" />
        </button>

        {/* Search Bar System */}
        <div ref={searchRef} className="relative flex-1 max-w-2xl mx-2">
          <form onSubmit={handleSearchSubmit} className="relative flex items-center">
            <input
              type="text"
              placeholder="Search flagship mobiles, laptops, fashion, audio..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onFocus={() => setIsSearchOpen(true)}
              className="w-full pl-11 pr-24 py-2.5 bg-gray-100/80 focus:bg-white rounded-2xl border border-transparent focus:border-brand-500 focus:ring-4 focus:ring-brand-500/10 text-sm transition-all duration-200"
            />
            <Search className="absolute left-4 w-4 h-4 text-gray-400 pointer-events-none" />
            
            <button
              type="submit"
              className="absolute right-1.5 px-4 py-1.5 bg-brand-600 hover:bg-brand-700 text-white rounded-xl text-xs font-semibold shadow-sm transition-colors"
            >
              Search
            </button>
          </form>

          {/* Auto Suggestions & Search History Overlay */}
          {isSearchOpen && (
            <div className="absolute top-full left-0 right-0 mt-2 bg-white rounded-2xl shadow-2xl border border-gray-100 overflow-hidden z-50 animate-fadeIn">
              {searchQuery.trim() ? (
                <div className="p-3">
                  <p className="text-xs font-bold text-gray-400 uppercase tracking-wider px-3 mb-2">Matching Products</p>
                  {matchingProducts.length > 0 ? (
                    matchingProducts.map((p) => (
                      <div
                        key={p.id}
                        onClick={() => {
                          setIsSearchOpen(false);
                          navigate(`/product/${p.id}`);
                        }}
                        className="flex items-center gap-3 p-2 rounded-xl hover:bg-brand-50/60 cursor-pointer transition-colors"
                      >
                        <img src={p.images[0]} alt={p.title} className="w-10 h-10 object-cover rounded-lg" />
                        <div className="flex-1 min-w-0">
                          <p className="text-sm font-medium text-gray-900 truncate">{p.title}</p>
                          <p className="text-xs text-brand-600 font-semibold">₹{p.price.toLocaleString()}</p>
                        </div>
                      </div>
                    ))
                  ) : (
                    <p className="text-xs text-gray-500 px-3 py-2">No matching products found.</p>
                  )}
                </div>
              ) : (
                <div className="p-4 flex flex-col gap-4">
                  {/* Recent Searches */}
                  {searchHistory.length > 0 && (
                    <div>
                      <div className="flex justify-between items-center mb-2">
                        <span className="text-xs font-bold text-gray-400 uppercase tracking-wider flex items-center gap-1.5">
                          <History className="w-3.5 h-3.5" /> Recent Searches
                        </span>
                        <button
                          onClick={clearSearchHistory}
                          className="text-xs text-rose-500 hover:underline"
                        >
                          Clear
                        </button>
                      </div>
                      <div className="flex flex-wrap gap-2">
                        {searchHistory.map((item, idx) => (
                          <div
                            key={idx}
                            className="flex items-center gap-1.5 bg-gray-100 hover:bg-brand-50 hover:text-brand-600 text-gray-700 text-xs px-3 py-1.5 rounded-full cursor-pointer transition-colors"
                          >
                            <span onClick={() => handleSuggestionClick(item)}>{item}</span>
                            <X 
                              className="w-3 h-3 text-gray-400 hover:text-rose-500" 
                              onClick={(e) => {
                                e.stopPropagation();
                                removeSearchHistoryItem(item);
                              }} 
                            />
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Popular Searches */}
                  <div>
                    <span className="text-xs font-bold text-gray-400 uppercase tracking-wider block mb-2">Popular Tags</span>
                    <div className="flex flex-wrap gap-2">
                      {['iPhone 15 Pro', 'Sony Headphones', 'ASUS ROG', 'Nike Shoes', 'Dyson Airwrap', 'Atomic Habits'].map((tag, idx) => (
                        <button
                          key={idx}
                          onClick={() => handleSuggestionClick(tag)}
                          className="bg-brand-50/60 hover:bg-brand-100 text-brand-700 text-xs font-medium px-3 py-1.5 rounded-full transition-colors"
                        >
                          {tag}
                        </button>
                      ))}
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Right Navigation Actions */}
        <div className="flex items-center gap-2 sm:gap-4">
          
          {/* AutoCart Agentic AI Button */}
          <button
            onClick={onOpenAIAssistant}
            className="flex items-center gap-1.5 bg-gradient-to-r from-indigo-600 via-purple-600 to-indigo-700 hover:from-indigo-700 hover:to-purple-700 text-white text-xs font-bold px-3 py-2 rounded-xl shadow-md shadow-indigo-600/30 transition-all hover:scale-105 active:scale-95"
            title="AutoCart Agentic AI (Discovery & Customer Support)"
          >
            <Bot className="w-4 h-4 text-amber-300 animate-pulse" />
            <span className="inline font-extrabold tracking-wide">AutoCart AI</span>
          </button>

          {/* Orders Link */}
          <Link
            to="/dashboard?tab=orders"
            className="hidden md:flex flex-col items-center text-gray-700 hover:text-brand-600 text-xs font-medium p-1 transition-colors"
          >
            <Package className="w-5 h-5 text-gray-600" />
            <span>Orders</span>
          </Link>

          {/* Wishlist Link */}
          <Link
            to="/wishlist"
            className="relative flex flex-col items-center text-gray-700 hover:text-brand-600 text-xs font-medium p-1 transition-colors"
          >
            <Heart className="w-5 h-5 text-gray-600" />
            <span className="hidden sm:inline">Wishlist</span>
            {wishlistCount > 0 && (
              <span className="absolute -top-1 right-1 bg-rose-500 text-white text-[10px] font-bold w-4 h-4 rounded-full flex items-center justify-center shadow-sm">
                {wishlistCount}
              </span>
            )}
          </Link>

          {/* Cart Link */}
          <Link
            to="/cart"
            className="relative flex items-center gap-2.5 bg-brand-50 hover:bg-brand-100 text-brand-700 px-3.5 py-2 rounded-xl font-bold text-xs transition-colors"
          >
            <div className="relative">
              <ShoppingBag className="w-5 h-5 text-brand-600" />
              {totalItemsCount > 0 && (
                <span className="absolute -top-2 -right-2 bg-brand-600 text-white text-[10px] font-bold w-4 h-4 rounded-full flex items-center justify-center">
                  {totalItemsCount}
                </span>
              )}
            </div>
            <span className="hidden sm:inline font-extrabold text-brand-900">
              ₹{grandTotal.toLocaleString()}
            </span>
          </Link>

          {/* Account Menu / Login */}
          <div className="relative">
            {isAuthenticated ? (
              <button
                onClick={() => setIsAccountMenuOpen(!isAccountMenuOpen)}
                className="flex items-center gap-2 p-1.5 rounded-xl hover:bg-gray-100 transition-colors"
              >
                <img
                  src={user.avatar || 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=200&q=80'}
                  alt={user.name}
                  className="w-8 h-8 rounded-full object-cover border border-brand-200"
                />
                <span className="hidden lg:inline text-xs font-semibold text-gray-800">{user.name.split(' ')[0]}</span>
                <ChevronDown className="w-3.5 h-3.5 text-gray-500" />
              </button>
            ) : (
              <Link
                to="/login"
                className="flex items-center gap-1.5 bg-gray-900 hover:bg-gray-800 text-white text-xs font-semibold px-4 py-2 rounded-xl shadow-sm transition-colors"
              >
                <User className="w-4 h-4" />
                <span>Login</span>
              </Link>
            )}

            {/* Account Dropdown */}
            {isAccountMenuOpen && isAuthenticated && (
              <div className="absolute right-0 mt-2 w-52 bg-white rounded-2xl shadow-xl border border-gray-100 p-2 z-50 animate-slide-down">
                <div className="p-3 border-b border-gray-100">
                  <p className="text-xs font-bold text-gray-900">{user.name}</p>
                  <p className="text-[11px] text-gray-400 truncate">{user.email}</p>
                </div>
                <div className="py-1">
                  <Link
                    to="/dashboard"
                    onClick={() => setIsAccountMenuOpen(false)}
                    className="flex items-center gap-2 px-3 py-2 text-xs text-gray-700 hover:bg-brand-50 hover:text-brand-600 rounded-xl transition-colors"
                  >
                    <User className="w-4 h-4" /> My Profile
                  </Link>
                  <Link
                    to="/dashboard?tab=orders"
                    onClick={() => setIsAccountMenuOpen(false)}
                    className="flex items-center gap-2 px-3 py-2 text-xs text-gray-700 hover:bg-brand-50 hover:text-brand-600 rounded-xl transition-colors"
                  >
                    <Package className="w-4 h-4" /> Orders & Tracking
                  </Link>
                  <Link
                    to="/wishlist"
                    onClick={() => setIsAccountMenuOpen(false)}
                    className="flex items-center gap-2 px-3 py-2 text-xs text-gray-700 hover:bg-brand-50 hover:text-brand-600 rounded-xl transition-colors"
                  >
                    <Heart className="w-4 h-4" /> Saved Wishlist
                  </Link>
                </div>
                <div className="pt-1 border-t border-gray-100">
                  <button
                    onClick={() => {
                      setIsAccountMenuOpen(false);
                      logout();
                    }}
                    className="w-full flex items-center gap-2 px-3 py-2 text-xs text-rose-600 hover:bg-rose-50 rounded-xl transition-colors"
                  >
                    <LogOut className="w-4 h-4" /> Sign Out
                  </button>
                </div>
              </div>
            )}
          </div>

        </div>
      </div>

      {/* Mobile Drawer Menu */}
      {isMobileMenuOpen && (
        <div className="md:hidden bg-white border-t border-gray-100 p-4 flex flex-col gap-3 animate-slide-down shadow-lg">
          <div className="flex items-center justify-between p-2 bg-gray-50 rounded-xl">
            <span className="text-xs text-gray-500 font-medium">Delivery Pincode:</span>
            <span className="text-xs font-bold text-gray-900">{selectedLocation}</span>
          </div>
          <Link
            to="/products"
            onClick={() => setIsMobileMenuOpen(false)}
            className="text-sm font-semibold text-gray-800 p-2 hover:bg-brand-50 rounded-xl"
          >
            All Products & Catalog
          </Link>
          <Link
            to="/dashboard?tab=orders"
            onClick={() => setIsMobileMenuOpen(false)}
            className="text-sm font-semibold text-gray-800 p-2 hover:bg-brand-50 rounded-xl"
          >
            My Orders
          </Link>
          <Link
            to="/wishlist"
            onClick={() => setIsMobileMenuOpen(false)}
            className="text-sm font-semibold text-gray-800 p-2 hover:bg-brand-50 rounded-xl flex items-center justify-between"
          >
            <span>Wishlist</span>
            <span className="bg-rose-100 text-rose-600 text-xs px-2 py-0.5 rounded-full font-bold">{wishlistCount}</span>
          </Link>
        </div>
      )}

      {/* Location Modal */}
      {isLocationModalOpen && (
        <div className="fixed inset-0 z-50 bg-black/50 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-white rounded-3xl p-6 max-w-md w-full shadow-2xl animate-scale-up">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-bold text-gray-900 flex items-center gap-2">
                <MapPin className="w-5 h-5 text-brand-600" /> Select Delivery Pincode
              </h3>
              <button onClick={() => setIsLocationModalOpen(false)} className="text-gray-400 hover:text-gray-600">
                <X className="w-5 h-5" />
              </button>
            </div>
            <p className="text-xs text-gray-500 mb-4">Enter your 6-digit delivery pincode to check stock availability and delivery timelines.</p>
            <div className="flex gap-2 mb-4">
              <input
                type="text"
                placeholder="Enter Pincode (e.g. 201301)"
                defaultValue="201301"
                id="pincodeInput"
                className="flex-1 px-4 py-2.5 rounded-xl border border-gray-300 focus:border-brand-500 text-sm"
              />
              <button
                onClick={() => {
                  const val = document.getElementById('pincodeInput').value;
                  if (val) setSelectedLocation(`Noida ${val}`);
                  setIsLocationModalOpen(false);
                }}
                className="px-5 py-2.5 bg-brand-600 hover:bg-brand-700 text-white rounded-xl font-semibold text-sm"
              >
                Apply
              </button>
            </div>
          </div>
        </div>
      )}
    </header>
  );
};
