import api from './api';

const getSessionId = () => {
  let sid = localStorage.getItem('autocart_ai_session_id');
  if (!sid) {
    sid = 'sess_' + Math.random().toString(36).substring(2, 12);
    localStorage.setItem('autocart_ai_session_id', sid);
  }
  return sid;
};

export const agentService = {
  /**
   * Agent A: Discovery Agent (Customer Shopping Portal with Location)
   */
  async discover(prompt, location = {}) {
    const res = await api.post('/ai/discovery', {
      prompt,
      sessionId: getSessionId(),
      lat: location.lat,
      lng: location.lng,
      pinCode: location.pincode,
    });
    return res.data;
  },

  /**
   * Agent B: Customer Engagement Agent (Customer Orders, Cart, Support)
   */
  async engage(prompt, cartItems = []) {
    const res = await api.post('/ai/customer-engagement', {
      prompt,
      cartItems,
      sessionId: getSessionId(),
    });
    return res.data;
  },

  /**
   * Agent D: Seller Onboarding Agent (Admin & Multi-Vendor Portal)
   */
  async onboardSeller(application) {
    const res = await api.post('/ai/seller-onboarding', application);
    return res.data;
  },

  /**
   * Agent E: Seller Business Assistant (Listing Generator & Stock Health)
   */
  async sellerAssistant(prompt, sellerId, extra = {}) {
    const res = await api.post('/ai/seller-assistant', {
      prompt,
      sellerId,
      ...extra,
    });
    return res.data;
  },

  /**
   * Agent F: Admin Marketplace Assistant (Application Audit & Compliance)
   */
  async adminAssistant(prompt) {
    const res = await api.post('/ai/admin-assistant', { prompt });
    return res.data;
  },

  /**
   * Product Comparison
   */
  async compareProducts(productIds) {
    const res = await api.post('/ai/compare', { productIds });
    return res.data;
  },

  /**
   * Execute 8-state transition action on seller application
   */
  async executeSellerApplicationAction(applicationId, action, reason = '') {
    const res = await api.post(`/admin/seller-applications/${applicationId}/action/`, {
      action,
      reason,
    });
    return res.data;
  },

  /**
   * Fetch all seller applications (Admin)
   */
  async getSellerApplications(state = '') {
    const url = state ? `/seller/applications?state=${state}` : '/seller/applications';
    const res = await api.get(url);
    return res.data;
  },

  /**
   * Clear session memory
   */
  clearSession() {
    localStorage.removeItem('autocart_ai_session_id');
  }
};

export default agentService;
