import React from 'react';
import Hero from '../../components/home/Hero';
import CategorySection from '../../components/home/CategorySection';
import FeaturedProducts from '../../components/home/FeaturedProducts';
import DealsSection from '../../components/home/DealsSection';
import BestSellers from '../../components/home/BestSellers';
import NewArrivals from '../../components/home/NewArrivals';
import PromotionalBanner from '../../components/home/PromotionalBanner';

export const Home = () => {
  return (
    <div className="space-y-4">
      <Hero />
      <CategorySection />
      <FeaturedProducts />
      <DealsSection />
      <PromotionalBanner />
      <BestSellers />
      <NewArrivals />
    </div>
  );
};

export default Home;
