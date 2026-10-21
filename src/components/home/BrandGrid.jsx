import React from 'react';
import { POPULAR_BRANDS } from '../../data/mockBanners';

export const BrandGrid = () => {
  return (
    <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="bg-gradient-to-br from-slate-900 via-indigo-950 to-slate-900 rounded-3xl p-8 text-white shadow-xl">
        <div className="text-center max-w-xl mx-auto mb-8">
          <h2 className="text-xl sm:text-2xl font-black tracking-tight">Official Partner Brands</h2>
          <p className="text-xs sm:text-sm text-gray-400 mt-1">100% Brand Certified Products with Manufacturer Warranty</p>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-6 gap-4">
          {POPULAR_BRANDS.map((brand, idx) => (
            <div
              key={idx}
              className="bg-white/10 backdrop-blur-md rounded-2xl p-4 flex items-center justify-center border border-white/10 hover:border-brand-400 hover:bg-white/20 transition-all cursor-pointer group"
            >
              <span className="text-base font-extrabold text-white group-hover:scale-110 transition-transform tracking-wider">
                {brand.name}
              </span>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};
