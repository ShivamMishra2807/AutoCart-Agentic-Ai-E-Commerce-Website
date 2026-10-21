import React from 'react';
import { Link } from 'react-router-dom';
import {
  Smartphone, Shirt, CookingPot, Sparkles, Dumbbell, BookOpen, Apple, Puzzle, Tag,
} from 'lucide-react';
import { firstImage } from './parts';
import './storefront.css';

/** The AutoCart mark: a shopping bag with a tick, in the brand colour. */
export const LogoMark = ({ size = 34 }) => (
  <svg viewBox="0 0 48 48" width={size} height={size} aria-hidden="true" focusable="false" style={{ flex: 'none' }}>
    <rect width="48" height="48" rx="13" fill="var(--brand)" />
    <path d="M14 18h20l-1.8 15.2a3 3 0 0 1-3 2.8H18.8a3 3 0 0 1-3-2.8L14 18z" fill="var(--on-brand)" />
    <path d="M19 18v-2a5 5 0 0 1 10 0v2" fill="none" stroke="var(--on-brand)" strokeWidth="3" strokeLinecap="round" />
    <path d="M20.5 26.5l3 3 5-6" fill="none" stroke="var(--brand)" strokeWidth="2.8" strokeLinecap="round" strokeLinejoin="round" />
  </svg>
);

export const BrandLink = ({ to = '/', size = 34, className = '' }) => (
  <Link to={to} className={`ac-brandlink ${className}`} aria-label="AutoCart home">
    <LogoMark size={size} />
    <span className="ac-logo">Auto<i>Cart</i></span>
  </Link>
);

const ICONS = [
  [/electronic|phone|laptop|tv/i, Smartphone], [/fashion|cloth|apparel|wear/i, Shirt], [/home|kitchen|furnit/i, CookingPot],
  [/beauty|personal|care|cosmetic/i, Sparkles], [/sport|fitness|gym/i, Dumbbell], [/book|stationery|office/i, BookOpen],
  [/grocery|food|gourmet/i, Apple], [/toy|baby|kid/i, Puzzle],
];
export const CategoryIcon = ({ name = '', size = 18, className = '' }) => {
  const Icon = (ICONS.find(([re]) => re.test(name)) || [null, Tag])[1];
  return <Icon size={size} className={className} aria-hidden="true" />;
};

/**
 * Product photo. When the catalogue reuses one photo for several products, only one of them may show it,
 * so shoppers are never shown a picture of the wrong thing. The others get a designed tile with the brand name.
 */
export const Photo = ({ p, w = 520, alt, className = '', eager = false }) => {
  const src = firstImage(p, w);
  if (src) return <img src={src} alt={alt ?? p.name} className={className} loading={eager ? 'eager' : 'lazy'} draggable="false" />;
  return (
    <div className={`ac-notile ${className}`} role="img" aria-label={alt ?? p.name}>
      <CategoryIcon name={p.category} size={w > 300 ? 44 : 20} />
      <b>{p.brand || p.category}</b>
      <span>{p.category}</span>
    </div>
  );
};
