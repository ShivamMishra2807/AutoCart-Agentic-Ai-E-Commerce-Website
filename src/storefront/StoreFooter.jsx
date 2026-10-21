import React from 'react';
import { Link } from 'react-router-dom';
import { BrandLink } from './Brand';
import './storefront.css';

export default function StoreFooter() {
  return (
    <footer className="ac-footer">
      <div className="ac-wrap">
        <div className="ac-footer-grid">
          <div>
            <BrandLink />
            <p>Products from local stores in your city, with real people to help whenever you need it.</p>
          </div>
          <div><h4>Shop</h4><ul>
            <li><Link to="/catalog">Everything we sell</Link></li>
            <li><Link to="/products">All products</Link></li>
            <li><Link to="/wishlist">Wishlist</Link></li>
            <li><Link to="/cart">Cart</Link></li>
          </ul></div>
          <div><h4>Account</h4><ul>
            <li><Link to="/login">Sign in</Link></li>
            <li><Link to="/register">Create account</Link></li>
            <li><Link to="/orders">Your orders</Link></li>
            <li><Link to="/support">Help and tickets</Link></li>
            <li><Link to="/contact">Contact us</Link></li>
          </ul></div>
          <div><h4>Sell</h4><ul>
            <li><Link to="/seller/apply">Become a seller</Link></li>
            <li><Link to="/seller/login">Seller sign in</Link></li>
          </ul></div>
        </div>
        <div className="ac-legal">
          <span>© {new Date().getFullYear()} AutoCart</span>
          <span>Product photos from Unsplash.</span>
        </div>
      </div>
    </footer>
  );
}
