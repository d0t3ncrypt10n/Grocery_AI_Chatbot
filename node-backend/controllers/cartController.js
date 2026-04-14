/**
 * Cart Controller
 * ===============
 * HTTP handlers for cart-related endpoints.
 */

const cartService = require('../services/cartService');

/**
 * POST /cart/add
 * Body: { user_id, product_id, quantity }
 */
async function addItem(req, res) {
  try {
    const { user_id, product_id, quantity = 1 } = req.body;

    if (!user_id || !product_id) {
      return res.status(400).json({ success: false, error: 'user_id and product_id are required' });
    }

    const cart = await cartService.addItem(user_id, product_id, quantity);
    res.status(201).json({ success: true, ...cart });
  } catch (error) {
    console.error('Add to cart error:', error.message);
    res.status(400).json({ success: false, error: error.message });
  }
}

/**
 * POST /cart/add-all
 * Body: { user_id, products: [{ product_id, quantity }] }
 */
async function addAll(req, res) {
  try {
    const { user_id, products } = req.body;

    if (!user_id || !products || !Array.isArray(products)) {
      return res.status(400).json({ success: false, error: 'user_id and products array are required' });
    }

    const cart = await cartService.addMultipleItems(user_id, products);
    res.status(201).json({ success: true, ...cart });
  } catch (error) {
    console.error('Add all to cart error:', error.message);
    res.status(400).json({ success: false, error: error.message });
  }
}

/**
 * GET /cart/:userId
 */
async function getCart(req, res) {
  try {
    const cart = await cartService.getCartWithItems(req.params.userId);
    res.json({ success: true, ...cart });
  } catch (error) {
    console.error('Get cart error:', error.message);
    res.status(500).json({ success: false, error: 'Failed to get cart' });
  }
}

/**
 * DELETE /cart/:userId
 */
async function clearCart(req, res) {
  try {
    const result = await cartService.clearCart(req.params.userId);
    res.json({ success: true, ...result });
  } catch (error) {
    console.error('Clear cart error:', error.message);
    res.status(500).json({ success: false, error: 'Failed to clear cart' });
  }
}

/**
 * DELETE /cart/:userId/items/:itemId
 */
async function removeItem(req, res) {
  try {
    const cart = await cartService.removeItem(req.params.userId, req.params.itemId);
    res.json({ success: true, ...cart });
  } catch (error) {
    console.error('Remove item error:', error.message);
    res.status(400).json({ success: false, error: error.message });
  }
}

/**
 * PUT /cart/:userId/items/:itemId
 * Body: { quantity }
 */
async function updateItemQuantity(req, res) {
  try {
    const { quantity } = req.body;

    if (quantity === undefined) {
      return res.status(400).json({ success: false, error: 'quantity is required' });
    }

    const cart = await cartService.updateItemQuantity(
      req.params.userId,
      req.params.itemId,
      quantity
    );
    res.json({ success: true, ...cart });
  } catch (error) {
    console.error('Update quantity error:', error.message);
    res.status(400).json({ success: false, error: error.message });
  }
}

module.exports = {
  addItem,
  addAll,
  getCart,
  clearCart,
  removeItem,
  updateItemQuantity,
};
