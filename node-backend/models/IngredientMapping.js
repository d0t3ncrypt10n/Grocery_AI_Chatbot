/**
 * IngredientMapping Model
 * =======================
 * Maps ingredient names (from recipes) to product search keywords.
 * Helps bridge "2 cups chopped onions" → searching for "onion" products.
 */

const { DataTypes } = require('sequelize');
const { sequelize } = require('../config/database');

const IngredientMapping = sequelize.define('IngredientMapping', {
  id: {
    type: DataTypes.INTEGER,
    primaryKey: true,
    autoIncrement: true,
  },
  ingredient_name: {
    type: DataTypes.STRING(100),
    allowNull: false,
    unique: true,
  },
  category: {
    type: DataTypes.STRING(50),
    allowNull: false,
  },
  search_keywords: {
    type: DataTypes.JSON, // Array of keywords to search products with
    allowNull: true,
    defaultValue: [],
  },
}, {
  tableName: 'ingredient_mappings',
  indexes: [
    { fields: ['ingredient_name'], unique: true },
    { fields: ['category'] },
  ],
});

module.exports = IngredientMapping;
