export const products = [
  // Electronics (1 - 6)
  {
    id: 'prod-101',
    name: 'boAt Airdopes 141 ANC TWS Earbuds',
    slug: 'boat-airdopes-141-anc',
    category: 'Electronics',
    categoryId: 'cat-1',
    brand: 'boAt',
    price: 1499,
    originalPrice: 4490,
    discount: 67,
    rating: 4.3,
    reviewCount: 12450,
    stock: 150,
    stockStatus: 'In Stock',
    featured: true,
    bestSeller: true,
    newArrival: false,
    images: [
      'https://images.unsplash.com/photo-1590658268037-6bf12165a8df?w=600&q=80',
      'https://images.unsplash.com/photo-1572536147248-ac59a8abfa4b?w=600&q=80',
      'https://images.unsplash.com/photo-1546435770-a3e426bf472b?w=600&q=80'
    ],
    description: 'Enjoy crystal clear audio with Active Noise Cancellation (up to 32dB), 42 Hours battery playback, BEAST mode for gaming, and ENx Technology for crisp voice calls.',
    specifications: {
      'Bluetooth Version': 'v5.3',
      'Playtime': 'Up to 42 Hours',
      'Noise Cancellation': '32dB ANC',
      'Water Resistance': 'IPX5',
      'Warranty': '1 Year Brand Warranty'
    },
    seller: 'boAt Official Store',
    createdAt: '2026-01-10'
  },
  {
    id: 'prod-102',
    name: 'Noise ColorFit Pulse 2 Max Smartwatch',
    slug: 'noise-colorfit-pulse-2-max',
    category: 'Electronics',
    categoryId: 'cat-1',
    brand: 'Noise',
    price: 1299,
    originalPrice: 5999,
    discount: 78,
    rating: 4.2,
    reviewCount: 8930,
    stock: 45,
    stockStatus: 'Low Stock',
    featured: true,
    bestSeller: true,
    newArrival: false,
    images: [
      'https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=600&q=80',
      'https://images.unsplash.com/photo-1508685096489-7aacd43bd3b1?w=600&q=80'
    ],
    description: '1.85-inch TFT Display with 550 nits brightness, Bluetooth calling, 100+ sports modes, Tru Sync feature, and 10 days battery life.',
    specifications: {
      'Display Size': '1.85 Inches',
      'Battery Life': '10 Days',
      'Calling': 'Bluetooth Calling enabled',
      'Sensors': 'SpO2, Heart Rate, Sleep Tracker',
      'Warranty': '1 Year Warranty'
    },
    seller: 'Noise Tech Labs',
    createdAt: '2026-01-15'
  },
  {
    id: 'prod-103',
    name: 'HP Pavilion 15 Core i5 13th Gen Laptop',
    slug: 'hp-pavilion-15-i5-13gen',
    category: 'Electronics',
    categoryId: 'cat-1',
    brand: 'HP',
    price: 64990,
    originalPrice: 79999,
    discount: 19,
    rating: 4.6,
    reviewCount: 3420,
    stock: 22,
    stockStatus: 'In Stock',
    featured: true,
    bestSeller: false,
    newArrival: true,
    images: [
      'https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=600&q=80',
      'https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=600&q=80'
    ],
    description: 'Intel Core i5-1335U, 16GB DDR4 RAM, 512GB NVMe SSD, 15.6" FHD IPS display, Backlit Keyboard, Audio by B&O, Windows 11 + MS Office 2021.',
    specifications: {
      'Processor': 'Intel Core i5-1335U 13th Gen',
      'RAM': '16 GB DDR4',
      'Storage': '512 GB SSD',
      'Display': '15.6 Inch Full HD IPS',
      'OS': 'Windows 11 Home'
    },
    seller: 'Appario Retail',
    createdAt: '2026-02-01'
  },
  {
    id: 'prod-104',
    name: 'OnePlus Nord CE 4 5G (Dark Chrome, 8GB RAM, 128GB)',
    slug: 'oneplus-nord-ce-4-5g',
    category: 'Electronics',
    categoryId: 'cat-1',
    brand: 'OnePlus',
    price: 24999,
    originalPrice: 27999,
    discount: 11,
    rating: 4.4,
    reviewCount: 9150,
    stock: 80,
    stockStatus: 'In Stock',
    featured: true,
    bestSeller: true,
    newArrival: true,
    images: [
      'https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=600&q=80',
      'https://images.unsplash.com/photo-1598327105666-5b89351aff97?w=600&q=80'
    ],
    description: 'Snapdragon 7 Gen 3, 100W SUPERVOOC Fast Charging, 5500mAh Battery, 50MP Sony LYT-600 Camera with OIS, 120Hz AMOLED Display.',
    specifications: {
      'Processor': 'Snapdragon 7 Gen 3',
      'Camera': '50MP OIS + 8MP Ultrawide',
      'Battery': '5500 mAh (100W Fast Charge)',
      'RAM/ROM': '8GB RAM | 128GB Storage'
    },
    seller: 'OnePlus Official',
    createdAt: '2026-02-05'
  },
  {
    id: 'prod-105',
    name: 'Sony WH-1000XM5 Wireless Headphones',
    slug: 'sony-wh-1000xm5-wireless-headphones',
    category: 'Electronics',
    categoryId: 'cat-1',
    brand: 'Sony',
    price: 29990,
    originalPrice: 34990,
    discount: 14,
    rating: 4.8,
    reviewCount: 5120,
    stock: 12,
    stockStatus: 'Low Stock',
    featured: false,
    bestSeller: false,
    newArrival: true,
    images: [
      'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=600&q=80',
      'https://images.unsplash.com/photo-1484704849700-f032a568e944?w=600&q=80'
    ],
    description: 'Industry-leading noise canceling with two processors and 8 microphones. 30-hour battery life, touch sensor controls, and ultra-comfortable lightweight design.',
    specifications: {
      'Noise Cancellation': 'Industry Leading Auto NC',
      'Battery Life': '30 Hours',
      'Driver Unit': '30mm',
      'Weight': '250g'
    },
    seller: 'Electronics Bazaar',
    createdAt: '2026-02-10'
  },
  {
    id: 'prod-106',
    name: 'Mi Smart TV 43 Inch 4K Ultra HD Google TV',
    slug: 'mi-smart-tv-43-4k-google-tv',
    category: 'Electronics',
    categoryId: 'cat-1',
    brand: 'Xiaomi',
    price: 26999,
    originalPrice: 42999,
    discount: 37,
    rating: 4.3,
    reviewCount: 15400,
    stock: 0,
    stockStatus: 'Out of Stock',
    featured: false,
    bestSeller: true,
    newArrival: false,
    images: [
      'https://images.unsplash.com/photo-1593784991095-a205069470b6?w=600&q=80'
    ],
    description: '4K Dolby Vision, 30W Dolby Audio, Google TV OS with PatchWall, Quad Core Processor, Dual Band Wi-Fi.',
    specifications: {
      'Screen Size': '43 Inches',
      'Resolution': '4K Ultra HD (3840x2160)',
      'Sound Output': '30 Watts Dolby Audio',
      'Smart TV OS': 'Google TV'
    },
    seller: 'Appario Retail',
    createdAt: '2026-01-05'
  },

  // Fashion (7 - 12)
  {
    id: 'prod-107',
    name: 'Allen Solly Men\'s Regular Fit Cotton Shirt',
    slug: 'allen-solly-mens-cotton-shirt',
    category: 'Fashion',
    categoryId: 'cat-2',
    brand: 'Allen Solly',
    price: 999,
    originalPrice: 2299,
    discount: 57,
    rating: 4.3,
    reviewCount: 4320,
    stock: 95,
    stockStatus: 'In Stock',
    featured: true,
    bestSeller: true,
    newArrival: false,
    images: [
      'https://images.unsplash.com/photo-1602810318383-e386cc2a3ccf?w=600&q=80',
      'https://images.unsplash.com/photo-1598033129183-c4f50c736f10?w=600&q=80'
    ],
    description: 'Premium 100% Breathable Cotton formal shirt. Perfect for office wear, casual evening outings, and business meetings.',
    specifications: {
      'Material': '100% Cotton',
      'Fit Type': 'Regular Fit',
      'Sleeve Type': 'Long Sleeve',
      'Care Instructions': 'Machine Wash Warm'
    },
    seller: 'Aditya Birla Fashion',
    createdAt: '2026-01-20'
  },
  {
    id: 'prod-108',
    name: 'Biba Women\'s Printed Anarkali Kurta Set with Dupatta',
    slug: 'biba-womens-printed-anarkali-kurta-set',
    category: 'Fashion',
    categoryId: 'cat-2',
    brand: 'Biba',
    price: 2499,
    originalPrice: 5995,
    discount: 58,
    rating: 4.5,
    reviewCount: 2840,
    stock: 40,
    stockStatus: 'In Stock',
    featured: true,
    bestSeller: true,
    newArrival: true,
    images: [
      'https://images.unsplash.com/photo-1610030469983-98e550d6193c?w=600&q=80',
      'https://images.unsplash.com/photo-1583391733956-3750e0ff4e8b?w=600&q=80'
    ],
    description: 'Traditional Ethnic Floral Printed Cotton Anarkali suit set with matching pants and net dupatta. Graceful and comfortable for festivities.',
    specifications: {
      'Fabric': '100% Premium Cotton',
      'Neck Style': 'V-Neck',
      'Occasion': 'Festive / Casual Ethnic',
      'Included Components': 'Kurta, Palazzo, Dupatta'
    },
    seller: 'Biba Apparels',
    createdAt: '2026-02-02'
  },
  {
    id: 'prod-109',
    name: 'Levi\'s 511 Men Slim Fit Stretchable Jeans',
    slug: 'levis-511-slim-fit-jeans',
    category: 'Fashion',
    categoryId: 'cat-2',
    brand: 'Levi\'s',
    price: 1899,
    originalPrice: 3999,
    discount: 53,
    rating: 4.4,
    reviewCount: 6710,
    stock: 60,
    stockStatus: 'In Stock',
    featured: false,
    bestSeller: true,
    newArrival: false,
    images: [
      'https://images.unsplash.com/photo-1541099649105-f69ad21f3246?w=600&q=80',
      'https://images.unsplash.com/photo-1582418702059-97ebafb35d09?w=600&q=80'
    ],
    description: 'Classic 5-pocket denim with stretch comfort. Modern slim fit cut through hip and thigh with a slim leg.',
    specifications: {
      'Fit': 'Slim Fit',
      'Fabric': '98% Cotton, 2% Elastane',
      'Closure': 'Zip Fly with Button Closure'
    },
    seller: 'Levi Strauss India',
    createdAt: '2026-01-18'
  },
  {
    id: 'prod-110',
    name: 'Puma Unisex Smash v2 Leather Sneakers',
    slug: 'puma-smash-v2-leather-sneakers',
    category: 'Fashion',
    categoryId: 'cat-2',
    brand: 'Puma',
    price: 2199,
    originalPrice: 4999,
    discount: 56,
    rating: 4.3,
    reviewCount: 7890,
    stock: 5,
    stockStatus: 'Low Stock',
    featured: true,
    bestSeller: false,
    newArrival: true,
    images: [
      'https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=600&q=80',
      'https://images.unsplash.com/photo-1600185365926-3a2ce3cdb9eb?w=600&q=80'
    ],
    description: 'Soft leather upper with iconic Puma formstrip design. Rubber outsole for traction and softfoam comfort insoles.',
    specifications: {
      'Outer Material': 'Genuine Leather',
      'Sole Material': 'Durable Rubber',
      'Fastening': 'Lace-Up'
    },
    seller: 'Puma Sports India',
    createdAt: '2026-02-12'
  },
  {
    id: 'prod-111',
    name: 'Ray-Ban Aviator Classic Unisex Sunglasses',
    slug: 'ray-ban-aviator-classic-sunglasses',
    category: 'Fashion',
    categoryId: 'cat-2',
    brand: 'Ray-Ban',
    price: 6790,
    originalPrice: 8590,
    discount: 21,
    rating: 4.7,
    reviewCount: 1890,
    stock: 18,
    stockStatus: 'In Stock',
    featured: false,
    bestSeller: false,
    newArrival: false,
    images: [
      'https://images.unsplash.com/photo-1572635196237-14b3f281503f?w=600&q=80'
    ],
    description: 'Iconic teardrop shape original Aviator with gold metal frame and G-15 green polarized lenses. 100% UV Protection.',
    specifications: {
      'Frame Material': 'Metal Gold',
      'Lens Color': 'G-15 Green Polarized',
      'UV Protection': '100% UV400'
    },
    seller: 'Luxottica Retail',
    createdAt: '2026-01-11'
  },
  {
    id: 'prod-112',
    name: 'Fastrack Casual Analog Watch for Men',
    slug: 'fastrack-casual-analog-watch',
    category: 'Fashion',
    categoryId: 'cat-2',
    brand: 'Fastrack',
    price: 1395,
    originalPrice: 1995,
    discount: 30,
    rating: 4.2,
    reviewCount: 5410,
    stock: 85,
    stockStatus: 'In Stock',
    featured: false,
    bestSeller: false,
    newArrival: false,
    images: [
      'https://images.unsplash.com/photo-1524805444758-089113d48a6d?w=600&q=80'
    ],
    description: 'Sporty brown leather strap with sleek black dial. Water resistant up to 50 meters and 2-year warranty.',
    specifications: {
      'Strap Material': 'Genuine Leather',
      'Dial Color': 'Black',
      'Water Resistance': '50M'
    },
    seller: 'Titan Company Ltd',
    createdAt: '2026-01-08'
  },

  // Home & Kitchen (13 - 18)
  {
    id: 'prod-113',
    name: 'Prestige Iris 750W Mixer Grinder with 4 Jars',
    slug: 'prestige-iris-750w-mixer-grinder',
    category: 'Home & Kitchen',
    categoryId: 'cat-3',
    brand: 'Prestige',
    price: 3299,
    originalPrice: 6295,
    discount: 48,
    rating: 4.4,
    reviewCount: 18450,
    stock: 70,
    stockStatus: 'In Stock',
    featured: true,
    bestSeller: true,
    newArrival: false,
    images: [
      'https://images.unsplash.com/photo-1578643463396-0997cb5328c1?w=600&q=80',
      'https://images.unsplash.com/photo-1556911220-e15b29be8c8f?w=600&q=80'
    ],
    description: '750 Watt heavy-duty motor, 3 Stainless Steel Jars + 1 Juicer Jar, sturdy handles, and overload protection switch.',
    specifications: {
      'Motor Power': '750 Watts',
      'Jars Included': '3 SS Jars + 1 Transparent Juicer Jar',
      'Speed Control': '3 Speed Control with Pulse',
      'Warranty': '2 Years Motor Warranty'
    },
    seller: 'TTK Prestige India',
    createdAt: '2026-01-14'
  },
  {
    id: 'prod-114',
    name: 'Pigeon by Stovekraft 3 Litre Outer Lid Pressure Cooker',
    slug: 'pigeon-3l-pressure-cooker',
    category: 'Home & Kitchen',
    categoryId: 'cat-3',
    brand: 'Pigeon',
    price: 799,
    originalPrice: 1595,
    discount: 50,
    rating: 4.2,
    reviewCount: 22100,
    stock: 110,
    stockStatus: 'In Stock',
    featured: false,
    bestSeller: true,
    newArrival: false,
    images: [
      'https://images.unsplash.com/photo-1584992236310-6edddc08acff?w=600&q=80'
    ],
    description: 'High grade virgin aluminium body with heat-resistant Bakelite handles. Induction & Gas stove compatible.',
    specifications: {
      'Capacity': '3 Litres',
      'Material': 'Virgin Aluminium',
      'Stove Compatibility': 'Gas & Induction'
    },
    seller: 'Stovekraft Official',
    createdAt: '2026-01-02'
  },
  {
    id: 'prod-115',
    name: 'Solimo 100% Cotton 144 TC Floral Bedsheet with 2 Pillow Covers',
    slug: 'solimo-cotton-double-bedsheet',
    category: 'Home & Kitchen',
    categoryId: 'cat-3',
    brand: 'Solimo',
    price: 699,
    originalPrice: 1600,
    discount: 56,
    rating: 4.3,
    reviewCount: 9400,
    stock: 55,
    stockStatus: 'In Stock',
    featured: false,
    bestSeller: false,
    newArrival: true,
    images: [
      'https://images.unsplash.com/photo-1616594039964-ae9021a400a0?w=600&q=80'
    ],
    description: 'Super soft King size double bedsheet made of 100% breathable cotton. Fade resistant colors and long lasting durability.',
    specifications: {
      'Thread Count': '144 TC',
      'Dimensions': '230 x 250 cm',
      'Fabric': '100% Cotton'
    },
    seller: 'Solimo Retails',
    createdAt: '2026-02-14'
  },
  {
    id: 'prod-116',
    name: 'Kent Grand Plus 9-Litre RO + UV + UF Water Purifier',
    slug: 'kent-grand-plus-ro-water-purifier',
    category: 'Home & Kitchen',
    categoryId: 'cat-3',
    brand: 'Kent',
    price: 14999,
    originalPrice: 20000,
    discount: 25,
    rating: 4.5,
    reviewCount: 11200,
    stock: 14,
    stockStatus: 'In Stock',
    featured: true,
    bestSeller: false,
    newArrival: false,
    images: [
      'https://images.unsplash.com/photo-1585837575652-267c041d77d4?w=600&q=80',
      'https://images.unsplash.com/photo-1527661591475-527312dd65f5?w=600&q=80'
    ],
    description: 'Multiple purification process RO+UV+UF+TDS Control. Zero Water Wastage Technology and 9L storage tank.',
    specifications: {
      'Purification Technology': 'RO + UV + UF + TDS Control',
      'Storage Capacity': '9 Litres',
      'Purification Rate': '20 L/hr'
    },
    seller: 'Kent RO Systems',
    createdAt: '2026-01-19'
  },
  {
    id: 'prod-117',
    name: 'Wipro Smart LED Bulb 12W 16 Million Colors',
    slug: 'wipro-smart-led-bulb-12w',
    category: 'Home & Kitchen',
    categoryId: 'cat-3',
    brand: 'Wipro',
    price: 599,
    originalPrice: 1490,
    discount: 60,
    rating: 4.1,
    reviewCount: 4890,
    stock: 200,
    stockStatus: 'In Stock',
    featured: false,
    bestSeller: false,
    newArrival: true,
    images: [
      'https://images.unsplash.com/photo-1550985616-10810253b84d?w=600&q=80'
    ],
    description: 'Wi-Fi enabled smart RGB bulb compatible with Amazon Alexa and Google Assistant. Dimmable and scheduling features via Wipro Next App.',
    specifications: {
      'Wattage': '12 Watts',
      'Cap Type': 'B22',
      'Connectivity': 'Wi-Fi 2.4GHz'
    },
    seller: 'Wipro Lighting',
    createdAt: '2026-02-10'
  },
  {
    id: 'prod-118',
    name: 'Milton Thermosteel Flip N Sip 1000ml Flask',
    slug: 'milton-thermosteel-1000ml-flask',
    category: 'Home & Kitchen',
    categoryId: 'cat-3',
    brand: 'Milton',
    price: 899,
    originalPrice: 1290,
    discount: 30,
    rating: 4.6,
    reviewCount: 16500,
    stock: 0,
    stockStatus: 'Out of Stock',
    featured: false,
    bestSeller: true,
    newArrival: false,
    images: [
      'https://images.unsplash.com/photo-1602143407151-7111542de6e8?w=600&q=80'
    ],
    description: 'Double walled vacuum insulated 304 Stainless Steel bottle. Keeps beverages hot or cold for 24 hours.',
    specifications: {
      'Capacity': '1000 ml',
      'Material': '18/8 Stainless Steel',
      'Insulation': '24 Hours Hot/Cold'
    },
    seller: 'Hamilton Housewares',
    createdAt: '2026-01-04'
  },

  // Beauty & Personal Care (19 - 24)
  {
    id: 'prod-119',
    name: 'Mamaearth Vitamin C Face Wash with Turmeric 150ml',
    slug: 'mamaearth-vitamin-c-face-wash',
    category: 'Beauty & Personal Care',
    categoryId: 'cat-4',
    brand: 'Mamaearth',
    price: 349,
    originalPrice: 399,
    discount: 13,
    rating: 4.4,
    reviewCount: 28900,
    stock: 300,
    stockStatus: 'In Stock',
    featured: true,
    bestSeller: true,
    newArrival: false,
    images: [
      'https://images.unsplash.com/photo-1556228720-195a672e8a03?w=600&q=80',
      'https://images.unsplash.com/photo-1571781926291-c477ebfd024b?w=600&q=80'
    ],
    description: 'Dermatologically tested face wash infused with natural Vitamin C and Turmeric for skin illumination and gentle cleansing.',
    specifications: {
      'Skin Type': 'All Skin Types',
      'Volume': '150 ml',
      'Key Ingredients': 'Vitamin C, Turmeric, Aloe Vera',
      'Free From': 'Parabens, SLS, Silicones'
    },
    seller: 'Honasa Consumer Ltd',
    createdAt: '2026-01-05'
  },
  {
    id: 'prod-120',
    name: 'The Derma Co 10% Niacinamide Face Serum 30ml',
    slug: 'the-derma-co-10-percent-niacinamide-serum',
    category: 'Beauty & Personal Care',
    categoryId: 'cat-4',
    brand: 'The Derma Co',
    price: 499,
    originalPrice: 599,
    discount: 17,
    rating: 4.5,
    reviewCount: 14200,
    stock: 120,
    stockStatus: 'In Stock',
    featured: true,
    bestSeller: true,
    newArrival: true,
    images: [
      'https://images.unsplash.com/photo-1620916566398-39f1143ab7be?w=600&q=80'
    ],
    description: 'Formulated with Niacinamide and Zinc to reduce acne marks, clear dark spots, control sebum and improve skin texture.',
    specifications: {
      'Active Ingredients': '10% Niacinamide + Zinc PCA',
      'Volume': '30 ml',
      'Target Concern': 'Acne Marks, Dark Spots'
    },
    seller: 'Derma Co Store',
    createdAt: '2026-02-04'
  },
  {
    id: 'prod-121',
    name: 'Philips BHD350/10 2100W Hair Dryer',
    slug: 'philips-bhd350-2100w-hair-dryer',
    category: 'Beauty & Personal Care',
    categoryId: 'cat-4',
    brand: 'Philips',
    price: 1999,
    originalPrice: 2495,
    discount: 20,
    rating: 4.6,
    reviewCount: 7650,
    stock: 45,
    stockStatus: 'In Stock',
    featured: false,
    bestSeller: false,
    newArrival: false,
    images: [
      'https://images.unsplash.com/photo-1522337360788-8b13dee7a37e?w=600&q=80'
    ],
    description: 'ThermoProtect attachment uniquely mixes warm and cool air for everyday hair care. 6 heat and speed settings with Ionic conditioning.',
    specifications: {
      'Wattage': '2100 Watts',
      'Settings': '6 Heat/Speed Combination',
      'Cord Length': '1.8 Meters'
    },
    seller: 'Philips Personal Care',
    createdAt: '2026-01-16'
  },
  {
    id: 'prod-122',
    name: 'Nivea Soft Light Moisturiser 300ml',
    slug: 'nivea-soft-light-moisturiser-300ml',
    category: 'Beauty & Personal Care',
    categoryId: 'cat-4',
    brand: 'Nivea',
    price: 299,
    originalPrice: 425,
    discount: 30,
    rating: 4.6,
    reviewCount: 31200,
    stock: 250,
    stockStatus: 'In Stock',
    featured: false,
    bestSeller: true,
    newArrival: false,
    images: [
      'https://images.unsplash.com/photo-1598440947619-2c35fc9aa908?w=600&q=80',
      'https://images.unsplash.com/photo-1616683693504-3ea7e9ad6fec?w=600&q=80'
    ],
    description: 'Non-greasy, fast-absorbing refreshing moisturising cream with Jojoba Oil and Vitamin E for soft skin.',
    specifications: {
      'Volume': '300 ml',
      'Key Ingredients': 'Vitamin E, Jojoba Oil'
    },
    seller: 'Beiersdorf India',
    createdAt: '2026-01-01'
  },
  {
    id: 'prod-123',
    name: 'Beardo Godfather Beard Oil 30ml',
    slug: 'beardo-godfather-beard-oil-30ml',
    category: 'Beauty & Personal Care',
    categoryId: 'cat-4',
    brand: 'Beardo',
    price: 249,
    originalPrice: 350,
    discount: 29,
    rating: 4.2,
    reviewCount: 15300,
    stock: 88,
    stockStatus: 'In Stock',
    featured: false,
    bestSeller: false,
    newArrival: false,
    images: [
      'https://images.unsplash.com/photo-1621607512214-68297480165e?w=600&q=80'
    ],
    description: 'Nourishes and softens beard hair, prevents itchiness, and gives a shiny non-sticky finish with Aloe Vera and Almond Oil extracts.',
    specifications: {
      'Volume': '30 ml',
      'Ingredients': 'Almond Oil, Aloe Vera, Castor Oil'
    },
    seller: 'Beardo Grooming',
    createdAt: '2026-01-22'
  },
  {
    id: 'prod-124',
    name: 'Maybelline New York Colossal Mascara Black',
    slug: 'maybelline-colossal-mascara',
    category: 'Beauty & Personal Care',
    categoryId: 'cat-4',
    brand: 'Maybelline',
    price: 339,
    originalPrice: 499,
    discount: 32,
    rating: 4.5,
    reviewCount: 21400,
    stock: 3,
    stockStatus: 'Low Stock',
    featured: false,
    bestSeller: true,
    newArrival: false,
    images: [
      'https://images.unsplash.com/photo-1631729371254-42c2892f0e6e?w=600&q=80'
    ],
    description: 'Instant 2x volume without clumping. Waterproof formula infused with collagen for dramatic eye makeup.',
    specifications: {
      'Shade': 'Washable Black',
      'Volume': '10 ml',
      'Waterproof': 'Yes'
    },
    seller: 'L\'Oreal India',
    createdAt: '2026-01-17'
  },

  // Sports & Fitness (25 - 28)
  {
    id: 'prod-125',
    name: 'Boldfit Anti Slip Yoga Mat 6mm for Men & Women',
    slug: 'boldfit-yoga-mat-6mm',
    category: 'Sports & Fitness',
    categoryId: 'cat-5',
    brand: 'Boldfit',
    price: 699,
    originalPrice: 1499,
    discount: 53,
    rating: 4.4,
    reviewCount: 9800,
    stock: 90,
    stockStatus: 'In Stock',
    featured: true,
    bestSeller: true,
    newArrival: false,
    images: [
      'https://images.unsplash.com/photo-1545205597-3d9d02c29597?w=600&q=80'
    ],
    description: 'Extra thick 6mm eco-friendly TPE yoga mat with alignment lines, sweat resistance, and carrying strap included.',
    specifications: {
      'Thickness': '6 mm',
      'Material': 'TPE Eco-Friendly',
      'Includes': 'Carrying Strap'
    },
    seller: 'Boldfit Official',
    createdAt: '2026-01-13'
  },
  {
    id: 'prod-126',
    name: 'Cosco Light Aluminium Badminton Racquet Pair',
    slug: 'cosco-badminton-racquet-pair',
    category: 'Sports & Fitness',
    categoryId: 'cat-5',
    brand: 'Cosco',
    price: 899,
    originalPrice: 1599,
    discount: 44,
    rating: 4.3,
    reviewCount: 5200,
    stock: 35,
    stockStatus: 'In Stock',
    featured: false,
    bestSeller: false,
    newArrival: true,
    images: [
      'https://images.unsplash.com/photo-1626224583764-f87db24ac4ea?w=600&q=80'
    ],
    description: 'Lightweight aluminium frame with steel shaft. Package includes 2 badminton racquets and 1 full cover.',
    specifications: {
      'Weight': '95-98g',
      'Frame Material': 'Aluminium',
      'Includes': 'Full Cover Case'
    },
    seller: 'Cosco Sports India',
    createdAt: '2026-02-07'
  },
  {
    id: 'prod-127',
    name: 'Nivia Storm Football Size 5',
    slug: 'nivia-storm-football-size-5',
    category: 'Sports & Fitness',
    categoryId: 'cat-5',
    brand: 'Nivia',
    price: 499,
    originalPrice: 850,
    discount: 41,
    rating: 4.2,
    reviewCount: 6400,
    stock: 65,
    stockStatus: 'In Stock',
    featured: false,
    bestSeller: true,
    newArrival: false,
    images: [
      'https://images.unsplash.com/photo-1579952363873-27f3bade9f55?w=600&q=80'
    ],
    description: '32-panel rubber synthetic football designed for hard and rough ground training sessions.',
    specifications: {
      'Size': 'Size 5',
      'Material': 'Rubberized Synthetic',
      'Ideal For': 'Hard Ground / Grass'
    },
    seller: 'Freewill Sports Pvt Ltd',
    createdAt: '2026-01-28'
  },
  {
    id: 'prod-128',
    name: 'Kobo Rubber Hex Dumbbell Set 10KG (5KG x 2)',
    slug: 'kobo-hex-dumbbell-set-10kg',
    category: 'Sports & Fitness',
    categoryId: 'cat-5',
    brand: 'Kobo',
    price: 1899,
    originalPrice: 3200,
    discount: 40,
    rating: 4.6,
    reviewCount: 3100,
    stock: 15,
    stockStatus: 'In Stock',
    featured: true,
    bestSeller: false,
    newArrival: false,
    images: [
      'https://images.unsplash.com/photo-1584735935682-2f2b69dff9d2?w=600&q=80'
    ],
    description: 'Heavy duty hex dumbbells with rubber coating and ergonomic knurled chrome steel handles.',
    specifications: {
      'Weight': '5 KG x 2 = 10 KG',
      'Shape': 'Hexagonal Anti-roll Design',
      'Grip': 'Chrome Knurled'
    },
    seller: 'Kobo Fitness Essentials',
    createdAt: '2026-01-19'
  },

  // Books & Stationery (29 - 31)
  {
    id: 'prod-129',
    name: 'Atomic Habits by James Clear (Hardcover Edition)',
    slug: 'atomic-habits-james-clear',
    category: 'Books & Stationery',
    categoryId: 'cat-6',
    brand: 'Penguin Random House',
    price: 499,
    originalPrice: 799,
    discount: 37,
    rating: 4.9,
    reviewCount: 45800,
    stock: 500,
    stockStatus: 'In Stock',
    featured: true,
    bestSeller: true,
    newArrival: false,
    images: [
      'https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=600&q=80'
    ],
    description: 'An Easy & Proven Way to Build Good Habits & Break Bad Ones. Over 10 million copies sold worldwide.',
    specifications: {
      'Author': 'James Clear',
      'Binding': 'Paperback / Hardcover',
      'Pages': '320 Pages',
      'Language': 'English'
    },
    seller: 'BookWorm India',
    createdAt: '2026-01-01'
  },
  {
    id: 'prod-130',
    name: 'Classmate Octane Gel Pen (Pack of 10 Blue Pens)',
    slug: 'classmate-octane-gel-pen-pack-10',
    category: 'Books & Stationery',
    categoryId: 'cat-6',
    brand: 'Classmate',
    price: 100,
    originalPrice: 120,
    discount: 17,
    rating: 4.6,
    reviewCount: 8900,
    stock: 400,
    stockStatus: 'In Stock',
    featured: false,
    bestSeller: false,
    newArrival: false,
    images: [
      'https://images.unsplash.com/photo-1585776245991-cf89dd7fc73a?w=600&q=80',
      'https://images.unsplash.com/photo-1569683795645-b62e50fbf103?w=600&q=80'
    ],
    description: 'Smooth Japanese gel ink technology with comfortable rubber grip. Ideal for long exam writing.',
    specifications: {
      'Ink Color': 'Blue',
      'Quantity': '10 Pens',
      'Tip Size': '0.5 mm'
    },
    seller: 'ITC Limited',
    createdAt: '2026-01-15'
  },
  {
    id: 'prod-131',
    name: 'Psychology of Money by Morgan Housel',
    slug: 'psychology-of-money-morgan-housel',
    category: 'Books & Stationery',
    categoryId: 'cat-6',
    brand: 'Jaico Publishing',
    price: 299,
    originalPrice: 399,
    discount: 25,
    rating: 4.8,
    reviewCount: 38200,
    stock: 210,
    stockStatus: 'In Stock',
    featured: true,
    bestSeller: true,
    newArrival: false,
    images: [
      'https://images.unsplash.com/photo-1512820790803-83ca734da794?w=600&q=80'
    ],
    description: 'Timeless lessons on wealth, greed, and happiness doing well with money isn’t necessarily about what you know. It’s about how you behave.',
    specifications: {
      'Author': 'Morgan Housel',
      'Pages': '252 Pages',
      'Publisher': 'Jaico Publishing House'
    },
    seller: 'BookWorm India',
    createdAt: '2026-01-10'
  },

  // Grocery & Gourmet (32 - 34)
  {
    id: 'prod-132',
    name: 'Tata Sampann Unpolished Toor Dal / Arhar Dal 1kg',
    slug: 'tata-sampann-unpolished-toor-dal-1kg',
    category: 'Grocery & Gourmet',
    categoryId: 'cat-7',
    brand: 'Tata Sampann',
    price: 165,
    originalPrice: 195,
    discount: 15,
    rating: 4.6,
    reviewCount: 14500,
    stock: 350,
    stockStatus: 'In Stock',
    featured: false,
    bestSeller: true,
    newArrival: false,
    images: [
      'https://images.unsplash.com/photo-1586201375761-83865001e31c?w=600&q=80'
    ],
    description: 'Rich in protein unpolished toor dal sourced directly from farms. No artificial polishing or chemicals.',
    specifications: {
      'Weight': '1 kg',
      'Dietary Preference': '100% Vegetarian',
      'Origin': 'India'
    },
    seller: 'Tata Consumer Products',
    createdAt: '2026-01-03'
  },
  {
    id: 'prod-133',
    name: 'Happilo Premium California Almonds 500g Pack',
    slug: 'happilo-premium-california-almonds-500g',
    category: 'Grocery & Gourmet',
    categoryId: 'cat-7',
    brand: 'Happilo',
    price: 449,
    originalPrice: 675,
    discount: 33,
    rating: 4.5,
    reviewCount: 22400,
    stock: 180,
    stockStatus: 'In Stock',
    featured: true,
    bestSeller: true,
    newArrival: true,
    images: [
      'https://images.unsplash.com/photo-1509440159596-0249088772ff?w=600&q=80',
      'https://images.unsplash.com/photo-1563729784474-d77dbb933a9e?w=600&q=80'
    ],
    description: 'Raw, crispy and 100% natural premium California Badam packed in resealable pouch.',
    specifications: {
      'Weight': '500 grams',
      'Key Benefits': 'High Energy & Fiber',
      'Packaging': 'Resealable Zip Lock Bag'
    },
    seller: 'Happilo International',
    createdAt: '2026-02-08'
  },
  {
    id: 'prod-134',
    name: 'Fortune Sunlite Refined Sunflower Oil 5 Litre Jar',
    slug: 'fortune-sunlite-sunflower-oil-5l',
    category: 'Grocery & Gourmet',
    categoryId: 'cat-7',
    brand: 'Fortune',
    price: 685,
    originalPrice: 780,
    discount: 12,
    rating: 4.4,
    reviewCount: 19800,
    stock: 80,
    stockStatus: 'In Stock',
    featured: false,
    bestSeller: false,
    newArrival: false,
    images: [
      'https://images.unsplash.com/photo-1474979266404-7eaacbcd87c5?w=600&q=80'
    ],
    description: 'Light, healthy and easy to digest edible cooking oil fortified with Vitamin A and D.',
    specifications: {
      'Volume': '5 Litres',
      'Oil Type': 'Refined Sunflower Oil'
    },
    seller: 'Adani Wilmar',
    createdAt: '2026-01-12'
  },

  {
    "id": "prod-201",
    "name": "Apple iPad 10th Gen 10.9-inch Wi-Fi",
    "slug": "apple-ipad-10th-gen-10-9-inch-wi-fi",
    "category": "Electronics",
    "categoryId": "cat-1",
    "brand": "Apple",
    "price": 42990,
    "originalPrice": 49900,
    "discount": 14,
    "rating": 4.1,
    "reviewCount": 2387,
    "stock": 125,
    "stockStatus": "In Stock",
    "featured": false,
    "bestSeller": false,
    "newArrival": true,
    "images": [
      "https://images.unsplash.com/photo-1498049794561-7780e7231661?w=500&q=80?w=600&q=80"
    ],
    "description": "Apple iPad 10th Gen 10.9-inch Wi-Fi from Apple, selected for the AutoCart everyday shopping collection with quality, value and reliable performance.",
    "specifications": {
      "Brand": "Apple",
      "Category": "Electronics",
      "Warranty": "1 Year Warranty"
    },
    "seller": "Apple Official Store",
    "createdAt": "2026-03-01"
  },
  {
    "id": "prod-202",
    "name": "JBL Tune 770NC Wireless Headphones",
    "slug": "jbl-tune-770nc-wireless-headphones",
    "category": "Electronics",
    "categoryId": "cat-1",
    "brand": "JBL",
    "price": 4999,
    "originalPrice": 7999,
    "discount": 38,
    "rating": 4.4,
    "reviewCount": 2524,
    "stock": 132,
    "stockStatus": "In Stock",
    "featured": false,
    "bestSeller": false,
    "newArrival": false,
    "images": [
      "https://images.unsplash.com/photo-1498049794561-7780e7231661?w=500&q=80?w=600&q=80"
    ],
    "description": "JBL Tune 770NC Wireless Headphones from JBL, selected for the AutoCart everyday shopping collection with quality, value and reliable performance.",
    "specifications": {
      "Brand": "JBL",
      "Category": "Electronics",
      "Warranty": "1 Year Warranty"
    },
    "seller": "JBL Official Store",
    "createdAt": "2026-03-01"
  },
  {
    "id": "prod-203",
    "name": "Logitech MX Master 3S Wireless Mouse",
    "slug": "logitech-mx-master-3s-wireless-mouse",
    "category": "Electronics",
    "categoryId": "cat-1",
    "brand": "Logitech",
    "price": 6999,
    "originalPrice": 9995,
    "discount": 30,
    "rating": 4.7,
    "reviewCount": 2661,
    "stock": 139,
    "stockStatus": "In Stock",
    "featured": true,
    "bestSeller": false,
    "newArrival": false,
    "images": [
      "https://images.unsplash.com/photo-1498049794561-7780e7231661?w=500&q=80?w=600&q=80"
    ],
    "description": "Logitech MX Master 3S Wireless Mouse from Logitech, selected for the AutoCart everyday shopping collection with quality, value and reliable performance.",
    "specifications": {
      "Brand": "Logitech",
      "Category": "Electronics",
      "Warranty": "1 Year Warranty"
    },
    "seller": "Logitech Official Store",
    "createdAt": "2026-03-01"
  },
  {
    "id": "prod-204",
    "name": "Samsung 24-inch FHD Monitor",
    "slug": "samsung-24-inch-fhd-monitor",
    "category": "Electronics",
    "categoryId": "cat-1",
    "brand": "Samsung",
    "price": 10499,
    "originalPrice": 14999,
    "discount": 30,
    "rating": 4.1,
    "reviewCount": 2798,
    "stock": 146,
    "stockStatus": "In Stock",
    "featured": false,
    "bestSeller": true,
    "newArrival": true,
    "images": [
      "https://images.unsplash.com/photo-1498049794561-7780e7231661?w=500&q=80?w=600&q=80"
    ],
    "description": "Samsung 24-inch FHD Monitor from Samsung, selected for the AutoCart everyday shopping collection with quality, value and reliable performance.",
    "specifications": {
      "Brand": "Samsung",
      "Category": "Electronics",
      "Warranty": "1 Year Warranty"
    },
    "seller": "Samsung Official Store",
    "createdAt": "2026-03-01"
  },
  {
    "id": "prod-205",
    "name": "Canon EOS 200D II DSLR Camera",
    "slug": "canon-eos-200d-ii-dslr-camera",
    "category": "Electronics",
    "categoryId": "cat-1",
    "brand": "Canon",
    "price": 54990,
    "originalPrice": 61995,
    "discount": 11,
    "rating": 4.4,
    "reviewCount": 2935,
    "stock": 23,
    "stockStatus": "Low Stock",
    "featured": false,
    "bestSeller": false,
    "newArrival": false,
    "images": [
      "https://images.unsplash.com/photo-1498049794561-7780e7231661?w=500&q=80?w=600&q=80"
    ],
    "description": "Canon EOS 200D II DSLR Camera from Canon, selected for the AutoCart everyday shopping collection with quality, value and reliable performance.",
    "specifications": {
      "Brand": "Canon",
      "Category": "Electronics",
      "Warranty": "1 Year Warranty"
    },
    "seller": "Canon Official Store",
    "createdAt": "2026-03-01"
  },
  {
    "id": "prod-206",
    "name": "Mi 20000mAh Power Bank",
    "slug": "mi-20000mah-power-bank",
    "category": "Electronics",
    "categoryId": "cat-1",
    "brand": "Xiaomi",
    "price": 1699,
    "originalPrice": 2499,
    "discount": 32,
    "rating": 4.7,
    "reviewCount": 3072,
    "stock": 30,
    "stockStatus": "Low Stock",
    "featured": false,
    "bestSeller": false,
    "newArrival": false,
    "images": [
      "https://images.unsplash.com/photo-1498049794561-7780e7231661?w=500&q=80?w=600&q=80"
    ],
    "description": "Mi 20000mAh Power Bank from Xiaomi, selected for the AutoCart everyday shopping collection with quality, value and reliable performance.",
    "specifications": {
      "Brand": "Xiaomi",
      "Category": "Electronics",
      "Warranty": "1 Year Warranty"
    },
    "seller": "Xiaomi Official Store",
    "createdAt": "2026-03-01"
  },
  {
    "id": "prod-207",
    "name": "Levi’s Men 511 Slim Fit Jeans",
    "slug": "levi-s-men-511-slim-fit-jeans",
    "category": "Fashion",
    "categoryId": "cat-2",
    "brand": "Levi’s",
    "price": 2399,
    "originalPrice": 3999,
    "discount": 40,
    "rating": 4.1,
    "reviewCount": 3209,
    "stock": 37,
    "stockStatus": "In Stock",
    "featured": false,
    "bestSeller": false,
    "newArrival": true,
    "images": [
      "https://images.unsplash.com/photo-1445205170230-053b83016050?w=500&q=80?w=600&q=80"
    ],
    "description": "Levi’s Men 511 Slim Fit Jeans from Levi’s, selected for the AutoCart everyday shopping collection with quality, value and reliable performance.",
    "specifications": {
      "Brand": "Levi’s",
      "Category": "Fashion",
      "Warranty": "Manufacturer Warranty"
    },
    "seller": "Levi’s Official Store",
    "createdAt": "2026-03-01"
  },
  {
    "id": "prod-208",
    "name": "Puma Men’s Running T-Shirt",
    "slug": "puma-men-s-running-t-shirt",
    "category": "Fashion",
    "categoryId": "cat-2",
    "brand": "Puma",
    "price": 1299,
    "originalPrice": 1999,
    "discount": 35,
    "rating": 4.4,
    "reviewCount": 3346,
    "stock": 44,
    "stockStatus": "In Stock",
    "featured": false,
    "bestSeller": true,
    "newArrival": false,
    "images": [
      "https://images.unsplash.com/photo-1445205170230-053b83016050?w=500&q=80?w=600&q=80"
    ],
    "description": "Puma Men’s Running T-Shirt from Puma, selected for the AutoCart everyday shopping collection with quality, value and reliable performance.",
    "specifications": {
      "Brand": "Puma",
      "Category": "Fashion",
      "Warranty": "Manufacturer Warranty"
    },
    "seller": "Puma Official Store",
    "createdAt": "2026-03-01"
  },
  {
    "id": "prod-209",
    "name": "Allen Solly Women’s Casual Shirt",
    "slug": "allen-solly-women-s-casual-shirt",
    "category": "Fashion",
    "categoryId": "cat-2",
    "brand": "Allen Solly",
    "price": 1499,
    "originalPrice": 2499,
    "discount": 40,
    "rating": 4.7,
    "reviewCount": 3483,
    "stock": 51,
    "stockStatus": "In Stock",
    "featured": false,
    "bestSeller": false,
    "newArrival": false,
    "images": [
      "https://images.unsplash.com/photo-1445205170230-053b83016050?w=500&q=80?w=600&q=80"
    ],
    "description": "Allen Solly Women’s Casual Shirt from Allen Solly, selected for the AutoCart everyday shopping collection with quality, value and reliable performance.",
    "specifications": {
      "Brand": "Allen Solly",
      "Category": "Fashion",
      "Warranty": "Manufacturer Warranty"
    },
    "seller": "Allen Solly Official Store",
    "createdAt": "2026-03-01"
  },
  {
    "id": "prod-210",
    "name": "Campus Men’s Running Shoes",
    "slug": "campus-men-s-running-shoes",
    "category": "Fashion",
    "categoryId": "cat-2",
    "brand": "Campus",
    "price": 1799,
    "originalPrice": 2999,
    "discount": 40,
    "rating": 4.1,
    "reviewCount": 3620,
    "stock": 58,
    "stockStatus": "In Stock",
    "featured": true,
    "bestSeller": false,
    "newArrival": true,
    "images": [
      "https://images.unsplash.com/photo-1445205170230-053b83016050?w=500&q=80?w=600&q=80"
    ],
    "description": "Campus Men’s Running Shoes from Campus, selected for the AutoCart everyday shopping collection with quality, value and reliable performance.",
    "specifications": {
      "Brand": "Campus",
      "Category": "Fashion",
      "Warranty": "Manufacturer Warranty"
    },
    "seller": "Campus Official Store",
    "createdAt": "2026-03-01"
  },
  {
    "id": "prod-211",
    "name": "Biba Women’s Printed Kurta",
    "slug": "biba-women-s-printed-kurta",
    "category": "Fashion",
    "categoryId": "cat-2",
    "brand": "Biba",
    "price": 1599,
    "originalPrice": 2799,
    "discount": 43,
    "rating": 4.4,
    "reviewCount": 3757,
    "stock": 65,
    "stockStatus": "In Stock",
    "featured": false,
    "bestSeller": false,
    "newArrival": false,
    "images": [
      "https://images.unsplash.com/photo-1445205170230-053b83016050?w=500&q=80?w=600&q=80"
    ],
    "description": "Biba Women’s Printed Kurta from Biba, selected for the AutoCart everyday shopping collection with quality, value and reliable performance.",
    "specifications": {
      "Brand": "Biba",
      "Category": "Fashion",
      "Warranty": "Manufacturer Warranty"
    },
    "seller": "Biba Official Store",
    "createdAt": "2026-03-01"
  },
  {
    "id": "prod-212",
    "name": "Wildcraft Laptop Backpack 30L",
    "slug": "wildcraft-laptop-backpack-30l",
    "category": "Fashion",
    "categoryId": "cat-2",
    "brand": "Wildcraft",
    "price": 1899,
    "originalPrice": 2999,
    "discount": 37,
    "rating": 4.7,
    "reviewCount": 3894,
    "stock": 72,
    "stockStatus": "In Stock",
    "featured": false,
    "bestSeller": true,
    "newArrival": false,
    "images": [
      "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=600&auto=format&fit=crop&q=80"
    ],
    "description": "Wildcraft Laptop Backpack 30L from Wildcraft, selected for the AutoCart everyday shopping collection with quality, value and reliable performance.",
    "specifications": {
      "Brand": "Wildcraft",
      "Category": "Fashion",
      "Warranty": "Manufacturer Warranty"
    },
    "seller": "Wildcraft Official Store",
    "createdAt": "2026-03-01"
  },
  {
    "id": "prod-213",
    "name": "Prestige Induction Cooktop 1600W",
    "slug": "prestige-induction-cooktop-1600w",
    "category": "Home & Kitchen",
    "categoryId": "cat-3",
    "brand": "Prestige",
    "price": 2299,
    "originalPrice": 3495,
    "discount": 34,
    "rating": 4.1,
    "reviewCount": 4031,
    "stock": 79,
    "stockStatus": "In Stock",
    "featured": false,
    "bestSeller": false,
    "newArrival": true,
    "images": [
      "https://images.unsplash.com/photo-1556911220-e15b29be8c8f?w=500&q=80?w=600&q=80"
    ],
    "description": "Prestige Induction Cooktop 1600W from Prestige, selected for the AutoCart everyday shopping collection with quality, value and reliable performance.",
    "specifications": {
      "Brand": "Prestige",
      "Category": "Home & Kitchen",
      "Warranty": "1 Year Warranty"
    },
    "seller": "Prestige Official Store",
    "createdAt": "2026-03-01"
  },
  {
    "id": "prod-214",
    "name": "Philips Air Fryer 4.1L",
    "slug": "philips-air-fryer-4-1l",
    "category": "Home & Kitchen",
    "categoryId": "cat-3",
    "brand": "Philips",
    "price": 5999,
    "originalPrice": 8995,
    "discount": 33,
    "rating": 4.4,
    "reviewCount": 4168,
    "stock": 86,
    "stockStatus": "In Stock",
    "featured": false,
    "bestSeller": false,
    "newArrival": false,
    "images": [
      "https://images.unsplash.com/photo-1556911220-e15b29be8c8f?w=500&q=80?w=600&q=80"
    ],
    "description": "Philips Air Fryer 4.1L from Philips, selected for the AutoCart everyday shopping collection with quality, value and reliable performance.",
    "specifications": {
      "Brand": "Philips",
      "Category": "Home & Kitchen",
      "Warranty": "1 Year Warranty"
    },
    "seller": "Philips Official Store",
    "createdAt": "2026-03-01"
  },
  {
    "id": "prod-215",
    "name": "Milton Thermosteel Flask 1L",
    "slug": "milton-thermosteel-flask-1l",
    "category": "Home & Kitchen",
    "categoryId": "cat-3",
    "brand": "Milton",
    "price": 899,
    "originalPrice": 1499,
    "discount": 40,
    "rating": 4.7,
    "reviewCount": 4305,
    "stock": 93,
    "stockStatus": "In Stock",
    "featured": false,
    "bestSeller": false,
    "newArrival": false,
    "images": [
      "https://images.unsplash.com/photo-1556911220-e15b29be8c8f?w=500&q=80?w=600&q=80"
    ],
    "description": "Milton Thermosteel Flask 1L from Milton, selected for the AutoCart everyday shopping collection with quality, value and reliable performance.",
    "specifications": {
      "Brand": "Milton",
      "Category": "Home & Kitchen",
      "Warranty": "1 Year Warranty"
    },
    "seller": "Milton Official Store",
    "createdAt": "2026-03-01"
  },
  {
    "id": "prod-216",
    "name": "Wakefit Memory Foam Pillow",
    "slug": "wakefit-memory-foam-pillow",
    "category": "Home & Kitchen",
    "categoryId": "cat-3",
    "brand": "Wakefit",
    "price": 999,
    "originalPrice": 1799,
    "discount": 44,
    "rating": 4.1,
    "reviewCount": 4442,
    "stock": 100,
    "stockStatus": "In Stock",
    "featured": false,
    "bestSeller": true,
    "newArrival": true,
    "images": [
      "https://images.unsplash.com/photo-1556911220-e15b29be8c8f?w=500&q=80?w=600&q=80"
    ],
    "description": "Wakefit Memory Foam Pillow from Wakefit, selected for the AutoCart everyday shopping collection with quality, value and reliable performance.",
    "specifications": {
      "Brand": "Wakefit",
      "Category": "Home & Kitchen",
      "Warranty": "1 Year Warranty"
    },
    "seller": "Wakefit Official Store",
    "createdAt": "2026-03-01"
  },
  {
    "id": "prod-217",
    "name": "IKEA LED Floor Lamp",
    "slug": "ikea-led-floor-lamp",
    "category": "Home & Kitchen",
    "categoryId": "cat-3",
    "brand": "IKEA",
    "price": 2499,
    "originalPrice": 3999,
    "discount": 38,
    "rating": 4.4,
    "reviewCount": 4579,
    "stock": 107,
    "stockStatus": "In Stock",
    "featured": true,
    "bestSeller": false,
    "newArrival": false,
    "images": [
      "https://images.unsplash.com/photo-1556911220-e15b29be8c8f?w=500&q=80?w=600&q=80"
    ],
    "description": "IKEA LED Floor Lamp from IKEA, selected for the AutoCart everyday shopping collection with quality, value and reliable performance.",
    "specifications": {
      "Brand": "IKEA",
      "Category": "Home & Kitchen",
      "Warranty": "1 Year Warranty"
    },
    "seller": "IKEA Official Store",
    "createdAt": "2026-03-01"
  },
  {
    "id": "prod-218",
    "name": "Borosil Glass Lunch Box Set",
    "slug": "borosil-glass-lunch-box-set",
    "category": "Home & Kitchen",
    "categoryId": "cat-3",
    "brand": "Borosil",
    "price": 1299,
    "originalPrice": 1999,
    "discount": 35,
    "rating": 4.7,
    "reviewCount": 4716,
    "stock": 114,
    "stockStatus": "In Stock",
    "featured": false,
    "bestSeller": false,
    "newArrival": false,
    "images": [
      "https://images.unsplash.com/photo-1556911220-e15b29be8c8f?w=500&q=80?w=600&q=80"
    ],
    "description": "Borosil Glass Lunch Box Set from Borosil, selected for the AutoCart everyday shopping collection with quality, value and reliable performance.",
    "specifications": {
      "Brand": "Borosil",
      "Category": "Home & Kitchen",
      "Warranty": "1 Year Warranty"
    },
    "seller": "Borosil Official Store",
    "createdAt": "2026-03-01"
  },
  {
    "id": "prod-219",
    "name": "Minimalist 2% Salicylic Acid Face Serum",
    "slug": "minimalist-2-salicylic-acid-face-serum",
    "category": "Beauty & Personal Care",
    "categoryId": "cat-4",
    "brand": "Minimalist",
    "price": 549,
    "originalPrice": 699,
    "discount": 21,
    "rating": 4.1,
    "reviewCount": 4853,
    "stock": 121,
    "stockStatus": "In Stock",
    "featured": false,
    "bestSeller": false,
    "newArrival": true,
    "images": [
      "https://images.unsplash.com/photo-1522337360788-8b13dee7a37e?w=500&q=80?w=600&q=80"
    ],
    "description": "Minimalist 2% Salicylic Acid Face Serum from Minimalist, selected for the AutoCart everyday shopping collection with quality, value and reliable performance.",
    "specifications": {
      "Brand": "Minimalist",
      "Category": "Beauty & Personal Care",
      "Warranty": "Manufacturer Warranty"
    },
    "seller": "Minimalist Official Store",
    "createdAt": "2026-03-01"
  },
  {
    "id": "prod-220",
    "name": "Mamaearth Onion Hair Serum",
    "slug": "mamaearth-onion-hair-serum",
    "category": "Beauty & Personal Care",
    "categoryId": "cat-4",
    "brand": "Mamaearth",
    "price": 449,
    "originalPrice": 599,
    "discount": 25,
    "rating": 4.4,
    "reviewCount": 4990,
    "stock": 128,
    "stockStatus": "In Stock",
    "featured": false,
    "bestSeller": true,
    "newArrival": false,
    "images": [
      "https://images.unsplash.com/photo-1522337360788-8b13dee7a37e?w=500&q=80?w=600&q=80"
    ],
    "description": "Mamaearth Onion Hair Serum from Mamaearth, selected for the AutoCart everyday shopping collection with quality, value and reliable performance.",
    "specifications": {
      "Brand": "Mamaearth",
      "Category": "Beauty & Personal Care",
      "Warranty": "Manufacturer Warranty"
    },
    "seller": "Mamaearth Official Store",
    "createdAt": "2026-03-01"
  },
  {
    "id": "prod-221",
    "name": "Lakmé Absolute Matte Lip Color",
    "slug": "lakm-absolute-matte-lip-color",
    "category": "Beauty & Personal Care",
    "categoryId": "cat-4",
    "brand": "Lakmé",
    "price": 699,
    "originalPrice": 950,
    "discount": 26,
    "rating": 4.7,
    "reviewCount": 5127,
    "stock": 135,
    "stockStatus": "In Stock",
    "featured": false,
    "bestSeller": false,
    "newArrival": false,
    "images": [
      "https://images.unsplash.com/photo-1522337360788-8b13dee7a37e?w=500&q=80?w=600&q=80"
    ],
    "description": "Lakmé Absolute Matte Lip Color from Lakmé, selected for the AutoCart everyday shopping collection with quality, value and reliable performance.",
    "specifications": {
      "Brand": "Lakmé",
      "Category": "Beauty & Personal Care",
      "Warranty": "Manufacturer Warranty"
    },
    "seller": "Lakmé Official Store",
    "createdAt": "2026-03-01"
  },
  {
    "id": "prod-222",
    "name": "Nivea Men Face Wash 150ml",
    "slug": "nivea-men-face-wash-150ml",
    "category": "Beauty & Personal Care",
    "categoryId": "cat-4",
    "brand": "Nivea",
    "price": 249,
    "originalPrice": 325,
    "discount": 23,
    "rating": 4.1,
    "reviewCount": 5264,
    "stock": 142,
    "stockStatus": "In Stock",
    "featured": false,
    "bestSeller": false,
    "newArrival": true,
    "images": [
      "https://images.unsplash.com/photo-1522337360788-8b13dee7a37e?w=500&q=80?w=600&q=80"
    ],
    "description": "Nivea Men Face Wash 150ml from Nivea, selected for the AutoCart everyday shopping collection with quality, value and reliable performance.",
    "specifications": {
      "Brand": "Nivea",
      "Category": "Beauty & Personal Care",
      "Warranty": "Manufacturer Warranty"
    },
    "seller": "Nivea Official Store",
    "createdAt": "2026-03-01"
  },
  {
    "id": "prod-223",
    "name": "Philips Beard Trimmer Series 3000",
    "slug": "philips-beard-trimmer-series-3000",
    "category": "Beauty & Personal Care",
    "categoryId": "cat-4",
    "brand": "Philips",
    "price": 1599,
    "originalPrice": 2295,
    "discount": 30,
    "rating": 4.4,
    "reviewCount": 5401,
    "stock": 19,
    "stockStatus": "Low Stock",
    "featured": false,
    "bestSeller": false,
    "newArrival": false,
    "images": [
      "https://images.unsplash.com/photo-1522337360788-8b13dee7a37e?w=500&q=80?w=600&q=80"
    ],
    "description": "Philips Beard Trimmer Series 3000 from Philips, selected for the AutoCart everyday shopping collection with quality, value and reliable performance.",
    "specifications": {
      "Brand": "Philips",
      "Category": "Beauty & Personal Care",
      "Warranty": "Manufacturer Warranty"
    },
    "seller": "Philips Official Store",
    "createdAt": "2026-03-01"
  },
  {
    "id": "prod-224",
    "name": "The Derma Co 1% Hyaluronic Sunscreen",
    "slug": "the-derma-co-1-hyaluronic-sunscreen",
    "category": "Beauty & Personal Care",
    "categoryId": "cat-4",
    "brand": "The Derma Co",
    "price": 499,
    "originalPrice": 699,
    "discount": 29,
    "rating": 4.7,
    "reviewCount": 5538,
    "stock": 26,
    "stockStatus": "Low Stock",
    "featured": true,
    "bestSeller": true,
    "newArrival": false,
    "images": [
      "https://images.unsplash.com/photo-1522337360788-8b13dee7a37e?w=500&q=80?w=600&q=80"
    ],
    "description": "The Derma Co 1% Hyaluronic Sunscreen from The Derma Co, selected for the AutoCart everyday shopping collection with quality, value and reliable performance.",
    "specifications": {
      "Brand": "The Derma Co",
      "Category": "Beauty & Personal Care",
      "Warranty": "Manufacturer Warranty"
    },
    "seller": "The Derma Co Official Store",
    "createdAt": "2026-03-01"
  },
  {
    "id": "prod-225",
    "name": "Decathlon Domyos Yoga Mat 8mm",
    "slug": "decathlon-domyos-yoga-mat-8mm",
    "category": "Sports & Fitness",
    "categoryId": "cat-5",
    "brand": "Domyos",
    "price": 799,
    "originalPrice": 1199,
    "discount": 33,
    "rating": 4.1,
    "reviewCount": 5675,
    "stock": 33,
    "stockStatus": "Low Stock",
    "featured": false,
    "bestSeller": false,
    "newArrival": true,
    "images": [
      "https://images.unsplash.com/photo-1517838277536-f5f99be501cd?w=500&q=80?w=600&q=80"
    ],
    "description": "Decathlon Domyos Yoga Mat 8mm from Domyos, selected for the AutoCart everyday shopping collection with quality, value and reliable performance.",
    "specifications": {
      "Brand": "Domyos",
      "Category": "Sports & Fitness",
      "Warranty": "1 Year Warranty"
    },
    "seller": "Domyos Official Store",
    "createdAt": "2026-03-01"
  },
  {
    "id": "prod-226",
    "name": "Yonex GR 303 Badminton Racket",
    "slug": "yonex-gr-303-badminton-racket",
    "category": "Sports & Fitness",
    "categoryId": "cat-5",
    "brand": "Yonex",
    "price": 1299,
    "originalPrice": 1899,
    "discount": 32,
    "rating": 4.4,
    "reviewCount": 5812,
    "stock": 40,
    "stockStatus": "In Stock",
    "featured": false,
    "bestSeller": false,
    "newArrival": false,
    "images": [
      "https://images.unsplash.com/photo-1517838277536-f5f99be501cd?w=500&q=80?w=600&q=80"
    ],
    "description": "Yonex GR 303 Badminton Racket from Yonex, selected for the AutoCart everyday shopping collection with quality, value and reliable performance.",
    "specifications": {
      "Brand": "Yonex",
      "Category": "Sports & Fitness",
      "Warranty": "1 Year Warranty"
    },
    "seller": "Yonex Official Store",
    "createdAt": "2026-03-01"
  },
  {
    "id": "prod-227",
    "name": "Cosco Basketball Size 7",
    "slug": "cosco-basketball-size-7",
    "category": "Sports & Fitness",
    "categoryId": "cat-5",
    "brand": "Cosco",
    "price": 899,
    "originalPrice": 1299,
    "discount": 31,
    "rating": 4.7,
    "reviewCount": 5949,
    "stock": 47,
    "stockStatus": "In Stock",
    "featured": false,
    "bestSeller": false,
    "newArrival": false,
    "images": [
      "https://images.unsplash.com/photo-1517838277536-f5f99be501cd?w=500&q=80?w=600&q=80"
    ],
    "description": "Cosco Basketball Size 7 from Cosco, selected for the AutoCart everyday shopping collection with quality, value and reliable performance.",
    "specifications": {
      "Brand": "Cosco",
      "Category": "Sports & Fitness",
      "Warranty": "1 Year Warranty"
    },
    "seller": "Cosco Official Store",
    "createdAt": "2026-03-01"
  },
  {
    "id": "prod-228",
    "name": "Strauss Adjustable Dumbbell Set 20kg",
    "slug": "strauss-adjustable-dumbbell-set-20kg",
    "category": "Sports & Fitness",
    "categoryId": "cat-5",
    "brand": "Strauss",
    "price": 2499,
    "originalPrice": 3999,
    "discount": 38,
    "rating": 4.1,
    "reviewCount": 6086,
    "stock": 54,
    "stockStatus": "In Stock",
    "featured": false,
    "bestSeller": true,
    "newArrival": true,
    "images": [
      "https://images.unsplash.com/photo-1517838277536-f5f99be501cd?w=500&q=80?w=600&q=80"
    ],
    "description": "Strauss Adjustable Dumbbell Set 20kg from Strauss, selected for the AutoCart everyday shopping collection with quality, value and reliable performance.",
    "specifications": {
      "Brand": "Strauss",
      "Category": "Sports & Fitness",
      "Warranty": "1 Year Warranty"
    },
    "seller": "Strauss Official Store",
    "createdAt": "2026-03-01"
  },
  {
    "id": "prod-229",
    "name": "Nivia Storm Football",
    "slug": "nivia-storm-football",
    "category": "Sports & Fitness",
    "categoryId": "cat-5",
    "brand": "Nivia",
    "price": 699,
    "originalPrice": 999,
    "discount": 30,
    "rating": 4.4,
    "reviewCount": 6223,
    "stock": 61,
    "stockStatus": "In Stock",
    "featured": false,
    "bestSeller": false,
    "newArrival": false,
    "images": [
      "https://images.unsplash.com/photo-1517838277536-f5f99be501cd?w=500&q=80?w=600&q=80"
    ],
    "description": "Nivia Storm Football from Nivia, selected for the AutoCart everyday shopping collection with quality, value and reliable performance.",
    "specifications": {
      "Brand": "Nivia",
      "Category": "Sports & Fitness",
      "Warranty": "1 Year Warranty"
    },
    "seller": "Nivia Official Store",
    "createdAt": "2026-03-01"
  },
  {
    "id": "prod-230",
    "name": "Boldfit Gym Gloves",
    "slug": "boldfit-gym-gloves",
    "category": "Sports & Fitness",
    "categoryId": "cat-5",
    "brand": "Boldfit",
    "price": 499,
    "originalPrice": 799,
    "discount": 38,
    "rating": 4.7,
    "reviewCount": 6360,
    "stock": 68,
    "stockStatus": "In Stock",
    "featured": false,
    "bestSeller": false,
    "newArrival": false,
    "images": [
      "https://images.unsplash.com/photo-1517838277536-f5f99be501cd?w=500&q=80?w=600&q=80"
    ],
    "description": "Boldfit Gym Gloves from Boldfit, selected for the AutoCart everyday shopping collection with quality, value and reliable performance.",
    "specifications": {
      "Brand": "Boldfit",
      "Category": "Sports & Fitness",
      "Warranty": "1 Year Warranty"
    },
    "seller": "Boldfit Official Store",
    "createdAt": "2026-03-01"
  },
  {
    "id": "prod-231",
    "name": "Atomic Habits",
    "slug": "atomic-habits",
    "category": "Books & Stationery",
    "categoryId": "cat-6",
    "brand": "Penguin",
    "price": 499,
    "originalPrice": 799,
    "discount": 38,
    "rating": 4.1,
    "reviewCount": 6497,
    "stock": 75,
    "stockStatus": "In Stock",
    "featured": true,
    "bestSeller": false,
    "newArrival": true,
    "images": [
      "https://images.unsplash.com/photo-1512820790803-83ca734da794?w=500&q=80?w=600&q=80"
    ],
    "description": "Atomic Habits from Penguin, selected for the AutoCart everyday shopping collection with quality, value and reliable performance.",
    "specifications": {
      "Brand": "Penguin",
      "Category": "Books & Stationery",
      "Warranty": "Manufacturer Warranty"
    },
    "seller": "Penguin Official Store",
    "createdAt": "2026-03-01"
  },
  {
    "id": "prod-232",
    "name": "The Psychology of Money",
    "slug": "the-psychology-of-money",
    "category": "Books & Stationery",
    "categoryId": "cat-6",
    "brand": "Jaico",
    "price": 299,
    "originalPrice": 499,
    "discount": 40,
    "rating": 4.4,
    "reviewCount": 6634,
    "stock": 82,
    "stockStatus": "In Stock",
    "featured": false,
    "bestSeller": true,
    "newArrival": false,
    "images": [
      "https://images.unsplash.com/photo-1512820790803-83ca734da794?w=500&q=80?w=600&q=80"
    ],
    "description": "The Psychology of Money from Jaico, selected for the AutoCart everyday shopping collection with quality, value and reliable performance.",
    "specifications": {
      "Brand": "Jaico",
      "Category": "Books & Stationery",
      "Warranty": "Manufacturer Warranty"
    },
    "seller": "Jaico Official Store",
    "createdAt": "2026-03-01"
  },
  {
    "id": "prod-233",
    "name": "Clean Code",
    "slug": "clean-code",
    "category": "Books & Stationery",
    "categoryId": "cat-6",
    "brand": "Pearson",
    "price": 899,
    "originalPrice": 1299,
    "discount": 31,
    "rating": 4.7,
    "reviewCount": 6771,
    "stock": 89,
    "stockStatus": "In Stock",
    "featured": false,
    "bestSeller": false,
    "newArrival": false,
    "images": [
      "https://images.unsplash.com/photo-1512820790803-83ca734da794?w=500&q=80?w=600&q=80"
    ],
    "description": "Clean Code from Pearson, selected for the AutoCart everyday shopping collection with quality, value and reliable performance.",
    "specifications": {
      "Brand": "Pearson",
      "Category": "Books & Stationery",
      "Warranty": "Manufacturer Warranty"
    },
    "seller": "Pearson Official Store",
    "createdAt": "2026-03-01"
  },
  {
    "id": "prod-234",
    "name": "Ikigai",
    "slug": "ikigai",
    "category": "Books & Stationery",
    "categoryId": "cat-6",
    "brand": "Penguin",
    "price": 299,
    "originalPrice": 499,
    "discount": 40,
    "rating": 4.1,
    "reviewCount": 6908,
    "stock": 96,
    "stockStatus": "In Stock",
    "featured": false,
    "bestSeller": false,
    "newArrival": true,
    "images": [
      "https://images.unsplash.com/photo-1512820790803-83ca734da794?w=500&q=80?w=600&q=80"
    ],
    "description": "Ikigai from Penguin, selected for the AutoCart everyday shopping collection with quality, value and reliable performance.",
    "specifications": {
      "Brand": "Penguin",
      "Category": "Books & Stationery",
      "Warranty": "Manufacturer Warranty"
    },
    "seller": "Penguin Official Store",
    "createdAt": "2026-03-01"
  },
  {
    "id": "prod-235",
    "name": "Classmate Long Notebook Pack",
    "slug": "classmate-long-notebook-pack",
    "category": "Books & Stationery",
    "categoryId": "cat-6",
    "brand": "Classmate",
    "price": 399,
    "originalPrice": 520,
    "discount": 23,
    "rating": 4.4,
    "reviewCount": 7045,
    "stock": 103,
    "stockStatus": "In Stock",
    "featured": false,
    "bestSeller": false,
    "newArrival": false,
    "images": [
      "https://images.unsplash.com/photo-1512820790803-83ca734da794?w=500&q=80?w=600&q=80"
    ],
    "description": "Classmate Long Notebook Pack from Classmate, selected for the AutoCart everyday shopping collection with quality, value and reliable performance.",
    "specifications": {
      "Brand": "Classmate",
      "Category": "Books & Stationery",
      "Warranty": "Manufacturer Warranty"
    },
    "seller": "Classmate Official Store",
    "createdAt": "2026-03-01"
  },
  {
    "id": "prod-236",
    "name": "Faber-Castell Colour Pencil Set",
    "slug": "faber-castell-colour-pencil-set",
    "category": "Books & Stationery",
    "categoryId": "cat-6",
    "brand": "Faber-Castell",
    "price": 349,
    "originalPrice": 499,
    "discount": 30,
    "rating": 4.7,
    "reviewCount": 7182,
    "stock": 110,
    "stockStatus": "In Stock",
    "featured": false,
    "bestSeller": true,
    "newArrival": false,
    "images": [
      "https://images.unsplash.com/photo-1512820790803-83ca734da794?w=500&q=80?w=600&q=80"
    ],
    "description": "Faber-Castell Colour Pencil Set from Faber-Castell, selected for the AutoCart everyday shopping collection with quality, value and reliable performance.",
    "specifications": {
      "Brand": "Faber-Castell",
      "Category": "Books & Stationery",
      "Warranty": "Manufacturer Warranty"
    },
    "seller": "Faber-Castell Official Store",
    "createdAt": "2026-03-01"
  },
  {
    "id": "prod-237",
    "name": "Tata Sampann Toor Dal 1kg",
    "slug": "tata-sampann-toor-dal-1kg",
    "category": "Grocery & Gourmet",
    "categoryId": "cat-7",
    "brand": "Tata Sampann",
    "price": 189,
    "originalPrice": 230,
    "discount": 18,
    "rating": 4.1,
    "reviewCount": 7319,
    "stock": 117,
    "stockStatus": "In Stock",
    "featured": false,
    "bestSeller": false,
    "newArrival": true,
    "images": [
      "https://images.unsplash.com/photo-1542838132-92c53300491e?w=500&q=80?w=600&q=80"
    ],
    "description": "Tata Sampann Toor Dal 1kg from Tata Sampann, selected for the AutoCart everyday shopping collection with quality, value and reliable performance.",
    "specifications": {
      "Brand": "Tata Sampann",
      "Category": "Grocery & Gourmet",
      "Warranty": "Manufacturer Warranty"
    },
    "seller": "Tata Sampann Official Store",
    "createdAt": "2026-03-01"
  },
  {
    "id": "prod-238",
    "name": "Aashirvaad Atta 5kg",
    "slug": "aashirvaad-atta-5kg",
    "category": "Grocery & Gourmet",
    "categoryId": "cat-7",
    "brand": "Aashirvaad",
    "price": 299,
    "originalPrice": 345,
    "discount": 13,
    "rating": 4.4,
    "reviewCount": 7456,
    "stock": 124,
    "stockStatus": "In Stock",
    "featured": true,
    "bestSeller": false,
    "newArrival": false,
    "images": [
      "https://images.unsplash.com/photo-1542838132-92c53300491e?w=500&q=80?w=600&q=80"
    ],
    "description": "Aashirvaad Atta 5kg from Aashirvaad, selected for the AutoCart everyday shopping collection with quality, value and reliable performance.",
    "specifications": {
      "Brand": "Aashirvaad",
      "Category": "Grocery & Gourmet",
      "Warranty": "Manufacturer Warranty"
    },
    "seller": "Aashirvaad Official Store",
    "createdAt": "2026-03-01"
  },
  {
    "id": "prod-239",
    "name": "Tata Tea Gold 1kg",
    "slug": "tata-tea-gold-1kg",
    "category": "Grocery & Gourmet",
    "categoryId": "cat-7",
    "brand": "Tata Tea",
    "price": 499,
    "originalPrice": 610,
    "discount": 18,
    "rating": 4.7,
    "reviewCount": 7593,
    "stock": 131,
    "stockStatus": "In Stock",
    "featured": false,
    "bestSeller": false,
    "newArrival": false,
    "images": [
      "https://images.unsplash.com/photo-1542838132-92c53300491e?w=500&q=80?w=600&q=80"
    ],
    "description": "Tata Tea Gold 1kg from Tata Tea, selected for the AutoCart everyday shopping collection with quality, value and reliable performance.",
    "specifications": {
      "Brand": "Tata Tea",
      "Category": "Grocery & Gourmet",
      "Warranty": "Manufacturer Warranty"
    },
    "seller": "Tata Tea Official Store",
    "createdAt": "2026-03-01"
  },
  {
    "id": "prod-240",
    "name": "Happilo Premium Cashews 500g",
    "slug": "happilo-premium-cashews-500g",
    "category": "Grocery & Gourmet",
    "categoryId": "cat-7",
    "brand": "Happilo",
    "price": 499,
    "originalPrice": 699,
    "discount": 29,
    "rating": 4.1,
    "reviewCount": 7730,
    "stock": 138,
    "stockStatus": "In Stock",
    "featured": false,
    "bestSeller": true,
    "newArrival": true,
    "images": [
      "https://images.unsplash.com/photo-1542838132-92c53300491e?w=500&q=80?w=600&q=80"
    ],
    "description": "Happilo Premium Cashews 500g from Happilo, selected for the AutoCart everyday shopping collection with quality, value and reliable performance.",
    "specifications": {
      "Brand": "Happilo",
      "Category": "Grocery & Gourmet",
      "Warranty": "Manufacturer Warranty"
    },
    "seller": "Happilo Official Store",
    "createdAt": "2026-03-01"
  },
  {
    "id": "prod-241",
    "name": "Kissan Mixed Fruit Jam 500g",
    "slug": "kissan-mixed-fruit-jam-500g",
    "category": "Grocery & Gourmet",
    "categoryId": "cat-7",
    "brand": "Kissan",
    "price": 169,
    "originalPrice": 220,
    "discount": 23,
    "rating": 4.4,
    "reviewCount": 7867,
    "stock": 145,
    "stockStatus": "In Stock",
    "featured": false,
    "bestSeller": false,
    "newArrival": false,
    "images": [
      "https://images.unsplash.com/photo-1542838132-92c53300491e?w=500&q=80?w=600&q=80"
    ],
    "description": "Kissan Mixed Fruit Jam 500g from Kissan, selected for the AutoCart everyday shopping collection with quality, value and reliable performance.",
    "specifications": {
      "Brand": "Kissan",
      "Category": "Grocery & Gourmet",
      "Warranty": "Manufacturer Warranty"
    },
    "seller": "Kissan Official Store",
    "createdAt": "2026-03-01"
  },
  {
    "id": "prod-242",
    "name": "Saffola Oats 1kg",
    "slug": "saffola-oats-1kg",
    "category": "Grocery & Gourmet",
    "categoryId": "cat-7",
    "brand": "Saffola",
    "price": 199,
    "originalPrice": 260,
    "discount": 23,
    "rating": 4.7,
    "reviewCount": 8004,
    "stock": 22,
    "stockStatus": "Low Stock",
    "featured": false,
    "bestSeller": false,
    "newArrival": false,
    "images": [
      "https://images.unsplash.com/photo-1542838132-92c53300491e?w=500&q=80?w=600&q=80"
    ],
    "description": "Saffola Oats 1kg from Saffola, selected for the AutoCart everyday shopping collection with quality, value and reliable performance.",
    "specifications": {
      "Brand": "Saffola",
      "Category": "Grocery & Gourmet",
      "Warranty": "Manufacturer Warranty"
    },
    "seller": "Saffola Official Store",
    "createdAt": "2026-03-01"
  },
  {
    "id": "prod-243",
    "name": "LEGO Classic Creative Bricks 500 Pieces",
    "slug": "lego-classic-creative-bricks-500-pieces",
    "category": "Toys & Baby Care",
    "categoryId": "cat-8",
    "brand": "LEGO",
    "price": 2499,
    "originalPrice": 3299,
    "discount": 24,
    "rating": 4.1,
    "reviewCount": 8141,
    "stock": 29,
    "stockStatus": "Low Stock",
    "featured": false,
    "bestSeller": false,
    "newArrival": true,
    "images": [
      "https://images.unsplash.com/photo-1515488042361-ee00e0ddd4e4?w=500&q=80?w=600&q=80"
    ],
    "description": "LEGO Classic Creative Bricks 500 Pieces from LEGO, selected for the AutoCart everyday shopping collection with quality, value and reliable performance.",
    "specifications": {
      "Brand": "LEGO",
      "Category": "Toys & Baby Care",
      "Warranty": "Manufacturer Warranty"
    },
    "seller": "LEGO Official Store",
    "createdAt": "2026-03-01"
  },
  {
    "id": "prod-244",
    "name": "Hot Wheels 10 Car Pack",
    "slug": "hot-wheels-10-car-pack",
    "category": "Toys & Baby Care",
    "categoryId": "cat-8",
    "brand": "Hot Wheels",
    "price": 899,
    "originalPrice": 1199,
    "discount": 25,
    "rating": 4.4,
    "reviewCount": 8278,
    "stock": 36,
    "stockStatus": "In Stock",
    "featured": false,
    "bestSeller": true,
    "newArrival": false,
    "images": [
      "https://images.unsplash.com/photo-1515488042361-ee00e0ddd4e4?w=500&q=80?w=600&q=80"
    ],
    "description": "Hot Wheels 10 Car Pack from Hot Wheels, selected for the AutoCart everyday shopping collection with quality, value and reliable performance.",
    "specifications": {
      "Brand": "Hot Wheels",
      "Category": "Toys & Baby Care",
      "Warranty": "Manufacturer Warranty"
    },
    "seller": "Hot Wheels Official Store",
    "createdAt": "2026-03-01"
  },
  {
    "id": "prod-245",
    "name": "Funskool Stack & Learn Rings",
    "slug": "funskool-stack-learn-rings",
    "category": "Toys & Baby Care",
    "categoryId": "cat-8",
    "brand": "Funskool",
    "price": 399,
    "originalPrice": 599,
    "discount": 33,
    "rating": 4.7,
    "reviewCount": 8415,
    "stock": 43,
    "stockStatus": "In Stock",
    "featured": true,
    "bestSeller": false,
    "newArrival": false,
    "images": [
      "https://images.unsplash.com/photo-1515488042361-ee00e0ddd4e4?w=500&q=80?w=600&q=80"
    ],
    "description": "Funskool Stack & Learn Rings from Funskool, selected for the AutoCart everyday shopping collection with quality, value and reliable performance.",
    "specifications": {
      "Brand": "Funskool",
      "Category": "Toys & Baby Care",
      "Warranty": "Manufacturer Warranty"
    },
    "seller": "Funskool Official Store",
    "createdAt": "2026-03-01"
  },
  {
    "id": "prod-246",
    "name": "Pampers Baby Dry Pants Medium 64 Count",
    "slug": "pampers-baby-dry-pants-medium-64-count",
    "category": "Toys & Baby Care",
    "categoryId": "cat-8",
    "brand": "Pampers",
    "price": 899,
    "originalPrice": 1099,
    "discount": 18,
    "rating": 4.1,
    "reviewCount": 8552,
    "stock": 50,
    "stockStatus": "In Stock",
    "featured": false,
    "bestSeller": false,
    "newArrival": true,
    "images": [
      "https://images.unsplash.com/photo-1515488042361-ee00e0ddd4e4?w=500&q=80?w=600&q=80"
    ],
    "description": "Pampers Baby Dry Pants Medium 64 Count from Pampers, selected for the AutoCart everyday shopping collection with quality, value and reliable performance.",
    "specifications": {
      "Brand": "Pampers",
      "Category": "Toys & Baby Care",
      "Warranty": "Manufacturer Warranty"
    },
    "seller": "Pampers Official Store",
    "createdAt": "2026-03-01"
  },
  {
    "id": "prod-247",
    "name": "R for Rabbit Baby Feeding Bottle 250ml",
    "slug": "r-for-rabbit-baby-feeding-bottle-250ml",
    "category": "Toys & Baby Care",
    "categoryId": "cat-8",
    "brand": "R for Rabbit",
    "price": 349,
    "originalPrice": 499,
    "discount": 30,
    "rating": 4.4,
    "reviewCount": 8689,
    "stock": 57,
    "stockStatus": "In Stock",
    "featured": false,
    "bestSeller": false,
    "newArrival": false,
    "images": [
      "https://images.unsplash.com/photo-1515488042361-ee00e0ddd4e4?w=500&q=80?w=600&q=80"
    ],
    "description": "R for Rabbit Baby Feeding Bottle 250ml from R for Rabbit, selected for the AutoCart everyday shopping collection with quality, value and reliable performance.",
    "specifications": {
      "Brand": "R for Rabbit",
      "Category": "Toys & Baby Care",
      "Warranty": "Manufacturer Warranty"
    },
    "seller": "R for Rabbit Official Store",
    "createdAt": "2026-03-01"
  },
  {
    "id": "prod-248",
    "name": "Babyhug Cotton Romper Set",
    "slug": "babyhug-cotton-romper-set",
    "category": "Toys & Baby Care",
    "categoryId": "cat-8",
    "brand": "Babyhug",
    "price": 699,
    "originalPrice": 999,
    "discount": 30,
    "rating": 4.7,
    "reviewCount": 8826,
    "stock": 64,
    "stockStatus": "In Stock",
    "featured": false,
    "bestSeller": true,
    "newArrival": false,
    "images": [
      "https://images.unsplash.com/photo-1515488042361-ee00e0ddd4e4?w=500&q=80?w=600&q=80"
    ],
    "description": "Babyhug Cotton Romper Set from Babyhug, selected for the AutoCart everyday shopping collection with quality, value and reliable performance.",
    "specifications": {
      "Brand": "Babyhug",
      "Category": "Toys & Baby Care",
      "Warranty": "Manufacturer Warranty"
    },
    "seller": "Babyhug Official Store",
    "createdAt": "2026-03-01"
  }

];
