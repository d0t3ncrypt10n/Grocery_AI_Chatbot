/**
 * Cart Service
 * ============
 * Business logic for cart CRUD operations.
 * Handles upserts, batch adds, totals, and cleanup.
 */

const { Cart, CartItem, Product } = require('../models');

/**
 * Find or create a cart for a user.
 */
async function getOrCreateCart(userId) {
  const [cart] = await Cart.findOrCreate({
    where: { user_id: userId },
    defaults: { user_id: userId },
  });
  return cart;
}

/**
 * Add a single item to the user's cart.
 * If the product is already in the cart, increment the quantity.
 */
async function addItem(userId, productId, quantity = 1) {
  const cart = await getOrCreateCart(userId);

  // Check product exists and is in stock
  const product = await Product.findByPk(productId);
  if (!product) {
    throw new Error(`Product #${productId} not found`);
  }
  if (product.stock <= 0) {
    throw new Error(`${product.name} is out of stock`);
  }

  // Upsert: if item already exists in cart, increment quantity
  const [cartItem, created] = await CartItem.findOrCreate({
    where: { cart_id: cart.id, product_id: productId },
    defaults: { cart_id: cart.id, product_id: productId, quantity },
  });

  if (!created) {
    cartItem.quantity += quantity;
    await cartItem.save();
  }

  return getCartWithItems(userId);
}

/**
 * Batch add multiple items to the cart.
 * @param {string} userId
 * @param {Array<{product_id: number, quantity: number}>} products
 */
async function addMultipleItems(userId, products) {
  const cart = await getOrCreateCart(userId);

  for (const item of products) {
    const product = await Product.findByPk(item.product_id);
    if (!product || product.stock <= 0) continue;

    const [cartItem, created] = await CartItem.findOrCreate({
      where: { cart_id: cart.id, product_id: item.product_id },
      defaults: {
        cart_id: cart.id,
        product_id: item.product_id,
        quantity: item.quantity || 1,
      },
    });

    if (!created) {
      cartItem.quantity += item.quantity || 1;
      await cartItem.save();
    }
  }

  return getCartWithItems(userId);
}

/**
 * Get the user's cart with all items, product details, and totals.
 */
async function getCartWithItems(userId) {
  const cart = await Cart.findOne({
    where: { user_id: userId },
    include: [
      {
        association: 'items',
        include: [{ association: 'product' }],
      },
    ],
  });

  if (!cart) {
    return { items: [], total: 0, item_count: 0 };
  }

  const items = cart.items.map((ci) => ({
    id: ci.id,
    product_id: ci.product_id,
    quantity: ci.quantity,
    name: ci.product ? ci.product.name : 'Unknown',
    price: ci.product ? ci.product.price : 0,
    unit: ci.product ? ci.product.unit : '',
    image_url: ci.product ? ci.product.image_url : '',
    subtotal: ci.product ? ci.product.price * ci.quantity : 0,
  }));

  const total = items.reduce((sum, item) => sum + item.subtotal, 0);
  const itemCount = items.reduce((sum, item) => sum + item.quantity, 0);

  return {
    cart_id: cart.id,
    user_id: userId,
    items,
    total: Math.round(total * 100) / 100,
    item_count: itemCount,
  };
}

/**
 * Remove a single item from the cart.
 */
async function removeItem(userId, cartItemId) {
  const cart = await Cart.findOne({ where: { user_id: userId } });
  if (!cart) {
    throw new Error('Cart not found');
  }

  const deleted = await CartItem.destroy({
    where: { id: cartItemId, cart_id: cart.id },
  });

  if (deleted === 0) {
    throw new Error('Cart item not found');
  }

  return getCartWithItems(userId);
}

/**
 * Update quantity of a specific cart item.
 */
async function updateItemQuantity(userId, cartItemId, quantity) {
  if (quantity < 1) {
    return removeItem(userId, cartItemId);
  }

  const cart = await Cart.findOne({ where: { user_id: userId } });
  if (!cart) {
    throw new Error('Cart not found');
  }

  const cartItem = await CartItem.findOne({
    where: { id: cartItemId, cart_id: cart.id },
  });

  if (!cartItem) {
    throw new Error('Cart item not found');
  }

  cartItem.quantity = quantity;
  await cartItem.save();

  return getCartWithItems(userId);
}

/**
 * Clear all items from a user's cart.
 */
async function clearCart(userId) {
  const cart = await Cart.findOne({ where: { user_id: userId } });
  if (!cart) {
    return { items: [], total: 0, item_count: 0 };
  }

  await CartItem.destroy({ where: { cart_id: cart.id } });

  return { items: [], total: 0, item_count: 0 };
}

module.exports = {
  getOrCreateCart,
  addItem,
  addMultipleItems,
  getCartWithItems,
  removeItem,
  updateItemQuantity,
  clearCart,
};
