import api from './api';

export const productService = {
  getProducts: async (filters = {}) => {
    try {
      const params = new URLSearchParams();

      if (filters.category && filters.category !== 'All') {
        params.append('category', filters.category);
      }

      if (filters.brand && filters.brand.length > 0) {
        if (Array.isArray(filters.brand)) {
          filters.brand.forEach((b) => params.append('brand', b));
        } else {
          params.append('brand', filters.brand);
        }
      }

      if (filters.search) {
        params.append('search', filters.search);
      }

      if (filters.minPrice !== undefined && filters.minPrice !== '') {
        params.append('minPrice', filters.minPrice);
      }

      if (filters.maxPrice !== undefined && filters.maxPrice !== '') {
        params.append('maxPrice', filters.maxPrice);
      }

      if (filters.rating) {
        params.append('rating', filters.rating);
      }

      if (filters.inStockOnly) {
        params.append('inStockOnly', 'true');
      }

      if (filters.sortBy) {
        params.append('sortBy', filters.sortBy);
      }

      const queryString = params.toString();
      const url = queryString ? `/products?${queryString}` : '/products';
      const response = await api.get(url);
      return response.data;
    } catch (error) {
      console.error('Failed to fetch products:', error);
      throw error;
    }
  },

  getProductById: async (id) => {
    try {
      const response = await api.get(`/products/${id}/`);
      return response.data;
    } catch (error) {
      console.error(`Failed to fetch product ${id}:`, error);
      throw new Error('Product not found');
    }
  },

  getCategories: async () => {
    try {
      const response = await api.get('/categories');
      return response.data;
    } catch (error) {
      console.error('Failed to fetch categories:', error);
      throw error;
    }
  },
};

export default productService;
