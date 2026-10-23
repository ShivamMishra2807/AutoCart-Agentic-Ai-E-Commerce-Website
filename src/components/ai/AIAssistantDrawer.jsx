import React, { useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Bot, Sparkles, X, Send, Search, Headphones, PackageSearch,
  RotateCcw, Tag, ShoppingBag, ShieldCheck, ChevronRight, BrainCircuit,
  SlidersHorizontal, CheckCircle2, Clock, Trash2, Layers, Store, MapPin,
  Truck, ArrowRight, ExternalLink
} from 'lucide-react';
import { agentService } from '../../services/agentService';
import { ProductCard } from '../product/ProductCard';
import { useAuth } from '../../hooks/useAuth';
import { useCart } from '../../hooks/useCart';
import { useLocation } from '../../context/LocationContext';
import { MumbaiStoreMap } from '../map/MumbaiStoreMap';

const discoveryPrompts = [
  'Best wireless mouse between ₹1,000 and ₹1,500',
  'Find a laptop under ₹70,000 for programming',
  'Best wireless earbuds with active noise cancellation',
  'Show top rated running shoes under ₹3,000',
  'What are your best trending electronics today?',
];

const engagementPrompts = [
  'Where is my latest order and tracking status?',
  'What is the AutoCart return and refund policy?',
  'How much do I need to add to get free shipping?',
  'Can I cancel or change my shipping address?',
];

