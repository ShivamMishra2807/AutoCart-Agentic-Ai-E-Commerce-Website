import React, { useState } from 'react';
import { Link, NavLink } from 'react-router-dom';
import { Heart, Menu, X, Sparkles, Bot, MapPin, ChevronDown } from 'lucide-react';
import SearchBar from './SearchBar';
import UserMenu from './UserMenu';
import CartIcon from './CartIcon';
import LocationPickerModal from './LocationPickerModal';
import { MumbaiStoreMap } from '../map/MumbaiStoreMap';
import { useWishlist } from '../../hooks/useWishlist';
import { useLocation } from '../../context/LocationContext';

export const Navbar = ({ onOpenAIAssistant }) => {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [isLocationModalOpen, setIsLocationModalOpen] = useState(false);
  const [isMumbaiMapOpen, setIsMumbaiMapOpen] = useState(false);
  const { wishlistCount } = useWishlist();
  const { location } = useLocation();

  return (
    <header className="sticky top-0 z-40 bg-white border-b border-gray-200 shadow-sm">
      {/* Top Announcement Bar with Location */}
      <div className="bg-gradient-to-r from-indigo-700 via-purple-600 to-indigo-800 text-white text-xs font-semibold py-1.5 px-4 flex items-center justify-between">
        <div className="hidden sm:flex items-center gap-2">
          <Sparkles className="w-3.5 h-3.5 text-amber-300 animate-pulse" />
          <span>⚡ Festive Season Sale: Flat <strong>60% OFF</strong> + Extra ₹500 OFF with coupon <code className="bg-white/20 px-1.5 py-0.5 rounded font-mono text-[11px]">SUPER500</code></span>
        </div>
        <div className="flex items-center gap-2 ml-auto sm:ml-0">
          <button
            onClick={() => setIsMumbaiMapOpen(true)}
            className="flex items-center gap-1 text-[11px] sm:text-xs text-amber-200 hover:text-white font-bold bg-amber-400/20 hover:bg-amber-400/30 px-2.5 py-0.5 rounded-full transition cursor-pointer border border-amber-300/30"
            title="Browse 10 Mumbai Zones Physical Store Network"
          >
            <span>🗺️ Mumbai Stores</span>
          </button>

          <button
            onClick={() => setIsLocationModalOpen(true)}
            className="flex items-center gap-1.5 text-xs text-indigo-100 hover:text-white font-bold bg-white/10 hover:bg-white/20 px-2.5 py-0.5 rounded-full transition cursor-pointer"
            title="Change delivery location"
          >
            <MapPin className="w-3 h-3 text-amber-300" />
            <span>Deliver to: <strong>{location.area || location.city} ({location.pincode || '400069'})</strong></span>
            <ChevronDown className="w-3 h-3 text-indigo-200" />
          </button>
        </div>
      </div>

      {/* Location Modal */}
      <LocationPickerModal
        isOpen={isLocationModalOpen}
        onClose={() => setIsLocationModalOpen(false)}
      />

      {/* Mumbai Store Network Map Modal */}
      {isMumbaiMapOpen && (
        <MumbaiStoreMap
          isOpen={isMumbaiMapOpen}
          onClose={() => setIsMumbaiMapOpen(false)}
        />
      )}

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16 gap-4">
          {/* Logo & Mobile Menu Trigger */}
          <div className="flex items-center gap-3">
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="lg:hidden p-2 rounded-xl text-gray-600 hover:text-gray-900 hover:bg-gray-100"
            >
              {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>

            <Link to="/" className="flex items-center gap-2.5 group">
              <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-indigo-600 to-purple-600 flex items-center justify-center text-white font-extrabold text-xl shadow-md group-hover:scale-105 transition-transform">
                A
              </div>
              <div className="flex flex-col leading-tight">
                <span className="font-extrabold text-xl text-gray-900 tracking-tight">
                  Auto<span className="text-indigo-600">Cart</span>
                </span>
                <span className="text-[9px] font-bold text-amber-500 -mt-1 tracking-widest uppercase flex items-center gap-0.5">
                  ✦ Plus Assured
                </span>
              </div>
            </Link>
          </div>

          {/* Desktop Search Bar */}
          <div className="hidden md:flex flex-1 max-w-xl mx-4">
            <SearchBar />
          </div>

          {/* Actions: Wishlist, Cart, Profile & Agentic AI */}
          <div className="flex items-center gap-2 sm:gap-4">
            {/* AutoCart Agentic AI Action Button */}
            <button
              onClick={onOpenAIAssistant}
              className="flex items-center gap-1.5 bg-gradient-to-r from-indigo-600 via-purple-600 to-indigo-700 hover:from-indigo-700 hover:to-purple-700 text-white text-xs font-bold px-3 py-2 rounded-xl shadow-md shadow-indigo-600/30 transition-all hover:scale-105 active:scale-95 cursor-pointer"
              title="AutoCart Agentic AI (Discovery & Engagement)"
            >
              <Bot className="w-4 h-4 text-amber-300 animate-pulse" />
              <span className="hidden sm:inline font-extrabold tracking-wide">AutoCart AI</span>
            </button>

            <Link
              to="/wishlist"
              className="relative p-2 text-gray-700 hover:text-indigo-600 rounded-xl hover:bg-gray-100 transition hidden sm:flex items-center justify-center"
              title="Wishlist"
            >
              <Heart className="w-5 h-5" />
              {wishlistCount > 0 && (
                <span className="absolute -top-0.5 -right-0.5 flex h-4 w-4 items-center justify-center rounded-full bg-rose-500 text-[10px] font-bold text-white shadow">
                  {wishlistCount}
                </span>
              )}
            </Link>

            <CartIcon />
            <div className="h-6 w-px bg-gray-200 hidden sm:block" />
            <UserMenu />
          </div>
        </div>

        {/* Mobile Search Bar */}
        <div className="py-2 pb-3 md:hidden">
          <SearchBar />
        </div>
      </div>

      {/* Desktop Secondary Category Navigation */}
      <nav className="hidden lg:block bg-gray-50 border-t border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <ul className="flex items-center gap-8 py-2.5 text-xs font-semibold text-gray-600 tracking-wider uppercase overflow-x-auto">
            <li>
              <NavLink to="/products" className={({ isActive }) => (isActive ? 'text-indigo-600 font-bold' : 'hover:text-indigo-600')}>
                All Products
              </NavLink>
            </li>
            <li>
              <NavLink to="/products?category=Electronics" className="hover:text-indigo-600">
                Electronics
              </NavLink>
            </li>
            <li>
              <NavLink to="/products?category=Fashion" className="hover:text-indigo-600">
                Fashion
              </NavLink>
            </li>
            <li>
              <NavLink to="/products?category=Home %26 Kitchen" className="hover:text-indigo-600">
                Home & Kitchen
              </NavLink>
            </li>
            <li>
              <NavLink to="/products?category=Beauty %26 Personal Care" className="hover:text-indigo-600">
                Beauty & Grooming
              </NavLink>
            </li>
            <li>
              <NavLink to="/products?category=Sports %26 Fitness" className="hover:text-indigo-600">
                Sports & Fitness
              </NavLink>
            </li>
            <li>
              <NavLink to="/products?category=Books %26 Stationery" className="hover:text-indigo-600">
                Books
              </NavLink>
            </li>
            <li>
              <NavLink to="/products?category=Grocery %26 Gourmet" className="hover:text-indigo-600">
                Grocery
              </NavLink>
            </li>
            <li className="ml-auto">
              <button
                type="button"
                onClick={() => setIsMumbaiMapOpen(true)}
                className="flex items-center gap-1.5 text-indigo-700 font-extrabold hover:text-indigo-900 bg-indigo-50 border border-indigo-200/60 px-3 py-1 rounded-full text-[11px] transition cursor-pointer"
              >
                <span>📍 10 Mumbai Zones Store Network</span>
              </button>
            </li>
          </ul>
        </div>
      </nav>

      {/* Mobile Drawer Menu */}
      {mobileMenuOpen && (
        <div className="lg:hidden border-t border-gray-200 bg-white py-4 px-6 space-y-4 animate-fade-in">
          <button
            type="button"
            onClick={() => {
              setMobileMenuOpen(false);
              setIsMumbaiMapOpen(true);
            }}
            className="w-full text-left text-sm font-bold text-indigo-700 bg-indigo-50 border border-indigo-100 px-3.5 py-2.5 rounded-xl flex items-center justify-between"
          >
            <span>🗺️ Mumbai Store Network Map</span>
            <span className="text-[10px] font-bold bg-indigo-600 text-white px-2 py-0.5 rounded-full">10 Zones</span>
          </button>

          <div className="flex items-center justify-between pb-2 border-b border-gray-100">
            <span className="text-xs font-bold uppercase tracking-wider text-gray-400">Categories</span>
          </div>
          <div className="space-y-2">
            <Link
              to="/products"
              onClick={() => setMobileMenuOpen(false)}
              className="block text-sm font-semibold text-gray-800 hover:text-indigo-600 py-1.5"
            >
              All Categories & Products
            </Link>
            <Link
              to="/products?category=Electronics"
              onClick={() => setMobileMenuOpen(false)}
              className="block text-sm text-gray-600 hover:text-indigo-600 py-1"
            >
              Electronics & Gadgets
            </Link>
            <Link
              to="/products?category=Fashion"
              onClick={() => setMobileMenuOpen(false)}
              className="block text-sm text-gray-600 hover:text-indigo-600 py-1"
            >
              Fashion & Apparel
            </Link>
            <Link
              to="/products?category=Home %26 Kitchen"
              onClick={() => setMobileMenuOpen(false)}
              className="block text-sm text-gray-600 hover:text-indigo-600 py-1"
            >
              Home & Kitchen
            </Link>
            <Link
              to="/products?category=Beauty %26 Personal Care"
              onClick={() => setMobileMenuOpen(false)}
              className="block text-sm text-gray-600 hover:text-indigo-600 py-1"
            >
              Beauty & Personal Care
            </Link>
            <Link
              to="/wishlist"
              onClick={() => setMobileMenuOpen(false)}
              className="block text-sm text-gray-600 hover:text-indigo-600 py-1"
            >
              My Wishlist ({wishlistCount})
            </Link>
          </div>
        </div>
      )}
    </header>
  );
};

export default Navbar;
