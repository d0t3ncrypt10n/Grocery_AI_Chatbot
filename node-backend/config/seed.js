/**
 * Database Seed Script
 * ====================
 * Seeds the database with 55+ grocery products and 35+ ingredient mappings.
 * Idempotent: uses findOrCreate to avoid duplicates.
 *
 * Usage:  npm run seed
 */

const { sequelize } = require('./database');
const { Product, IngredientMapping } = require('../models');

// ─── Product Data ────────────────────────────────────────────────────────────

const products = [
  // ── Vegetables ──────────────────────────────────────────────
  { name: 'Onion (1 kg)', category: 'vegetables', price: 40, stock: 200, unit: 'kg', keywords: ['onion', 'pyaaz', 'pyaj'], image_url: '' },
  { name: 'Tomato (1 kg)', category: 'vegetables', price: 35, stock: 180, unit: 'kg', keywords: ['tomato', 'tamatar'], image_url: '' },
  { name: 'Potato (1 kg)', category: 'vegetables', price: 30, stock: 250, unit: 'kg', keywords: ['potato', 'aloo', 'alu'], image_url: '' },
  { name: 'Green Chili (100g)', category: 'vegetables', price: 10, stock: 100, unit: 'g', keywords: ['green chili', 'hari mirch', 'chili', 'chilli'], image_url: '' },
  { name: 'Ginger (100g)', category: 'vegetables', price: 15, stock: 120, unit: 'g', keywords: ['ginger', 'adrak'], image_url: '' },
  { name: 'Garlic (200g)', category: 'vegetables', price: 25, stock: 150, unit: 'g', keywords: ['garlic', 'lahsun'], image_url: '' },
  { name: 'Capsicum (250g)', category: 'vegetables', price: 30, stock: 80, unit: 'g', keywords: ['capsicum', 'bell pepper', 'shimla mirch'], image_url: '' },
  { name: 'Spinach (1 bunch)', category: 'vegetables', price: 20, stock: 60, unit: 'bunch', keywords: ['spinach', 'palak'], image_url: '' },
  { name: 'Cauliflower (1 pc)', category: 'vegetables', price: 35, stock: 50, unit: 'pieces', keywords: ['cauliflower', 'gobi', 'phool gobi'], image_url: '' },
  { name: 'Carrot (500g)', category: 'vegetables', price: 25, stock: 100, unit: 'g', keywords: ['carrot', 'gajar'], image_url: '' },
  { name: 'Peas (250g)', category: 'vegetables', price: 30, stock: 70, unit: 'g', keywords: ['peas', 'matar', 'green peas'], image_url: '' },
  { name: 'Coriander Leaves (1 bunch)', category: 'vegetables', price: 10, stock: 90, unit: 'bunch', keywords: ['coriander', 'cilantro', 'dhania', 'dhaniya'], image_url: '' },
  { name: 'Mint Leaves (1 bunch)', category: 'vegetables', price: 10, stock: 70, unit: 'bunch', keywords: ['mint', 'pudina'], image_url: '' },
  { name: 'Lemon (4 pcs)', category: 'vegetables', price: 20, stock: 120, unit: 'pieces', keywords: ['lemon', 'nimbu', 'lime'], image_url: '' },

  // ── Dairy ───────────────────────────────────────────────────
  { name: 'Amul Butter (100g)', category: 'dairy', price: 55, stock: 80, unit: 'g', keywords: ['butter', 'makhan'], image_url: '' },
  { name: 'Paneer (200g)', category: 'dairy', price: 80, stock: 60, unit: 'g', keywords: ['paneer', 'cottage cheese'], image_url: '' },
  { name: 'Milk (1 L)', category: 'dairy', price: 60, stock: 100, unit: 'litre', keywords: ['milk', 'doodh'], image_url: '' },
  { name: 'Curd / Yogurt (400g)', category: 'dairy', price: 35, stock: 90, unit: 'g', keywords: ['curd', 'yogurt', 'dahi'], image_url: '' },
  { name: 'Fresh Cream (200ml)', category: 'dairy', price: 45, stock: 50, unit: 'ml', keywords: ['cream', 'fresh cream', 'malai'], image_url: '' },
  { name: 'Cheese Slice (10 pcs)', category: 'dairy', price: 95, stock: 40, unit: 'pieces', keywords: ['cheese', 'cheese slice'], image_url: '' },
  { name: 'Ghee (500ml)', category: 'dairy', price: 280, stock: 30, unit: 'ml', keywords: ['ghee', 'clarified butter'], image_url: '' },

  // ── Grains & Staples ───────────────────────────────────────
  { name: 'Basmati Rice (1 kg)', category: 'grains', price: 120, stock: 100, unit: 'kg', keywords: ['rice', 'basmati', 'chawal'], image_url: '' },
  { name: 'Wheat Flour / Atta (1 kg)', category: 'grains', price: 45, stock: 120, unit: 'kg', keywords: ['flour', 'atta', 'wheat flour', 'wheat', 'chapati flour'], image_url: '' },
  { name: 'Pasta (500g)', category: 'grains', price: 65, stock: 60, unit: 'g', keywords: ['pasta', 'penne', 'spaghetti', 'macaroni'], image_url: '' },
  { name: 'Bread (400g)', category: 'grains', price: 35, stock: 50, unit: 'g', keywords: ['bread', 'loaf'], image_url: '' },
  { name: 'Noodles (300g)', category: 'grains', price: 30, stock: 80, unit: 'g', keywords: ['noodles', 'hakka noodles'], image_url: '' },
  { name: 'Poha / Flattened Rice (500g)', category: 'grains', price: 35, stock: 40, unit: 'g', keywords: ['poha', 'flattened rice', 'beaten rice'], image_url: '' },
  { name: 'Besan / Gram Flour (500g)', category: 'grains', price: 55, stock: 50, unit: 'g', keywords: ['besan', 'gram flour', 'chickpea flour'], image_url: '' },

  // ── Spices ─────────────────────────────────────────────────
  { name: 'Turmeric Powder (100g)', category: 'spices', price: 30, stock: 100, unit: 'g', keywords: ['turmeric', 'haldi'], image_url: '' },
  { name: 'Red Chili Powder (100g)', category: 'spices', price: 35, stock: 100, unit: 'g', keywords: ['red chili', 'lal mirch', 'chili powder', 'red chili powder'], image_url: '' },
  { name: 'Coriander Powder (100g)', category: 'spices', price: 30, stock: 90, unit: 'g', keywords: ['coriander powder', 'dhaniya powder'], image_url: '' },
  { name: 'Cumin Seeds (100g)', category: 'spices', price: 40, stock: 80, unit: 'g', keywords: ['cumin', 'jeera', 'cumin seeds'], image_url: '' },
  { name: 'Garam Masala (50g)', category: 'spices', price: 45, stock: 70, unit: 'g', keywords: ['garam masala', 'masala'], image_url: '' },
  { name: 'Salt (1 kg)', category: 'spices', price: 20, stock: 200, unit: 'kg', keywords: ['salt', 'namak'], image_url: '' },
  { name: 'Black Pepper (50g)', category: 'spices', price: 55, stock: 60, unit: 'g', keywords: ['black pepper', 'kali mirch', 'pepper'], image_url: '' },
  { name: 'Bay Leaves (25g)', category: 'spices', price: 25, stock: 50, unit: 'g', keywords: ['bay leaf', 'bay leaves', 'tej patta'], image_url: '' },
  { name: 'Cardamom (25g)', category: 'spices', price: 60, stock: 40, unit: 'g', keywords: ['cardamom', 'elaichi'], image_url: '' },
  { name: 'Cinnamon Sticks (50g)', category: 'spices', price: 45, stock: 40, unit: 'g', keywords: ['cinnamon', 'dalchini'], image_url: '' },
  { name: 'Cloves (25g)', category: 'spices', price: 50, stock: 35, unit: 'g', keywords: ['cloves', 'laung'], image_url: '' },
  { name: 'Mustard Seeds (100g)', category: 'spices', price: 25, stock: 60, unit: 'g', keywords: ['mustard seeds', 'rai', 'sarson'], image_url: '' },
  { name: 'Kasuri Methi (25g)', category: 'spices', price: 30, stock: 50, unit: 'g', keywords: ['kasuri methi', 'fenugreek', 'dried fenugreek'], image_url: '' },

  // ── Proteins ───────────────────────────────────────────────
  { name: 'Eggs (12 pcs)', category: 'proteins', price: 75, stock: 100, unit: 'pieces', keywords: ['egg', 'eggs', 'anda'], image_url: '' },
  { name: 'Chicken Breast (500g)', category: 'proteins', price: 180, stock: 50, unit: 'g', keywords: ['chicken', 'chicken breast', 'murgh'], image_url: '' },
  { name: 'Chicken Thighs (500g)', category: 'proteins', price: 150, stock: 40, unit: 'g', keywords: ['chicken thigh', 'chicken leg', 'tangdi'], image_url: '' },
  { name: 'Fish / Rohu (500g)', category: 'proteins', price: 200, stock: 30, unit: 'g', keywords: ['fish', 'rohu', 'machhi', 'machli'], image_url: '' },
  { name: 'Prawns (250g)', category: 'proteins', price: 250, stock: 20, unit: 'g', keywords: ['prawns', 'shrimp', 'jhinga'], image_url: '' },
  { name: 'Tofu (200g)', category: 'proteins', price: 60, stock: 30, unit: 'g', keywords: ['tofu', 'soy paneer'], substitute_for: 'paneer', image_url: '' },
  { name: 'Toor Dal (500g)', category: 'proteins', price: 70, stock: 80, unit: 'g', keywords: ['toor dal', 'arhar dal', 'dal', 'lentil'], image_url: '' },
  { name: 'Chana Dal (500g)', category: 'proteins', price: 65, stock: 70, unit: 'g', keywords: ['chana dal', 'bengal gram', 'chana'], image_url: '' },
  { name: 'Moong Dal (500g)', category: 'proteins', price: 75, stock: 60, unit: 'g', keywords: ['moong dal', 'green gram', 'moong'], image_url: '' },
  { name: 'Rajma / Kidney Beans (500g)', category: 'proteins', price: 90, stock: 50, unit: 'g', keywords: ['rajma', 'kidney beans'], image_url: '' },

  // ── Oils & Sauces ──────────────────────────────────────────
  { name: 'Mustard Oil (1 L)', category: 'oils_sauces', price: 180, stock: 40, unit: 'litre', keywords: ['mustard oil', 'sarson oil'], image_url: '' },
  { name: 'Sunflower Oil (1 L)', category: 'oils_sauces', price: 140, stock: 50, unit: 'litre', keywords: ['sunflower oil', 'cooking oil', 'oil', 'vegetable oil'], image_url: '' },
  { name: 'Olive Oil (250ml)', category: 'oils_sauces', price: 220, stock: 30, unit: 'ml', keywords: ['olive oil'], image_url: '' },
  { name: 'Tomato Ketchup (500g)', category: 'oils_sauces', price: 95, stock: 60, unit: 'g', keywords: ['ketchup', 'tomato ketchup', 'sauce'], image_url: '' },
  { name: 'Soy Sauce (200ml)', category: 'oils_sauces', price: 55, stock: 40, unit: 'ml', keywords: ['soy sauce'], image_url: '' },
];

