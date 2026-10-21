import axios from 'axios';

export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';
export const USE_MOCK_API = false;

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor for JWT auth token handling
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auracart_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    // File uploads: let the browser set the multipart boundary instead of forcing JSON.
    if (typeof FormData !== 'undefined' && config.data instanceof FormData) {
      // axios turns FormData into JSON while a JSON Content-Type is set, which drops the file. Remove it the way axios expects.
      if (typeof config.headers.delete === 'function') config.headers.delete('Content-Type');
      else delete config.headers['Content-Type'];
    }
    return config;
  },
  (error) => Promise.reject(error)
);

export default api;
