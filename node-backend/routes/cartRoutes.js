/**
 * Cart Routes
 * ===========
 * Express router for cart-related endpoints.
 */

const express = require('express');
const router = express.Router();
const cartController = require('../controllers/cartController');

// POST /cart/add — add single item
router.post('/add', cartController.addItem);

// POST /cart/add-all — batch add items
router.post('/add-all', cartController.addAll);

// GET /cart/:userId — get cart with items
router.get('/:userId', cartController.getCart);

// DELETE /cart/:userId — clear entire cart
router.delete('/:userId', cartController.clearCart);

// DELETE /cart/:userId/items/:itemId — remove single item
router.delete('/:userId/items/:itemId', cartController.removeItem);

// PUT /cart/:userId/items/:itemId — update quantity
router.put('/:userId/items/:itemId', cartController.updateItemQuantity);

module.exports = router;
