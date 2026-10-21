export const MOCK_ORDERS = [
  {
    id: "ORD-89210",
    date: "2026-08-19T14:32:00Z",
    totalAmount: 26990,
    status: "Shipped",
    currentStep: 3, // 0: Placed, 1: Confirmed, 2: Packed, 3: Shipped, 4: Out for Delivery, 5: Delivered
    estimatedDelivery: "Aug 23, 2026",
    shippingAddress: {
      fullName: "Shivam Sharma",
      street: "42 Tech Park Avenue, Sector 62",
      city: "Noida",
      state: "Uttar Pradesh",
      pincode: "201301",
      phone: "+91 98765 43210"
    },
    paymentMethod: "Credit Card (Visa ending 4242)",
    items: [
      {
        id: "prod-101",
        title: "Sony WH-1000XM5 Wireless Noise Canceling Headphones",
        brand: "Sony",
        price: 26990,
        quantity: 1,
        image: "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400&q=80",
        color: "Black"
      }
    ],
    timeline: [
      { title: "Order Placed", date: "Aug 19, 02:32 PM", completed: true, description: "Your order has been logged." },
      { title: "Confirmed", date: "Aug 19, 03:00 PM", completed: true, description: "Seller confirmed order readiness." },
      { title: "Packed", date: "Aug 20, 09:15 AM", completed: true, description: "Item packed at Delhi Fulfillment Center." },
      { title: "Shipped", date: "Aug 20, 06:45 PM", completed: true, description: "In transit via BlueDart Courier (Tracking #BD778901)." },
      { title: "Out for Delivery", date: "Expected Aug 23", completed: false, description: "Courier partner will deliver to your doorstep." },
      { title: "Delivered", date: "Expected Aug 23", completed: false, description: "Delivery completion." }
    ]
  },
  {
    id: "ORD-75124",
    date: "2026-08-10T10:15:00Z",
    totalAmount: 8995,
    status: "Delivered",
    currentStep: 5,
    estimatedDelivery: "Aug 12, 2026",
    shippingAddress: {
      fullName: "Shivam Sharma",
      street: "42 Tech Park Avenue, Sector 62",
      city: "Noida",
      state: "Uttar Pradesh",
      pincode: "201301",
      phone: "+91 98765 43210"
    },
    paymentMethod: "UPI (shivam@okicici)",
    items: [
      {
        id: "prod-104",
        title: "Nike Air Max 270 React Running Shoes",
        brand: "Nike",
        price: 8995,
        quantity: 1,
        image: "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=400&q=80",
        color: "Triple Red",
        size: "UK 9"
      }
    ],
    timeline: [
      { title: "Order Placed", date: "Aug 10, 10:15 AM", completed: true, description: "Payment received." },
      { title: "Confirmed", date: "Aug 10, 10:20 AM", completed: true, description: "Order verified." },
      { title: "Packed", date: "Aug 10, 04:00 PM", completed: true, description: "Packed in secure box." },
      { title: "Shipped", date: "Aug 11, 08:30 AM", completed: true, description: "Shipped via Express Delivery." },
      { title: "Out for Delivery", date: "Aug 12, 09:00 AM", completed: true, description: "Agent Ramesh (+91 9811122233) assigned." },
      { title: "Delivered", date: "Aug 12, 01:45 PM", completed: true, description: "Delivered to recipient." }
    ]
  }
];
