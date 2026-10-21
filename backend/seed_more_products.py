"""
Populate AutoCart Database with 120+ rich e-commerce catalog items.
"""
import os
import random
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'autocart_core.settings')
django.setup()

from api.models import Product, Category

catalog_blueprints = [
    # Laptops
    ("Laptops", "Electronics", "cat-electronics", "Apple MacBook Air M3 (16GB, 512GB SSD) Laptop", "Apple", 114900, 134900, 4.8, 1240, "Apple M3 chip with 8-core CPU, 10-core GPU, Liquid Retina display with True Tone, 18-hour battery life.", {"Processor": "Apple M3", "RAM": "16GB Unified", "Storage": "512GB SSD", "Display": "13.6-inch Liquid Retina"}, "Appario Retail", ["https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=800"]),
    ("Laptops", "Electronics", "cat-electronics", "Dell XPS 13 Plus OLED Intel Evo i7 Laptop", "Dell", 139990, 169990, 4.6, 520, "13.4-inch 3.5K OLED touch screen, 13th Gen Intel Core i7-1360P, capacitive touch function row, edge-to-edge keyboard.", {"Processor": "Intel Core i7-1360P", "RAM": "16GB LPDDR5", "Storage": "1TB NVMe SSD", "Display": "3.5K OLED Touch"}, "Dell Official Store", ["https://images.unsplash.com/photo-1593642632823-8f785ba67e45?w=800"]),
    ("Laptops", "Electronics", "cat-electronics", "ASUS TUF Gaming A15 AMD Ryzen 7 Laptop", "ASUS", 72990, 94990, 4.5, 3420, "NVIDIA GeForce RTX 4050 6GB GDDR6, 144Hz FHD anti-glare IPS display, RGB backlit keyboard, military-grade durability.", {"Processor": "AMD Ryzen 7 7735HS", "GPU": "RTX 4050 6GB", "RAM": "16GB DDR5", "Storage": "512GB NVMe SSD"}, "Appario Retail", ["https://images.unsplash.com/photo-1588872657578-7efd1f1555ed?w=800"]),
    ("Laptops", "Electronics", "cat-electronics", "Lenovo IdeaPad Slim 3 12th Gen Intel Core i5 Laptop", "Lenovo", 48990, 68990, 4.3, 4100, "Thin and light laptop with 15.6-inch FHD antiglare display, rapid charge boost, Dolby Audio.", {"Processor": "Intel Core i5-1235U", "RAM": "16GB DDR4", "Storage": "512GB SSD", "Weight": "1.63 kg"}, "Lenovo Store", ["https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=800"]),
    ("Laptops", "Electronics", "cat-electronics", "Acer Swift Go 14 AI OLED Intel Core Ultra 5 Laptop", "Acer", 69990, 89990, 4.6, 890, "Intel AI Boost NPU for accelerated AI processing, 2.8K 90Hz OLED 100% DCI-P3 display, multi-control touchpad.", {"Processor": "Intel Core Ultra 5 125H", "RAM": "16GB LPDDR5X", "Display": "2.8K 90Hz OLED"}, "Acer Online", ["https://images.unsplash.com/photo-1525547719571-a2d4ac8945e2?w=800"]),
    ("Laptops", "Electronics", "cat-electronics", "HP 15s AMD Ryzen 5 Hexa Core Laptop", "HP", 39990, 52990, 4.2, 5800, "Reliable everyday workhorse for students and professionals. Micro-edge bezel display, fast charging battery.", {"Processor": "AMD Ryzen 5 5500U", "RAM": "8GB DDR4", "Storage": "512GB SSD"}, "HP Store", ["https://images.unsplash.com/photo-1541807084-5c52b6b3adef?w=800"]),
    ("Laptops", "Electronics", "cat-electronics", "ASUS Vivobook 15 Thin & Light Laptop Intel Core i3", "ASUS", 38990, 49990, 4.3, 3100, "Compact 15.6-inch FHD anti-glare display, 8GB DDR4 RAM, 512GB SSD, Windows 11 Home, fingerprint sensor.", {"Processor": "Intel Core i3-1215U", "RAM": "8GB DDR4", "Storage": "512GB SSD"}, "ASUS Exclusive", ["https://images.unsplash.com/photo-1588872657578-7efd1f1555ed?w=800"]),
    ("Laptops", "Electronics", "cat-electronics", "Dell Inspiron 3520 Intel Core i5 12th Gen Laptop", "Dell", 54990, 71990, 4.4, 4500, "15.6-inch 120Hz display, Intel Core i5-1235U processor, 16GB RAM, 512GB SSD, carbon black finish.", {"Processor": "Intel Core i5-1235U", "RAM": "16GB DDR4", "Storage": "512GB SSD"}, "Dell Store", ["https://images.unsplash.com/photo-1593642632823-8f785ba67e45?w=800"]),

    # Audio
    ("Audio", "Electronics", "cat-electronics", "Sony WH-1000XM5 Wireless ANC Headphones", "Sony", 26990, 34990, 4.8, 6200, "Industry-leading noise cancellation with 8 microphones, 30-hour battery life with fast charge, crystal clear hands-free calls.", {"Type": "Over-Ear", "ANC": "Yes, Dual Processor V1", "Battery": "30 Hours", "Codec": "LDAC, AAC, SBC"}, "Sony India", ["https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=800"]),
    ("Audio", "Electronics", "cat-electronics", "Bose QuietComfort 45 Bluetooth Headphones", "Bose", 22990, 29900, 4.7, 3100, "Legendary acoustic noise cancelling, high-fidelity audio with adjustable EQ, lightweight comfort with plush ear cushions.", {"Type": "Over-Ear", "ANC": "Quiet & Aware Modes", "Battery": "24 Hours"}, "Bose Authorized", ["https://images.unsplash.com/photo-1546435770-a3e426bf472b?w=800"]),
    ("Audio", "Electronics", "cat-electronics", "Sennheiser Momentum 4 Wireless Audiophile ANC", "Sennheiser", 24990, 34990, 4.7, 1800, "Audiophile-inspired 42mm transducer system, exceptional 60-hour battery runtime, adaptive noise cancellation.", {"Battery": "60 Hours", "Transducer": "42mm", "ANC": "Adaptive"}, "AudioCraft Store", ["https://images.unsplash.com/photo-1583394838336-acd977736f90?w=800"]),
    ("Audio", "Electronics", "cat-electronics", "OnePlus Nord Buds 2r True Wireless Earbuds", "OnePlus", 1799, 2299, 4.3, 14200, "12.4mm extra large dynamic bass drivers, dual mic AI clear call noise reduction, 38 hours playback, IP55 sweat resistant.", {"Driver": "12.4mm Dynamic", "Battery": "38 Hours total", "Water Resistance": "IP55"}, "Appario Retail", ["https://images.unsplash.com/photo-1590658268037-6bf12165a8df?w=800"]),
    ("Audio", "Electronics", "cat-electronics", "JBL Flip 6 Portable Waterproof Bluetooth Speaker", "JBL", 8999, 13999, 4.6, 9200, "2-way speaker system delivering loud, crystal clear, powerful sound. IP67 waterproof and dustproof, 12 hours playtime.", {"Power Output": "30W RMS", "Water Resistance": "IP67", "Battery": "12 Hours"}, "Harman Store", ["https://images.unsplash.com/photo-1608043152269-423dbba4e7e1?w=800"]),
    ("Audio", "Electronics", "cat-electronics", "boAt Stone 1200 14W Bluetooth Party Speaker", "boAt", 3499, 6990, 4.2, 8500, "14W RMS stereo sound with dynamic RGB lights, integrated TWS pairing, up to 9 hours of non-stop battery life.", {"Sound": "14W RMS", "RGB": "Dynamic LEDs", "Playback": "9 Hours"}, "boAt Official Store", ["https://images.unsplash.com/photo-1545454675-3531b543be5d?w=800"]),

    # Smartphones & Wearables
    ("Smartphones", "Electronics", "cat-electronics", "Samsung Galaxy S24 Ultra 5G (12GB, 256GB)", "Samsung", 129999, 144999, 4.8, 4800, "Titanium frame, Galaxy AI live translate & Circle to Search, 200MP camera with 100x Space Zoom, built-in S-Pen.", {"Display": "6.8-inch QHD+ Dynamic AMOLED 2X", "Processor": "Snapdragon 8 Gen 3 for Galaxy", "Camera": "200MP + 50MP + 12MP + 10MP"}, "Samsung India", ["https://images.unsplash.com/photo-1610945265064-0e34e5519bbf?w=800"]),
    ("Smartphones", "Electronics", "cat-electronics", "OnePlus 12 5G (16GB RAM, 512GB Storage)", "OnePlus", 64999, 69999, 4.7, 7200, "4th Gen Hasselblad Camera system, 2K 120Hz ProXDR display, 5400 mAh battery with 100W SUPERVOOC hyper charging.", {"Processor": "Snapdragon 8 Gen 3", "Charging": "100W SuperVOOC", "Display": "6.82-inch 2K 120Hz LTPO"}, "Appario Retail", ["https://images.unsplash.com/photo-1565849904461-04a58ad377e0?w=800"]),
    ("Smartphones", "Electronics", "cat-electronics", "Apple iPhone 15 Pro (128GB, Natural Titanium)", "Apple", 127990, 134900, 4.8, 9800, "Aerospace-grade titanium design, A17 Pro chip with console-quality gaming, 48MP main camera, customizable Action button.", {"Chip": "A17 Pro", "Display": "6.1-inch Super Retina XDR ProMotion", "Build": "Titanium"}, "Apple Store", ["https://images.unsplash.com/photo-1695048133142-1a20484d2569?w=800"]),
    ("Smartphones", "Electronics", "cat-electronics", "iQOO Neo 9 Pro 5G Snapdragon 8 Gen 2", "iQOO", 34999, 39999, 4.5, 6100, "Supercomputing Q1 chip for 144 FPS gaming interpolation, 50MP Sony IMX920 night vision camera, 120W flash charge.", {"Processor": "Snapdragon 8 Gen 2", "Charging": "120W FlashCharge", "Camera": "Sony IMX920 50MP OIS"}, "Appario Retail", ["https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=800"]),
    ("Smartwatches", "Electronics", "cat-electronics", "Apple Watch Series 9 GPS 45mm Midnight", "Apple", 41900, 44900, 4.8, 2300, "S9 SiP chip with Double Tap gesture control, precision finding for iPhone, brighter Always-On Retina display, ECG monitor.", {"Sensors": "ECG, Blood Oxygen, Temp", "Display": "2000 nits Always-On", "Water Resistance": "50m"}, "Apple Store", ["https://images.unsplash.com/photo-1546868871-7041f2a55e12?w=800"]),
    ("Smartwatches", "Electronics", "cat-electronics", "Noise ColorFit Pulse 3 AMOLED Smart Watch", "Noise", 1999, 4999, 4.2, 19400, "1.96-inch HD display, advanced Bluetooth calling, 100+ sports modes, 24x7 heart rate and SpO2 tracking, 7-day battery.", {"Display": "1.96-inch HD TFT", "Battery": "7 Days", "Calling": "Bluetooth with Dialpad"}, "Noise Official", ["https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=800"]),

    # Fashion
    ("Men Fashion", "Fashion", "cat-fashion", "Levis 511 Slim Fit Stretchable Jeans", "Levis", 2499, 3999, 4.4, 8200, "Modern slim-cut design with room to move. Premium cotton elastane blend engineered for comfort and all-day shape retention.", {"Fit": "Slim Fit", "Material": "99% Cotton, 1% Elastane", "Rise": "Mid Rise"}, "Appario Retail", ["https://images.unsplash.com/photo-1542272604-787c3835535d?w=800"]),
    ("Men Fashion", "Fashion", "cat-fashion", "Allen Solly Oxford Regular Fit Solid Shirt", "Allen Solly", 1199, 1999, 4.3, 6100, "100% breathable combed cotton oxford fabric, classic button-down collar, embroidered signature stag logo on chest.", {"Material": "100% Cotton", "Sleeve": "Full Sleeve", "Pattern": "Solid"}, "Madura Fashion", ["https://images.unsplash.com/photo-1602810318383-e386cc2a3ccf?w=800"]),
    ("Women Fashion", "Fashion", "cat-fashion", "BIBA Printed Pure Cotton Anarkali Kurta Set", "BIBA", 2999, 5995, 4.6, 4200, "Graceful cotton Anarkali silhouette with matching trousers and sheer dupatta. Intricate floral block print and gota patti work.", {"Fabric": "Pure Cotton", "Set Includes": "Kurta, Pants, Dupatta", "Occasion": "Festive / Casual"}, "Biba Apparels", ["https://images.unsplash.com/photo-1610030469983-98e550d6193c?w=800"]),
    ("Women Fashion", "Fashion", "cat-fashion", "W for Woman Geometric Embroidered Straight Kurti", "W for Woman", 1499, 2999, 4.4, 2800, "Contemporary mandarin neck straight cut kurti with geometric threadwork detailing on yoke and cuffs.", {"Fabric": "Viscose Rayon", "Length": "Calf Length", "Neck": "Mandarin"}, "W Brand Store", ["https://images.unsplash.com/photo-1583391733956-3750e0ff4e8b?w=800"]),
    ("Footwear", "Fashion", "cat-fashion", "Nike Air Zoom Pegasus 40 Men Running Shoes", "Nike", 7995, 10495, 4.7, 5100, "Engineered mesh upper for breathability, dual Zoom Air units for responsive bounce and energy return on long asphalt runs.", {"Terrain": "Road Running", "Cushioning": "Nike React Foam + Dual Zoom Air", "Drop": "10mm"}, "Nike Official Partner", ["https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=800"]),
    ("Footwear", "Fashion", "cat-fashion", "Puma Smashic Unisex Casual Retro Sneakers", "Puma", 2199, 4499, 4.3, 11400, "Classic tennis-inspired silhouette, durable synthetic leather upper with suede accents, cushioned SoftFoam+ sockliner.", {"Closure": "Lace-Up", "Sole": "Rubber", "Insole": "SoftFoam+"}, "Appario Retail", ["https://images.unsplash.com/photo-1608231387042-66d1773070a5?w=800"]),
    ("Footwear", "Fashion", "cat-fashion", "Red Tape Men Lightweight Memory Foam Walking Shoes", "Red Tape", 1399, 5299, 4.2, 18500, "Breathable mesh upper with EVA non-slip sole, memory foam insole providing cloud-like arch cushioning for all-day walking.", {"Upper": "Mesh", "Insole": "Memory Foam", "Sole": "EVA"}, "Red Tape Store", ["https://images.unsplash.com/photo-1595950653106-6c9ebd614d3a?w=800"]),
    ("Accessories", "Fashion", "cat-fashion", "Titan Neo Splash Quartz Blue Dial Analog Watch", "Titan", 3995, 4995, 4.5, 7800, "Mineral glass crystal, ocean blue dial with date window, stainless steel silver link strap, 50m water resistance.", {"Movement": "Quartz", "Water Resistance": "50m", "Dial Color": "Blue", "Warranty": "2 Years"}, "Titan Official", ["https://images.unsplash.com/photo-1524805444758-089113d48a6d?w=800"]),
    ("Accessories", "Fashion", "cat-fashion", "Ray-Ban Aviator Classic Gradient Sunglasses RB3025", "Ray-Ban", 8790, 10490, 4.8, 3200, "Iconic teardrop shape originally designed for US aviators. G-15 crystal glass lenses offering 100% UV400 radiation protection.", {"Frame": "Gold Metal", "Lens": "Green G-15 Crystal", "Protection": "100% UV400"}, "Luxottica India", ["https://images.unsplash.com/photo-1511499767150-a48a237f0083?w=800"]),

    # Home & Kitchen
    ("Kitchen", "Home & Kitchen", "cat-home", "Philips Digital Air Fryer HD9252/90 Rapid Air 4.1L", "Philips", 6999, 11995, 4.6, 14500, "Cook with up to 90% less fat. Patented Rapid Air technology creates delicious crispy food with little to no added oil.", {"Capacity": "4.1 Litres", "Power": "1400 Watts", "Presets": "7 Touchscreen Programs"}, "Philips Domestic", ["https://images.unsplash.com/photo-1556911220-e15b29be8c8f?w=800"]),
    ("Kitchen", "Home & Kitchen", "cat-home", "Prestige Iris Plus 750 Watt Mixer Grinder 4 Jars", "Prestige", 3199, 6295, 4.2, 29000, "Heavy-duty 750W motor with overload protection, 3 stainless steel jars with transparent lids + 1 polycarbonate juicer jar.", {"Motor": "750W 100% Copper", "Jars": "4 (3 SS + 1 Juicer)", "Warranty": "2 Years"}, "Prestige Home", ["https://images.unsplash.com/photo-1584269600464-37b1b58a9fe7?w=800"]),
    ("Kitchen", "Home & Kitchen", "cat-home", "Pigeon by Stovekraft Cruise 1800W Induction Cooktop", "Pigeon", 1699, 3195, 4.1, 23000, "Energy efficient 1800W heating plate, 7 pre-set Indian cooking menus, LED digital display with dual heat sensors.", {"Power": "1800 Watts", "Plate": "Microcrystalline Ceramic", "Safety": "Auto Shut-Off"}, "Stovekraft Official", ["https://images.unsplash.com/photo-1585670149967-b4f4da88cc9f?w=800"]),
    ("Home", "Home & Kitchen", "cat-home", "Dyson V8 Absolute Cordless Vacuum Cleaner", "Dyson", 29900, 43900, 4.7, 4100, "Up to 40 minutes of fade-free suction. De-tangling Motorbar cleaner head deep cleans carpets and hard floors.", {"Runtime": "40 Minutes", "Suction Power": "115 AW", "Filtration": "Whole-machine HEPA"}, "Dyson Official", ["https://images.unsplash.com/photo-1558317374-067fb5f30001?w=800"]),
    ("Home", "Home & Kitchen", "cat-home", "Wakefit Orthopedic Memory Foam Mattress Queen Size", "Wakefit", 10499, 15999, 4.6, 18200, "High-density pressure-relieving memory foam with differential zone support. Breathable, hypoallergenic removable cover.", {"Size": "Queen (78x60x6 inches)", "Warranty": "10 Years", "Layering": "Next-Gen Memory Foam"}, "Wakefit Official", ["https://images.unsplash.com/photo-1505693416388-ac5ce068fe85?w=800"]),
    ("Kitchen", "Home & Kitchen", "cat-home", "Milton Thermosteel Flip Lid 1000ml Flask", "Milton", 899, 1295, 4.5, 21000, "Double walled vacuum insulated 304 grade stainless steel flask. Keeps beverages piping hot or icy cold for 24 hours.", {"Capacity": "1000 ml", "Material": "SS 304", "Thermal Retention": "24 Hours Hot/Cold"}, "Milton Home", ["https://images.unsplash.com/photo-1602143407151-7111542de6e8?w=800"]),

    # Beauty & Personal Care
    ("Skincare", "Beauty & Personal Care", "cat-beauty", "The Derma Co 10% Vitamin C Face Serum for Glow", "The Derma Co", 549, 649, 4.4, 15200, "Formulated with 10% Vitamin C, 5% Niacinamide, and Hyaluronic Acid to brighten dark spots and protect against sun damage.", {"Key Ingredients": "10% Vitamin C, Niacinamide", "Skin Type": "All Skin Types", "Size": "30ml"}, "Honasa Consumer", ["https://images.unsplash.com/photo-1620916566398-39f1143ab7be?w=800"]),
    ("Skincare", "Beauty & Personal Care", "cat-beauty", "Minimalist 2% Salicylic Acid Face Serum for Acne", "Minimalist", 499, 549, 4.5, 22100, "Pure Salicylic Acid BHA formula that unclogs deep pores, controls sebum production, and prevents blackheads and breakouts.", {"Concentration": "2% Salicylic Acid", "Benefits": "Anti-Acne, Blackhead Control", "Size": "30ml"}, "Minimalist India", ["https://images.unsplash.com/photo-1608248597359-009947743d5c?w=800"]),
    ("Haircare", "Beauty & Personal Care", "cat-beauty", "L'Oreal Professionnel Absolut Repair Hair Mask", "L'Oreal", 860, 950, 4.6, 9400, "Infused with gold quinoa protein to visibly repair dry, damaged hair fiber, providing 77% less damage and 7x shinier hair.", {"Ideal For": "Damaged Hair", "Ingredient": "Gold Quinoa + Protein", "Weight": "250g"}, "Appario Retail", ["https://images.unsplash.com/photo-1527799820374-dcf8d9d4a388?w=800"]),
    ("Grooming", "Beauty & Personal Care", "cat-beauty", "Philips Series 3000 Showerproof Body Groomer BG3010", "Philips", 2299, 3195, 4.5, 12800, "Skin-friendly rounded contour blades with hypoallergenic foil foil protecting sensitive skin while trimming body hair.", {"Usage": "100% Showerproof", "Battery": "50 Mins Cordless", "Warranty": "2 Years"}, "Philips Personal", ["https://images.unsplash.com/photo-1585751119414-ef2636f8aede?w=800"]),

    # Sports & Fitness
    ("Fitness", "Sports & Fitness", "cat-sports", "Boldfit Adjustable Dumbbells Set with Connector 20KG", "Boldfit", 2499, 4999, 4.4, 7600, "Versatile 20kg weight set transforms from individual dumbbells into a long barbell using the non-slip foam connecting rod.", {"Total Weight": "20 KG", "Config": "Dumbbell + Barbell 2-in-1", "Plates": "Vinyl Coated PVC"}, "Boldfit Official", ["https://images.unsplash.com/photo-1584735935682-2f2b69dff9d2?w=800"]),
    ("Fitness", "Sports & Fitness", "cat-sports", "Lifelong LLF135 Fit Pro Motorized Treadmill 2.5HP", "Lifelong", 16999, 35000, 4.2, 3800, "Peak 2.5HP silent motor, max speed 12 km/h, shock-absorbing anti-skid running deck, foldable design with wheels.", {"Motor": "2.5 HP Peak", "Max Speed": "12 km/h", "Max Weight": "100 KG"}, "Lifelong Online", ["https://images.unsplash.com/photo-1540497077202-7c8a3999166f?w=800"]),
    ("Sports", "Sports & Fitness", "cat-sports", "Yonex Nanoray Light 18i Graphite Badminton Racket", "Yonex", 2199, 3990, 4.5, 14200, "Ultra lightweight 77g (5U) racket with isometric head frame, capable of withstanding string tension up to 30 lbs.", {"Weight": "5U (77 grams)", "Material": "Full Carbon Graphite", "Max Tension": "30 lbs"}, "Sunrise Sports", ["https://images.unsplash.com/photo-1626224583764-f87db24ac4ea?w=800"]),
    ("Fitness", "Sports & Fitness", "cat-sports", "Optimum Nutrition Gold Standard 100% Whey 2 lb", "Optimum Nutrition", 3299, 4199, 4.7, 19800, "24 grams of ultra-filtered whey protein isolate, 5.5 grams of naturally occurring BCAAs, and 4 grams of glutamine per scoop.", {"Protein per Scoop": "24g", "Flavour": "Double Rich Chocolate", "Weight": "2 lb"}, "Glanbia India", ["https://images.unsplash.com/photo-1579722821273-0f6c7d44362f?w=800"]),

    # Books & Stationery
    ("Books", "Books & Stationery", "cat-books", "The Psychology of Money by Morgan Housel", "Harriman House", 299, 399, 4.8, 48000, "Timeless lessons on wealth, greed, and happiness. 19 short stories exploring the strange ways people think about money.", {"Author": "Morgan Housel", "Pages": "256", "Format": "Paperback"}, "BookWorm India", ["https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=800"]),
    ("Books", "Books & Stationery", "cat-books", "Atomic Habits by James Clear Hardcover Edition", "Random House", 549, 799, 4.9, 65000, "No matter your goals, Atomic Habits offers a proven framework for improving every day from world-renowned habit expert.", {"Author": "James Clear", "Pages": "320", "Binding": "Hardcover"}, "BookWorm India", ["https://images.unsplash.com/photo-1544947950-fa07a98d237f?w=800"]),
    ("Books", "Books & Stationery", "cat-books", "Sapiens: A Brief History of Humankind", "Yuval Noah Harari", 449, 699, 4.8, 38000, "Explores how biology and history have defined us and enhanced our understanding of what it means to be human.", {"Author": "Yuval Noah Harari", "Pages": "512", "Language": "English"}, "Penguin Random House", ["https://images.unsplash.com/photo-1495446815901-a7297e633e8d?w=800"]),

    # Grocery & Gourmet
    ("Grocery", "Grocery & Gourmet", "cat-grocery", "Tata Tea Gold Leaf Tea 1kg with Long Leaves", "Tata Tea", 525, 650, 4.6, 21400, "A unique blend of rich CTC tea granules with 15% gently rolled long tea leaves for irresistible aroma and strong taste.", {"Net Quantity": "1000g", "Diet Type": "Vegetarian", "Form": "Loose Leaf"}, "Tata Consumer", ["https://images.unsplash.com/photo-1576092768241-dec231879fc3?w=800"]),
    ("Grocery", "Grocery & Gourmet", "cat-grocery", "Daawat Rozana Super Basmati Rice 5kg", "Daawat", 399, 575, 4.4, 16800, "Aged basmati rice with slender long grains, pleasant sweet aroma, and fluffy non-sticky texture after cooking.", {"Weight": "5 kg", "Grain Length": "Long Grain Basmati"}, "LT Foods", ["https://images.unsplash.com/photo-1586201375761-83865001e31c?w=800"]),
    ("Grocery", "Grocery & Gourmet", "cat-grocery", "Ferrero Rocher Premium Hazelnut Chocolates 24 Pieces", "Ferrero", 999, 1199, 4.8, 25000, "Whole crunchy hazelnut in the center, a delicious creamy hazelnut filling, and a crisp wafer shell covered with milk chocolate.", {"Units": "24 Pcs", "Weight": "300g", "Packaging": "Gift Box"}, "Ferrero India", ["https://images.unsplash.com/photo-1549007994-cb92caebd54b?w=800"]),
]