export const AIAssistantDrawer = ({ isOpen, onClose }) => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const { cartItems, addToCart } = useCart();
  const { location, selectedStore, updateSelectedStore } = useLocation();
  const [mode, setMode] = useState('discovery');
  const [prompt, setPrompt] = useState('');
  const [loading, setLoading] = useState(false);
  const [thinkingStep, setThinkingStep] = useState('');
  const [thinkingProgress, setThinkingProgress] = useState(0);
  const [showMapModal, setShowMapModal] = useState(false);
  const [mapTargetProduct, setMapTargetProduct] = useState(null);

  const [messages, setMessages] = useState([
    {
      sender: 'ai',
      agent: 'discovery',
      text: 'Hello! I am AutoCart Agentic AI. How can I help your shopping journey today? I can discover products from our catalog, compare specs, check nearby physical store stock, or assist with your orders and policies.',
      products: [],
      nearbyStores: [],
      toolsExecuted: [],
      actions: ['Compare laptops', 'Find budget earbuds', 'Track my order', 'Check nearby stores'],
    },
  ]);

  const prompts = useMemo(() => (mode === 'discovery' ? discoveryPrompts : engagementPrompts), [mode]);

  if (!isOpen) return null;

  const switchMode = (next) => {
    setMode(next);
    setMessages([
      {
        sender: 'ai',
        agent: next,
        text:
          next === 'discovery'
            ? '🔍 **Discovery Agent Activated.** Ask me for any product, budget limit (e.g. "under ₹50,000"), brand, or specification comparison. I will query the live catalog and check nearby store availability.'
            : '🎧 **Customer Engagement Agent Activated.** I can securely review your orders, verify return windows, break down cart totals, and explain delivery policies.',
        products: [],
        nearbyStores: [],
        toolsExecuted: [],
      },
    ]);
  };

  const handleClearHistory = () => {
    agentService.clearSession();
    switchMode(mode);
  };

  const handleSend = async (e, directPrompt = null) => {
    e?.preventDefault();
    const userQuery = (directPrompt || prompt).trim();
    if (!userQuery || loading) return;

    setPrompt('');
    setMessages((prev) => [
      ...prev,
      { sender: 'user', text: userQuery, products: [], nearbyStores: [], toolsExecuted: [] },
    ]);
    setLoading(true);
    setThinkingProgress(1);
    setThinkingStep(
      mode === 'discovery'
        ? 'Parsing shopping requirements & catalog query...'
        : 'Authenticating customer session & permissions...'
    );

    // Responsive thinking steps without artificial delays
    const t1 = setTimeout(() => {
      setThinkingProgress(2);
      setThinkingStep(
        mode === 'discovery'
          ? 'Evaluating specifications & nearby Mumbai stores...'
          : 'Validating order timeline & courier tracking...'
      );
    }, 300);

    const t2 = setTimeout(() => {
      setThinkingProgress(3);
      setThinkingStep(
        mode === 'discovery'
          ? 'Formulating verified product recommendations...'
          : 'Formulating grounded customer response...'
      );
    }, 600);

    try {
      const apiCall =
        mode === 'discovery'
          ? agentService.discover(userQuery, location)
          : agentService.engage(userQuery, cartItems || []);

      const res = await apiCall;

      // Execute Cart and Store Actions returned by backend Agent tools
      if (res.cartAction?.type === 'ADD_TO_CART' && res.cartAction.product) {
        addToCart(res.cartAction.product, res.cartAction.quantity || 1);
      }
      if (res.orderAction?.store) {
        updateSelectedStore(res.orderAction.store);
      }

      setMessages((prev) => [
        ...prev,
        {
          sender: 'ai',
          agent: mode,
          text: res.reply,
          products: res.products || [],
          nearbyStores: res.nearbyStores || [],
          cartAction: res.cartAction,
          orderAction: res.orderAction,
          orders: res.orders || [],
          toolsExecuted: res.toolsExecuted || [],
          actions: res.suggestedActions || [],
          llmProvider: res.llmProvider,
        },
      ]);
    } catch (error) {
      setMessages((prev) => [
        ...prev,
        {
          sender: 'ai',
          agent: mode,
          text:
            '⚠️ I could not reach the backend agent engine. Please ensure the Django backend server is running at http://localhost:8000.',
          products: [],
          toolsExecuted: [],
        },
      ]);
    } finally {
      clearTimeout(t1);
      clearTimeout(t2);
      setLoading(false);
      setThinkingStep('');
      setThinkingProgress(0);
    }
  };

  return (
    <div className="fixed inset-0 z-[70] bg-slate-950/60 backdrop-blur-sm flex justify-end animate-in fade-in duration-200">
      <div className="w-full max-w-xl bg-slate-50 h-full shadow-2xl flex flex-col border-l border-slate-200">
        {/* Header */}
        <div className="bg-gradient-to-r from-slate-900 via-indigo-950 to-indigo-900 text-white p-5 border-b border-indigo-900/40">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-11 h-11 rounded-2xl bg-indigo-500/20 border border-indigo-400/30 flex items-center justify-center shadow-inner">
                <BrainCircuit className="w-6 h-6 text-amber-300" />
              </div>
              <div>
                <h3 className="font-extrabold text-base flex items-center gap-2">
                  AutoCart Shopping Assistant <Sparkles className="w-4 h-4 text-amber-300" />
                </h3>
                <p className="text-[11px] text-indigo-200 font-medium">
                  Personalized Recommendations • Live Catalog • Instant Support
                </p>
              </div>
            </div>
            <div className="flex items-center gap-1">
              <button
                onClick={handleClearHistory}
                title="Reset session conversation"
                className="p-2 rounded-xl text-slate-300 hover:text-white hover:bg-white/10 transition"
              >
                <Trash2 className="w-4 h-4" />
              </button>
              <button
                onClick={onClose}
                className="p-2 rounded-xl text-slate-300 hover:text-white hover:bg-white/10 transition"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
          </div>

          {/* Mode Switcher */}
          <div className="grid grid-cols-2 gap-2 mt-4 p-1 bg-black/25 rounded-2xl border border-white/10">
            <button
              onClick={() => switchMode('discovery')}
              className={`py-2 px-3 rounded-xl text-xs font-bold flex items-center justify-center gap-2 transition ${
                mode === 'discovery'
                  ? 'bg-indigo-600 text-white shadow-md shadow-indigo-700/50'
                  : 'text-indigo-200 hover:text-white hover:bg-white/5'
              }`}
            >
              <Search className="w-3.5 h-3.5" /> Discovery Agent
            </button>
            <button
              onClick={() => switchMode('engagement')}
              className={`py-2 px-3 rounded-xl text-xs font-bold flex items-center justify-center gap-2 transition ${
                mode === 'engagement'
                  ? 'bg-indigo-600 text-white shadow-md shadow-indigo-700/50'
                  : 'text-indigo-200 hover:text-white hover:bg-white/5'
              }`}
            >
              <Headphones className="w-3.5 h-3.5" /> Customer Engagement
            </button>
          </div>
        </div>

        {/* Suggested Prompts Pill Carousel */}
        <div className="px-4 py-3 bg-white border-b border-gray-200/80">
          <p className="text-[10px] font-bold uppercase tracking-wider text-gray-400 mb-2 flex items-center gap-1.5">
            <Sparkles className="w-3 h-3 text-indigo-500" /> Suggested Inquiries
          </p>
          <div className="flex gap-2 overflow-x-auto pb-1 hide-scrollbar">
            {prompts.map((item) => (
              <button
                key={item}
                onClick={() => handleSend(null, item)}
                className="shrink-0 px-3 py-1.5 rounded-xl bg-slate-50 hover:bg-indigo-50 text-slate-700 hover:text-indigo-700 border border-slate-200 hover:border-indigo-200 text-[11px] font-semibold transition shadow-xs"
              >
                {item}
              </button>
            ))}
          </div>
        </div>

        {/* Conversation Message List */}
        <div className="flex-1 overflow-y-auto p-4 flex flex-col gap-4">
          {messages.map((msg, index) => (
            <div
              key={index}
              className={`flex flex-col gap-2 max-w-[95%] ${
                msg.sender === 'user' ? 'self-end items-end' : 'self-start items-start'
              }`}
            >
              {/* Agent Badge */}
              {msg.sender === 'ai' && (
                <div className="flex items-center gap-2 text-[10px] font-bold text-gray-400">
                  <span className="flex items-center gap-1 px-2 py-0.5 rounded-md bg-indigo-50 text-indigo-700 border border-indigo-100">
                    <Bot className="w-3 h-3" />
                    {msg.agent === 'discovery' ? 'Product Advisor' : 'Customer Support'}
                  </span>
                </div>
              )}

              <div
                className={`p-4 rounded-2xl text-xs font-medium leading-relaxed whitespace-pre-line shadow-xs ${
                  msg.sender === 'user'
                    ? 'bg-indigo-600 text-white rounded-br-xs'
                    : 'bg-white text-gray-800 border border-gray-200 rounded-bl-xs'
                }`}
              >
                {msg.text}
              </div>

              {/* Verified Product Cards */}
              {msg.products?.length > 0 && (
                <div className="w-full mt-2">
                  <p className="text-[11px] font-bold text-gray-500 mb-2 flex items-center gap-1">
                    <PackageSearch className="w-3.5 h-3.5 text-indigo-600" />
                    Catalog Recommendations ({msg.products.length})
                  </p>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 w-full">
                    {msg.products.slice(0, 4).map((prod) => (
                      <ProductCard key={prod.id} product={prod} />
                    ))}
                  </div>
                </div>
              )}

              {/* Order Confirmation Card from Store */}
              {msg.orderAction && (
                <div className="w-full mt-2 p-4 bg-gradient-to-r from-emerald-950 via-slate-900 to-indigo-950 text-white rounded-2xl border border-emerald-500/40 shadow-lg space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="flex items-center gap-1.5 font-black text-xs text-emerald-400">
                      <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                      Hyperlocal Store Order Confirmed
                    </span>
                    <span className="text-[10px] font-mono bg-emerald-500/20 text-emerald-300 px-2 py-0.5 rounded-full border border-emerald-500/30">
                      #{msg.orderAction.orderId}
                    </span>
                  </div>
                  <div className="text-xs space-y-1">
                    <p className="font-extrabold text-sm text-slate-100">{msg.orderAction.store?.storeName}</p>
                    <p className="text-[11px] text-slate-300">
                      Delivery ETA: <strong className="text-emerald-300">~{msg.orderAction.estimatedMinutes} mins</strong> • Tracking: <span className="font-mono text-indigo-300">{msg.orderAction.trackingNumber}</span>
                    </p>
                  </div>
                  <div className="flex items-center gap-2 pt-1.5 border-t border-white/10">
                    <button
                      onClick={() => {
                        onClose();
                        navigate(`/orders/${msg.orderAction.orderId}`);
                      }}
                      className="flex-1 py-1.5 px-3 rounded-xl bg-emerald-500 hover:bg-emerald-600 text-white font-bold text-[11px] transition text-center shadow-xs"
                    >
                      Choose Payment / Pay with UPI
                    </button>
                    <button
                      onClick={() => {
                        onClose();
                        navigate('/checkout');
                      }}
                      className="py-1.5 px-3 rounded-xl bg-white/15 hover:bg-white/25 text-white font-medium text-[11px] transition text-center"
                    >
                      Checkout Page
                    </button>
                  </div>
                </div>
              )}

              {/* Nearby Local Partner Stores Card */}
              {msg.nearbyStores?.length > 0 && (
                <div className="w-full mt-2 p-3.5 bg-gradient-to-br from-indigo-50/90 via-white to-purple-50/50 rounded-2xl border border-indigo-100 shadow-xs space-y-2.5">
                  <div className="flex items-center justify-between">
                    <span className="font-extrabold text-gray-900 flex items-center gap-1.5 text-[11px]">
                      <Store className="w-3.5 h-3.5 text-indigo-600" />
                      Verified Stock in Mumbai Partner Stores
                    </span>
                    <button
                      onClick={() => {
                        setMapTargetProduct(msg.products?.[0] || null);
                        setShowMapModal(true);
                      }}
                      className="text-[10px] font-bold text-indigo-700 bg-indigo-100/90 hover:bg-indigo-200 px-2.5 py-1 rounded-full transition flex items-center gap-1 shadow-2xs"
                    >
                      <MapPin className="w-3 h-3 text-indigo-600" /> View Map
                    </button>
                  </div>
                  <div className="space-y-1.5">
                    {msg.nearbyStores.slice(0, 3).map((st, idx) => (
                      <div
                        key={st.storeId || idx}
                        className="p-2.5 bg-white rounded-xl border border-indigo-100/80 flex items-center justify-between shadow-2xs hover:border-indigo-300 transition"
                      >
                        <div>
                          <div className="flex items-center gap-1.5">
                            {idx === 0 && <span className="text-[9px] font-black uppercase bg-amber-100 text-amber-800 px-1.5 py-0.2 rounded">Closest</span>}
                            <p className="font-bold text-gray-900 text-[11px]">{st.storeName}</p>
                          </div>
                          <p className="text-[10px] text-gray-500 mt-0.5">{st.address}, {st.city}</p>
                        </div>
                        <div className="flex items-center gap-2">
                          <div className="text-right shrink-0">
                            <span className="font-extrabold text-indigo-600 text-xs">{st.distanceKm} km</span>
                            <p className="text-[10px] text-emerald-600 font-bold">
                              {st.availableQuantity || st.availableStock || 'In Stock'} units
                            </p>
                          </div>
                          <button
                            onClick={() => {
                              updateSelectedStore(st);
                              if (msg.products?.[0]) {
                                addToCart(msg.products[0], 1);
                              }
                              onClose();
                              navigate('/checkout');
                            }}
                            title="Choose payment and checkout from this store"
                            className="px-2.5 py-1.5 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white font-bold text-[11px] transition flex items-center gap-1 shadow-xs"
                          >
                            <span>Pay / Order</span>
                            <ArrowRight className="w-3.5 h-3.5" />
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Order Tracking Cards */}
              {msg.orders?.length > 0 && (
                <div className="w-full mt-2 space-y-2">
                  <p className="text-[11px] font-bold text-gray-500 flex items-center gap-1">
                    <Clock className="w-3.5 h-3.5 text-indigo-600" /> Verified Order Records
                  </p>
                  {msg.orders.slice(0, 2).map((ord) => (
                    <div
                      key={ord.id}
                      className="p-3 bg-white rounded-xl border border-gray-200 text-xs shadow-xs"
                    >
                      <div className="flex items-center justify-between font-bold text-gray-800">
                        <span>Order #{ord.id}</span>
                        <span className="text-emerald-600 bg-emerald-50 px-2 py-0.5 rounded text-[10px]">
                          {ord.status}
                        </span>
                      </div>
                      <p className="text-gray-500 text-[11px] mt-1">
                        Date: {ord.date} • Total: ₹{ord.totalAmount} • Payment: {ord.paymentStatus}
                      </p>
                    </div>
                  ))}
                </div>
              )}

              {/* Action suggestions */}
              {msg.actions?.length > 0 && (
                <div className="flex flex-wrap gap-1.5 mt-1">
                  {msg.actions.map((act) => (
                    <button
                      key={act}
                      onClick={() => handleSend(null, act)}
                      className="px-2.5 py-1 rounded-lg bg-gray-100 hover:bg-indigo-50 hover:text-indigo-600 text-[10px] font-semibold text-gray-600 transition"
                    >
                      → {act}
                    </button>
                  ))}
                </div>
              )}
            </div>
          ))}

          {/* Multi-Stage Agentic Reasoning State */}
          {loading && (
            <div className="flex flex-col gap-2.5 p-4 bg-white rounded-2xl border border-indigo-100 shadow-sm text-xs w-full max-w-md animate-in fade-in duration-200">
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 rounded-xl bg-indigo-50 border border-indigo-100 text-indigo-600 flex items-center justify-center shrink-0">
                  <BrainCircuit className="w-4 h-4 animate-spin text-indigo-600" />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between">
                    <p className="font-extrabold text-gray-900 text-xs">
                      Agentic AI Thinking
                    </p>
                    <span className="text-[10px] font-bold text-indigo-600 bg-indigo-50 px-2 py-0.5 rounded-full">
                      Step {thinkingProgress || 1}/3
                    </span>
                  </div>
                  <p className="text-[11px] text-gray-600 font-medium mt-0.5 truncate">
                    {thinkingStep || (mode === 'discovery' ? 'Analyzing catalog specifications...' : 'Verifying customer order history...')}
                  </p>
                </div>
              </div>

              {/* Animated Progress Bar */}
              <div className="w-full bg-gray-100 h-1.5 rounded-full overflow-hidden">
                <div
                  className="bg-gradient-to-r from-indigo-500 to-indigo-600 h-full rounded-full transition-all duration-700 ease-out"
                  style={{
                    width: thinkingProgress === 1 ? '35%' : thinkingProgress === 2 ? '70%' : '95%'
                  }}
                />
              </div>
            </div>
          )}
        </div>

        {/* Input Bar */}
        <form onSubmit={handleSend} className="p-4 bg-white border-t border-gray-200">
          <div className="flex gap-2">
            <input
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              placeholder={
                mode === 'discovery'
                  ? 'Describe what you want to buy (e.g. "wireless earbuds under ₹2000")...'
                  : 'Ask about an order, return policy, delivery charge, or checkout...'
              }
              className="flex-1 px-4 py-3 bg-gray-50 border border-gray-200 rounded-2xl text-xs font-medium focus:border-indigo-500 focus:bg-white focus:outline-none transition"
            />
            <button
              disabled={loading || !prompt.trim()}
              type="submit"
              className="px-5 rounded-2xl bg-indigo-600 hover:bg-indigo-700 text-white disabled:opacity-40 transition shadow-md shadow-indigo-600/20 flex items-center justify-center"
            >
              <Send className="w-4 h-4" />
            </button>
          </div>

          {/* Privacy & Guardrails Footer */}
          <div className="flex items-center justify-between mt-3 text-[10px] text-gray-400 font-medium px-1">
            <span className="flex items-center gap-1">
              <PackageSearch className="w-3 h-3 text-indigo-500" /> Real DB catalog
            </span>
            <span className="flex items-center gap-1">
              <ShieldCheck className="w-3 h-3 text-emerald-500" /> Bounded tool execution
            </span>
            <span className="flex items-center gap-1">
              <CheckCircle2 className="w-3 h-3 text-amber-500" /> Consequential actions confirmed
            </span>
          </div>
        </form>
      </div>

      {/* Interactive Mumbai Hyperlocal Stores Modal */}
      <MumbaiStoreMap
        isOpen={showMapModal}
        onClose={() => setShowMapModal(false)}
        productId={mapTargetProduct?.id}
        productName={mapTargetProduct?.name}
        onSelectStore={(st) => {
          updateSelectedStore(st);
          setShowMapModal(false);
          handleSend(null, "Order from this store");
        }}
      />
    </div>
  );
};

export default AIAssistantDrawer;
