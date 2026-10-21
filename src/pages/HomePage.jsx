import React, { useEffect, useState } from 'react';
import { HeroCarousel } from '../components/home/HeroCarousel';
import { TopCategories } from '../components/home/TopCategories';
import { FlashDeals } from '../components/home/FlashDeals';
import { ProductSection } from '../components/home/ProductSection';
import { BrandGrid } from '../components/home/BrandGrid';
import { Newsletter } from '../components/home/Newsletter';
import { productService } from '../services/productService';
import { ProductGridSkeleton } from '../components/common/SkeletonLoader';

export const HomePage = () => {
  const [featuredData, setFeaturedData] = useState({ flashDeals: [], bestSellers: [], trending: [] });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchHomeData = async () => {
      try {
        const data = await productService.getFeaturedProducts();
        setFeaturedData(data);
      } catch (err) {
        console.error("Error fetching homepage products:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchHomeData();
  }, []);

  return (
    <div className="space-y-4 pb-12">
      <HeroCarousel />
      <TopCategories />
      <FlashDeals />

      {loading ? (
        <div className="max-w-7xl mx-auto px-4 py-8">
          <ProductGridSkeleton count={4} />
        </div>
      ) : (
        <>
          <ProductSection
            title="Deals of the Day"
            subtitle="Handpicked top discounts on flagship gadgets & fashion"
            products={featuredData.bestSellers}
          />

          <ProductSection
            title="Trending & Best Sellers"
            subtitle="Most popular items loved by over 100,000+ customers this week"
            products={featuredData.trending}
          />
        </>
      )}

      <BrandGrid />
      <Newsletter />
    </div>
  );
};
