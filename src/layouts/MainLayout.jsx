import React, { useState, useEffect } from 'react';
import { Outlet, useLocation } from 'react-router-dom';
import { Navbar } from '../components/common/Navbar';
import { CategoryNav } from '../components/common/CategoryNav';
import { Footer } from '../components/common/Footer';
import { AIAssistantDrawer } from '../components/ai/AIAssistantDrawer';
import { ArrowUp, Sparkles } from 'lucide-react';

export const MainLayout = () => {
  const [isAIOpen, setIsAIOpen] = useState(false);
  const [showScrollTop, setShowScrollTop] = useState(false);
  const { pathname } = useLocation();

  // Scroll to top on route change
  useEffect(() => {
    window.scrollTo(0, 0);
  }, [pathname]);

  // Monitor scroll for back-to-top button
  useEffect(() => {
    const handleScroll = () => {
      if (window.scrollY > 300) {
        setShowScrollTop(true);
      } else {
        setShowScrollTop(false);
      }
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const scrollToTop = () => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  return (
    <div className="min-h-screen flex flex-col bg-gray-50 selection:bg-brand-500 selection:text-white">
      <Navbar onOpenAIAssistant={() => setIsAIOpen(true)} />
      <CategoryNav />
      
      <main className="flex-1">
        <Outlet />
      </main>

      <Footer />

      {/* Floating Scroll To Top Button */}
      {showScrollTop && (
        <button
          onClick={scrollToTop}
          className="fixed bottom-6 left-6 z-40 p-3 rounded-2xl bg-white shadow-xl border border-gray-200 text-gray-700 hover:text-brand-600 hover:border-brand-300 transition-all duration-300 hover:scale-110"
          aria-label="Scroll to top"
        >
          <ArrowUp className="w-5 h-5" />
        </button>
      )}

      {/* Floating AutoCart Agentic AI Button */}
      <button
        onClick={() => setIsAIOpen(true)}
        className="fixed bottom-6 right-6 z-40 flex items-center gap-2.5 px-4 py-3 rounded-full bg-gradient-to-r from-indigo-600 via-purple-600 to-indigo-700 text-white font-extrabold text-xs shadow-2xl shadow-indigo-700/50 hover:shadow-indigo-600/70 hover:scale-105 active:scale-95 transition-all duration-300 border border-white/20 group"
        title="Open AutoCart Agentic AI"
      >
        <div className="w-6 h-6 rounded-full bg-white/20 flex items-center justify-center">
          <Sparkles className="w-3.5 h-3.5 text-amber-300 animate-spin" style={{ animationDuration: '4s' }} />
        </div>
        <span className="tracking-wide">Ask Agentic AI</span>
        <span className="flex h-2 w-2 relative">
          <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-amber-400 opacity-75"></span>
          <span className="relative inline-flex rounded-full h-2 w-2 bg-amber-300"></span>
        </span>
      </button>

      {/* AI Assistant Drawer Component */}
      <AIAssistantDrawer isOpen={isAIOpen} onClose={() => setIsAIOpen(false)} />
    </div>
  );
};