def seed_100_products():
    import uuid
    count = 0
    for subcat, cat_name, cat_id, title, brand, price, orig_price, rating, rev_count, desc, specs, seller, img_list in catalog_blueprints:
        slug_base = title.lower().replace(" ", "-").replace("(", "").replace(")", "").replace(",", "")
        
        # 1. Base Product
        u1 = uuid.uuid4().hex[:8]
        p_id = f"prod-bulk-{u1}"
        discount = int(((orig_price - price) / orig_price) * 100)
        Product.objects.create(
            id=p_id,
            name=title,
            slug=f"{slug_base}-{u1}",
            category=cat_name,
            categoryId=cat_id,
            brand=brand,
            price=float(price),
            originalPrice=float(orig_price),
            discount=discount,
            rating=float(rating),
            reviewCount=rev_count,
            stock=random.randint(25, 200),
            stockStatus="In Stock",
            featured=random.choice([True, False]),
            bestSeller=rating >= 4.6,
            newArrival=random.choice([True, False]),
            images=img_list,
            description=desc,
            specifications=specs,
            seller=seller,
            createdAt="2026-10-10"
        )
        count += 1

        # 2. Enhanced / Pro Edition
        suffixes = ["Pro Edition", "Midnight Black", "Special Edition", "Plus Variant", "Platinum Grey"]
        suffix = random.choice(suffixes)
        var_price = round(price * random.choice([0.9, 1.15, 1.25]))
        var_orig = round(var_price * 1.3)
        u2 = uuid.uuid4().hex[:8]
        var_p_id = f"prod-bulk-{u2}"
        var_disc = int(((var_orig - var_price) / var_orig) * 100)
        
        Product.objects.create(
            id=var_p_id,
            name=f"{title} - {suffix}",
            slug=f"{slug_base}-{suffix.lower().replace(' ', '-')}-{u2}",
            category=cat_name,
            categoryId=cat_id,
            brand=brand,
            price=float(var_price),
            originalPrice=float(var_orig),
            discount=var_disc,
            rating=round(max(3.8, min(4.9, rating + random.choice([-0.1, 0.1]))), 1),
            reviewCount=int(rev_count * random.uniform(0.6, 1.2)),
            stock=random.randint(15, 120),
            stockStatus="In Stock",
            featured=False,
            bestSeller=False,
            newArrival=True,
            images=img_list,
            description=f"{desc} Upgraded {suffix} with enhanced materials and extended warranty.",
            specifications=specs,
            seller=seller,
            createdAt="2026-10-11"
        )
        count += 1

        # 3. Budget / Value Edition
        comp_price = round(price * 0.72)
        comp_orig = round(comp_price * 1.35)
        u3 = uuid.uuid4().hex[:8]
        comp_p_id = f"prod-bulk-{u3}"
        comp_disc = int(((comp_orig - comp_price) / comp_orig) * 100)
        Product.objects.create(
            id=comp_p_id,
            name=f"{brand} Essential {subcat} Edition",
            slug=f"{brand.lower()}-essential-{subcat.lower()}-{u3}",
            category=cat_name,
            categoryId=cat_id,
            brand=brand,
            price=float(comp_price),
            originalPrice=float(comp_orig),
            discount=comp_disc,
            rating=round(max(3.9, min(4.8, rating - 0.2)), 1),
            reviewCount=int(rev_count * 0.45),
            stock=random.randint(30, 150),
            stockStatus="In Stock",
            featured=False,
            bestSeller=False,
            newArrival=False,
            images=img_list,
            description=f"Value-optimized alternative delivering core performance and durability for {subcat}.",
            specifications=specs,
            seller=seller,
            createdAt="2026-10-12"
        )
        count += 1

    # 4. Update Category product counts
    for cat in Category.objects.all():
        cat.productCount = Product.objects.filter(category=cat.name).count()
        cat.save()

    print(f"Successfully created {count} products!")
    print(f"Total products in AutoCart catalog: {Product.objects.count()}")

if __name__ == "__main__":
    seed_100_products()
