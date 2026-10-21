import api from './api';

export const authService = {
  login: async (email, password) => {
    try {
      const response = await api.post('/auth/login', { email, password });
      return response.data;
    } catch (error) {
      const errorMsg = error.response?.data?.detail || error.message || 'Invalid email or password';
      throw new Error(errorMsg);
    }
  },

  register: async (userData) => {
    try {
      const response = await api.post('/auth/register', userData);
      return response.data;
    } catch (error) {
      const errorMsg = error.response?.data?.detail || error.message || 'Registration failed';
      throw new Error(errorMsg);
    }
  },

  getCurrentUser: async () => {
    try {
      const response = await api.get('/auth/me');
      return response.data;
    } catch {
      const storedUser = localStorage.getItem('auracart_user');
      if (storedUser) {
        return JSON.parse(storedUser);
      }
      return null;
    }
  },
};

export default authService;
