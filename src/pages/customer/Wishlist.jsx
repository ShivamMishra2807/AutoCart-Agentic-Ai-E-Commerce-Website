import React, { useEffect, useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import { Heart } from 'lucide-react';
import api from '../../services/api';
import { useWishlist } from '../../hooks/useWishlist';
import { ProductCard, asList, tonesFor } from '../../storefront/parts';
import '../../storefront/storefront.css';
import '../../storefront/forms.css';

export const Wishlist = () => {
  const { wishlistItems } = useWishlist();
  const [categories, setCategories] = useState([]);
  useEffect(() => { document.title = 'Your wishlist | AutoCart'; api.get('/categories').then((r) => setCategories(asList(r.data))).catch(() => {}); }, []);
  const tones = useMemo(() => tonesFor(categories), [categories]);

  return (
    <div className="ac ac-page"><div className="ac-wrap">
      <h1 className="ac-display">Your wishlist</h1>
      <p className="ac-sub">{wishlistItems.length ? `${wishlistItems.length} saved. Tap the heart on any product to add or remove it.` : 'Things you save show up here.'}</p>
      {wishlistItems.length === 0 ? (
        <div className="ac-box" style={{ marginTop: 28, textAlign: 'center', padding: 48 }}>
          <Heart size={44} color="var(--brand)" />
          <h2 style={{ marginTop: 12 }}>Nothing saved yet</h2>
          <Link to="/catalog" className="ac-btn ac-btn-blue ac-btn-small" style={{ marginTop: 8 }}>Find something you love</Link>
        </div>
      ) : (
        <div className="ac-grid" style={{ marginTop: 32 }}>{wishlistItems.map((p) => <ProductCard key={p.id} p={p} tone={tones[p.category]} />)}</div>
      )}
    </div></div>
  );
};

export default Wishlist;
