import React from 'react';

export const Badge = ({ children, variant = 'gray', size = 'sm', className = '' }) => {
  const variants = {
    gray: 'bg-gray-100 text-gray-700',
    green: 'bg-emerald-100 text-emerald-800',
    yellow: 'bg-amber-100 text-amber-800',
    red: 'bg-rose-100 text-rose-800',
    indigo: 'bg-indigo-100 text-indigo-800',
    blue: 'bg-sky-100 text-sky-800',
  };

  const sizes = {
    sm: 'px-2 py-0.5 text-xs font-semibold',
    md: 'px-2.5 py-1 text-xs font-bold',
  };

  return (
    <span
      className={`inline-flex items-center rounded-full ${variants[variant]} ${sizes[size]} ${className}`}
    >
      {children}
    </span>
  );
};

export default Badge;
