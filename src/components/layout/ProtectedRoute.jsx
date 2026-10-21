import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';
import Loader from '../common/Loader';

/**
 * Keeps a page for signed-in people. Pass `roles` (or `requireAdmin`) to keep it for staff or sellers.
 * Each kind of person is sent to their own sign-in page.
 */
export const ProtectedRoute = ({ children, requireAdmin = false, roles = null }) => {
  const { isAuthenticated, user, loading } = useAuth();
  const location = useLocation();

  if (loading) {
    return <Loader fullScreen text="Checking credentials..." />;
  }

  const allowed = requireAdmin ? ['ADMIN', 'STAFF'] : roles;
  const login = requireAdmin ? '/admin/login' : roles?.includes('SELLER') ? '/seller/login' : '/login';

  if (!isAuthenticated) {
    return <Navigate to={login} state={{ from: location }} replace />;
  }

  if (allowed && !allowed.includes(user?.role)) {
    return <Navigate to={login} state={{ from: location, denied: true }} replace />;
  }

  return children;
};

export default ProtectedRoute;
