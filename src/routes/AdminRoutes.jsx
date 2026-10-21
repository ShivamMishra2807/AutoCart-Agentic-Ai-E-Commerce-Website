import React from 'react';
import { Routes, Route } from 'react-router-dom';
import AdminLayout from '../admin/components/AdminLayout';
import ProtectedRoute from '../components/layout/ProtectedRoute';

import Dashboard from '../pages/admin/Dashboard';
import Products from '../pages/admin/Products';
import AddProduct from '../pages/admin/AddProduct';
import EditProduct from '../pages/admin/EditProduct';
import Categories from '../pages/admin/Categories';
import Orders from '../pages/admin/Orders';
import OrderDetails from '../pages/admin/OrderDetails';
import Users from '../pages/admin/Users';
import Sellers from '../pages/admin/Sellers';
import Inventory from '../pages/admin/Inventory';
import Reviews from '../pages/admin/Reviews';
import Coupons from '../pages/admin/Coupons';
import Analytics from '../pages/admin/Analytics';
import Settings from '../pages/admin/Settings';
import SellerOnboardingAI from '../pages/admin/SellerOnboardingAI';
import SupportInbox from '../pages/admin/SupportInbox';
import Enquiries from '../pages/admin/Enquiries';
import Payments from '../pages/admin/Payments';

export const AdminRoutes = () => {
  return (
    <ProtectedRoute requireAdmin={true}>
      <AdminLayout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/products" element={<Products />} />
          <Route path="/products/add" element={<AddProduct />} />
          <Route path="/products/edit/:id" element={<EditProduct />} />
          <Route path="/categories" element={<Categories />} />
          <Route path="/orders" element={<Orders />} />
          <Route path="/orders/:id" element={<OrderDetails />} />
          <Route path="/users" element={<Users />} />
          <Route path="/sellers" element={<Sellers />} />
          <Route path="/inventory" element={<Inventory />} />
          <Route path="/reviews" element={<Reviews />} />
          <Route path="/coupons" element={<Coupons />} />
          <Route path="/analytics" element={<Analytics />} />
          <Route path="/settings" element={<Settings />} />
          <Route path="/ai-seller-onboarding" element={<SellerOnboardingAI />} />
          <Route path="/support" element={<SupportInbox />} />
          <Route path="/enquiries" element={<Enquiries />} />
          <Route path="/payments" element={<Payments />} />
        </Routes>
      </AdminLayout>
    </ProtectedRoute>
  );
};

export default AdminRoutes;
