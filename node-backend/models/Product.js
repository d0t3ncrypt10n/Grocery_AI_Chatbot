/**
 * Product Model
 * =============
 * Represents a grocery product in the store inventory.
 */

const { DataTypes } = require('sequelize');
const { sequelize } = require('../config/database');

const Product = sequelize.define('Product', {
  id: {
    type: DataTypes.INTEGER,
    primaryKey: true,
    autoIncrement: true,
  },
  name: {
    type: DataTypes.STRING(100),
    allowNull: false,
    validate: { notEmpty: true },
  },
  category: {
    type: DataTypes.STRING(50),
    allowNull: false,
    validate: { notEmpty: true },
  },
  price: {
    type: DataTypes.FLOAT,
    allowNull: false,
    defaultValue: 0,
    validate: { min: 0 },
  },
  stock: {
    type: DataTypes.INTEGER,
    allowNull: false,
    defaultValue: 0,
    validate: { min: 0 },
  },
  unit: {
    type: DataTypes.STRING(20),
    allowNull: false,
    defaultValue: 'pieces',
  },
  keywords: {
    type: DataTypes.JSON, // Array of search keywords
    allowNull: true,
    defaultValue: [],
  },
  image_url: {
    type: DataTypes.STRING(500),
    allowNull: true,
  },
  substitute_for: {
    type: DataTypes.STRING(100), // Which ingredient this substitutes
    allowNull: true,
  },
}, {
  tableName: 'products',
  indexes: [
    { fields: ['name'] },
    { fields: ['category'] },
  ],
});

module.exports = Product;
