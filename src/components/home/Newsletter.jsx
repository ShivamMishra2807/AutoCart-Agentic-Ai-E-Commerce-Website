import React, { useState } from 'react';
import { Mail, CheckCircle2 } from 'lucide-react';
import { useToast } from '../../context/ToastContext';

export const Newsletter = () => {
  const [email, setEmail] = useState('');
  const [submitted, setSubmitted] = useState(false);
  const { addToast } = useToast();

  const handleSubmit = (e) => {
    e.preventDefault();
    if (email && email.includes('@')) {
      setSubmitted(true);
      addToast('Thank you for subscribing! Check your email for ₹500 off coupon.', 'success');
      setEmail('');
    } else {
      addToast('Please enter a valid email address.', 'error');
    }
  };

  return (
    <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
      <div className="bg-gradient-to-r from-brand-600 via-indigo-600 to-purple-700 rounded-3xl p-8 sm:p-12 text-white shadow-2xl relative overflow-hidden flex flex-col md:flex-row items-center justify-between gap-8">
        
        <div className="max-w-xl z-10">
          <div className="inline-flex items-center gap-2 bg-white/20 px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider mb-3">
            <Mail className="w-3.5 h-3.5" /> Newsletter
          </div>
          <h2 className="text-2xl sm:text-4xl font-black tracking-tight leading-tight">
            Subscribe & Get ₹500 Instant Discount Coupon
          </h2>
          <p className="text-xs sm:text-sm text-gray-200 mt-2">
            Join 150,000+ happy shoppers. Receive exclusive VIP offers, secret flash deal alerts & new product launches directly in your inbox.
          </p>
        </div>

        <div className="w-full max-w-md z-10">
          {submitted ? (
            <div className="bg-white/20 backdrop-blur-md border border-white/30 rounded-2xl p-4 flex items-center gap-3">
              <CheckCircle2 className="w-6 h-6 text-emerald-300 shrink-0" />
              <span className="text-sm font-semibold">You're subscribed! Use promo code <strong>FIRST500</strong> at checkout.</span>
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="flex flex-col sm:flex-row gap-2 bg-white/10 backdrop-blur-md p-2 rounded-2xl border border-white/20">
              <input
                type="email"
                placeholder="Enter your email address..."
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full px-4 py-3 bg-white text-gray-900 placeholder-gray-400 rounded-xl text-sm font-medium focus:outline-none"
                required
              />
              <button
                type="submit"
                className="px-6 py-3 bg-gray-900 hover:bg-black text-white font-extrabold rounded-xl text-sm transition-all whitespace-nowrap shadow-lg"
              >
                Claim ₹500
              </button>
            </form>
          )}
        </div>

      </div>
    </section>
  );
};
