import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { MOCK_CATEGORIES } from '../../data/mockCategories';
import { useFilter } from '../../context/FilterContext';
import { 
  Tv, 
  Smartphone, 
  Laptop, 
  Shirt, 
  Home, 
  Sparkles, 
  Dumbbell, 
  BookOpen, 
  Watch,
  Grid
} from 'lucide-react';

const categoryIconMap = {
  electronics: Tv,
  mobiles: Smartphone,
  laptops: Laptop,
  fashion: Shirt,
  home: Home,
  beauty: Sparkles,
  sports: Dumbbell,
  books: BookOpen,
  accessories: Watch
};

export const CategoryNav = () => {
  const navigate = useNavigate();
  const { selectedCategory, setSelectedCategory } = useFilter();

  const handleCategoryClick = (catId) => {
    setSelectedCategory(catId);
    navigate(`/products?category=${catId}`);
  };

  return (
    <div className="bg-white border-b border-gray-100 shadow-2xs py-2 overflow-x-auto hide-scrollbar">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex items-center gap-2 sm:gap-6 min-w-max">
        <button
          onClick={() => handleCategoryClick('all')}
          className={`flex items-center gap-2 text-xs font-semibold px-3 py-1.5 rounded-full transition-all ${
            selectedCategory === 'all'
              ? 'bg-brand-600 text-white shadow-sm'
              : 'text-gray-600 hover:bg-gray-100'
          }`}
        >
          <Grid className="w-3.5 h-3.5" />
          <span>All Categories</span>
        </button>

        {MOCK_CATEGORIES.map((cat) => {
          const IconComponent = categoryIconMap[cat.id] || Grid;
          const isSelected = selectedCategory === cat.id;

          return (
            <button
              key={cat.id}
              onClick={() => handleCategoryClick(cat.id)}
              className={`flex items-center gap-2 text-xs font-medium px-3 py-1.5 rounded-full transition-all whitespace-nowrap ${
                isSelected
                  ? 'bg-brand-600 text-white shadow-sm font-semibold'
                  : 'text-gray-600 hover:text-brand-600 hover:bg-brand-50/60'
              }`}
            >
              <IconComponent className={`w-3.5 h-3.5 ${isSelected ? 'text-white' : 'text-gray-500'}`} />
              <span>{cat.name}</span>
            </button>
          );
        })}
      </div>
    </div>
  );
};
