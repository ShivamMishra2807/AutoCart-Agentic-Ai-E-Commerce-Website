import BuyGate from '../../storefront/BuyGate';
import React, { useEffect, useState } from 'react';
import { useLocation as useRoute } from 'react-router-dom';
import { Sparkles } from 'lucide-react';
import StoreHeader from '../../storefront/StoreHeader';
import StoreFooter from '../../storefront/StoreFooter';
import SupportChat from '../../storefront/SupportChat';
import '../../storefront/storefront.css';
import '../../storefront/forms.css';

/**
 * Shared shell for every customer page: the Navy & Gold header and footer, the support chat,
 * and (still available from inside the chat) the advanced shopping assistant.
 * Pages that use their own full-width design (the home page and the pages built with .ac styles) skip the padded container.
 */
export const MainLayout = ({ children }) => {
  const { pathname } = useRoute();
  const [chatOpen, setChatOpen] = useState(false);

  // Any page can ask for the assistant with openAssistant() (see storefront/parts.jsx).
  useEffect(() => {
    const open = () => setChatOpen(true);
    window.addEventListener('autocart:open-assistant', open);
    return () => window.removeEventListener('autocart:open-assistant', open);
  }, []);

  useEffect(() => { window.scrollTo({ top: 0 }); }, [pathname]);

  const fullWidth = ['/', '/catalog', '/products', '/search', '/cart', '/checkout', '/order-success', '/wishlist', '/profile', '/orders', '/support', '/contact', '/seller/apply', '/login', '/register'].includes(pathname)
    || pathname.startsWith('/orders/') || pathname.startsWith('/products/');

  return (
    <div className="min-h-screen flex flex-col bg-white text-gray-900 font-sans antialiased relative">
      <div className="ac ac-host"><StoreHeader /></div>
      {fullWidth ? (
        <main key={pathname} className="flex-1 w-full ac-route">{children}</main>
      ) : (
        <main key={pathname} className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6 sm:py-8 ac-route">{children}</main>
      )}
      <div className="ac ac-host"><StoreFooter /></div>

      <div className="ac ac-host">
        <BuyGate />
        <button className="ac-chat" onClick={() => setChatOpen(true)} aria-label="Open Saathi, the AutoCart shopping assistant">
          <Sparkles size={20} /><span>Ask Saathi</span>
        </button>
        <SupportChat isOpen={chatOpen} onClose={() => setChatOpen(false)} />
      </div>
    </div>
  );
};

export default MainLayout;
