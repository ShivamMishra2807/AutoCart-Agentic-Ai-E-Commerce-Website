import React, { useState, useRef, useEffect } from 'react';
import { Menu, Bell, Search, Sparkles, AlertTriangle, AlertCircle, ShoppingBag, CheckCheck, Trash2, X, ChevronRight, LogOut, Store, Settings, ChevronDown, ClipboardCheck } from 'lucide-react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';
import api from '../../services/api';

const TYPE = { bad: 'critical', warn: 'warning', info: 'info', good: 'info' };

/** Turn the admin briefing (real counts from the database) into bell alerts. */
const toAlerts = (briefing = []) => briefing.map((b, i) => ({
  id: `b-${i}`, type: TYPE[b.level] || 'info', title: b.text, message: '', time: 'Now',
  unread: b.level === 'bad' || b.level === 'warn', link: b.link || '/admin', actionText: b.link ? 'Open' : 'Dashboard',
}));

export const AdminNavbar = ({ onToggleSidebar }) => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [profileOpen, setProfileOpen] = useState(false);
  const profileRef = useRef(null);
  const [notificationsOpen, setNotificationsOpen] = useState(false);
  const [notifications, setNotifications] = useState([]);
  const [filter, setFilter] = useState('all'); // 'all' | 'unread'
  const dropdownRef = useRef(null);

  useEffect(() => { api.get('/admin/overview').then((r) => setNotifications(toAlerts(r.data.briefing))).catch(() => setNotifications([])); }, []);

  // Close the profile menu on an outside click or Esc
  useEffect(() => {
    if (!profileOpen) return undefined;
    const out = (e) => { if (profileRef.current && !profileRef.current.contains(e.target)) setProfileOpen(false); };
    const esc = (e) => { if (e.key === 'Escape') setProfileOpen(false); };
    document.addEventListener('mousedown', out); document.addEventListener('keydown', esc);
    return () => { document.removeEventListener('mousedown', out); document.removeEventListener('keydown', esc); };
  }, [profileOpen]);

  const signOut = () => { setProfileOpen(false); logout(); navigate('/admin/login'); };

  const unreadCount = notifications.filter(n => n.unread).length;

  // Close dropdown on outside click or Esc key
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setNotificationsOpen(false);
      }
    };
    const handleKeyDown = (event) => {
      if (event.key === 'Escape') {
        setNotificationsOpen(false);
      }
    };

    if (notificationsOpen) {
      document.addEventListener('mousedown', handleClickOutside);
      document.addEventListener('keydown', handleKeyDown);
    }
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
      document.removeEventListener('keydown', handleKeyDown);
    };
  }, [notificationsOpen]);

  const markAllAsRead = () => {
    setNotifications(prev => prev.map(n => ({ ...n, unread: false })));
  };

  const markAsRead = (id) => {
    setNotifications(prev => prev.map(n => n.id === id ? { ...n, unread: false } : n));
  };

  const clearAllNotifications = () => {
    setNotifications([]);
  };

  const handleNotificationClick = (item) => {
    markAsRead(item.id);
    setNotificationsOpen(false);
    if (item.link) {
      navigate(item.link);
    }
  };

  const displayedNotifications = filter === 'unread'
    ? notifications.filter(n => n.unread)
    : notifications;

  return (
    <header className="sticky top-0 z-30 bg-white border-b border-gray-200 h-16 flex items-center justify-between px-4 sm:px-8 shadow-sm">
      <div className="flex items-center gap-4">
        <div className="hidden md:flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-indigo-50 text-indigo-700 text-[10px] font-extrabold border border-indigo-100">
          <Sparkles className="w-3 h-3" /> AI Marketplace Operations
        </div>
        <button
          onClick={onToggleSidebar}
          className="lg:hidden p-2 rounded-lg text-gray-600 hover:bg-gray-100 transition"
          aria-label="Toggle Navigation Sidebar"
        >
          <Menu className="w-5 h-5" />
        </button>

        {/* Global Admin Search Bar */}
        <form
          onSubmit={(e) => {
            e.preventDefault();
            const term = e.currentTarget.elements.adminSearch.value.trim();
            if (term) {
              navigate(`/admin/products?search=${encodeURIComponent(term)}`);
            }
          }}
          className="relative hidden sm:block w-72"
        >
          <input
            name="adminSearch"
            type="text"
            placeholder="Search products, brands, orders (Press Enter)..."
            className="w-full pl-9 pr-4 py-1.5 text-xs bg-gray-100 border border-gray-200 rounded-full focus:bg-white focus:border-indigo-500 focus:outline-none transition shadow-xs"
          />
          <Search className="absolute left-3 top-2 w-3.5 h-3.5 text-gray-400" />
        </form>
      </div>

      {/* Admin Profile & Notifications */}
      <div className="flex items-center gap-3 sm:gap-4">
        {/* Interactive Notification Bell */}
        <div className="relative" ref={dropdownRef}>
          <button
            onClick={() => setNotificationsOpen(prev => !prev)}
            className={`relative p-2 rounded-full transition ${
              notificationsOpen
                ? 'bg-indigo-50 text-indigo-600 ring-2 ring-indigo-500/20'
                : 'text-gray-500 hover:bg-gray-100 hover:text-gray-700'
            }`}
            title="Marketplace Notifications"
            aria-label="Open notifications"
          >
            <Bell className="w-5 h-5" />
            {unreadCount > 0 && (
              <span className="absolute -top-0.5 -right-0.5 min-w-[18px] h-[18px] px-1 rounded-full bg-rose-500 text-white text-[10px] font-extrabold flex items-center justify-center shadow-sm animate-pulse">
                {unreadCount}
              </span>
            )}
          </button>

          {/* Notification Dropdown Panel */}
          {notificationsOpen && (
            <div className="absolute right-0 mt-3 w-80 sm:w-96 bg-white rounded-2xl shadow-2xl border border-gray-200 z-50 overflow-hidden animate-in fade-in slide-in-from-top-2 duration-150">
              {/* Header */}
              <div className="p-4 border-b border-gray-100 bg-gray-50/70 flex items-center justify-between">
                <div>
                  <div className="flex items-center gap-2">
                    <h3 className="font-extrabold text-sm text-gray-900">What needs attention</h3>
                    {unreadCount > 0 && (
                      <span className="px-2 py-0.5 rounded-full bg-rose-100 text-rose-700 text-[10px] font-extrabold">
                        {unreadCount} new
                      </span>
                    )}
                  </div>
                  <p className="text-[11px] text-gray-500 mt-0.5">Worked out from your live data</p>
                </div>
                <div className="flex items-center gap-1">
                  {unreadCount > 0 && (
                    <button
                      onClick={markAllAsRead}
                      className="p-1.5 text-gray-500 hover:text-indigo-600 hover:bg-white rounded-lg transition"
                      title="Mark all as read"
                    >
                      <CheckCheck className="w-4 h-4" />
                    </button>
                  )}
                  {notifications.length > 0 && (
                    <button
                      onClick={clearAllNotifications}
                      className="p-1.5 text-gray-400 hover:text-rose-600 hover:bg-white rounded-lg transition"
                      title="Clear notifications"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  )}
                  <button
                    onClick={() => setNotificationsOpen(false)}
                    className="p-1.5 text-gray-400 hover:text-gray-700 hover:bg-white rounded-lg transition"
                  >
                    <X className="w-4 h-4" />
                  </button>
                </div>
              </div>

              {/* Filter tabs */}
              <div className="flex items-center px-4 py-2 border-b border-gray-100 bg-white gap-2 text-xs">
                <button
                  onClick={() => setFilter('all')}
                  className={`px-2.5 py-1 rounded-lg font-bold transition ${
                    filter === 'all'
                      ? 'bg-indigo-50 text-indigo-700'
                      : 'text-gray-500 hover:text-gray-900'
                  }`}
                >
                  All ({notifications.length})
                </button>
                <button
                  onClick={() => setFilter('unread')}
                  className={`px-2.5 py-1 rounded-lg font-bold transition ${
                    filter === 'unread'
                      ? 'bg-indigo-50 text-indigo-700'
                      : 'text-gray-500 hover:text-gray-900'
                  }`}
                >
                  Unread ({unreadCount})
                </button>
              </div>

              {/* List */}
              <div className="max-h-[360px] overflow-y-auto divide-y divide-gray-100">
                {displayedNotifications.length === 0 ? (
                  <div className="py-12 px-4 text-center">
                    <Bell className="w-8 h-8 text-gray-300 mx-auto mb-2" />
                    <p className="text-xs font-bold text-gray-700">No alerts right now</p>
                    <p className="text-[11px] text-gray-400 mt-1">
                      Seller applications, tickets, orders and stock are all in check.
                    </p>
                  </div>
                ) : (
                  displayedNotifications.map((notif) => (
                    <div
                      key={notif.id}
                      onClick={() => handleNotificationClick(notif)}
                      className={`p-3.5 hover:bg-gray-50 cursor-pointer transition flex items-start gap-3 ${
                        notif.unread ? 'bg-indigo-50/30' : 'bg-white'
                      }`}
                    >
                      {/* Icon */}
                      <div className="mt-0.5 flex-shrink-0">
                        {notif.type === 'critical' ? (
                          <div className="w-8 h-8 rounded-xl bg-rose-100 text-rose-600 flex items-center justify-center">
                            <AlertTriangle className="w-4 h-4" />
                          </div>
                        ) : notif.type === 'warning' ? (
                          <div className="w-8 h-8 rounded-xl bg-amber-100 text-amber-600 flex items-center justify-center">
                            <AlertCircle className="w-4 h-4" />
                          </div>
                        ) : (
                          <div className="w-8 h-8 rounded-xl bg-emerald-100 text-emerald-600 flex items-center justify-center">
                            <ShoppingBag className="w-4 h-4" />
                          </div>
                        )}
                      </div>

                      {/* Content */}
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center justify-between gap-1">
                          <p className={`text-xs font-bold truncate ${notif.unread ? 'text-gray-900' : 'text-gray-700'}`}>
                            {notif.title}
                          </p>
                          {notif.unread && (
                            <span className="w-2 h-2 rounded-full bg-indigo-600 flex-shrink-0" />
                          )}
                        </div>
                        <p className="text-[11px] text-gray-500 mt-1 line-clamp-2 leading-relaxed">
                          {notif.message}
                        </p>
                        <div className="mt-2 flex items-center justify-between">
                          <span className="text-[10px] text-gray-400 font-medium">{notif.time}</span>
                          <span className="inline-flex items-center gap-1 text-[11px] font-extrabold text-indigo-600 hover:text-indigo-800">
                            {notif.actionText} <ChevronRight className="w-3 h-3" />
                          </span>
                        </div>
                      </div>
                    </div>
                  ))
                )}
              </div>

              {/* Footer */}
              <div className="p-2.5 bg-gray-50 border-t border-gray-100 text-center">
                <Link
                  to="/admin/ai-seller-onboarding"
                  onClick={() => setNotificationsOpen(false)}
                  className="text-[11px] font-bold text-indigo-600 hover:text-indigo-800 transition"
                >
                  Open AI Seller Onboarding Workspace →
                </Link>
              </div>
            </div>
          )}
        </div>

        <div className="h-6 w-px bg-gray-200" />

        {/* Profile menu */}
        <div className="relative" ref={profileRef}>
          <button onClick={() => setProfileOpen((v) => !v)} aria-haspopup="menu" aria-expanded={profileOpen} aria-label="Open account menu"
            className="flex items-center gap-3 rounded-xl px-2 py-1 hover:bg-gray-100 transition focus:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500">
            <span className="w-9 h-9 rounded-full bg-indigo-600 text-white font-bold text-sm flex items-center justify-center shadow">
              {user?.name ? user.name.charAt(0).toUpperCase() : 'A'}
            </span>
            <span className="hidden sm:block text-left">
              <span className="block text-sm font-bold text-gray-900 leading-tight">{user?.name || 'Admin User'}</span>
              <span className="block text-xs text-gray-500 font-semibold uppercase">Administrator</span>
            </span>
            <ChevronDown className={`w-4 h-4 text-gray-500 transition ${profileOpen ? 'rotate-180' : ''}`} />
          </button>
          {profileOpen && (
            <div role="menu" className="absolute right-0 mt-3 w-72 bg-white rounded-2xl shadow-2xl border border-gray-200 z-50 overflow-hidden">
              <div className="p-4 border-b border-gray-100 bg-gray-50">
                <p className="font-bold text-gray-900">{user?.name || 'Admin User'}</p>
                <p className="text-sm text-gray-500 break-all">{user?.email}</p>
              </div>
              <div className="p-2 text-sm font-semibold text-gray-800">
                <Link role="menuitem" to="/admin/ai-seller-onboarding" onClick={() => setProfileOpen(false)} className="flex items-center gap-3 px-3 py-2.5 rounded-xl hover:bg-gray-100"><ClipboardCheck className="w-4 h-4" /> Seller applications</Link>
                <Link role="menuitem" to="/admin/settings" onClick={() => setProfileOpen(false)} className="flex items-center gap-3 px-3 py-2.5 rounded-xl hover:bg-gray-100"><Settings className="w-4 h-4" /> Settings</Link>
                <Link role="menuitem" to="/" onClick={() => setProfileOpen(false)} className="flex items-center gap-3 px-3 py-2.5 rounded-xl hover:bg-gray-100"><Store className="w-4 h-4" /> View the customer store</Link>
                <button role="menuitem" onClick={signOut} className="w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-red-700 hover:bg-red-50"><LogOut className="w-4 h-4" /> Sign out</button>
              </div>
            </div>
          )}
        </div>
      </div>
    </header>
  );
};

export default AdminNavbar;
