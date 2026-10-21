import React from 'react';
import { Link } from 'react-router-dom';
import { ArrowRight, Tag } from 'lucide-react';

export const PromotionalBanner = () => {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-12">
      {/* Banner 1 */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-r from-purple-900 to-indigo-900 text-white p-8 shadow-lg flex flex-col justify-between h-64">
        <div className="relative z-10 space-y-2">
          <span className="inline-flex items-center gap-1.5 bg-amber-400 text-slate-950 font-bold text-[10px] uppercase px-2.5 py-1 rounded">
            <Tag className="w-3 h-3" /> Special Collection
          </span>
          <h3 className="text-2xl font-extrabold tracking-tight">Audio & Smart Gadgets</h3>
          <p className="text-xs text-purple-200 max-w-xs">Upgrade your lifestyle with noise cancelling headphones & TWS earbuds starting at ₹999.</p>
        </div>
        <div className="relative z-10 pt-4">
          <Link
            to="/products?category=Electronics"
            className="inline-flex items-center gap-2 bg-white text-purple-950 font-bold text-xs px-5 py-2.5 rounded-lg shadow hover:bg-purple-50 transition"
          >
            Explore Electronics
            <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>
        <img
          src="https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=500&q=80"
          alt="Promotional audio"
          className="absolute right-[-20px] bottom-[-20px] w-48 h-48 object-contain opacity-40 mix-blend-overlay pointer-events-none"
        />
      </div>

      {/* Banner 2 */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-r from-slate-900 to-emerald-950 text-white p-8 shadow-lg flex flex-col justify-between h-64">
        <div className="relative z-10 space-y-2">
          <span className="inline-flex items-center gap-1.5 bg-emerald-400 text-slate-950 font-bold text-[10px] uppercase px-2.5 py-1 rounded">
            Up to 50% OFF
          </span>
          <h3 className="text-2xl font-extrabold tracking-tight">Festive Ethnic & Fashion</h3>
          <p className="text-xs text-emerald-200 max-w-xs">Curated designer sarees, Anarkali kurtas & casual denim for everyday wear.</p>
        </div>
        <div className="relative z-10 pt-4">
          <Link
            to="/products?category=Fashion"
            className="inline-flex items-center gap-2 bg-white text-emerald-950 font-bold text-xs px-5 py-2.5 rounded-lg shadow hover:bg-emerald-50 transition"
          >
            Shop Fashion
            <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>
        <img
          src="https://images.unsplash.com/photo-1610030469983-98e550d6193c?w=500&q=80"
          alt="Promotional fashion"
          className="absolute right-[-20px] bottom-[-20px] w-48 h-48 object-contain opacity-40 mix-blend-overlay pointer-events-none"
        />
      </div>
    </div>
  );
};

export default PromotionalBanner;
