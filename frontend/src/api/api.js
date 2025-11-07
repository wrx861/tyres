import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Получить Telegram user данные
export const getTelegramUser = () => {
  if (window.Telegram?.WebApp) {
    const user = window.Telegram.WebApp.initDataUnsafe?.user;
    return user ? {
      telegram_id: user.id.toString(),
      username: user.username || null,
      first_name: user.first_name || null,
      last_name: user.last_name || null
    } : null;
  }
  // Для тестирования вне Telegram
  return {
    telegram_id: '123456789',
    username: 'testuser',
    first_name: 'Test',
    last_name: 'User'
  };
};

// Auth
export const authenticateUser = async (userData) => {
  const response = await axios.post(`${API}/auth/telegram`, userData);
  return response.data;
};

// Products - Tires
export const searchTires = async (params) => {
  const response = await axios.get(`${API}/products/tires/search`, { params });
  return response.data;
};

// Products - Disks
export const searchDisks = async (params) => {
  const response = await axios.get(`${API}/products/disks/search`, { params });
  return response.data;
};

// Cars
export const getCarBrands = async () => {
  const response = await axios.get(`${API}/cars/brands`);
  return response.data;
};

export const getCarModels = async (brand) => {
  const response = await axios.get(`${API}/cars/models`, { params: { brand } });
  return response.data;
};

export const getCarYears = async (brand, model) => {
  const response = await axios.get(`${API}/cars/years`, { params: { brand, model } });
  return response.data;
};

export const getCarModifications = async (brand, model, year_begin, year_end) => {
  const response = await axios.get(`${API}/cars/modifications`, { 
    params: { brand, model, year_begin, year_end } 
  });
  return response.data;
};

export const getGoodsByCar = async (params) => {
  const response = await axios.get(`${API}/cars/goods`, { params });
  return response.data;
};

// Warehouses
export const getWarehouses = async () => {
  const response = await axios.get(`${API}/products/warehouses`);
  return response.data;
};

// Orders
export const createOrder = async (orderData, telegramId) => {
  const response = await axios.post(
    `${API}/orders?telegram_id=${telegramId}`, 
    orderData
  );
  return response.data;
};

export const getMyOrders = async (telegramId) => {
  const response = await axios.get(`${API}/orders/my`, {
    params: { telegram_id: telegramId }
  });
  return response.data;
};

export const getOrderDetails = async (orderId, telegramId) => {
  const response = await axios.get(`${API}/orders/${orderId}`, {
    params: { telegram_id: telegramId }
  });
  return response.data;
};

// Admin
export const getPendingOrders = async (telegramId) => {
  const response = await axios.get(`${API}/orders/admin/pending`, {
    params: { telegram_id: telegramId }
  });
  return response.data;
};

export const confirmOrder = async (orderId, telegramId, adminComment = null) => {
  const response = await axios.post(
    `${API}/orders/${orderId}/confirm?telegram_id=${telegramId}`,
    { admin_comment: adminComment }
  );
  return response.data;
};

export const rejectOrder = async (orderId, telegramId, reason) => {
  const response = await axios.post(
    `${API}/orders/${orderId}/reject?telegram_id=${telegramId}`,
    { reason }
  );
  return response.data;
};

export const getMarkup = async (telegramId) => {
  const response = await axios.get(`${API}/admin/markup`, {
    params: { telegram_id: telegramId }
  });
  return response.data;
};

export const updateMarkup = async (telegramId, markupPercentage) => {
  const response = await axios.put(
    `${API}/admin/markup?telegram_id=${telegramId}`,
    { markup_percentage: markupPercentage }
  );
  return response.data;
};

export const getAdminStats = async (telegramId) => {
  const response = await axios.get(`${API}/admin/stats`, {
    params: { telegram_id: telegramId }
  });
  return response.data;
};

// Admin - User Management
export const getAllUsers = async (telegramId) => {
  const response = await axios.get(`${API}/admin/users`, {
    params: { telegram_id: telegramId }
  });
  return response.data;
};

export const blockUser = async (adminTelegramId, userTelegramId) => {
  const response = await axios.post(
    `${API}/admin/users/${userTelegramId}/block?telegram_id=${adminTelegramId}`
  );
  return response.data;
};

export const unblockUser = async (adminTelegramId, userTelegramId) => {
  const response = await axios.post(
    `${API}/admin/users/${userTelegramId}/unblock?telegram_id=${adminTelegramId}`
  );
  return response.data;
};

// Admin - Activity Logs
export const getUserActivity = async (telegramId, filters = {}) => {
  const response = await axios.get(`${API}/admin/activity`, {
    params: { telegram_id: telegramId, ...filters }
  });
  return response.data;
};

// Cart
export const getCart = async (telegramId) => {
  const response = await axios.get(`${API}/cart/${telegramId}`);
  return response.data;
};

export const addToCart = async (telegramId, item) => {
  const response = await axios.post(`${API}/cart/${telegramId}/items`, item);
  return response.data;
};

export const updateCartItem = async (telegramId, itemCode, warehouseId, quantity) => {
  const response = await axios.put(
    `${API}/cart/${telegramId}/items/${itemCode}?warehouse_id=${warehouseId}`,
    { quantity }
  );
  return response.data;
};

export const removeFromCart = async (telegramId, itemCode, warehouseId) => {
  const response = await axios.delete(
    `${API}/cart/${telegramId}/items/${itemCode}?warehouse_id=${warehouseId}`
  );
  return response.data;
};

export const clearCart = async (telegramId) => {
  const response = await axios.delete(`${API}/cart/${telegramId}`);
  return response.data;
};

