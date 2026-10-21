import api, { USE_MOCK_API } from './api';
import { MOCK_PRODUCTS } from '../data/mockProducts';

/**
 * AI Service Integration Layer
 * Prepared for AI Agent 1 (Shopping Assistant) & AI Agent 2 (Personalized Recommendation Agent)
 */
export const aiService = {
  /**
   * AI Agent 1 — Natural Language Product Search & Query Assistant
   */
  async searchProductsWithAI(naturalQuery) {
    if (USE_MOCK_API) {
      await new Promise(r => setTimeout(r, 900));
      const queryLower = naturalQuery.toLowerCase();
      
      let matchingProducts = [...MOCK_PRODUCTS];

      if (queryLower.includes('laptop') || queryLower.includes('programming') || queryLower.includes('code')) {
        matchingProducts = MOCK_PRODUCTS.filter(p => p.category === 'laptops');
      } else if (queryLower.includes('earbuds') || queryLower.includes('headphone') || queryLower.includes('audio') || queryLower.includes('music')) {
        matchingProducts = MOCK_PRODUCTS.filter(p => p.category === 'electronics');
      } else if (queryLower.includes('phone') || queryLower.includes('mobile') || queryLower.includes('5g')) {
        matchingProducts = MOCK_PRODUCTS.filter(p => p.category === 'mobiles');
      } else if (queryLower.includes('shoe') || queryLower.includes('nike') || queryLower.includes('wear')) {
        matchingProducts = MOCK_PRODUCTS.filter(p => p.category === 'fashion');
      }

      return {
        reply: `Based on your request "${naturalQuery}", I found ${matchingProducts.length} top-rated match(es) in our store with high performance ratings.`,
        suggestedFilters: { category: matchingProducts[0]?.category || 'all' },
        products: matchingProducts.slice(0, 4)
      };
    }
    const res = await api.post('/ai/shopping-assistant', { prompt: naturalQuery });
    return res.data;
  },

  /**
   * AI Agent 2 — Personalized Shopping & Recommendations
   */
  async getPersonalizedRecommendations(userHistory = []) {
    if (USE_MOCK_API) {
      await new Promise(r => setTimeout(r, 400));
      return {
        title: "Recommended For You by AuraAI",
        subtitle: "Based on your recent browsing & shopping preferences",
        products: MOCK_PRODUCTS.filter(p => p.isTrending || p.rating >= 4.7).slice(0, 4)
      };
    }
    const res = await api.post('/ai/recommendations', { userHistory });
    return res.data;
  },

  /**
   * AI Product Comparison
   */
  async compareProducts(productIds) {
    if (USE_MOCK_API) {
      await new Promise(r => setTimeout(r, 500));
      const items = MOCK_PRODUCTS.filter(p => productIds.includes(p.id));
      return {
        summary: `Comparing ${items.map(i => i.title).join(' vs ')}`,
        items
      };
    }
    const res = await api.post('/ai/compare', { productIds });
    return res.data;
  }
};

export default aiService;
