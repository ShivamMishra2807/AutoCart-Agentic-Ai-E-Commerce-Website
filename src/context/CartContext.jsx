import { useAuth } from '../hooks/useAuth';
import React, { createContext, useState, useEffect } from 'react';
import { cartService } from '../services/cartService';

export const CartContext = createContext(null);

export const CartProvider = ({ children }) => {
  const { user } = useAuth();
  const [cartItems, setCartItems] = useState(() => {
    const saved = localStorage.getItem('auracart_cart');
    return saved ? JSON.parse(saved) : [];
  });
  const [coupon, setCoupon] = useState(null);
  const [discountAmount, setDiscountAmount] = useState(0);

  useEffect(() => {
    localStorage.setItem('auracart_cart', JSON.stringify(cartItems));
  }, [cartItems]);

  // After a visitor signs in as a customer, put what they wanted in the cart (and continue to checkout for Buy now).
  useEffect(() => {
    if (!user || user.role !== 'CUSTOMER') return;
    let pending = null;
    try { pending = JSON.parse(sessionStorage.getItem('autocart_pending_buy') || 'null'); sessionStorage.removeItem('autocart_pending_buy'); } catch { pending = null; }
    if (!pending?.product) return;
    setCartItems((prev) => (prev.some((i) => i.id === pending.product.id) ? prev : [...prev, { ...pending.product, quantity: pending.quantity || 1 }]));
    if (pending.buyNow) window.dispatchEvent(new CustomEvent('autocart:resume-buy'));
  }, [user]);

  const addToCart = (product, quantity = 1, opts = {}) => {
    // Only customer accounts can buy. A visitor goes to the customer sign-in (their choice is remembered);
    // a seller or admin gets an explanation. Both are handled by BuyGate.
    if (!user || user.role !== 'CUSTOMER') {
      if (!user) {
        try { sessionStorage.setItem('autocart_pending_buy', JSON.stringify({ product, quantity, buyNow: !!opts.buyNow })); } catch { /* private mode: they just add it again after signing in */ }
      }
      window.dispatchEvent(new CustomEvent('autocart:buy-blocked', { detail: { role: user?.role || null } }));
      return false;
    }
    setCartItems((prev) => {
      const existing = prev.find((item) => item.id === product.id);
      if (existing) {
        return prev.map((item) =>
          item.id === product.id ? { ...item, quantity: item.quantity + quantity } : item
        );
      }
      return [...prev, { ...product, quantity }];
    });
    return true;
  };

  const removeFromCart = (productId) => {
    setCartItems((prev) => prev.filter((item) => item.id !== productId));
  };

  const updateQuantity = (productId, newQuantity) => {
    if (newQuantity <= 0) {
      removeFromCart(productId);
      return;
    }
    setCartItems((prev) =>
      prev.map((item) => (item.id === productId ? { ...item, quantity: newQuantity } : item))
    );
  };

  const clearCart = () => {
    setCartItems([]);
    setCoupon(null);
    setDiscountAmount(0);
  };

  const applyCoupon = async (code) => {
    const subtotal = getSubtotal();
    const result = await cartService.applyCoupon(code, subtotal);
    setCoupon(result.coupon);
    setDiscountAmount(result.discountAmount);
    return result;
  };

  const removeCoupon = () => {
    setCoupon(null);
    setDiscountAmount(0);
  };

  const getSubtotal = () => {
    return cartItems.reduce((total, item) => total + item.price * item.quantity, 0);
  };

  const getDeliveryCharge = () => {
    const subtotal = getSubtotal();
    if (subtotal === 0) return 0;
    return subtotal > 499 || coupon?.code === 'FREESHIP' ? 0 : 40;
  };

  const getFinalTotal = () => {
    const subtotal = getSubtotal();
    const delivery = getDeliveryCharge();
    return Math.max(0, subtotal - discountAmount + delivery);
  };

  const getItemCount = () => {
    return cartItems.reduce((count, item) => count + item.quantity, 0);
  };

  return (
    <CartContext.Provider
      value={{
        cartItems,
        addToCart,
        removeFromCart,
        updateQuantity,
        clearCart,
        coupon,
        discountAmount,
        applyCoupon,
        removeCoupon,
        subtotal: getSubtotal(),
        deliveryCharge: getDeliveryCharge(),
        finalTotal: getFinalTotal(),
        itemCount: getItemCount(),
      }}
    >
      {children}
    </CartContext.Provider>
  );
};
