import fs from 'fs';
import { categories } from '../src/data/categories.js';
import { products } from '../src/data/products.js';
import { coupons } from '../src/data/coupons.js';
import { sellers } from '../src/data/sellers.js';
import { users } from '../src/data/users.js';
import { orders } from '../src/data/orders.js';

const allData = {
  categories,
  products,
  coupons,
  sellers,
  users,
  orders
};

fs.writeFileSync('seed_data.json', JSON.stringify(allData, null, 2), 'utf-8');
console.log('Successfully dumped seed_data.json with:', {
  categories: categories.length,
  products: products.length,
  coupons: coupons.length,
  sellers: sellers.length,
  users: users.length,
  orders: orders.length
});
