import React from 'react';
import { Routes, Route } from 'react-router-dom';
import MainLayout from '../components/layout/MainLayout';
import ProtectedRoute from '../components/layout/ProtectedRoute';

import Home from '../storefront/Home';
import ClassicHome from '../pages/customer/Home';
import Catalog from '../storefront/Catalog';
import SupportPage from '../pages/support/SupportPage';
import ContactPage from '../pages/contact/ContactPage';
import Products from '../pages/customer/Products';
import ProductDetails from '../storefront/ProductPage';
import Cart from '../pages/customer/Cart';
import Checkout from '../pages/customer/Checkout';
import OrderSuccess from '../pages/customer/OrderSuccess';
import Orders from '../pages/customer/Orders';
import OrderDetails from '../pages/customer/OrderDetails';
import Profile from '../pages/customer/Profile';
import Wishlist from '../pages/customer/Wishlist';
import SearchResults from '../pages/customer/SearchResults';

import Login from '../pages/auth/Login';
import Register from '../pages/auth/Register';
import ForgotPassword from '../pages/auth/ForgotPassword';
import SellerApplyPage from '../pages/seller/SellerApplyPage';
import SellerDashboardPage from '../pages/seller/SellerDashboardPage';

export const CustomerRoutes = () => {
  return (
    <MainLayout>
      <Routes>
        {/* Public customer pages */}
        <Route path="/" element={<Home />} />
        <Route path="/classic" element={<ClassicHome />} />
        <Route path="/catalog" element={<Catalog />} />
        <Route path="/support" element={<SupportPage />} />
        <Route path="/contact" element={<ContactPage />} />
        <Route path="/products" element={<Catalog />} />
        <Route path="/products/:id" element={<ProductDetails />} />
        <Route path="/search" element={<Catalog />} />
        <Route path="/cart" element={<Cart />} />
        <Route path="/wishlist" element={<Wishlist />} />

        {/* Multi-Vendor Seller Onboarding & Business Copilot */}
        <Route path="/seller/apply" element={<SellerApplyPage />} />

        {/* Auth pages */}
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/forgot-password" element={<ForgotPassword />} />

        {/* Customer Protected Pages */}
        <Route
          path="/checkout"
          element={
            <ProtectedRoute roles={['CUSTOMER']}>
              <Checkout />
            </ProtectedRoute>
          }
        />
        <Route
          path="/order-success"
          element={
            <ProtectedRoute>
              <OrderSuccess />
            </ProtectedRoute>
          }
        />
        <Route
          path="/orders"
          element={
            <ProtectedRoute>
              <Orders />
            </ProtectedRoute>
          }
        />
        <Route
          path="/orders/:id"
          element={
            <ProtectedRoute>
              <OrderDetails />
            </ProtectedRoute>
          }
        />
        <Route
          path="/profile"
          element={
            <ProtectedRoute>
              <Profile />
            </ProtectedRoute>
          }
        />
      </Routes>
    </MainLayout>
  );
};

export default CustomerRoutes;
