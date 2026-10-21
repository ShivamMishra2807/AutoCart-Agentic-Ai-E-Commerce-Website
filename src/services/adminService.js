import api from './api';

export const adminService = {
  getDashboardStats: async () => {
    try {
      const response = await api.get('/admin/stats');
      return response.data;
    } catch (error) {
      console.error('Failed to get dashboard stats:', error);
      throw error;
    }
  },

  getAnalyticsData: async () => {
    try {
      const response = await api.get('/admin/analytics');
      return response.data;
    } catch (error) {
      console.error('Failed to get analytics data:', error);
      throw error;
    }
  },

  getAllProducts: async () => {
    try {
      const response = await api.get('/products');
      return response.data;
    } catch (error) {
      console.error('Failed to get all products:', error);
      throw error;
    }
  },

  getAllOrders: async () => {
    try {
      const response = await api.get('/orders');
      return response.data;
    } catch (error) {
      console.error('Failed to get all orders:', error);
      throw error;
    }
  },

  getAllUsers: async () => {
    try {
      const response = await api.get('/users');
      return response.data;
    } catch (error) {
      console.error('Failed to get all users:', error);
      throw error;
    }
  },

  getAllCategories: async () => {
    try {
      const response = await api.get('/categories');
      return response.data;
    } catch (error) {
      console.error('Failed to get all categories:', error);
      throw error;
    }
  },

  getAllSellers: async () => {
    try {
      const response = await api.get('/sellers');
      return response.data;
    } catch (error) {
      console.error('Failed to get all sellers:', error);
      throw error;
    }
  },

  getAllCoupons: async () => {
    try {
      const response = await api.get('/coupons');
      return response.data;
    } catch (error) {
      console.error('Failed to get all coupons:', error);
      throw error;
    }
  },
};

export default adminService;
