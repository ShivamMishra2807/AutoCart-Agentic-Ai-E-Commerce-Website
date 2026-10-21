import React, { useState, useEffect } from 'react';
import ProductCard from '../product/ProductCard';
import { products } from '../../data/products';
import { Flame, Clock } from 'lucide-react';

export const DealsSection = () => {
  const deals = products.filter((p) => p.discount >= 40).slice(0, 4);

  // Live countdown timer
  const [timeLeft, setTimeLeft] = useState({
    hours: 7,
    minutes: 48,
    seconds: 35,
  });

  useEffect(() => {
    const timer = setInterval(() => {
      setTimeLeft((prev) => {
        if (prev.seconds > 0) {
          return { ...prev, seconds: prev.seconds - 1 };
        } else if (prev.minutes > 0) {
          return { ...prev, minutes: 59, seconds: 59 };
        } else if (prev.hours > 0) {
          return { hours: prev.hours - 1, minutes: 59, seconds: 59 };
        }
        return { hours: 8, minutes: 0, seconds: 0 };
      });
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  const pad = (n) => String(n).padStart(2, '0');

  return (
    <section className="mb-12 bg-gradient-to-r from-rose-50 via-amber-50 to-orange-50 p-6 sm:p-8 rounded-3xl border border-rose-100 transition-colors">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between mb-6 gap-3">
        <div className="flex items-center gap-3">
          <div className="p-2.5 bg-gradient-to-tr from-rose-500 to-orange-500 text-white rounded-2xl shadow-lg shadow-rose-500/30">
            <Flame className="w-6 h-6 animate-pulse" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-xl sm:text-2xl font-black text-gray-900 tracking-tight">
                Deal of the Day
              </h2>
              <span className="bg-rose-500 text-white text-[10px] font-extrabold px-2 py-0.5 rounded-full uppercase tracking-wider animate-pulse">
                Hot
              </span>
            </div>
            <p className="text-xs sm:text-sm text-rose-700 font-medium">
              Up to 70% discount on top tech and fashion brands
            </p>
          </div>
        </div>

        {/* Live Ticking Countdown Box */}
        <div className="inline-flex items-center gap-2 px-4 py-2 bg-white/90 backdrop-blur-md rounded-2xl border border-rose-200 text-xs font-bold text-rose-700 shadow-sm w-fit">
          <Clock className="w-4 h-4 text-rose-500 animate-spin" style={{ animationDuration: '6s' }} />
          <span>Ends in:</span>
          <div className="flex items-center gap-1 font-mono text-sm font-black">
            <span className="bg-rose-100 text-rose-800 px-1.5 py-0.5 rounded">
              {pad(timeLeft.hours)}h
            </span>
            :
            <span className="bg-rose-100 text-rose-800 px-1.5 py-0.5 rounded">
              {pad(timeLeft.minutes)}m
            </span>
            :
            <span className="bg-rose-100 text-rose-800 px-1.5 py-0.5 rounded">
              {pad(timeLeft.seconds)}s
            </span>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6">
        {deals.map((product) => (
          <ProductCard key={product.id} product={product} />
        ))}
      </div>
    </section>
  );
};

export default DealsSection;
