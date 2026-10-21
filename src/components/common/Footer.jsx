import React from 'react';
import { Link } from 'react-router-dom';
import { 
  ShoppingBag, 
  ShieldCheck, 
  Truck, 
  RotateCcw, 
  Headphones, 
  Mail, 
  Phone, 
  MapPin, 
  Lock,
  ArrowRight
} from 'lucide-react';

export const Footer = () => {
  return (
    <footer className="bg-slate-900 text-gray-300 pt-16 pb-8 border-t border-slate-800">
      {/* Value Proposition Badges */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mb-12 pb-12 border-b border-slate-800">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
          <div className="flex items-center gap-4 p-4 rounded-2xl bg-slate-800/50 border border-slate-700/50">
            <div className="w-12 h-12 rounded-xl bg-brand-600/20 text-brand-400 flex items-center justify-center shrink-0">
              <Truck className="w-6 h-6" />
            </div>
            <div>
              <h4 className="text-sm font-bold text-white">Free Fast Shipping</h4>
              <p className="text-xs text-gray-400">On all orders above ₹999</p>
            </div>
          </div>

          <div className="flex items-center gap-4 p-4 rounded-2xl bg-slate-800/50 border border-slate-700/50">
            <div className="w-12 h-12 rounded-xl bg-emerald-500/20 text-emerald-400 flex items-center justify-center shrink-0">
              <ShieldCheck className="w-6 h-6" />
            </div>
            <div>
              <h4 className="text-sm font-bold text-white">100% Authentic</h4>
              <p className="text-xs text-gray-400">Directly from authorized brands</p>
            </div>
          </div>

          <div className="flex items-center gap-4 p-4 rounded-2xl bg-slate-800/50 border border-slate-700/50">
            <div className="w-12 h-12 rounded-xl bg-purple-500/20 text-purple-400 flex items-center justify-center shrink-0">
              <RotateCcw className="w-6 h-6" />
            </div>
            <div>
              <h4 className="text-sm font-bold text-white">7-Day Easy Returns</h4>
              <p className="text-xs text-gray-400">No questions asked refund</p>
            </div>
          </div>

          <div className="flex items-center gap-4 p-4 rounded-2xl bg-slate-800/50 border border-slate-700/50">
            <div className="w-12 h-12 rounded-xl bg-amber-500/20 text-amber-400 flex items-center justify-center shrink-0">
              <Headphones className="w-6 h-6" />
            </div>
            <div>
              <h4 className="text-sm font-bold text-white">24/7 Customer Care</h4>
              <p className="text-xs text-gray-400">Dedicated support hotline</p>
            </div>
          </div>
        </div>
      </div>

      {/* Main Footer Links */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-10 mb-12">
        
        {/* Brand Overview */}
        <div className="lg:col-span-2 flex flex-col gap-4">
          <Link to="/" className="flex items-center gap-2">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-brand-500 to-indigo-600 flex items-center justify-center text-white shadow-lg">
              <ShoppingBag className="w-5 h-5" />
            </div>
            <span className="text-2xl font-extrabold text-white">AuraCart</span>
          </Link>
          <p className="text-xs text-gray-400 leading-relaxed max-w-sm">
            AuraCart is a next-generation e-commerce platform delivering flagship electronics, fashion, mobile devices, and lifestyle products with lightning-fast delivery and AI-driven recommendations.
          </p>
          <div className="flex items-center gap-3 text-xs text-gray-400 pt-2">
            <div className="flex items-center gap-1.5"><Lock className="w-4 h-4 text-emerald-400" /> 256-Bit SSL Encryption</div>
          </div>
        </div>

        {/* Quick Shop Links */}
        <div>
          <h4 className="text-sm font-bold text-white uppercase tracking-wider mb-4">Shop Categories</h4>
          <ul className="space-y-2.5 text-xs">
            <li><Link to="/products?category=electronics" className="hover:text-white transition-colors">Electronics & Audio</Link></li>
            <li><Link to="/products?category=mobiles" className="hover:text-white transition-colors">Mobiles & Tablets</Link></li>
            <li><Link to="/products?category=laptops" className="hover:text-white transition-colors">Laptops & Computers</Link></li>
            <li><Link to="/products?category=fashion" className="hover:text-white transition-colors">Fashion & Apparel</Link></li>
            <li><Link to="/products?category=home" className="hover:text-white transition-colors">Home & Kitchen</Link></li>
            <li><Link to="/products?category=beauty" className="hover:text-white transition-colors">Beauty & Personal Care</Link></li>
          </ul>
        </div>

        {/* Customer Support */}
        <div>
          <h4 className="text-sm font-bold text-white uppercase tracking-wider mb-4">Customer Care</h4>
          <ul className="space-y-2.5 text-xs">
            <li><Link to="/dashboard?tab=orders" className="hover:text-white transition-colors">Track Order</Link></li>
            <li><Link to="/cart" className="hover:text-white transition-colors">View Cart</Link></li>
            <li><Link to="/wishlist" className="hover:text-white transition-colors">Saved Wishlist</Link></li>
            <li><a href="#faq" className="hover:text-white transition-colors">Shipping Policy</a></li>
            <li><a href="#returns" className="hover:text-white transition-colors">Returns & Refunds</a></li>
            <li><a href="#terms" className="hover:text-white transition-colors">Terms of Service</a></li>
          </ul>
        </div>

        {/* Contact Info */}
        <div>
          <h4 className="text-sm font-bold text-white uppercase tracking-wider mb-4">Get In Touch</h4>
          <ul className="space-y-3 text-xs text-gray-400">
            <li className="flex items-start gap-2.5">
              <MapPin className="w-4 h-4 text-brand-400 shrink-0 mt-0.5" />
              <span>AuraCart Tower, Sector 62, Noida, UP 201301</span>
            </li>
            <li className="flex items-center gap-2.5">
              <Phone className="w-4 h-4 text-brand-400 shrink-0" />
              <span>+91 1800-420-9900 (Toll Free)</span>
            </li>
            <li className="flex items-center gap-2.5">
              <Mail className="w-4 h-4 text-brand-400 shrink-0" />
              <span>support@auracart.com</span>
            </li>
          </ul>
        </div>

      </div>

      {/* Copyright & Payment Badges */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-8 border-t border-slate-800 flex flex-col md:flex-row items-center justify-between gap-4 text-xs text-gray-500">
        <p>© 2026 AuraCart Technologies Pvt Ltd. All rights reserved.</p>
        <div className="flex items-center gap-3">
          <span className="bg-slate-800 text-gray-300 font-semibold px-2.5 py-1 rounded">UPI</span>
          <span className="bg-slate-800 text-gray-300 font-semibold px-2.5 py-1 rounded">VISA</span>
          <span className="bg-slate-800 text-gray-300 font-semibold px-2.5 py-1 rounded">Mastercard</span>
          <span className="bg-slate-800 text-gray-300 font-semibold px-2.5 py-1 rounded">RuPay</span>
          <span className="bg-slate-800 text-gray-300 font-semibold px-2.5 py-1 rounded">NetBanking</span>
        </div>
      </div>
    </footer>
  );
};
