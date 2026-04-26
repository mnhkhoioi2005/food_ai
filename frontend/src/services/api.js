import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor - add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor - handle errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    // Don't redirect to login for chat endpoint (allows unauthenticated use)
    const requestUrl = error.config?.url || '';
    const isChatEndpoint = requestUrl.includes('/chat');
    if (error.response?.status === 401 && !isChatEndpoint) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// ==================== Auth API ====================
export const authAPI = {
  register: (data) => api.post('/auth/register', data),
  login: (data) => api.post('/auth/login/json', data),
  getMe: () => api.get('/auth/me'),
  updateMe: (data) => api.put('/auth/me', data),
  changePassword: (data) => api.post('/auth/change-password', data),
};

// ==================== Food API ====================
export const foodAPI = {
  search: (params) => api.get('/foods', { params }),
  getById: (id) => api.get(`/foods/${id}`),
  getBySlug: (slug) => api.get(`/foods/slug/${slug}`),
  getPopular: (limit = 10) => api.get('/foods/popular', { params: { limit } }),
  getFilters: () => api.get('/foods/filters'),
  getIngredients: () => api.get('/foods/ingredients'),
  getAllergies: () => api.get('/foods/allergies'),

  // Admin
  create: (data) => api.post('/foods', data),
  update: (id, data) => api.put(`/foods/${id}`, data),
  delete: (id) => api.delete(`/foods/${id}`),
  getAdminAll: (params) => api.get('/foods/admin/all', { params }),
  getCount: () => api.get('/foods/admin/count'),
};

// ==================== Recognition API ====================
export const recognitionAPI = {
  uploadImage: (file) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post('/recognition/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
  cameraCapture: (file) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post('/recognition/camera', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
  getHistory: (limit = 20) => api.get('/recognition/history', { params: { limit } }),
  getStats: () => api.get('/recognition/admin/stats'),
};

// ==================== Recommendation API ====================
export const recommendationAPI = {
  get: (data) => api.post('/recommendations', data),
  getNearby: (lat, lng, limit = 10) =>
    api.get('/recommendations/nearby', { params: { latitude: lat, longitude: lng, limit } }),
  getPersonalized: (limit = 10) =>
    api.get('/recommendations/personalized', { params: { limit } }),
  getByTaste: (params) => api.get('/recommendations/by-taste', { params }),
  getSimilar: (foodId, limit = 5) =>
    api.get(`/recommendations/similar/${foodId}`, { params: { limit } }),

  // Interactions
  recordInteraction: (data) => api.post('/recommendations/interaction', data),
  getHistory: (limit = 50) => api.get('/recommendations/history', { params: { limit } }),
};

// ==================== User API ====================
export const userAPI = {
  getAll: (params) => api.get('/users', { params }),
  getById: (id) => api.get(`/users/${id}`),
  update: (id, data) => api.put(`/users/${id}`, data),
  delete: (id) => api.delete(`/users/${id}`),
  getCount: () => api.get('/users/count'),
  getPreferences: (id) => api.get(`/users/${id}/preferences`),
  updatePreferences: (id, data) => api.put(`/users/${id}/preferences`, data),
};

// ==================== Chat AI API ====================
export const chatAPI = {
  send: (data) => api.post('/chat/', data),
  health: () => api.get('/chat/health'),
};

export default api;

