import React from 'react';
import { Routes, Route } from 'react-router-dom';
import CustomerRoutes from './CustomerRoutes';
import AdminRoutes from './AdminRoutes';
import { Navigate } from 'react-router-dom';
import RoleLogin from '../pages/auth/RoleLogin';
import SellerCenter from '../pages/seller/SellerCenter';
import SellerShell from '../pages/seller/SellerShell';
import SellerApplyPage from '../pages/seller/SellerApplyPage';
import ProtectedRoute from '../components/layout/ProtectedRoute';

export const AppRoutes = () => {
  return (
    <Routes>
      <Route path="/preview" element={<Navigate to="/" replace />} />
      <Route path="/admin/login" element={<RoleLogin key="admin" role="admin" />} />
      <Route path="/seller/login" element={<RoleLogin key="seller" role="seller" />} />
      <Route path="/seller/apply" element={<SellerShell><SellerApplyPage /></SellerShell>} />
      <Route path="/seller/dashboard" element={<ProtectedRoute roles={['SELLER']}><SellerCenter /></ProtectedRoute>} />
      <Route path="/admin/*" element={<AdminRoutes />} />
      <Route path="/*" element={<CustomerRoutes />} />
    </Routes>
  );
};

export default AppRoutes;
