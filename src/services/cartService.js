import api from './api';

export const cartService = {
  applyCoupon: async (code, subtotal) => {
    try {
      const response = await api.post('/coupons/apply', { code, subtotal });
      return response.data;
    } catch (error) {
      const errorMsg = error.response?.data?.detail || error.message || 'Invalid or expired coupon code';
      throw new Error(errorMsg);
    }
  },
};

export default cartService;
