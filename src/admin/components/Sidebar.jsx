import React from 'react';
import { NavLink, Link } from 'react-router-dom';
import {
  LayoutDashboard,
  Package,
  FolderTree,
  ShoppingBag,
  Users,
  Store,
  Boxes,
  MessageSquare,
  Ticket,
  BarChart3,
  Settings,
  X,
  BrainCircuit,
  LifeBuoy,
  HelpCircle,
  CreditCard,
} from 'lucide-react';

export const Sidebar = ({ isOpen, onClose }) => {
  const menuItems = [
    { name: 'Dashboard', path: '/admin', icon: LayoutDashboard, exact: true },
    { name: 'Products', path: '/admin/products', icon: Package },
    { name: 'Categories', path: '/admin/categories', icon: FolderTree },
    { name: 'Orders', path: '/admin/orders', icon: ShoppingBag },
    { name: 'Users', path: '/admin/users', icon: Users },
    { name: 'Sellers', path: '/admin/sellers', icon: Store },
    { name: 'Inventory', path: '/admin/inventory', icon: Boxes },
    { name: 'Reviews', path: '/admin/reviews', icon: MessageSquare },
    { name: 'Coupons', path: '/admin/coupons', icon: Ticket },
    { name: 'Analytics', path: '/admin/analytics', icon: BarChart3 },
    { name: 'Seller applications', path: '/admin/ai-seller-onboarding', icon: BrainCircuit },
    { name: 'Support inbox', path: '/admin/support', icon: LifeBuoy },
    { name: 'Enquiries', path: '/admin/enquiries', icon: HelpCircle },
    { name: 'Payments', path: '/admin/payments', icon: CreditCard },
    { name: 'Settings', path: '/admin/settings', icon: Settings },
  ];

  return (
    <>
      {/* Mobile backdrop overlay */}
      {isOpen && (
        <div
          className="fixed inset-0 z-40 bg-gray-900/50 backdrop-blur-sm lg:hidden"
          onClick={onClose}
        />
      )}

      <aside
        className={`fixed top-0 left-0 z-50 h-full w-64 bg-white text-gray-600 flex flex-col border-r border-gray-200 transition-transform duration-300 lg:translate-x-0 ${
          isOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        {/* Sidebar Header */}
        <div className="flex items-center justify-between h-16 px-6 border-b border-gray-200">
          <Link to="/admin" className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-indigo-600 flex items-center justify-center text-white font-extrabold text-lg shadow-md">
              A
            </div>
            <div className="flex flex-col">
              <span className="font-extrabold text-lg text-gray-900 tracking-tight">
                Auto<span className="text-indigo-600">Admin</span>
              </span>
              <span className="text-[9px] font-bold text-slate-400 uppercase tracking-widest -mt-1">
                Dashboard v1.0
              </span>
            </div>
          </Link>
          <button onClick={onClose} className="lg:hidden p-1 text-gray-500 hover:text-gray-900">
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Navigation Menu */}
        <nav className="flex-1 overflow-y-auto px-3 py-4 space-y-1">
          {menuItems.map((item) => (
            <NavLink
              key={item.name}
              to={item.path}
              end={item.exact}
              onClick={() => onClose && onClose()}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-xs font-semibold transition-all ${
                  isActive
                    ? 'bg-indigo-600 text-white font-bold shadow-md shadow-indigo-600/30'
                    : 'text-gray-600 hover:bg-indigo-50 hover:text-indigo-700'
                }`
              }
            >
              <item.icon className="w-4 h-4 shrink-0" />
              <span>{item.name}</span>
            </NavLink>
          ))}
        </nav>

        {/* Back to Customer Store link */}
        <div className="p-4 border-t border-gray-200">
          <Link
            to="/"
            className="flex items-center justify-center gap-2 w-full py-2.5 px-4 bg-indigo-50 hover:bg-indigo-100 text-indigo-700 text-xs font-bold rounded-xl transition"
          >
            &larr; Return to Customer Store
          </Link>
        </div>
      </aside>
    </>
  );
};

export default Sidebar;