// ─── Ingredient Mapping Data ─────────────────────────────────────────────────

const ingredientMappings = [
  // Vegetables
  { ingredient_name: 'onion', category: 'vegetables', search_keywords: ['onion', 'pyaaz'] },
  { ingredient_name: 'tomato', category: 'vegetables', search_keywords: ['tomato', 'tamatar'] },
  { ingredient_name: 'potato', category: 'vegetables', search_keywords: ['potato', 'aloo'] },
  { ingredient_name: 'ginger', category: 'vegetables', search_keywords: ['ginger', 'adrak'] },
  { ingredient_name: 'garlic', category: 'vegetables', search_keywords: ['garlic', 'lahsun'] },
  { ingredient_name: 'green chili', category: 'vegetables', search_keywords: ['green chili', 'hari mirch'] },
  { ingredient_name: 'capsicum', category: 'vegetables', search_keywords: ['capsicum', 'bell pepper'] },
  { ingredient_name: 'spinach', category: 'vegetables', search_keywords: ['spinach', 'palak'] },
  { ingredient_name: 'cauliflower', category: 'vegetables', search_keywords: ['cauliflower', 'gobi'] },
  { ingredient_name: 'carrot', category: 'vegetables', search_keywords: ['carrot', 'gajar'] },
  { ingredient_name: 'peas', category: 'vegetables', search_keywords: ['peas', 'matar'] },
  { ingredient_name: 'coriander', category: 'vegetables', search_keywords: ['coriander', 'cilantro', 'dhania'] },
  { ingredient_name: 'mint', category: 'vegetables', search_keywords: ['mint', 'pudina'] },
  { ingredient_name: 'lemon', category: 'vegetables', search_keywords: ['lemon', 'nimbu', 'lime'] },

  // Dairy
  { ingredient_name: 'butter', category: 'dairy', search_keywords: ['butter', 'makhan'] },
  { ingredient_name: 'paneer', category: 'dairy', search_keywords: ['paneer', 'cottage cheese'] },
  { ingredient_name: 'milk', category: 'dairy', search_keywords: ['milk', 'doodh'] },
  { ingredient_name: 'curd', category: 'dairy', search_keywords: ['curd', 'yogurt', 'dahi'] },
  { ingredient_name: 'cream', category: 'dairy', search_keywords: ['cream', 'fresh cream', 'malai'] },
  { ingredient_name: 'ghee', category: 'dairy', search_keywords: ['ghee', 'clarified butter'] },
  { ingredient_name: 'cheese', category: 'dairy', search_keywords: ['cheese'] },

  // Grains
  { ingredient_name: 'rice', category: 'grains', search_keywords: ['rice', 'basmati', 'chawal'] },
  { ingredient_name: 'flour', category: 'grains', search_keywords: ['flour', 'atta', 'wheat flour'] },
  { ingredient_name: 'pasta', category: 'grains', search_keywords: ['pasta', 'spaghetti', 'penne'] },
  { ingredient_name: 'bread', category: 'grains', search_keywords: ['bread'] },

  // Spices
  { ingredient_name: 'turmeric', category: 'spices', search_keywords: ['turmeric', 'haldi'] },
  { ingredient_name: 'cumin', category: 'spices', search_keywords: ['cumin', 'jeera'] },
  { ingredient_name: 'garam masala', category: 'spices', search_keywords: ['garam masala'] },
  { ingredient_name: 'salt', category: 'spices', search_keywords: ['salt', 'namak'] },
  { ingredient_name: 'pepper', category: 'spices', search_keywords: ['black pepper', 'pepper'] },
  { ingredient_name: 'red chili powder', category: 'spices', search_keywords: ['red chili', 'chili powder'] },

  // Proteins
  { ingredient_name: 'egg', category: 'proteins', search_keywords: ['egg', 'eggs', 'anda'] },
  { ingredient_name: 'chicken', category: 'proteins', search_keywords: ['chicken', 'chicken breast', 'murgh'] },
  { ingredient_name: 'dal', category: 'proteins', search_keywords: ['dal', 'lentil', 'toor dal'] },
  { ingredient_name: 'fish', category: 'proteins', search_keywords: ['fish', 'rohu', 'machli'] },

  // Oils
  { ingredient_name: 'oil', category: 'oils_sauces', search_keywords: ['oil', 'cooking oil', 'sunflower oil'] },
];

// ─── Seed Function ───────────────────────────────────────────────────────────

async function seed() {
  try {
    console.log('🌱 Starting database seed...');

    // Sync tables
    await sequelize.sync();

    // Seed products
    let productCount = 0;
    for (const product of products) {
      const [, created] = await Product.findOrCreate({
        where: { name: product.name },
        defaults: product,
      });
      if (created) productCount++;
    }
    console.log(`  ✅ Products: ${productCount} new / ${products.length} total`);

    // Seed ingredient mappings
    let mappingCount = 0;
    for (const mapping of ingredientMappings) {
      const [, created] = await IngredientMapping.findOrCreate({
        where: { ingredient_name: mapping.ingredient_name },
        defaults: mapping,
      });
      if (created) mappingCount++;
    }
    console.log(`  ✅ Ingredient Mappings: ${mappingCount} new / ${ingredientMappings.length} total`);

    console.log('🌱 Seed complete!');
  } catch (error) {
    console.error('❌ Seed failed:', error.message);
    process.exit(1);
  }
}

// Run directly
if (require.main === module) {
  seed().then(() => process.exit(0));
}

module.exports = { seed };
