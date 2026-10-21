import api from './api';

export const orderService = {
  createOrder: async (orderData) => {
    try {
      const response = await api.post('/orders', orderData);
      return response.data;
    } catch (error) {
      console.error('Failed to create order:', error);
      throw error;
    }
  },

  getUserOrders: async (email) => {
    try {
      const url = email ? `/orders?email=${encodeURIComponent(email)}` : '/orders';
      const response = await api.get(url);
      return response.data;
    } catch (error) {
      console.error('Failed to fetch user orders:', error);
      throw error;
    }
  },

  getOrderById: async (id) => {
    try {
      const response = await api.get(`/orders/${id}/`);
      return response.data;
    } catch (error) {
      console.error(`Failed to fetch order ${id}:`, error);
      throw new Error('Order not found');
    }
  },
};

export default orderService;
