export const ORDER_STATUSES = {
  PENDING: 'Pending',
  CONFIRMED: 'Confirmed',
  PROCESSING: 'Processing',
  SHIPPED: 'Shipped',
  OUT_FOR_DELIVERY: 'Out for Delivery',
  DELIVERED: 'Delivered',
  CANCELLED: 'Cancelled',
};

export const PAYMENT_METHODS = [
  { id: 'upi', name: 'UPI (GPay / PhonePe / Paytm)', icon: 'Smartphone' },
  { id: 'card', name: 'Credit / Debit Card', icon: 'CreditCard' },
  { id: 'netbanking', name: 'Net Banking', icon: 'Landmark' },
  { id: 'cod', name: 'Cash on Delivery', icon: 'Banknote', badge: 'Available' },
];

export const USER_ROLES = {
  CUSTOMER: 'CUSTOMER',
  ADMIN: 'ADMIN',
  SELLER: 'SELLER',
};
