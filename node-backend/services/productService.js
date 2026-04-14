/**
 * Product Service
 * ===============
 * Business logic for product search — exact, fuzzy (LIKE + keywords), and category modes.
 */

const { Op } = require('sequelize');
const { Product, IngredientMapping } = require('../models');

/**
 * Search products with multiple strategies.
 * @param {string} query - Search term
 * @param {string} mode - 'exact' | 'fuzzy' | 'category'
 * @param {string} category - Filter by category
 * @param {number} maxPrice - Max price filter
 * @returns {Promise<Object[]>}
 */
async function searchProducts(query = '', mode = 'fuzzy', category = '', maxPrice = null) {
  const where = {};

  // Price filter
  if (maxPrice) {
    where.price = { [Op.lte]: parseFloat(maxPrice) };
  }

  // Stock filter — only in-stock products
  where.stock = { [Op.gt]: 0 };

  // Category filter
  if (category) {
    where.category = category;
  }

  if (mode === 'exact') {
    // ── Exact match ──
    where.name = query;
    return Product.findAll({ where });
  }

  if (mode === 'category') {
    // ── Category browse ──
    return Product.findAll({ where, order: [['name', 'ASC']] });
  }

  // ── Fuzzy search (default) ────
  if (!query) {
    return Product.findAll({ where, order: [['category', 'ASC'], ['name', 'ASC']] });
  }

  const lowerQuery = query.toLowerCase().trim();

  // Step 1: Try name LIKE match
  const likeResults = await Product.findAll({
    where: {
      ...where,
      name: { [Op.like]: `%${lowerQuery}%` },
    },
    order: [['name', 'ASC']],
  });

  if (likeResults.length > 0) {
    return likeResults;
  }

  // Step 2: Search by keywords (JSON field)
  // For SQLite, we search the JSON-serialized string
  const allProducts = await Product.findAll({ where });
  const keywordMatches = allProducts.filter((product) => {
    const keywords = product.keywords || [];
    return keywords.some((kw) => {
      const lowerKw = kw.toLowerCase();
      return lowerKw.includes(lowerQuery) || lowerQuery.includes(lowerKw);
    });
  });

  if (keywordMatches.length > 0) {
    return keywordMatches;
  }

  // Step 3: Check ingredient mappings to translate the query
  const mapping = await IngredientMapping.findOne({
    where: {
      [Op.or]: [
        { ingredient_name: { [Op.like]: `%${lowerQuery}%` } },
      ],
    },
  });

  if (mapping) {
    const searchKeywords = mapping.search_keywords || [];
    const mappedResults = allProducts.filter((product) => {
      const productKeywords = product.keywords || [];
      const productNameLower = product.name.toLowerCase();

      return searchKeywords.some((sk) => {
        const lowerSk = sk.toLowerCase();
        return (
          productNameLower.includes(lowerSk) ||
          productKeywords.some((pk) => pk.toLowerCase().includes(lowerSk))
        );
      });
    });

    if (mappedResults.length > 0) {
      return mappedResults;
    }
  }

  // Step 4: Partial word matching as final fallback
  const partialMatches = allProducts.filter((product) => {
    const nameLower = product.name.toLowerCase();
    const words = lowerQuery.split(/\s+/);
    return words.some((word) => word.length >= 3 && nameLower.includes(word));
  });

  return partialMatches;
}

/**
 * Get a single product by ID.
 */
async function getProductById(id) {
  return Product.findByPk(id);
}

/**
 * Get all distinct product categories.
 */
async function getAllCategories() {
  const products = await Product.findAll({
    attributes: ['category'],
    group: ['category'],
    order: [['category', 'ASC']],
  });
  return products.map((p) => p.category);
}

module.exports = {
  searchProducts,
  getProductById,
  getAllCategories,
};
