/**
 * API Service
 * ===========
 * Axios clients for Flask AI (5000) and Node.js Backend (4000).
 */

import axios from 'axios';

const FLASK_URL = 'http://localhost:5000';
const NODE_URL = 'http://localhost:4000';

const flaskApi = axios.create({ baseURL: FLASK_URL, timeout: 15000 });
const nodeApi = axios.create({ baseURL: NODE_URL, timeout: 10000 });

// ── AI Service ──────────────────────────────────────────────────────────────

export async function sendMessage(message, userId) {
  const { data } = await flaskApi.post('/ai/process', {
    message,
    user_id: userId,
  });
  return data;
}

export async function checkAiHealth() {
  const { data } = await flaskApi.get('/ai/health');
  return data;
}

// ── Product Service ─────────────────────────────────────────────────────────

export async function searchProducts(query, mode = 'fuzzy', category = '', maxPrice = null) {
  const params = { q: query, mode };
  if (category) params.category = category;
  if (maxPrice) params.max_price = maxPrice;

  const { data } = await nodeApi.get('/products/search', { params });
  return data;
}

export async function getCategories() {
  const { data } = await nodeApi.get('/products/categories');
  return data;
}

// ── Cart Service ────────────────────────────────────────────────────────────

export async function getCart(userId) {
  const { data } = await nodeApi.get(`/cart/${userId}`);
  return data;
}

export async function addToCart(userId, productId, quantity = 1) {
  const { data } = await nodeApi.post('/cart/add', {
    user_id: userId,
    product_id: productId,
    quantity,
  });
  return data;
}

export async function addAllToCart(userId, products) {
  const { data } = await nodeApi.post('/cart/add-all', {
    user_id: userId,
    products,
  });
  return data;
}

export async function removeFromCart(userId, itemId) {
  const { data } = await nodeApi.delete(`/cart/${userId}/items/${itemId}`);
  return data;
}

export async function updateCartQuantity(userId, itemId, quantity) {
  const { data } = await nodeApi.put(`/cart/${userId}/items/${itemId}`, { quantity });
  return data;
}

export async function clearCart(userId) {
  const { data } = await nodeApi.delete(`/cart/${userId}`);
  return data;
}
