import React from 'react';
import { Link } from 'react-router-dom';
import { ShieldCheck, Truck, RotateCcw, Headphones, Mail, Phone, MapPin } from 'lucide-react';

export const Footer = () => {
  return (
    <footer className="bg-slate-900 text-slate-300 pt-12 pb-8 border-t border-slate-800">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Top Trust Features */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-6 pb-10 border-b border-slate-800 text-center sm:text-left">
          <div className="flex items-center gap-3">
            <div className="p-3 bg-slate-800 rounded-xl text-indigo-400">
              <Truck className="w-6 h-6" />
            </div>
            <div>
              <h4 className="text-xs font-bold text-white uppercase tracking-wider">Express Shipping</h4>
              <p className="text-[11px] text-slate-400">Free delivery on orders over ₹499</p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <div className="p-3 bg-slate-800 rounded-xl text-indigo-400">
              <ShieldCheck className="w-6 h-6" />
            </div>
            <div>
              <h4 className="text-xs font-bold text-white uppercase tracking-wider">100% Authentic</h4>
              <p className="text-[11px] text-slate-400">Direct from authorized brands</p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <div className="p-3 bg-slate-800 rounded-xl text-indigo-400">
              <RotateCcw className="w-6 h-6" />
            </div>
            <div>
              <h4 className="text-xs font-bold text-white uppercase tracking-wider">Easy Returns</h4>
              <p className="text-[11px] text-slate-400">7 days hassle-free returns</p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <div className="p-3 bg-slate-800 rounded-xl text-indigo-400">
              <Headphones className="w-6 h-6" />
            </div>
            <div>
              <h4 className="text-xs font-bold text-white uppercase tracking-wider">24/7 Support</h4>
              <p className="text-[11px] text-slate-400">Dedicated Indian helpline</p>
            </div>
          </div>
        </div>

        {/* Links Grid */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8 py-10">
          <div className="space-y-4">
            <Link to="/" className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-lg bg-indigo-600 flex items-center justify-center text-white font-extrabold text-lg">
                A
              </div>
              <span className="font-extrabold text-xl text-white tracking-tight">
                Aura<span className="text-indigo-400">Cart</span>
              </span>
            </Link>
            <p className="text-xs text-slate-400 leading-relaxed">
              India's premier e-commerce shopping destination offering genuine products with fast nationwide shipping & secure payments.
            </p>
            <div className="flex items-center gap-2 text-xs text-slate-400">
              <MapPin className="w-4 h-4 text-indigo-400 shrink-0" />
              <span>Noida, Uttar Pradesh, India - 201301</span>
            </div>
          </div>

          <div>
            <h4 className="text-xs font-bold text-white uppercase tracking-wider mb-4">Shop Categories</h4>
            <ul className="space-y-2 text-xs">
              <li><Link to="/products?category=Electronics" className="hover:text-indigo-400 transition">Electronics & Audio</Link></li>
              <li><Link to="/products?category=Fashion" className="hover:text-indigo-400 transition">Fashion & Apparel</Link></li>
              <li><Link to="/products?category=Home %26 Kitchen" className="hover:text-indigo-400 transition">Home & Kitchen</Link></li>
              <li><Link to="/products?category=Beauty %26 Personal Care" className="hover:text-indigo-400 transition">Beauty & Personal Care</Link></li>
              <li><Link to="/products?category=Sports %26 Fitness" className="hover:text-indigo-400 transition">Sports & Gym Gear</Link></li>
            </ul>
          </div>

          <div>
            <h4 className="text-xs font-bold text-white uppercase tracking-wider mb-4">Customer Service</h4>
            <ul className="space-y-2 text-xs">
              <li><Link to="/orders" className="hover:text-indigo-400 transition">Track Your Order</Link></li>
              <li><Link to="/profile" className="hover:text-indigo-400 transition">My Profile & Addresses</Link></li>
              <li><Link to="/cart" className="hover:text-indigo-400 transition">View Shopping Cart</Link></li>
              <li><Link to="/wishlist" className="hover:text-indigo-400 transition">Wishlist Items</Link></li>
              <li><Link to="/login" className="hover:text-indigo-400 transition">Login / Register</Link></li>
            </ul>
          </div>

          <div>
            <h4 className="text-xs font-bold text-white uppercase tracking-wider mb-4">Contact Us</h4>
            <div className="space-y-3 text-xs">
              <div className="flex items-center gap-2">
                <Phone className="w-4 h-4 text-indigo-400" />
                <span>+91 1800-123-4567 (Toll-Free)</span>
              </div>
              <div className="flex items-center gap-2">
                <Mail className="w-4 h-4 text-indigo-400" />
                <span>support@auracart.in</span>
              </div>
              <div className="pt-2">
                <p className="text-[10px] text-slate-500 uppercase tracking-widest font-bold mb-2">Supported Payments</p>
                <div className="flex gap-2 text-xs font-mono text-slate-400">
                  <span className="px-2 py-1 bg-slate-800 rounded">UPI</span>
                  <span className="px-2 py-1 bg-slate-800 rounded">GPay</span>
                  <span className="px-2 py-1 bg-slate-800 rounded">Cards</span>
                  <span className="px-2 py-1 bg-slate-800 rounded">COD</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Bottom Copyright */}
        <div className="pt-6 border-t border-slate-800 text-center text-xs text-slate-500 flex flex-col sm:flex-row items-center justify-between gap-4">
          <p>© {new Date().getFullYear()} AuraCart India E-Commerce Platform. All rights reserved.</p>
          <div className="flex gap-4">
            <span className="hover:text-slate-400 cursor-pointer">Privacy Policy</span>
            <span className="hover:text-slate-400 cursor-pointer">Terms of Service</span>
            <span className="hover:text-slate-400 cursor-pointer">Security</span>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
