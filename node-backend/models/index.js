/**
 * Models Index
 * ============
 * Sets up model associations and exports all models.
 */

const Product = require('./Product');
const IngredientMapping = require('./IngredientMapping');
const Cart = require('./Cart');
const CartItem = require('./CartItem');

// ─── Associations ────────────────────────────────────────────────────────────

// Cart has many CartItems
Cart.hasMany(CartItem, {
  foreignKey: 'cart_id',
  as: 'items',
  onDelete: 'CASCADE',
});
CartItem.belongsTo(Cart, {
  foreignKey: 'cart_id',
  as: 'cart',
});

// CartItem belongs to Product
CartItem.belongsTo(Product, {
  foreignKey: 'product_id',
  as: 'product',
});
Product.hasMany(CartItem, {
  foreignKey: 'product_id',
  as: 'cart_items',
});

module.exports = {
  Product,
  IngredientMapping,
  Cart,
  CartItem,
};
