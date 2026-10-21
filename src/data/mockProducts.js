export const MOCK_PRODUCTS = [
  {
    id: "prod-101",
    title: "Sony WH-1000XM5 Wireless Noise Canceling Headphones",
    brand: "Sony",
    category: "electronics",
    description: "Industry-leading noise cancellation optimized to two processors and 8 microphones. Magnificent Sound, engineered to perfection with the new Integrated Processor V1.",
    price: 26990,
    originalPrice: 34990,
    discount: 23,
    rating: 4.8,
    reviewCount: 3420,
    images: [
      "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=800&q=80",
      "https://images.unsplash.com/photo-1583394838336-acd977736f90?w=800&q=80"
    ],
    colors: ["Black", "Silver", "Midnight Blue"],
    sizes: ["One Size"],
    stock: 45,
    deliveryDate: "Tomorrow by 2 PM",
    isFlashDeal: true,
    isBestSeller: true,
    isTrending: true,
    specifications: {
      "Battery Life": "Up to 30 Hours",
      "Bluetooth Version": "5.2",
      "Driver Unit": "30mm",
      "Weight": "250g"
    },
    highlights: [
      "Industry Leading Noise Cancellation",
      "Ultra-comfortable lightweight design",
      "Speak-to-Chat technology"
    ]
  },
  {
    id: "prod-102",
    title: "Apple iPhone 15 Pro Max (256 GB) - Natural Titanium",
    brand: "Apple",
    category: "mobiles",
    description: "Forged in titanium and featuring the groundbreaking A17 Pro chip, a customizable Action button, and the most powerful iPhone camera system ever.",
    price: 139900,
    originalPrice: 159900,
    discount: 13,
    rating: 4.9,
    reviewCount: 5120,
    images: [
      "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=800&q=80",
      "https://images.unsplash.com/photo-1592750475338-74b7b21085ab?w=800&q=80"
    ],
    colors: ["Natural Titanium", "Blue Titanium", "Black Titanium"],
    sizes: ["256 GB", "512 GB", "1 TB"],
    stock: 18,
    deliveryDate: "Get it by Sunday",
    isFlashDeal: false,
    isBestSeller: true,
    isTrending: true,
    specifications: {
      "Display": "6.7-inch Super Retina XDR display",
      "Processor": "A17 Pro chip",
      "Main Camera": "48MP Main | Ultra Wide | Telephoto"
    },
    highlights: [
      "Aerospace-grade titanium design",
      "A17 Pro Chip for next-level gaming",
      "48MP Camera with 5x Optical Zoom"
    ]
  },
  {
    id: "prod-103",
    title: "ASUS ROG Zephyrus G16 OLED Gaming Laptop",
    brand: "Asus",
    category: "laptops",
    description: "Powered by Intel Core Ultra 9 processor and NVIDIA RTX 4070 GPU in an ultra-thin CNC aluminum chassis with a breathtaking 2.5K 240Hz OLED screen.",
    price: 184990,
    originalPrice: 219990,
    discount: 16,
    rating: 4.7,
    reviewCount: 890,
    images: [
      "https://images.unsplash.com/photo-1603302576837-37561b2e2302?w=800&q=80",
      "https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=800&q=80"
    ],
    colors: ["Eclipse Gray", "Platinum White"],
    sizes: ["16GB RAM / 1TB SSD", "32GB RAM / 2TB SSD"],
    stock: 12,
    deliveryDate: "Tomorrow by 6 PM",
    isFlashDeal: true,
    isBestSeller: false,
    isTrending: true,
    specifications: {
      "Processor": "Intel Core Ultra 9 185H",
      "Graphics": "NVIDIA GeForce RTX 4070 8GB",
      "Display": "16-inch 2.5K 240Hz OLED"
    },
    highlights: [
      "Stunning 240Hz OLED Display",
      "Sleek CNC Aluminum Chassis"
    ]
  },
  {
    id: "prod-104",
    title: "Nike Air Max 270 React Running Shoes",
    brand: "Nike",
    category: "fashion",
    description: "Combines Nike's tallest Max Air unit with resilient Nike React foam for continuous cushioning that doesn't quit.",
    price: 8995,
    originalPrice: 12995,
    discount: 31,
    rating: 4.6,
    reviewCount: 1840,
    images: [
      "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=800&q=80",
      "https://images.unsplash.com/photo-1608231387042-66d1773070a5?w=800&q=80"
    ],
    colors: ["Triple Red", "Black White"],
    sizes: ["UK 7", "UK 8", "UK 9", "UK 10"],
    stock: 55,
    deliveryDate: "Get it in 2 Days",
    isFlashDeal: true,
    isBestSeller: true,
    isTrending: false,
    specifications: {
      "Upper Material": "Mesh & Synthetic",
      "Sole Material": "Rubber Air Unit"
    },
    highlights: [
      "Max Air 270 unit delivers unrivaled comfort",
      "Nike React smooth cushioning"
    ]
  },
  {
    id: "prod-105",
    title: "Samsung Galaxy S24 Ultra 5G (Titanium Gray)",
    brand: "Samsung",
    category: "mobiles",
    description: "Welcome to the era of mobile AI. With Galaxy AI, search like never before, get real-time voice translation, and format notes.",
    price: 129999,
    originalPrice: 144999,
    discount: 10,
    rating: 4.8,
    reviewCount: 2980,
    images: [
      "https://images.unsplash.com/photo-1610945265064-0e34e5519bbf?w=800&q=80"
    ],
    colors: ["Titanium Gray", "Titanium Black"],
    sizes: ["256 GB", "512 GB"],
    stock: 22,
    deliveryDate: "Tomorrow by 11 AM",
    isFlashDeal: false,
    isBestSeller: true,
    isTrending: true,
    specifications: {
      "Display": "6.8-inch QHD+ AMOLED 120Hz",
      "Processor": "Snapdragon 8 Gen 3 for Galaxy"
    },
    highlights: [
      "Galaxy AI Live Translate & Circle to Search",
      "Integrated built-in S Pen"
    ]
  },
  {
    id: "prod-106",
    title: "Nespresso Vertuo Next Coffee Machine",
    brand: "Nespresso",
    category: "home",
    description: "Vertuo Next offers fresh brewed Coffee with crema as well as delicious authentic Espresso. Reads barcoded pods to extract optimal flavor.",
    price: 14990,
    originalPrice: 19990,
    discount: 25,
    rating: 4.5,
    reviewCount: 650,
    images: [
      "https://images.unsplash.com/photo-1517668808822-9ebe02f2a6e8?w=800&q=80"
    ],
    colors: ["Matte Black"],
    sizes: ["Standard"],
    stock: 30,
    deliveryDate: "Get it by Monday",
    isFlashDeal: false,
    isBestSeller: false,
    isTrending: true,
    specifications: {
      "Water Tank": "1.1 Liters",
      "Heat Up Time": "25 Seconds"
    },
    highlights: [
      "Centrifusion extraction technology"
    ]
  },
  {
    id: "prod-107",
    title: "Dyson Airwrap Multi-Styler Complete Long",
    brand: "Dyson",
    category: "beauty",
    description: "Curl, shape, smooth and hide flyaways with no extreme heat. Re-engineered attachments harness Enhanced Coanda airflow.",
    price: 45900,
    originalPrice: 49900,
    discount: 8,
    rating: 4.7,
    reviewCount: 1430,
    images: [
      "https://images.unsplash.com/photo-1522337360788-8b13dee7a37e?w=800&q=80"
    ],
    colors: ["Strawberry Bronze"],
    sizes: ["Long Barrel"],
    stock: 14,
    deliveryDate: "Tomorrow by 5 PM",
    isFlashDeal: true,
    isBestSeller: true,
    isTrending: true,
    specifications: {
      "Airflow": "13.5 l/s",
      "Wattage": "1300W"
    },
    highlights: [
      "Coanda airflow styles without extreme heat damage"
    ]
  },
  {
    id: "prod-108",
    title: "Apple Watch Ultra 2 GPS + Cellular 49mm Titanium",
    brand: "Apple",
    category: "accessories",
    description: "The ultimate sports and adventure watch. Featuring a lightweight titanium case, extra-long battery life, and the brightest Apple display ever.",
    price: 89900,
    originalPrice: 94900,
    discount: 5,
    rating: 4.9,
    reviewCount: 780,
    images: [
      "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=800&q=80"
    ],
    colors: ["Titanium Natural"],
    sizes: ["Alpine Loop Medium"],
    stock: 20,
    deliveryDate: "Get it in 2 Days",
    isFlashDeal: false,
    isBestSeller: true,
    isTrending: true,
    specifications: {
      "Case": "49mm Titanium",
      "Display": "3000 nits Always-On Retina"
    },
    highlights: [
      "Precision dual-frequency GPS"
    ]
  },
  {
    id: "prod-109",
    title: "Atomic Habits by James Clear (Hardcover Edition)",
    brand: "Penguin Books",
    category: "books",
    description: "An easy and proven way to build good habits and break bad ones. Tiny changes produce remarkable results in this #1 New York Times bestseller.",
    price: 599,
    originalPrice: 799,
    discount: 25,
    rating: 4.9,
    reviewCount: 18450,
    images: [
      "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=800&q=80"
    ],
    colors: ["Hardcover"],
    sizes: ["Standard Edition"],
    stock: 150,
    deliveryDate: "Tomorrow by 10 AM",
    isFlashDeal: true,
    isBestSeller: true,
    isTrending: false,
    specifications: {
      "Author": "James Clear",
      "Pages": "320 Pages"
    },
    highlights: [
      "#1 World Bestseller"
    ]
  },
  {
    id: "prod-110",
    title: "Decathlon Kiprun Fast Road Running Treadmill",
    brand: "Decathlon",
    category: "sports",
    description: "Foldable electric home treadmill with up to 16 km/h speed and 10 incline levels for intense cardinal training.",
    price: 34999,
    originalPrice: 44999,
    discount: 22,
    rating: 4.4,
    reviewCount: 310,
    images: [
      "https://images.unsplash.com/photo-1517838277536-f5f99be501cd?w=800&q=80",
      "https://images.unsplash.com/photo-1540497077202-7c8a3999166f?w=800&q=80"
    ],
    colors: ["Matte Black"],
    sizes: ["Standard Foldable"],
    stock: 8,
    deliveryDate: "Get it by Wednesday",
    isFlashDeal: false,
    isBestSeller: false,
    isTrending: false,
    specifications: {
      "Motor": "2.5 HP Continuous",
      "Speed Range": "1 - 16 km/h"
    },
    highlights: [
      "Compact easy-fold mechanism"
    ]
  },
  {
    id: "prod-111",
    title: "Yonex Nanoflare 800 Professional Badminton Racket",
    brand: "Yonex",
    category: "sports",
    description: "Designed for lightning-fast drive shots and incredible head-light maneuverability. Razor frame for reduced air resistance.",
    price: 14490,
    originalPrice: 17990,
    discount: 19,
    rating: 4.7,
    reviewCount: 520,
    images: [
      "https://images.unsplash.com/photo-1626224583764-f87db24ac4ea?w=800&q=80"
    ],
    colors: ["Matte Black / Gold"],
    sizes: ["4U G5"],
    stock: 25,
    deliveryDate: "Get it in 2 Days",
    isFlashDeal: true,
    isBestSeller: true,
    isTrending: true,
    specifications: {
      "Flex": "Stiff",
      "Frame": "HM Graphite / M40X",
      "Weight": "83g"
    },
    highlights: [
      "Razor Frame design for extreme speed"
    ]
  },
  {
    id: "prod-112",
    title: "Garmin Forerunner 965 AMOLED GPS Running Smartwatch",
    brand: "Garmin",
    category: "sports",
    description: "Train brilliantly with a colorful 1.4-inch AMOLED display, premium titanium bezel, and full-color built-in mapping.",
    price: 67490,
    originalPrice: 74990,
    discount: 10,
    rating: 4.9,
    reviewCount: 410,
    images: [
      "https://images.unsplash.com/photo-1510017803434-a899398421b3?w=800&q=80"
    ],
    colors: ["Black / Amp Yellow"],
    sizes: ["47mm"],
    stock: 14,
    deliveryDate: "Tomorrow by 12 PM",
    isFlashDeal: false,
    isBestSeller: true,
    isTrending: true,
    specifications: {
      "Display": "1.4-inch AMOLED Always-On",
      "Battery Life": "Up to 23 days in smartwatch mode"
    },
    highlights: [
      "Built-in Full-Color TopoMaps"
    ]
  },
  {
    id: "prod-113",
    title: "Dell XPS 13 Touch Laptop (Intel i7, 16GB RAM)",
    brand: "Dell",
    category: "laptops",
    description: "Immerse yourself in 4K+ InfinityEdge display technology. Machined aluminum enclosure with carbon fiber palm rest.",
    price: 114990,
    originalPrice: 139990,
    discount: 18,
    rating: 4.6,
    reviewCount: 920,
    images: [
      "https://images.unsplash.com/photo-1593642632823-8f785ba67e45?w=800&q=80"
    ],
    colors: ["Platinum Silver"],
    sizes: ["16GB RAM / 512GB SSD"],
    stock: 15,
    deliveryDate: "Tomorrow by 2 PM",
    isFlashDeal: false,
    isBestSeller: false,
    isTrending: true,
    specifications: {
      "Processor": "Intel Core i7 13th Gen",
      "RAM": "16GB LPDDR5"
    },
    highlights: [
      "Four-sided InfinityEdge display"
    ]
  },
  {
    id: "prod-114",
    title: "Ray-Ban Aviator Classic Polarized Sunglasses",
    brand: "Ray-Ban",
    category: "accessories",
    description: "Currently one of the most iconic sunglass models in the world. Originally designed for U.S. aviators in 1937.",
    price: 9490,
    originalPrice: 11990,
    discount: 21,
    rating: 4.7,
    reviewCount: 2450,
    images: [
      "https://images.unsplash.com/photo-1511499767150-a48a237f0083?w=800&q=80"
    ],
    colors: ["Gold Frame / G-15 Green Lens"],
    sizes: ["Standard 58mm"],
    stock: 60,
    deliveryDate: "Get it in 2 Days",
    isFlashDeal: true,
    isBestSeller: true,
    isTrending: false,
    specifications: {
      "Frame": "Metal Gold Plated",
      "UV": "100% UV400"
    },
    highlights: [
      "100% UV Protection G-15 Lenses"
    ]
  },
  {
    id: "prod-115",
    title: "Philips Digital Air Fryer HD9252 with Touchscreen",
    brand: "Philips",
    category: "home",
    description: "Rapid Air Technology with unique starfish design swirling hot air to create delicious foods that are crispy on the outside.",
    price: 8990,
    originalPrice: 11995,
    discount: 25,
    rating: 4.6,
    reviewCount: 3890,
    images: [
      "https://images.unsplash.com/photo-1584269600464-37b1b58a9fe7?w=800&q=80"
    ],
    colors: ["Black"],
    sizes: ["4.1 Liters"],
    stock: 40,
    deliveryDate: "Tomorrow by 11 AM",
    isFlashDeal: true,
    isBestSeller: true,
    isTrending: true,
    specifications: {
      "Power": "1400 Watts",
      "Capacity": "4.1L (0.8kg)"
    },
    highlights: [
      "90% Less Fat cooking with Rapid Air Tech"
    ]
  },
  {
    id: "prod-116",
    title: "The Psychology of Money by Morgan Housel",
    brand: "HarperCollins",
    category: "books",
    description: "Timeless lessons on wealth, greed, and happiness doing well with money isn't necessarily about what you know.",
    price: 349,
    originalPrice: 499,
    discount: 30,
    rating: 4.8,
    reviewCount: 22100,
    images: [
      "https://images.unsplash.com/photo-1592496001020-d31bd830651f?w=800&q=80"
    ],
    colors: ["Paperback"],
    sizes: ["Standard"],
    stock: 200,
    deliveryDate: "Tomorrow by 10 AM",
    isFlashDeal: false,
    isBestSeller: true,
    isTrending: true,
    specifications: {
      "Author": "Morgan Housel",
      "Pages": "252 Pages"
    },
    highlights: [
      "Over 5 Million copies sold"
    ]
  }
];
