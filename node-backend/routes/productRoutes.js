/**
 * Product Routes
 * ==============
 * Express router for product-related endpoints.
 */

const express = require('express');
const router = express.Router();
const productController = require('../controllers/productController');

// GET /products/search?q=onion&mode=fuzzy&category=vegetables&max_price=100
router.get('/search', productController.searchProducts);

// GET /products/categories
router.get('/categories', productController.getCategories);

// GET /products/:id
router.get('/:id', productController.getProduct);

module.exports = router;
