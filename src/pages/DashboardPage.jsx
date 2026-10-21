import React, { useState, useEffect } from 'react';
import { useSearchParams, Link } from 'react-router-dom';
import { 
  User, 
  Package, 
  Heart, 
  MapPin, 
  CreditCard, 
  Bell, 
  Settings, 
  LogOut,
  ChevronRight,
  Truck
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { orderService } from '../services/orderService';
import { formatCurrency, formatDate } from '../utils/formatters';
import { Breadcrumbs } from '../components/common/Breadcrumbs';

export const DashboardPage = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const activeTab = searchParams.get('tab') || 'profile';

  const { user, logout, updateProfile } = useAuth();
  const [orders, setOrders] = useState([]);
  const [loadingOrders, setLoadingOrders] = useState(true);

  // Edit profile state
  const [name, setName] = useState(user?.name || 'Shivam Sharma');
  const [phone, setPhone] = useState(user?.phone || '+91 98765 43210');

  useEffect(() => {
    const fetchOrders = async () => {
      setLoadingOrders(true);
      try {
        const data = await orderService.getOrders();
        setOrders(data);
      } catch (err) {
        console.error("Error fetching orders:", err);
      } finally {
        setLoadingOrders(false);
      }
    };
    fetchOrders();
  }, []);

  const handleTabChange = (tabKey) => {
    setSearchParams({ tab: tabKey });
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-6">
      <Breadcrumbs items={[{ label: 'User Dashboard' }]} />

      <div className="flex justify-between items-center pb-2 border-b border-gray-100">
        <div>
          <h1 className="text-2xl sm:text-3xl font-black text-gray-900 tracking-tight">Account Dashboard</h1>
          <p className="text-xs text-gray-500 font-medium mt-0.5">
            Manage your personal profile, track active shipments, and view order history.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
        
        {/* Sidebar Tabs Navigation */}
        <aside className="lg:col-span-3 bg-white rounded-3xl p-4 border border-gray-100 shadow-sm flex flex-col gap-1">
          <button
            onClick={() => handleTabChange('profile')}
            className={`flex items-center gap-3 px-4 py-3 rounded-2xl text-xs font-bold transition-all text-left ${
              activeTab === 'profile' ? 'bg-brand-600 text-white shadow-sm' : 'text-gray-700 hover:bg-gray-50'
            }`}
          >
            <User className="w-4 h-4" /> My Profile
          </button>

          <button
            onClick={() => handleTabChange('orders')}
            className={`flex items-center gap-3 px-4 py-3 rounded-2xl text-xs font-bold transition-all text-left justify-between ${
              activeTab === 'orders' ? 'bg-brand-600 text-white shadow-sm' : 'text-gray-700 hover:bg-gray-50'
            }`}
          >
            <div className="flex items-center gap-3">
              <Package className="w-4 h-4" /> My Orders
            </div>
            {orders.length > 0 && (
              <span className={`text-[10px] px-2 py-0.5 rounded-full ${activeTab === 'orders' ? 'bg-white/20 text-white' : 'bg-brand-100 text-brand-700'}`}>
                {orders.length}
              </span>
            )}
          </button>

          <button
            onClick={() => handleTabChange('addresses')}
            className={`flex items-center gap-3 px-4 py-3 rounded-2xl text-xs font-bold transition-all text-left ${
              activeTab === 'addresses' ? 'bg-brand-600 text-white shadow-sm' : 'text-gray-700 hover:bg-gray-50'
            }`}
          >
            <MapPin className="w-4 h-4" /> Saved Addresses
          </button>

          <button
            onClick={() => handleTabChange('payments')}
            className={`flex items-center gap-3 px-4 py-3 rounded-2xl text-xs font-bold transition-all text-left ${
              activeTab === 'payments' ? 'bg-brand-600 text-white shadow-sm' : 'text-gray-700 hover:bg-gray-50'
            }`}
          >
            <CreditCard className="w-4 h-4" /> Saved Payment Cards
          </button>

          <div className="pt-2 border-t border-gray-100">
            <button
              onClick={logout}
              className="w-full flex items-center gap-3 px-4 py-3 rounded-2xl text-xs font-bold text-rose-600 hover:bg-rose-50 transition-all text-left"
            >
              <LogOut className="w-4 h-4" /> Sign Out
            </button>
          </div>
        </aside>

        {/* Tab Content Container */}
        <div className="lg:col-span-9 bg-white rounded-3xl p-6 sm:p-8 border border-gray-100 shadow-sm min-h-[400px]">
          
          {/* Profile Tab */}
          {activeTab === 'profile' && (
            <div className="space-y-6">
              <h3 className="text-base font-extrabold text-gray-900 border-b border-gray-100 pb-3">Personal Profile Details</h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="text-xs font-bold text-gray-700 uppercase tracking-wider block mb-1">Full Name</label>
                  <input
                    type="text"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    className="w-full px-4 py-2.5 bg-gray-50 border border-gray-200 rounded-xl text-xs font-semibold"
                  />
                </div>
                <div>
                  <label className="text-xs font-bold text-gray-700 uppercase tracking-wider block mb-1">Email</label>
                  <input
                    type="email"
                    disabled
                    value={user?.email || 'shivam@example.com'}
                    className="w-full px-4 py-2.5 bg-gray-100 border border-gray-200 rounded-xl text-xs font-semibold text-gray-500 cursor-not-allowed"
                  />
                </div>
                <div>
                  <label className="text-xs font-bold text-gray-700 uppercase tracking-wider block mb-1">Phone</label>
                  <input
                    type="text"
                    value={phone}
                    onChange={(e) => setPhone(e.target.value)}
                    className="w-full px-4 py-2.5 bg-gray-50 border border-gray-200 rounded-xl text-xs font-semibold"
                  />
                </div>
              </div>
              <button
                onClick={() => updateProfile({ name, phone })}
                className="px-6 py-2.5 bg-brand-600 hover:bg-brand-700 text-white font-bold text-xs rounded-xl shadow-sm"
              >
                Save Changes
              </button>
            </div>
          )}

          {/* Orders Tab */}
          {activeTab === 'orders' && (
            <div className="space-y-6">
              <h3 className="text-base font-extrabold text-gray-900 border-b border-gray-100 pb-3">My Orders & Tracking</h3>

              {orders.length === 0 ? (
                <p className="text-xs text-gray-500 py-8 text-center">No past orders found.</p>
              ) : (
                <div className="space-y-4">
                  {orders.map((ord) => (
                    <div key={ord.id} className="p-4 sm:p-5 rounded-2xl border border-gray-100 bg-gray-50/50 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
                      <div className="flex items-center gap-4">
                        <div className="w-12 h-12 rounded-xl bg-brand-100 text-brand-700 flex items-center justify-center font-bold">
                          <Package className="w-6 h-6" />
                        </div>
                        <div>
                          <div className="flex items-center gap-2">
                            <span className="text-sm font-extrabold text-gray-900">Order #{ord.id}</span>
                            <span className="text-[10px] font-bold bg-emerald-100 text-emerald-800 px-2 py-0.5 rounded-full">{ord.status}</span>
                          </div>
                          <p className="text-xs text-gray-500 font-medium">Placed: {formatDate(ord.date)} | Total: {formatCurrency(ord.totalAmount)}</p>
                        </div>
                      </div>

                      <Link
                        to={`/orders/track/${ord.id}`}
                        className="px-4 py-2 bg-gray-900 hover:bg-black text-white rounded-xl text-xs font-bold flex items-center gap-1.5 shadow-xs"
                      >
                        <Truck className="w-3.5 h-3.5" /> Track Package
                      </Link>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* Addresses Tab */}
          {activeTab === 'addresses' && (
            <div className="space-y-6">
              <h3 className="text-base font-extrabold text-gray-900 border-b border-gray-100 pb-3">Saved Addresses</h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div className="p-4 rounded-2xl border border-gray-200 bg-gray-50">
                  <span className="text-xs font-bold bg-gray-200 text-gray-800 px-2 py-0.5 rounded">Home</span>
                  <p className="text-xs font-bold text-gray-900 mt-2">Shivam Sharma</p>
                  <p className="text-xs text-gray-600">42 Tech Park Avenue, Sector 62, Noida, UP 201301</p>
                </div>
              </div>
            </div>
          )}

          {/* Payments Tab */}
          {activeTab === 'payments' && (
            <div className="space-y-6">
              <h3 className="text-base font-extrabold text-gray-900 border-b border-gray-100 pb-3">Saved Payment Methods</h3>
              <div className="p-4 rounded-2xl border border-gray-200 bg-gray-50 flex items-center justify-between max-w-sm">
                <div className="flex items-center gap-3">
                  <CreditCard className="w-6 h-6 text-brand-600" />
                  <div>
                    <p className="text-xs font-bold text-gray-900">Visa ending in 4242</p>
                    <p className="text-[11px] text-gray-400">Expires 12/28</p>
                  </div>
                </div>
              </div>
            </div>
          )}

        </div>

      </div>
    </div>
  );
};
