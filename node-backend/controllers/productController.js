/**
 * Product Controller
 * ==================
 * HTTP handlers for product-related endpoints.
 */

const productService = require('../services/productService');

/**
 * GET /products/search?q=&mode=&category=&max_price=
 */
async function searchProducts(req, res) {
  try {
    const { q = '', mode = 'fuzzy', category = '', max_price } = req.query;

    const products = await productService.searchProducts(q, mode, category, max_price);

    res.json({
      success: true,
      query: q,
      mode,
      count: products.length,
      products,
    });
  } catch (error) {
    console.error('Product search error:', error.message);
    res.status(500).json({
      success: false,
      error: 'Failed to search products',
      products: [],
    });
  }
}

/**
 * GET /products/categories
 */
async function getCategories(req, res) {
  try {
    const categories = await productService.getAllCategories();
    res.json({ success: true, categories });
  } catch (error) {
    console.error('Get categories error:', error.message);
    res.status(500).json({ success: false, error: 'Failed to get categories' });
  }
}

/**
 * GET /products/:id
 */
async function getProduct(req, res) {
  try {
    const product = await productService.getProductById(req.params.id);

    if (!product) {
      return res.status(404).json({ success: false, error: 'Product not found' });
    }

    res.json({ success: true, product });
  } catch (error) {
    console.error('Get product error:', error.message);
    res.status(500).json({ success: false, error: 'Failed to get product' });
  }
}

module.exports = {
  searchProducts,
  getCategories,
  getProduct,
};
