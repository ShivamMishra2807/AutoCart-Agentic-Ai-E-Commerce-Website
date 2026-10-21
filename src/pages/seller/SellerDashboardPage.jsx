import React, { useState, useEffect } from 'react';
import {
  Sparkles, Bot, Package, TrendingUp, AlertTriangle, CheckCircle2,
  Tag, Store, RefreshCw, PlusCircle, ArrowUpRight, DollarSign, Loader2
} from 'lucide-react';
import agentService from '../../services/agentService';
import EnquiryInbox from '../../storefront/EnquiryInbox';
import api from '../../services/api';

export const SellerDashboardPage = () => {
  const [activeTab, setActiveTab] = useState('copilot'); // 'copilot' | 'health' | 'listings'
  const [prompt, setPrompt] = useState('');
  const [title, setTitle] = useState('Wireless Noise Cancelling Gaming Headphones');
  const [category, setCategory] = useState('Electronics');
  const [rawSpecs, setRawSpecs] = useState('Bluetooth 5.3, 40hr battery, 40mm titanium drivers, RGB lighting, 32ms ultra-low latency');
  
  const [listingDraft, setListingDraft] = useState(null);
  const [generating, setGenerating] = useState(false);
  const [inventoryHealth, setInventoryHealth] = useState(null);
  const [healthLoading, setHealthLoading] = useState(false);
  const [publishedNotice, setPublishedNotice] = useState('');

  useEffect(() => {
    fetchInventoryHealth();
  }, []);

  const fetchInventoryHealth = async () => {
    setHealthLoading(true);
    try {
      const res = await agentService.sellerAssistant('Check inventory and low stock health', 'sel-techhub');
      setInventoryHealth(res.inventoryHealth || null);
    } catch (err) {
      console.warn('Could not load inventory health', err);
    } finally {
      setHealthLoading(false);
    }
  };

  const handleGenerateListing = async (e) => {
    e?.preventDefault();
    setGenerating(true);
    setPublishedNotice('');
    try {
      const res = await agentService.sellerAssistant('Create product listing', 'sel-techhub', {
        title,
        category,
        rawSpecs,
      });
      setListingDraft(res.listingDraft || null);
    } catch (err) {
      console.error(err);
    } finally {
      setGenerating(false);
    }
  };

  const handlePublishListing = () => {
    setPublishedNotice(`Listing "${listingDraft?.suggestedTitle}" submitted to marketplace staging. Awaiting catalog index verification.`);
    setTimeout(() => {
      setListingDraft(null);
    }, 3000);
  };

  return (
    <div className="max-w-6xl mx-auto py-8 px-4 space-y-8">
      {/* Banner */}
      <div className="rounded-3xl bg-gradient-to-r from-slate-900 via-indigo-950 to-purple-950 text-white p-6 sm:p-8 shadow-xl">
        <div className="flex items-start justify-between gap-4">
          <div>
            <span className="text-[10px] font-extrabold uppercase tracking-widest text-indigo-300">
              Agent E • Seller Business Copilot
            </span>
            <h1 className="text-2xl sm:text-3xl font-extrabold mt-1 flex items-center gap-2">
              <Bot className="w-7 h-7 text-amber-300" /> Seller Business Assistant
            </h1>
            <p className="text-xs text-indigo-200 mt-2 max-w-xl leading-relaxed">
              Accelerate your marketplace revenue with AI listing generation, real catalog price benchmarking, and physical store stock replenishment alerts.
            </p>
          </div>
          <div className="hidden sm:flex items-center gap-2 bg-white/10 px-3.5 py-2 rounded-2xl border border-white/10 text-xs font-bold text-amber-300">
            <Store className="w-4 h-4" />
            <span>Apex Electronics Hub</span>
          </div>
        </div>

        {/* Tab Controls */}
        <div className="flex gap-2 mt-6 pt-6 border-t border-white/10 text-xs">
          <button
            onClick={() => setActiveTab('copilot')}
            className={`px-4 py-2 rounded-xl font-bold transition flex items-center gap-1.5 ${
              activeTab === 'copilot'
                ? 'bg-indigo-600 text-white shadow-md'
                : 'bg-white/10 text-indigo-200 hover:bg-white/20'
            }`}
          >
            <Sparkles className="w-3.5 h-3.5 text-amber-300" />
            AI Listing Generator
          </button>
          <button
            onClick={() => setActiveTab('health')}
            className={`px-4 py-2 rounded-xl font-bold transition flex items-center gap-1.5 ${
              activeTab === 'health'
                ? 'bg-indigo-600 text-white shadow-md'
                : 'bg-white/10 text-indigo-200 hover:bg-white/20'
            }`}
          >
            <AlertTriangle className="w-3.5 h-3.5 text-amber-400" />
            Stock Health & Replenishment
          </button>
        </div>
      </div>

      {publishedNotice && (
        <div className="p-4 bg-emerald-50 border border-emerald-200 rounded-2xl text-xs text-emerald-800 font-bold flex items-center gap-2">
          <CheckCircle2 className="w-5 h-5 text-emerald-600 shrink-0" />
          <span>{publishedNotice}</span>
        </div>
      )}

      {/* TAB 1: AI LISTING GENERATOR */}
      {activeTab === 'copilot' && (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* Input Form (5 cols) */}
          <div className="lg:col-span-5 bg-white rounded-3xl border border-gray-100 shadow-sm p-6 space-y-4">
            <h2 className="text-sm font-extrabold text-gray-900 flex items-center gap-2">
              <PlusCircle className="w-4 h-4 text-indigo-600" /> Product Draft Details
            </h2>

            <form onSubmit={handleGenerateListing} className="space-y-3.5 text-xs font-bold text-gray-600">
              <label className="block">
                <span>Working Product Title *</span>
                <input
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  placeholder="e.g. Ergonomic Gaming Mouse"
                  className="mt-1 w-full px-3.5 py-2.5 rounded-xl border border-gray-200 focus:outline-none focus:border-indigo-600 font-semibold"
                />
              </label>

              <label className="block">
                <span>Category</span>
                <select
                  value={category}
                  onChange={(e) => setCategory(e.target.value)}
                  className="mt-1 w-full px-3.5 py-2.5 rounded-xl border border-gray-200 focus:outline-none focus:border-indigo-600 font-semibold bg-white"
                >
                  <option value="Electronics">Electronics & Audio</option>
                  <option value="Laptops">Laptops & Computers</option>
                  <option value="Fashion">Fashion & Apparel</option>
                  <option value="Home & Kitchen">Home & Kitchen</option>
                </select>
              </label>

              <label className="block">
                <span>Raw Specifications & Key Features</span>
                <textarea
                  rows={4}
                  value={rawSpecs}
                  onChange={(e) => setRawSpecs(e.target.value)}
                  placeholder="Paste specs, dimensions, battery life, materials..."
                  className="mt-1 w-full px-3.5 py-2.5 rounded-xl border border-gray-200 focus:outline-none focus:border-indigo-600 font-medium"
                />
              </label>

              <button
                type="submit"
                disabled={generating || !title}
                className="w-full py-3 rounded-xl bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700 text-white font-extrabold text-xs shadow-md transition disabled:opacity-50 flex items-center justify-center gap-2 cursor-pointer"
              >
                {generating ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    <span>Agent E Drafting Listing...</span>
                  </>
                ) : (
                  <>
                    <Sparkles className="w-4 h-4 text-amber-300" />
                    <span>Generate Optimized Listing</span>
                  </>
                )}
              </button>
            </form>
          </div>

          {/* AI Output / Listing Preview (7 cols) */}
          <div className="lg:col-span-7 bg-white rounded-3xl border border-gray-100 shadow-sm p-6 space-y-5">
            <h2 className="text-sm font-extrabold text-gray-900 flex items-center justify-between">
              <span className="flex items-center gap-2">
                <Bot className="w-4 h-4 text-indigo-600" /> Generated Listing Preview
              </span>
              {listingDraft && (
                <span className="text-[10px] font-bold text-amber-600 bg-amber-50 px-2.5 py-0.5 rounded-full border border-amber-200">
                  Draft — Requires Confirmation
                </span>
              )}
            </h2>

            {listingDraft ? (
              <div className="space-y-4 text-xs">
                {/* Title */}
                <div>
                  <span className="text-[10px] font-extrabold uppercase tracking-wider text-gray-400">
                    Optimized Marketplace Title
                  </span>
                  <p className="text-sm font-extrabold text-gray-900 mt-0.5 leading-snug">
                    {listingDraft.suggestedTitle}
                  </p>
                </div>

                {/* Pricing Benchmark */}
                <div className="p-3.5 bg-indigo-50/70 border border-indigo-100 rounded-2xl grid grid-cols-2 gap-3">
                  <div>
                    <span className="text-[10px] font-bold text-gray-500 uppercase">
                      Recommended Price
                    </span>
                    <p className="text-xl font-black text-indigo-950 mt-0.5">
                      ₹{listingDraft.recommendedPrice?.toLocaleString()}
                    </p>
                    <p className="text-[10px] text-gray-400">Competitive match for category</p>
                  </div>
                  <div>
                    <span className="text-[10px] font-bold text-gray-500 uppercase">
                      Suggested MSRP
                    </span>
                    <p className="text-xl font-bold text-gray-500 line-through mt-0.5">
                      ₹{listingDraft.suggestedMSRP?.toLocaleString()}
                    </p>
                    <p className="text-[10px] text-emerald-600 font-bold">~25% Buyer Savings</p>
                  </div>
                </div>

                {/* Description */}
                <div>
                  <span className="text-[10px] font-extrabold uppercase tracking-wider text-gray-400">
                    Draft Description & Marketing Copy
                  </span>
                  <p className="mt-1 text-gray-700 leading-relaxed font-medium bg-gray-50 p-3.5 rounded-xl border border-gray-100">
                    {listingDraft.draftDescription}
                  </p>
                </div>

                {/* Publish Action Button */}
                <div className="pt-2 flex items-center justify-between border-t border-gray-100">
                  <p className="text-[10px] text-gray-400">
                    Confirmation checkpoint required before publishing to live customers.
                  </p>
                  <button
                    onClick={handlePublishListing}
                    className="px-5 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white font-extrabold text-xs shadow-md transition flex items-center gap-1.5 cursor-pointer"
                  >
                    <CheckCircle2 className="w-4 h-4" />
                    <span>Approve & Publish Listing</span>
                  </button>
                </div>
              </div>
            ) : (
              <div className="h-64 flex flex-col items-center justify-center text-center p-6 text-gray-400 space-y-2">
                <Sparkles className="w-8 h-8 text-indigo-300" />
                <p className="text-xs font-bold text-gray-700">No Draft Generated Yet</p>
                <p className="text-[11px] max-w-xs text-gray-400">
                  Fill in your product title and raw specs on the left, then click "Generate Optimized Listing" to draft your catalog copy.
                </p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* TAB 2: INVENTORY HEALTH & REPLENISHMENT */}
      {activeTab === 'health' && (
        <div className="bg-white rounded-3xl border border-gray-100 shadow-sm p-6 sm:p-8 space-y-5">
          <div className="flex items-center justify-between border-b pb-4">
            <div>
              <span className="text-[10px] font-extrabold uppercase tracking-widest text-indigo-600">
                Agent E Inventory Diagnostics
              </span>
              <h2 className="text-base font-extrabold text-gray-900 mt-0.5">
                Physical Partner Stores Stock Health
              </h2>
            </div>
            <button
              onClick={fetchInventoryHealth}
              disabled={healthLoading}
              className="p-2 rounded-xl bg-gray-50 hover:bg-indigo-50 text-gray-700 hover:text-indigo-600 transition"
              title="Refresh inventory diagnostics"
            >
              <RefreshCw className={`w-4 h-4 ${healthLoading ? 'animate-spin' : ''}`} />
            </button>
          </div>

          {inventoryHealth ? (
            <div className="space-y-5 text-xs">
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                <div className="p-4 bg-indigo-50/70 border border-indigo-100 rounded-2xl">
                  <span className="text-[10px] font-bold text-gray-500 uppercase">Fulfillment Hubs</span>
                  <p className="text-2xl font-black text-indigo-950 mt-0.5">{inventoryHealth.storesCount}</p>
                </div>
                <div className="p-4 bg-amber-50/70 border border-amber-100 rounded-2xl">
                  <span className="text-[10px] font-bold text-gray-500 uppercase">Low Stock Alerts</span>
                  <p className="text-2xl font-black text-amber-700 mt-0.5">{inventoryHealth.lowStockAlertCount}</p>
                </div>
                <div className="p-4 bg-emerald-50/70 border border-emerald-100 rounded-2xl">
                  <span className="text-[10px] font-bold text-gray-500 uppercase">Health Score</span>
                  <p className="text-2xl font-black text-emerald-700 mt-0.5">94% Optimal</p>
                </div>
              </div>

              {/* Alert items */}
              {inventoryHealth.lowStockAlerts?.length > 0 && (
                <div className="space-y-2">
                  <p className="text-xs font-extrabold text-gray-800 uppercase tracking-wider">
                    High-Priority Restock Recommendations
                  </p>
                  <div className="space-y-2">
                    {inventoryHealth.lowStockAlerts.map((al, idx) => (
                      <div
                        key={idx}
                        className="p-3 bg-gray-50 rounded-2xl border border-gray-100 flex items-center justify-between"
                      >
                        <div>
                          <p className="font-extrabold text-gray-900">{al.productName}</p>
                          <p className="text-[10px] text-gray-400">Store: {al.storeName}</p>
                        </div>
                        <div className="flex items-center gap-3">
                          <span className="px-2 py-0.5 rounded-full text-[10px] font-extrabold bg-rose-100 text-rose-800 border border-rose-200">
                            {al.availableQuantity} units left
                          </span>
                          <button
                            onClick={() => alert(`Replenishment batch PO dispatched for ${al.productName}`)}
                            className="px-3 py-1.5 rounded-xl bg-slate-900 hover:bg-black text-white font-bold text-[11px] transition cursor-pointer"
                          >
                            Dispatch Restock
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ) : (
            <p className="text-xs text-gray-400 py-6 text-center">Loading inventory health metrics...</p>
          )}
        </div>
      )}
      <EnquiryInbox title="Questions about your products" />
    </div>
  );
};

export default SellerDashboardPage;
