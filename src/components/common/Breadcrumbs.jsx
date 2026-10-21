import React from 'react';
import { Link } from 'react-router-dom';
import { ChevronRight, Home } from 'lucide-react';

export const Breadcrumbs = ({ items = [] }) => {
  return (
    <nav className="flex items-center gap-2 text-xs text-gray-500 py-3 overflow-x-auto hide-scrollbar">
      <Link to="/" className="flex items-center gap-1 hover:text-brand-600 transition-colors">
        <Home className="w-3.5 h-3.5" />
        <span>Home</span>
      </Link>
      {items.map((item, index) => (
        <React.Fragment key={index}>
          <ChevronRight className="w-3 h-3 text-gray-400 shrink-0" />
          {item.link ? (
            <Link to={item.link} className="hover:text-brand-600 transition-colors whitespace-nowrap">
              {item.label}
            </Link>
          ) : (
            <span className="text-gray-800 font-medium truncate max-w-[200px]">
              {item.label}
            </span>
          )}
        </React.Fragment>
      ))}
    </nav>
  );
};
