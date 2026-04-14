/**
 * Server Entry Point
 * ==================
 * Express application — mounts middleware, routes, syncs DB, seeds data.
 *
 * Usage:  npm start  or  npm run dev
 */

require('dotenv').config();
const express = require('express');
const cors = require('cors');
const morgan = require('morgan');

const { sequelize, testConnection } = require('./config/database');
const { seed } = require('./config/seed');
const productRoutes = require('./routes/productRoutes');
const cartRoutes = require('./routes/cartRoutes');

const app = express();
const PORT = parseInt(process.env.PORT || '4000', 10);

// ─── Middleware ──────────────────────────────────────────────────────────────

app.use(cors({
  origin: [
    'http://localhost:3000',
    'http://localhost:5173',
    'http://127.0.0.1:3000',
    'http://127.0.0.1:5173',
    'http://localhost:5000', // Flask AI service
  ],
  methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
  allowedHeaders: ['Content-Type'],
}));

app.use(express.json());
app.use(morgan('dev'));

// ─── Routes ─────────────────────────────────────────────────────────────────

app.use('/products', productRoutes);
app.use('/cart', cartRoutes);

// Health check
app.get('/health', (req, res) => {
  res.json({
    status: 'healthy',
    service: 'node-backend',
    port: PORT,
    uptime: process.uptime(),
  });
});

// Root
app.get('/', (req, res) => {
  res.json({
    service: 'Grocery AI — Node.js E-commerce Backend',
    version: '1.0.0',
    endpoints: {
      'GET /products/search?q=&mode=&category=&max_price=': 'Search products',
      'GET /products/categories': 'List categories',
      'GET /products/:id': 'Get product by ID',
      'POST /cart/add': 'Add item to cart',
      'POST /cart/add-all': 'Batch add items',
      'GET /cart/:userId': 'Get cart',
      'DELETE /cart/:userId': 'Clear cart',
      'DELETE /cart/:userId/items/:itemId': 'Remove item',
      'PUT /cart/:userId/items/:itemId': 'Update quantity',
      'GET /health': 'Health check',
    },
  });
});

// 404 catch-all
app.use((req, res) => {
  res.status(404).json({ error: 'Endpoint not found' });
});

// Error handler
app.use((err, req, res, next) => {
  console.error('Unhandled error:', err.message);
  res.status(500).json({ error: 'Internal server error' });
});

// ─── Start Server ───────────────────────────────────────────────────────────

async function start() {
  try {
    // Test DB connection
    await testConnection();

    // Sync tables (creates if not exist)
    await sequelize.sync();
    console.log('✅ Database tables synced');

    // Seed data
    await seed();

    // Start listening
    app.listen(PORT, () => {
      console.log(`\n🚀 Node.js Backend running on http://localhost:${PORT}`);
      console.log(`   Products API: http://localhost:${PORT}/products/search?q=onion`);
      console.log(`   Cart API:     http://localhost:${PORT}/cart/{userId}`);
      console.log(`   Health:       http://localhost:${PORT}/health\n`);
    });
  } catch (error) {
    console.error('❌ Failed to start server:', error.message);
    process.exit(1);
  }
}

start();
