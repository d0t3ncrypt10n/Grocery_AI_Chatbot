/**
 * Cart Model
 * ==========
 * Represents a user's shopping cart.
 */

const { DataTypes } = require('sequelize');
const { sequelize } = require('../config/database');

const Cart = sequelize.define('Cart', {
  id: {
    type: DataTypes.INTEGER,
    primaryKey: true,
    autoIncrement: true,
  },
  user_id: {
    type: DataTypes.STRING(100),
    allowNull: false,
  },
}, {
  tableName: 'carts',
  indexes: [
    { fields: ['user_id'] },
  ],
});

module.exports = Cart;
