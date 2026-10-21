import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { ChevronLeft, ChevronRight, ArrowRight, Sparkles } from 'lucide-react';
import { HERO_BANNERS } from '../../data/mockBanners';

export const HeroCarousel = () => {
  const [currentIndex, setCurrentIndex] = useState(0);

  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentIndex((prev) => (prev + 1) % HERO_BANNERS.length);
    }, 5000);
    return () => clearInterval(timer);
  }, []);

  const handlePrev = () => {
    setCurrentIndex((prev) => (prev - 1 + HERO_BANNERS.length) % HERO_BANNERS.length);
  };

  const handleNext = () => {
    setCurrentIndex((prev) => (prev + 1) % HERO_BANNERS.length);
  };

  const currentBanner = HERO_BANNERS[currentIndex];

  return (
    <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
      <div className={`relative overflow-hidden rounded-3xl bg-gradient-to-r ${currentBanner.bgGradient} min-h-[360px] sm:min-h-[440px] flex items-center shadow-2xl transition-all duration-700`}>
        
        {/* Background Image Overlay */}
        <div className="absolute inset-0 opacity-25 mix-blend-overlay">
          <img src={currentBanner.image} alt={currentBanner.title} className="w-full h-full object-cover" />
        </div>

        {/* Content Container */}
        <div className="relative z-10 p-8 sm:p-14 max-w-2xl text-white flex flex-col gap-4">
          <div className="inline-flex items-center gap-2 bg-white/10 backdrop-blur-md px-3.5 py-1.5 rounded-full text-xs font-bold tracking-wider uppercase border border-white/20 w-fit">
            <Sparkles className="w-4 h-4 text-amber-300" />
            <span>{currentBanner.tag}</span>
          </div>

          <h1 className="text-3xl sm:text-5xl font-black tracking-tight leading-tight">
            {currentBanner.title}
          </h1>

          <p className="text-sm sm:text-lg text-gray-200 font-medium leading-relaxed">
            {currentBanner.subtitle}
          </p>

          <div className="pt-2">
            <Link
              to={currentBanner.ctaLink}
              className="inline-flex items-center gap-2 bg-white hover:bg-brand-50 text-gray-900 font-extrabold px-6 py-3.5 rounded-2xl text-sm shadow-xl shadow-black/20 hover:scale-105 transition-all"
            >
              <span>{currentBanner.ctaText}</span>
              <ArrowRight className="w-4 h-4 text-brand-600" />
            </Link>
          </div>
        </div>

        {/* Hero Product Visual Preview */}
        <div className="hidden lg:block absolute right-12 top-1/2 -translate-y-1/2 w-80 h-80 rounded-3xl overflow-hidden shadow-2xl border-4 border-white/10 rotate-2 hover:rotate-0 transition-transform duration-500">
          <img src={currentBanner.image} alt={currentBanner.title} className="w-full h-full object-cover" />
        </div>

        {/* Carousel Controls */}
        <button
          onClick={handlePrev}
          className="absolute left-4 top-1/2 -translate-y-1/2 p-3 rounded-full bg-black/20 hover:bg-black/40 text-white backdrop-blur-sm transition-all"
          aria-label="Previous Slide"
        >
          <ChevronLeft className="w-6 h-6" />
        </button>

        <button
          onClick={handleNext}
          className="absolute right-4 top-1/2 -translate-y-1/2 p-3 rounded-full bg-black/20 hover:bg-black/40 text-white backdrop-blur-sm transition-all"
          aria-label="Next Slide"
        >
          <ChevronRight className="w-6 h-6" />
        </button>

        {/* Carousel Indicators */}
        <div className="absolute bottom-4 left-1/2 -translate-x-1/2 flex gap-2 z-10">
          {HERO_BANNERS.map((_, idx) => (
            <button
              key={idx}
              onClick={() => setCurrentIndex(idx)}
              className={`h-2 rounded-full transition-all ${
                currentIndex === idx ? 'w-8 bg-white' : 'w-2 bg-white/40'
              }`}
            />
          ))}
        </div>

      </div>
    </div>
  );
};
