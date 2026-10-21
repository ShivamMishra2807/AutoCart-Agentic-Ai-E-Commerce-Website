import React from 'react';
import { ArrowRight, ShoppingBag, ShieldCheck, Truck, RefreshCw, Zap } from 'lucide-react';
import { Link } from 'react-router-dom';

export const Hero = () => {
  return (
    <div className="relative overflow-hidden bg-gradient-to-br from-indigo-600 via-indigo-700 to-purple-800 text-white py-12 lg:py-16 rounded-3xl mb-12 shadow-xl">
      {/* Decorative Light Glows */}
      <div className="absolute top-0 right-0 -mt-10 -mr-10 w-96 h-96 bg-white/10 rounded-full blur-3xl pointer-events-none" />
      <div className="absolute bottom-0 left-0 -mb-10 -ml-10 w-96 h-96 bg-purple-400/20 rounded-full blur-3xl pointer-events-none" />

      <div className="relative max-w-7xl mx-auto px-6 sm:px-8 lg:px-12 grid grid-cols-1 lg:grid-cols-2 gap-10 items-center">
        {/* Left Copy */}
        <div className="space-y-5 text-center lg:text-left">
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-white/20 border border-white/30 text-white text-xs font-bold uppercase tracking-widest backdrop-blur-md">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping" />
            Big Festive Shopping Carnival
          </div>

          <h1 className="text-3xl sm:text-5xl lg:text-5xl font-black tracking-tight leading-tight">
            Upgrade Your Lifestyle with <span className="text-amber-300">Mega Savings</span>
          </h1>

          <p className="text-indigo-100 text-sm sm:text-base max-w-xl mx-auto lg:mx-0 font-medium leading-relaxed">
            Shop genuine electronics, trendsetting fashion, and home essentials with guaranteed 24-hour dispatch and verified brand warranty.
          </p>

          <div className="flex flex-col sm:flex-row items-center justify-center lg:justify-start gap-3.5 pt-2">
            <Link
              to="/products"
              className="w-full sm:w-auto inline-flex items-center justify-center gap-2 bg-amber-400 hover:bg-amber-300 text-gray-900 font-extrabold px-8 py-3.5 rounded-2xl shadow-lg shadow-amber-400/30 transition-all transform hover:-translate-y-0.5 active:scale-95"
            >
              <ShoppingBag className="w-5 h-5 text-gray-900" />
              Shop Now
            </Link>
            <Link
              to="/products?sortBy=price_low_high"
              className="w-full sm:w-auto inline-flex items-center justify-center gap-2 bg-white/15 hover:bg-white/25 text-white font-bold px-6 py-3.5 rounded-2xl border border-white/25 backdrop-blur-md transition-all active:scale-95"
            >
              View Festive Deals
              <ArrowRight className="w-4 h-4" />
            </Link>
          </div>

          {/* Value Badges */}
          <div className="pt-6 border-t border-white/20 grid grid-cols-3 gap-3 text-xs font-semibold text-white/90">
            <div className="flex items-center justify-center lg:justify-start gap-2">
              <Truck className="w-4 h-4 text-amber-300 shrink-0" />
              <span>Free Delivery &gt; ₹499</span>
            </div>
            <div className="flex items-center justify-center lg:justify-start gap-2">
              <ShieldCheck className="w-4 h-4 text-amber-300 shrink-0" />
              <span>100% Genuine Brands</span>
            </div>
            <div className="flex items-center justify-center lg:justify-start gap-2">
              <RefreshCw className="w-4 h-4 text-amber-300 shrink-0" />
              <span>7 Days Easy Return</span>
            </div>
          </div>
        </div>

        {/* Right Featured Banner Showcase */}
        <div className="relative flex justify-center">
          <div className="relative w-full max-w-md bg-white p-3 rounded-3xl shadow-2xl border border-white/20 transform hover:scale-[1.02] transition-transform">
            <img
              src="https://images.unsplash.com/photo-1498049794561-7780e7231661?w=800&q=80"
              alt="Hero showcase"
              className="w-full h-64 sm:h-72 object-cover rounded-2xl"
            />
            <div className="p-3 bg-gray-50 rounded-2xl mt-2 flex items-center justify-between border border-gray-100">
              <div>
                <p className="text-[11px] font-bold text-indigo-600 uppercase tracking-wider flex items-center gap-1">
                  <Zap className="w-3.5 h-3.5 fill-indigo-600" /> Deal of the Day
                </p>
                <h4 className="text-sm font-extrabold text-gray-900">boAt Airdopes 141 ANC</h4>
                <p className="text-xs text-gray-500 font-semibold">
                  Starting at <span className="text-gray-900 font-bold">₹1,499</span>{' '}
                  <span className="line-through text-gray-400">₹4,490</span>
                </p>
              </div>
              <span className="bg-rose-500 text-white font-extrabold text-xs px-3 py-1.5 rounded-xl shadow">
                67% OFF
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Hero;
