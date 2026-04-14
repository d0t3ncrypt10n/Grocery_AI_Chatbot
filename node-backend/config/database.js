/**
 * Database Configuration
 * ======================
 * Sequelize ORM setup with SQLite for development.
 * Switch to PostgreSQL by changing DB_DIALECT in .env
 */

const { Sequelize } = require('sequelize');
const path = require('path');
require('dotenv').config();

const dialect = process.env.DB_DIALECT || 'sqlite';

let sequelize;

if (dialect === 'sqlite') {
  // SQLite — zero-config local development
  const storagePath = process.env.DB_STORAGE || './database.sqlite';
  sequelize = new Sequelize({
    dialect: 'sqlite',
    storage: path.resolve(__dirname, '..', storagePath),
    logging: false, // Set to console.log for SQL debugging
    define: {
      timestamps: true,
      underscored: true, // Use snake_case for columns
    },
  });
} else {
  // PostgreSQL — production configuration
  sequelize = new Sequelize(
    process.env.DB_NAME || 'grocery_ai',
    process.env.DB_USER || 'postgres',
    process.env.DB_PASSWORD || '',
    {
      host: process.env.DB_HOST || 'localhost',
      port: parseInt(process.env.DB_PORT || '5432'),
      dialect: 'postgres',
      logging: false,
      define: {
        timestamps: true,
        underscored: true,
      },
      pool: {
        max: 10,
        min: 2,
        acquire: 30000,
        idle: 10000,
      },
    }
  );
}

// Test connection
async function testConnection() {
  try {
    await sequelize.authenticate();
    console.log('✅ Database connection established successfully');
  } catch (error) {
    console.error('❌ Unable to connect to the database:', error.message);
    process.exit(1);
  }
}

module.exports = { sequelize, testConnection };
