"""
AutoCart 300 Products Catalog Expansion Script
Increases the product catalog from 90 to exactly 300 high-quality, realistic e-commerce products.
Populates StoreInventory mappings across stores and synchronizes Category product counters.
"""
import os
import sys
import random
import uuid
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'autocart_core.settings')
import django
django.setup()

from api.models import Product, Category, Store, StoreInventory

NEW_PRODUCTS = [
    # ---------------- ELECTRONICS (27 products) ----------------
    (
        "cat-1", "Electronics", "Lenovo ThinkPad X1 Carbon Gen 11 Ultrabook", "Lenovo",
        149990, 189990, 4.8, 920,
        "Ultralight business laptop with carbon-fiber reinforced chassis, 13th Gen Intel Core i7, 2.8K OLED display, and all-day battery life with Rapid Charge.",
        {"Processor": "Intel Core i7-1365U", "RAM": "16GB LPDDR5", "Storage": "1TB PCIe NVMe SSD", "Display": "14-inch 2.8K OLED", "Weight": "1.12 kg"},
        "Appario Retail",
        ["https://images.unsplash.com/photo-1588872657578-7efd1f1555ed?w=800"]
    ),
    (
        "cat-1", "Electronics", "ASUS ROG Zephyrus G14 Gaming Laptop", "ASUS",
        134990, 164990, 4.7, 1420,
        "Compact 14-inch gaming powerhouse with AMD Ryzen 9 7940HS, NVIDIA RTX 4060, ROG Nebula 165Hz QHD+ display, and AniMe Matrix lid display.",
        {"Processor": "AMD Ryzen 9 7940HS", "GPU": "NVIDIA RTX 4060 8GB", "RAM": "16GB DDR5", "Display": "14-inch QHD+ 165Hz"},
        "Appario Retail",
        ["https://images.unsplash.com/photo-1593642632823-8f785ba67e45?w=800"]
    ),
    (
        "cat-1", "Electronics", "HP Spectre x360 2-in-1 OLED Touch Laptop", "HP",
        124990, 154990, 4.6, 780,
        "Precision-crafted gem-cut aluminum convertible laptop with 3K2K OLED touch display, Intel Core i7 Evo, rechargeable MPP 2.0 tilt pen included.",
        {"Processor": "Intel Core i7-1355U", "RAM": "16GB LPDDR4x", "Storage": "512GB NVMe SSD", "Display": "13.5-inch 3K2K OLED Touch"},
        "HP Store",
        ["https://images.unsplash.com/photo-1541807084-5c52b6b3adef?w=800"]
    ),
    (
        "cat-1", "Electronics", "LG UltraGear 27-inch 144Hz IPS Gaming Monitor", "LG",
        22999, 32000, 4.7, 3450,
        "QHD (2560 x 1440) Nano IPS display with 1ms GtG response time, NVIDIA G-SYNC Compatible, AMD FreeSync Premium, HDR10 with 98% DCI-P3 color gamut.",
        {"Resolution": "2560 x 1440 QHD", "Refresh Rate": "144Hz", "Response Time": "1ms GtG", "Panel": "Nano IPS"},
        "Electronics Bazaar",
        ["https://images.unsplash.com/photo-1527443224154-c4a3942d3acf?w=800"]
    ),
    (
        "cat-1", "Electronics", "Samsung Odyssey G7 32-inch Curved QLED Gaming Monitor", "Samsung",
        45999, 62000, 4.8, 1890,
        "Deep 1000R curvature matching human field of view, 240Hz refresh rate, 1ms response, Quantum Dot color technology with HDR600 peak brightness.",
        {"Screen Size": "32 inches", "Curvature": "1000R", "Refresh Rate": "240Hz", "Technology": "QLED + HDR600"},
        "Samsung Official Store",
        ["https://images.unsplash.com/photo-1547119957-637f8679db1e?w=800"]
    ),
    (
        "cat-1", "Electronics", "Keychron K2 Wireless Mechanical Keyboard (Hot-Swappable)", "Keychron",
        7999, 10999, 4.7, 4200,
        "Compact 75% layout wireless Bluetooth mechanical keyboard with RGB backlighting, Mac and Windows compatibility, Gateron G Pro mechanical switches.",
        {"Layout": "75% Compact (84 keys)", "Connectivity": "Bluetooth 5.1 & Type-C", "Battery": "4000 mAh", "Switches": "Gateron Brown"},
        "Appario Retail",
        ["https://images.unsplash.com/photo-1587829741301-dc798b83add3?w=800"]
    ),
    (
        "cat-1", "Electronics", "Logitech G502 HERO High Performance Gaming Mouse", "Logitech",
        3995, 4995, 4.8, 28900,
        "HERO 25K optical sensor with sub-micron tracking, 11 programmable buttons, adjustable weights, and LIGHTSYNC customizable RGB lighting.",
        {"Sensor": "HERO 25K DPI", "Buttons": "11 Programmable", "Weights": "5x 3.6g adjustable", "Connectivity": "USB Wired"},
        "Logitech Official Store",
        ["https://images.unsplash.com/photo-1615663245857-ac93bb7c39e7?w=800"]
    ),
    (
        "cat-1", "Electronics", "Corsair K70 RGB PRO Mechanical Gaming Keyboard", "Corsair",
        13999, 17999, 4.6, 1250,
        "Durable brushed aluminum frame, CHERRY MX Speed Silver optical-mechanical switches with 8000Hz hyper-polling powered by AXON technology.",
        {"Switches": "CHERRY MX Speed Silver", "Polling Rate": "8000Hz AXON", "Keycaps": "Double-shot PBT", "Lighting": "Per-key RGB"},
        "Appario Retail",
        ["https://images.unsplash.com/photo-1595225476474-87563907a212?w=800"]
    ),
    (
        "cat-1", "Electronics", "Sony WH-CH720N Noise Cancelling Wireless Headphones", "Sony",
        9990, 14990, 4.5, 6100,
        "Lightweight comfortable over-ear design powered by Integrated Processor V1, dual noise sensor technology, up to 35 hours battery life.",
        {"Type": "Over-Ear Wireless", "ANC": "Integrated Processor V1", "Battery": "35 Hours", "Weight": "192g"},
        "boAt Official Store",
        ["https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=800"]
    ),
    (
        "cat-1", "Electronics", "Apple AirPods Pro (2nd Gen) with USB-C Charging Case", "Apple",
        22990, 24900, 4.8, 14200,
        "Up to 2x more Active Noise Cancellation, Adaptive Audio, Transparency mode, Personalized Spatial Audio with dynamic head tracking, MagSafe USB-C case.",
        {"Chip": "H2 Headphone Chip", "ANC": "Adaptive Audio + Active ANC", "Water Resistance": "IP54 Sweat and Water", "Charging": "USB-C MagSafe"},
        "Apple Official Store",
        ["https://images.unsplash.com/photo-1600294037681-c80b4cb5b434?w=800"]
    ),
    (
        "cat-1", "Electronics", "Marshall Stanmore III Bluetooth Home Speaker", "Marshall",
        34999, 39999, 4.8, 1100,
        "Iconic vintage aesthetic room-filling speaker with re-engineered wider soundstage, Bluetooth 5.2, 3.5mm AUX and RCA inputs, 80W Class D output.",
        {"Total Power": "80W Class D", "Drivers": "One 50W Woofer + Two 15W Tweeters", "Frequency": "45–20,000 Hz"},
        "Electronics Bazaar",
        ["https://images.unsplash.com/photo-1545454675-3531b543be5d?w=800"]
    ),
    (
        "cat-1", "Electronics", "JBL Bar 500 Pro Dolby Atmos 5.1ch Soundbar", "JBL",
        44999, 59999, 4.7, 980,
        "MultiBeam technology delivering true 3D spatial sound, 10-inch wireless down-firing subwoofer, 590W total output, AirPlay, Alexa and Chromecast built-in.",
        {"Total Output": "590W", "Subwoofer": "10-inch Wireless 300W", "Surround": "Dolby Atmos 5.1 MultiBeam"},
        "boAt Official Store",
        ["https://images.unsplash.com/photo-1545454675-3531b543be5d?w=800"]
    ),
    (
        "cat-1", "Electronics", "Audio-Technica ATH-M50x Professional Studio Monitor Headphones", "Audio-Technica",
        13490, 18990, 4.8, 19400,
        "Critically acclaimed sonic performance praised by top audio engineers, proprietary 45mm large-aperture drivers, 90-degree swiveling earcups.",
        {"Driver Size": "45mm Neodymium", "Frequency Response": "15 - 28,000 Hz", "Design": "Circumaural Closed-Back"},
        "Appario Retail",
        ["https://images.unsplash.com/photo-1546435770-a3e426bf472b?w=800"]
    ),
    (
        "cat-1", "Electronics", "Google Pixel 8 Pro 5G (128GB, Obsidian)", "Google",
        79999, 106999, 4.7, 4300,
        "Google Tensor G3 AI processor, 6.7-inch Super Actua 1-120Hz display, pro triple camera system with Best Take, Magic Editor, and Audio Magic Eraser.",
        {"Processor": "Google Tensor G3", "Display": "6.7-inch Super Actua LTPO", "Camera": "50MP Main + 48MP UW + 48MP Telephoto"},
        "Appario Retail",
        ["https://images.unsplash.com/photo-1598327105666-5b89351aff97?w=800"]
    ),
    (
        "cat-1", "Electronics", "Apple iPad Air 11-inch (M2 Chip, 128GB, Wi-Fi)", "Apple",
        59900, 64900, 4.8, 3800,
        "Blazing-fast Apple M2 chip, gorgeous 11-inch Liquid Retina display with P3 wide color, landscape 12MP Center Stage camera, Apple Pencil Pro support.",
        {"Chip": "Apple M2 (8-core CPU, 10-core GPU)", "Display": "11-inch Liquid Retina", "Storage": "128GB"},
        "Apple Official Store",
        ["https://images.unsplash.com/photo-1544244015-0df4b3ffc6b0?w=800"]
    ),
    (
        "cat-1", "Electronics", "Samsung Galaxy Tab S9 FE 10.9-inch with S-Pen", "Samsung",
        34999, 44999, 4.6, 5200,
        "IP68 water and dust resistant tablet with responsive in-box S-Pen, 90Hz adaptive display, 8000 mAh long-lasting battery, dual AKG speakers.",
        {"Screen": "10.9-inch 90Hz WQXGA", "Battery": "8000 mAh", "Pen": "S-Pen Included in Box", "Water Resistance": "IP68"},
        "Samsung Official Store",
        ["https://images.unsplash.com/photo-1561154464-82e9adf32764?w=800"]
    ),
    (
        "cat-1", "Electronics", "Amazfit GTR 4 Smart Watch with Dual-Band GPS", "Amazfit",
        15999, 23999, 4.4, 3800,
        "Industry-first circularly-polarized dual-band GPS antenna, 1.43-inch HD AMOLED display, 150+ sports modes, 14-day ultra-long battery life.",
        {"Display": "1.43-inch HD AMOLED", "GPS": "Dual-Band 6 Satellite Systems", "Battery": "14 Days Typical Usage"},
        "Appario Retail",
        ["https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=800"]
    ),
    (
        "cat-1", "Electronics", "Anker 737 Power Bank (PowerCore 24K, 140W Two-Way)", "Anker",
        11999, 14999, 4.8, 2900,
        "Ultra-powerful 140W bi-directional fast charging with Power Delivery 3.1, smart digital display showing live output wattage, 24,000 mAh capacity.",
        {"Capacity": "24,000 mAh", "Max Output": "140W USB-C PD 3.1", "Ports": "2x USB-C + 1x USB-A"},
        "Appario Retail",
        ["https://images.unsplash.com/photo-1609592424350-0255b768a44c?w=800"]
    ),
    (
        "cat-1", "Electronics", "Belkin 3-in-1 Fast Wireless Charging Pad with MagSafe", "Belkin",
        12999, 15999, 4.7, 1800,
        "Official MagSafe 15W fast wireless charging station for iPhone 15/14/13, Apple Watch Ultra/Series 9 fast charger, and dedicated AirPods Qi tray.",
        {"Output": "15W MagSafe Fast Charge", "Compatibility": "iPhone, Apple Watch, AirPods", "Design": "Lay-flat Travel Friendly"},
        "Appario Retail",
        ["https://images.unsplash.com/photo-1622445268096-7787f739fcfa?w=800"]
    ),
    (
        "cat-1", "Electronics", "Sony Alpha 7 IV Full-Frame Mirrorless Camera Body", "Sony",
        209990, 242990, 4.9, 1150,
        "33MP full-frame Exmor R back-illuminated sensor, 4K 60p 10-bit 4:2:2 video, real-time eye AF for humans, animals and birds, 759 phase-detection points.",
        {"Sensor": "33MP Full-Frame BSI CMOS", "Video": "4K 60p 10-bit 4:2:2", "Stabilization": "5-axis In-body IS (5.5 stops)"},
        "Electronics Bazaar",
        ["https://images.unsplash.com/photo-1516035069371-29a1b244cc32?w=800"]
    ),
    (
        "cat-1", "Electronics", "GoPro HERO12 Black 5.3K Action Camera", "GoPro",
        37990, 45000, 4.7, 4500,
        "Incredible 5.3K60 and 4K120 video resolution, Emmy award-winning HyperSmooth 6.0 stabilization with 360-degree horizon lock, waterproof down to 33 feet.",
        {"Video": "5.3K60 / 4K120 / 2.7K240", "Stabilization": "HyperSmooth 6.0 + 360 Horizon Lock", "Waterproof": "10m without housing"},
        "Appario Retail",
        ["https://images.unsplash.com/photo-1526170375885-4d8ecf77b99f?w=800"]
    ),
    (
        "cat-1", "Electronics", "DJI Mini 4 Pro Drone with RC 2 Controller", "DJI",
        94990, 112000, 4.8, 890,
        "Sub-249g ultra-lightweight folding drone, omnidirectional obstacle sensing, 4K/60fps HDR true vertical shooting, 34-minute flight endurance.",
        {"Weight": "Under 249 grams", "Obstacle Sensing": "Omnidirectional ActiveTrack 360", "Flight Time": "Up to 34 Mins"},
        "Electronics Bazaar",
        ["https://images.unsplash.com/photo-1508614589041-895b88991e3e?w=800"]
    ),
    (
        "cat-1", "Electronics", "Elgato Stream Deck MK.2 Studio Controller", "Elgato",
        13499, 16999, 4.8, 3800,
        "15 customizable LCD keys to control apps, tools and platforms with one touch. Detachable desktop stand, interchangeable faceplates, macro chaining.",
        {"Keys": "15 Customizable LCD Buttons", "Interface": "USB 2.0 Type-C", "Compatibility": "OBS, Twitch, YouTube, Spotify"},
        "Appario Retail",
        ["https://images.unsplash.com/photo-1595225476474-87563907a212?w=800"]
    ),
    (
        "cat-1", "Electronics", "Logitech Brio 4K Ultra HD Pro Webcam", "Logitech",
        16995, 24995, 4.6, 6200,
        "Ultra 4K HD video calling at 30 fps, RightLight 3 with HDR automatically adjusts to highlight face in backlighting, dual omni-directional noise-canceling mics.",
        {"Resolution": "4K UHD 30fps / 1080p 60fps", "HDR": "RightLight 3 Auto Adjust", "Field of View": "65 / 78 / 90 degrees"},
        "Logitech Official Store",
        ["https://images.unsplash.com/photo-1587829741301-dc798b83add3?w=800"]
    ),
    (
        "cat-1", "Electronics", "Xiaomi Smart TV X Pro 55-inch 4K Google TV", "Xiaomi",
        41999, 49999, 4.5, 8700,
        "Vivid 4K Dolby Vision IQ display, premium metal bezel-less frame, 30W stereo speakers with Dolby Atmos and DTS:X, hands-free Google Assistant.",
        {"Screen": "55-inch 4K HDR10+ Dolby Vision IQ", "Audio": "30W Dolby Atmos", "OS": "Google TV with PatchWall"},
        "Xiaomi Official Store",
        ["https://images.unsplash.com/photo-1593784991095-a205069470b6?w=800"]
    ),
    (
        "cat-1", "Electronics", "OnePlus Pad 11.61-inch 144Hz 8GB RAM 128GB Tablet", "OnePlus",
        34999, 39999, 4.6, 4200,
        "Unique 7:5 ReadFit aspect ratio, 144Hz refresh rate 2.8K display, MediaTek Dimensity 9000 flagship chip, 67W SUPERVOOC charging with 9510 mAh battery.",
        {"Display": "11.61-inch 144Hz 7:5 ReadFit", "Chipset": "MediaTek Dimensity 9000", "Charging": "67W Fast Charge"},
        "OnePlus Official",
        ["https://images.unsplash.com/photo-1544244015-0df4b3ffc6b0?w=800"]
    ),
    (
        "cat-1", "Electronics", "SanDisk Extreme 1TB Portable External NVMe SSD", "SanDisk",
        9999, 14999, 4.8, 18400,
        "Blazing fast read speeds up to 1050MB/s and write up to 1000MB/s, 2-meter drop protection, IP55 water and dust resistance with durable silicone shell.",
        {"Capacity": "1TB NVMe", "Speed": "Up to 1050 MB/s", "Durability": "IP55 Water & Dust Resistant"},
        "Appario Retail",
        ["https://images.unsplash.com/photo-1597872200969-2b65d56bd16b?w=800"]
    ),

    # ---------------- FASHION (27 products) ----------------
    (
        "cat-2", "Fashion", "Tommy Hilfiger Classic Pique Slim Fit Polo T-Shirt", "Tommy Hilfiger",
        2799, 3999, 4.5, 3400,
        "100% breathable organic cotton pique knit, ribbed polo collar with two-button placket, signature Tommy Hilfiger flag embroidery on the chest.",
        {"Fabric": "100% Organic Cotton", "Fit": "Slim Fit", "Pattern": "Solid Pique"},
        "Aditya Birla Fashion",
        ["https://images.unsplash.com/photo-1586363104862-3a5e2ab60d99?w=800"]
    ),
    (
        "cat-2", "Fashion", "Levi's Men's The Trucker Denim Jacket Medium Indigo", "Levi's",
        3899, 5999, 4.7, 5100,
        "The original jean jacket since 1967. Sturdy non-stretch denim with point collar, front button placket, button-flap chest pockets and side welt pockets.",
        {"Material": "100% Heavyweight Cotton Denim", "Wash": "Medium Indigo", "Closure": "Button Front"},
        "Levi Strauss India",
        ["https://images.unsplash.com/photo-1576995853123-5a10305d93c0?w=800"]
    ),
    (
        "cat-2", "Fashion", "Peter England Royal Blue Textured Slim Fit Formal Blazer", "Peter England",
        4999, 7999, 4.4, 2100,
        "Single-breasted 2-button notch lapel blazer crafted from wrinkle-resistant poly-viscose blend. Perfect for formal business meetings and celebratory occasions.",
        {"Fabric": "Poly-Viscose Stretch Blend", "Lapel": "Notch Lapel", "Fit": "Slim Fit"},
        "Aditya Birla Fashion",
        ["https://images.unsplash.com/photo-1507679799987-c73779587ccf?w=800"]
    ),
    (
        "cat-2", "Fashion", "Flying Machine Men's Slim Tapered Stretch Chinos", "Flying Machine",
        1499, 2499, 4.3, 4800,
        "Versatile everyday chinos tailored with cotton-twill stretch fabric. Features clean slant pockets and buttoned back welt pockets.",
        {"Material": "98% Cotton, 2% Spandex", "Rise": "Mid-Rise", "Fit": "Slim Tapered"},
        "Appario Retail",
        ["https://images.unsplash.com/photo-1473966968600-fa801b869a1a?w=800"]
    ),
    (
        "cat-2", "Fashion", "U.S. Polo Assn. Long Sleeve Oxford Button-Down Shirt", "U.S. Polo Assn.",
        1799, 2999, 4.4, 6200,
        "Classic casual shirt woven from long-staple combed cotton oxford cloth. Finished with button-down collar and authentic double-horseman chest logo.",
        {"Fabric": "100% Combed Cotton", "Sleeve": "Long Sleeve", "Fit": "Custom Fit"},
        "Aditya Birla Fashion",
        ["https://images.unsplash.com/photo-1602810318383-e386cc2a3ccf?w=800"]
    ),
    (
        "cat-2", "Fashion", "Fabindia Hand-Block Printed Tussar Silk Saree", "Fabindia",
        7990, 11990, 4.8, 1400,
        "Authentic pure Tussar silk drape handcrafted by traditional artisans using wooden blocks and natural vegetable dyes. Includes unstitched blouse piece.",
        {"Material": "100% Pure Tussar Silk", "Length": "6.3 Meters with Blouse", "Craft": "Hand-Block Print"},
        "Biba Apparels",
        ["https://images.unsplash.com/photo-1610030469983-98e550d6193c?w=800"]
    ),
    (
        "cat-2", "Fashion", "Global Desi Bohemian Floral Tiered Maxi Dress", "Global Desi",
        2199, 3999, 4.5, 2300,
        "Vibrant bohemian printed tiered dress with smocked bodice, ruffled cap sleeves, and breathable viscose fabric that drapes effortlessly.",
        {"Fabric": "100% Viscose Rayon", "Length": "Ankle Length Maxi", "Neck": "Square Neck"},
        "Biba Apparels",
        ["https://images.unsplash.com/photo-1572804013309-59a88b7e92f1?w=800"]
    ),
    (
        "cat-2", "Fashion", "Zara Style Double-Breasted Wool Blend Trench Coat", "Zara Style",
        6990, 9990, 4.6, 950,
        "Timeless structured trench coat featuring tortoiseshell buttons, storm flaps, removable waist belt, and premium thermal wool-blend insulation.",
        {"Material": "60% Wool, 40% Polyester", "Closure": "Double-Breasted", "Length": "Knee-Length"},
        "Appario Retail",
        ["https://images.unsplash.com/photo-1544441893-675973e31985?w=800"]
    ),
    (
        "cat-2", "Fashion", "Vero Moda High-Waist Pleated Wide-Leg Trousers", "Vero Moda",
        1899, 3299, 4.4, 3100,
        "Chic workwear trousers with elegant front pleats, high-rise contour waistband, side pockets, and wide straight leg cut for elevated styling.",
        {"Fabric": "Polyester Spandex Crepe", "Fit": "Wide Leg", "Rise": "High Rise"},
        "Appario Retail",
        ["https://images.unsplash.com/photo-1594633312681-425c7b97ccd1?w=800"]
    ),
    (
        "cat-2", "Fashion", "Levi's 721 High Rise Skinny Jeans for Women", "Levi's",
        2699, 4299, 4.6, 7800,
        "Flattering high-rise waist with Levi's Sculpt Hyperstretch fabric that hugs curves, holds shape, and won't bag out throughout the day.",
        {"Material": "70% Cotton, 20% Polyester, 8% Viscose, 2% Elastane", "Rise": "High Rise (10.25 inch)", "Leg": "Skinny"},
        "Levi Strauss India",
        ["https://images.unsplash.com/photo-1541099649105-f69ad21f3246?w=800"]
    ),
    (
        "cat-2", "Fashion", "Adidas Ultraboost Light Running Shoes", "Adidas",
        10999, 15999, 4.8, 6400,
        "Lightest BOOST foam yet for explosive energy return on every stride. Primeknit+ upper hugs the foot with tailored support.",
        {"Midsole": "Light BOOST Foam", "Upper": "Adidas Primeknit+", "Outsole": "Continental Natural Rubber"},
        "Appario Retail",
        ["https://images.unsplash.com/photo-1587563871167-1ee9c731aefb?w=800"]
    ),
    (
        "cat-2", "Fashion", "Converse Chuck Taylor All Star Classic High Top Canvas", "Converse",
        3499, 4999, 4.7, 18200,
        "Timeless ankle-high canvas silhouette with diamond pattern rubber tread, medial eyelets for airflow, and iconic All Star ankle patch.",
        {"Upper": "Heavyweight Canvas", "Sole": "Vulcanized Rubber", "Insole": "OrthoLite Cushioning"},
        "Appario Retail",
        ["https://images.unsplash.com/photo-1525966222134-fcfa99b8ae77?w=800"]
    ),
    (
        "cat-2", "Fashion", "Clarks Tilden Cap Leather Derby Formal Shoes", "Clarks",
        4499, 6999, 4.6, 4200,
        "Supple genuine full-grain leather upper with classic cap toe detailing, OrthoLite footbed with Cushion Soft technology for all-day office comfort.",
        {"Upper": "100% Genuine Full-Grain Leather", "Insole": "OrthoLite Cushion Soft", "Closure": "Lace-Up"},
        "Appario Retail",
        ["https://images.unsplash.com/photo-1614252235316-8c857d38b5f4?w=800"]
    ),
    (
        "cat-2", "Fashion", "Skechers Men's GO WALK 6 Stretch Fit Slip-On Shoes", "Skechers",
        3699, 5499, 4.5, 9800,
        "Lightweight ULTRA GO cushioning with high-rebound Hyper Pillar Technology for enhanced support, breathable athletic engineered mesh upper.",
        {"Cushioning": "ULTRA GO Midsole", "Pillars": "High-Rebound Hyper Pillar", "Style": "Hands-Free Slip-On"},
        "Appario Retail",
        ["https://images.unsplash.com/photo-1595950653106-6c9ebd614d3a?w=800"]
    ),
    (
        "cat-2", "Fashion", "Birkenstock Arizona Two-Strap Cork Footbed Sandals", "Birkenstock",
        5990, 7990, 4.7, 7300,
        "Anatomically shaped cork-latex footbed with suede lining, durable Birko-Flor synthetic upper, dual individually adjustable metal pin buckles.",
        {"Footbed": "Natural Cork-Latex", "Lining": "Suede Leather", "Made In": "Germany"},
        "Appario Retail",
        ["https://images.unsplash.com/photo-1603808033192-082d6919d3e1?w=800"]
    ),
    (
        "cat-2", "Fashion", "Woodland Men's Camel Rugged Leather Outdoor Boots", "Woodland",
        3895, 4995, 4.4, 11200,
        "Heavy-duty nubuck leather construction with grooved high-traction rubber outsole designed for rough terrains, hiking trails, and urban street style.",
        {"Material": "Genuine Nubuck Leather", "Sole": "Grooved Thermoplastic Rubber", "Ankle": "Padded Collar"},
        "Appario Retail",
        ["https://images.unsplash.com/photo-1520639888713-7851133b1ed0?w=800"]
    ),
    (
        "cat-2", "Fashion", "Fossil Men's Derrick RFID-Blocking Leather Bifold Wallet", "Fossil",
        2495, 3495, 4.7, 6500,
        "Crafted from premium 100% genuine vintage leather with special RFID-blocking lining to protect credit and debit cards from electronic theft.",
        {"Material": "100% Genuine Cowhide Leather", "Slots": "8 Card Slots, 2 Slip Pockets, 1 Bill Compartment", "Security": "RFID Blocking"},
        "Titan Company Ltd",
        ["https://images.unsplash.com/photo-1627123424574-724758594e93?w=800"]
    ),
    (
        "cat-2", "Fashion", "Michael Kors Jet Set Travel Saffiano Leather Tote Bag", "Michael Kors",
        14990, 24900, 4.8, 1900,
        "Structured scratch-resistant Saffiano leather tote with polished gold-tone hardware, top zip fastening, and generous interior laptop divider.",
        {"Material": "100% Saffiano Leather", "Dimensions": "15 W x 10 H x 4.5 D inches", "Hardware": "Gold-Tone"},
        "Luxottica Retail",
        ["https://images.unsplash.com/photo-1584917865442-de89df76afd3?w=800"]
    ),
    (
        "cat-2", "Fashion", "Oakley Holbrook Matte Black Prizm Black Sunglasses", "Oakley",
        7990, 9990, 4.8, 3200,
        "Classic American frame design accented by metal rivets and Oakley square-O icons. Prizm lenses maximize contrast and enhance visibility in bright light.",
        {"Frame": "O Matter Lightweight Stress-Resistant", "Lens": "Prizm Black", "UV Protection": "100% UV400"},
        "Luxottica Retail",
        ["https://images.unsplash.com/photo-1511499767150-a48a237f0083?w=800"]
    ),
    (
        "cat-2", "Fashion", "American Tourister 32L Water-Resistant Laptop Backpack", "American Tourister",
        1699, 3200, 4.4, 14200,
        "Durable 600D ripstop polyester with 3 large zippered compartments, dedicated 15.6-inch padded laptop pocket, and Ergo-on-back airflow mesh padding.",
        {"Capacity": "32 Litres", "Laptop Sleeve": "Fits up to 15.6 inches", "Warranty": "1 Year International"},
        "Swift Logistics & Retailers",
        ["https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=800"]
    ),
    (
        "cat-2", "Fashion", "Daniel Wellington Classic Sheffield 40mm Rose Gold Watch", "Daniel Wellington",
        11999, 16999, 4.7, 4100,
        "Ultra-thin 6mm case in rose gold-tone stainless steel with eggshell white dial and genuine Italian black leather strap. Japanese quartz movement.",
        {"Case Thickness": "6mm", "Dial Size": "40mm", "Strap": "Genuine Italian Leather", "Movement": "Japanese Quartz"},
        "Titan Company Ltd",
        ["https://images.unsplash.com/photo-1524805444758-089113d48a6d?w=800"]
    ),
    (
        "cat-2", "Fashion", "Ray-Ban Clubmaster Classic Mock Tortoise Sunglasses", "Ray-Ban",
        8990, 10990, 4.8, 4800,
        "Retro browline style sunglasses favored by cultural intellectuals. Polished acetate frame with gold rims and classic G-15 mineral glass lenses.",
        {"Model": "RB3016 Clubmaster", "Lens": "Green G-15 Crystal", "Frame": "Tortoise and Gold Metal"},
        "Luxottica Retail",
        ["https://images.unsplash.com/photo-1511499767150-a48a237f0083?w=800"]
    ),
    (
        "cat-2", "Fashion", "Biba Women's Embroidered Georgette Dupatta Navy Blue", "Biba",
        899, 1499, 4.4, 2900,
        "Lightweight georgette dupatta accented with delicate sequin bootis and fine zari embroidery along the scalloped borders.",
        {"Fabric": "Poly Georgette", "Length": "2.25 Meters", "Work": "Zari and Sequin Embroidery"},
        "Biba Apparels",
        ["https://images.unsplash.com/photo-1610030469983-98e550d6193c?w=800"]
    ),
    (
        "cat-2", "Fashion", "Under Armour Men's Tech 2.0 Short-Sleeve Athletic T-Shirt", "Under Armour",
        1399, 1999, 4.5, 8700,
        "UA Tech fabric is quick-drying, ultra-soft and has a more natural feel. Anti-odor technology prevents the growth of odor-causing microbes.",
        {"Material": "100% Polyester UA Tech", "Fit": "Loose Fit", "Technology": "Moisture Transport System"},
        "Puma Sports India",
        ["https://images.unsplash.com/photo-1521572267360-ee0c2909d518?w=800"]
    ),
    (
        "cat-2", "Fashion", "Wildcraft 45L Unisex Rucksack for Trekking with Rain Cover", "Wildcraft",
        2899, 4499, 4.6, 6100,
        "Engineered for weekend hikes and backpacking trips. Ergonomic padded waist belt, adjustable sternum strap, integrated neon waterproof rain cover.",
        {"Capacity": "45 Litres", "Rain Cover": "Included in base pocket", "Material": "High-Density Nylon"},
        "Wildcraft Official Store",
        ["https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=800"]
    ),
    (
        "cat-2", "Fashion", "Campus Men's OXYFIT Running Shoes Navy Blue", "Campus",
        1199, 1899, 4.2, 13400,
        "Knitted upper for snug flexible fit with supportive TPU heel counter and cushioned Springy Fit midsole for daily jogging and gym sessions.",
        {"Upper": "Breathable Mesh Knit", "Closure": "Lace-Up", "Sole": "Phylon + Rubber Grip"},
        "Campus Official Store",
        ["https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=800"]
    ),
    (
        "cat-2", "Fashion", "Tommy Hilfiger Men's Reversible Genuine Leather Belt", "Tommy Hilfiger",
        1999, 2999, 4.5, 4300,
        "Versatile 2-in-1 reversible design with classic black on one side and rich brown on the other. Polished gunmetal twist buckle with engraved logo.",
        {"Material": "100% Genuine Full-Grain Leather", "Width": "35mm", "Design": "Reversible Black/Brown"},
        "Aditya Birla Fashion",
        ["https://images.unsplash.com/photo-1624222247344-550fb60583dc?w=800"]
    ),

    # ---------------- HOME & KITCHEN (27 products) ----------------
    (
        "cat-3", "Home & Kitchen", "Instant Pot Duo 7-in-1 Electric Pressure Cooker 6 Qt", "Instant Pot",
        8999, 12999, 4.8, 16800,
        "Replaces 7 appliances: pressure cooker, slow cooker, rice cooker, steamer, sauté pan, yogurt maker, and food warmer with 13 smart touch programs.",
        {"Capacity": "5.7 Litres (6 Quart)", "Power": "1000 Watts", "Programs": "13 One-Touch Cooking Modes", "Pot": "Food Grade 304 SS"},
        "Appario Retail",
        ["https://images.unsplash.com/photo-1556911220-e15b29be8c8f?w=800"]
    ),
    (
        "cat-3", "Home & Kitchen", "Morphy Richards Europa 800W Espresso & Cappuccino Coffee Maker", "Morphy Richards",
        4499, 6995, 4.3, 8900,
        "Brew authentic rich espresso, lattes, and frothy cappuccinos at home. Includes steam wand for milk frothing and stainless steel 4-cup carafe.",
        {"Power": "800 Watts", "Pressure": "Bar Pump Equivalent Steam", "Carafe": "4-Cup Heat Resistant Glass"},
        "Philips Official Store",
        ["https://images.unsplash.com/photo-1517668808822-9ebb02ae2a0e?w=800"]
    ),
    (
        "cat-3", "Home & Kitchen", "Wonderchef Nutri-blend 400W Mixer Grinder & Smoothie Maker", "Wonderchef",
        2499, 4500, 4.5, 23500,
        "High-grade Japanese stainless steel blades rotate at 22,000 RPM to break down whole fruits, seeds and tough nuts into silky nutritious smoothies.",
        {"Motor": "400 Watts 22000 RPM", "Jars": "2 Unbreakable Tritan Polycarbonate Jars", "Blades": "4-Wing Blending + 2-Wing Grinding"},
        "Hamilton Housewares",
        ["https://images.unsplash.com/photo-1584269600464-37b1b58a9fe7?w=800"]
    ),
    (
        "cat-3", "Home & Kitchen", "Kent Grand Plus RO+UV+UF+TDS Water Purifier", "Kent",
        15999, 21000, 4.6, 14200,
        "Multi-stage purification process with Mineral RO technology that retains essential natural minerals. In-tank UV disinfection keeps stored water pure.",
        {"Capacity": "9 Litres Tank", "Purification Rate": "20 L/hr", "Technology": "RO + UV + UF + TDS Controller"},
        "Kent RO Systems",
        ["https://images.unsplash.com/photo-1585670149967-b4f4da88cc9f?w=800"]
    ),
    (
        "cat-3", "Home & Kitchen", "Meyer Pre-Seasoned Cast Iron Skillet 26cm", "Meyer",
        1899, 2699, 4.7, 7200,
        "100% natural pre-seasoned cast iron skillet without chemical coatings. Superior heat retention and even heat distribution for searing, frying and baking.",
        {"Diameter": "26 cm (10.25 inch)", "Material": "Pre-Seasoned Cast Iron", "Induction Friendly": "Yes, All Cooktops"},
        "Stovekraft Official",
        ["https://images.unsplash.com/photo-1584269600464-37b1b58a9fe7?w=800"]
    ),
    (
        "cat-3", "Home & Kitchen", "Borosil Glass Mixing Bowl Set with Snap Lids (Set of 3)", "Borosil",
        1299, 1795, 4.8, 12400,
        "Made from 100% borosilicate glass that withstands temperatures up to 350°C. Safe for microwave, oven, freezer, and dishwasher with airtight snap lids.",
        {"Capacities": "500ml, 1000ml, 1500ml", "Material": "100% Borosilicate Glass", "Lids": "BPA-Free Airtight"},
        "Borosil Official Store",
        ["https://images.unsplash.com/photo-1556911220-e15b29be8c8f?w=800"]
    ),
    (
        "cat-3", "Home & Kitchen", "Cello Opalware Imperial Dinner Set (33 Pieces)", "Cello",
        2999, 4995, 4.5, 9800,
        "Chip-resistant and thermal shock resistant white opal glass dinnerware with elegant floral motif. 100% bone ash free and microwave safe.",
        {"Pieces": "33 Pcs (6 Full Plates, 6 Quarter, 12 Bowls, 2 Serving, 1 Platter)", "Material": "Toughened Opal Glass"},
        "Solimo Retails",
        ["https://images.unsplash.com/photo-1614707267537-b85aaf00c4b7?w=800"]
    ),
    (
        "cat-3", "Home & Kitchen", "Xiaomi Smart Air Purifier 4 with True HEPA Filter", "Xiaomi",
        13999, 16999, 4.7, 5600,
        "Captures 99.97% of 0.3-micron particles including smoke, pet dander and pollen. High CADR of 400m³/h cleans a 48m² room in just 10 minutes.",
        {"CADR": "400 m³/h Clean Air", "Filtration": "3-in-1 True HEPA Filter", "Control": "Mi Home App + Alexa / Google"},
        "Xiaomi Official Store",
        ["https://images.unsplash.com/photo-1585771724684-38269d6639fd?w=800"]
    ),
    (
        "cat-3", "Home & Kitchen", "Ecovacs Deebot N8 Robotic Vacuum & Mopping Cleaner", "Ecovacs",
        24900, 39900, 4.6, 2800,
        "TrueMapping dToF laser navigation maps your home with 4x precision. 2300Pa suction power with OZMO mopping system in a single pass.",
        {"Suction Power": "2300 Pa", "Navigation": "dToF Laser Radar", "Battery": "3200 mAh (110 Mins Runtime)"},
        "Appario Retail",
        ["https://images.unsplash.com/photo-1558317374-067fb5f30001?w=800"]
    ),
    (
        "cat-3", "Home & Kitchen", "SleepyCat Hybrid Latex Memory Foam Pillow (Pack of 2)", "SleepyCat",
        2199, 3499, 4.6, 8400,
        "Ergonomically contoured cervical neck support pillow combining responsive natural latex with pressure-relieving gel memory foam.",
        {"Core": "Natural Latex + Memory Foam", "Cover": "Bamboo Breathable Fabric", "Count": "Pack of 2"},
        "Wakefit Official Store",
        ["https://images.unsplash.com/photo-1584100936595-c0654b55a2e2?w=800"]
    ),
    (
        "cat-3", "Home & Kitchen", "Green Soul Monster Ultimate T Ergonomic Gaming & Desk Chair", "Green Soul",
        17990, 24990, 4.7, 6100,
        "Heavy-duty internal metal frame with premium breathable spandex fabric, magnetic memory foam neck pillow, 4D armrests, and 180° recline mechanism.",
        {"Mechanism": "Multifunctional Frog Mechanism", "Gas Lift": "Class 4 Hydraulic", "Weight Capacity": "135 KG"},
        "Appario Retail",
        ["https://images.unsplash.com/photo-1580481077195-c3a821a58875?w=800"]
    ),
    (
        "cat-3", "Home & Kitchen", "Philips Hue White & Color Ambiance Smart LED Starter Kit", "Philips",
        7999, 10999, 4.7, 3400,
        "Includes 3 E27 color smart bulbs and Hue Bridge. 16 million colors and 50,000 shades of warm-to-cool white light synced with music, movies and games.",
        {"Base": "E27 Screw Base", "Colors": "16 Million Colors + Tunable White", "Bridge": "Hue Bridge Included"},
        "Philips Official Store",
        ["https://images.unsplash.com/photo-1550524514-9b6999b19e27?w=800"]
    ),
    (
        "cat-3", "Home & Kitchen", "Bajaj Majesty 1603 T 16-Litre Oven Toaster Grill (OTG)", "Bajaj",
        3699, 5299, 4.3, 11400,
        "Powder-coated stainless steel body with 60-minute timer and auto shut-off. Includes baking tray, grill rack, tong and crumb tray.",
        {"Capacity": "16 Litres", "Power": "1200 Watts", "Heating Elements": "Top and Bottom Quartz"},
        "Appario Retail",
        ["https://images.unsplash.com/photo-1584269600464-37b1b58a9fe7?w=800"]
    ),
    (
        "cat-3", "Home & Kitchen", "Prestige Svachh Hard Anodized 3 Litre Pressure Cooker", "Prestige",
        1899, 2590, 4.5, 17800,
        "Unique deep lid design controls froth spillage, durable hard anodized body with induction base and comfortable cool-touch handles.",
        {"Capacity": "3.0 Litres", "Material": "Hard Anodized Aluminum", "Base": "Gas and Induction Compatible"},
        "Prestige Official Store",
        ["https://images.unsplash.com/photo-1584269600464-37b1b58a9fe7?w=800"]
    ),
    (
        "cat-3", "Home & Kitchen", "Havells Crabtree 1000W Heavyweight Dry Iron", "Havells",
        1199, 1795, 4.4, 9100,
        "Heavy 1.7kg soleplate delivers crisp crease-free clothes with minimal arm pressure. Greblon non-stick German coating glides effortlessly.",
        {"Power": "1000 Watts", "Weight": "1.7 kg Heavyweight", "Soleplate": "Greblon Non-Stick Coating"},
        "Appario Retail",
        ["https://images.unsplash.com/photo-1544441893-675973e31985?w=800"]
    ),
    (
        "cat-3", "Home & Kitchen", "Solimo 100% Pure Combed Cotton Queen Bedsheet Set with 2 Pillow Covers", "Solimo",
        899, 1599, 4.3, 14800,
        "Super soft 144 thread count pure combed cotton bedsheet designed for queen-size beds. Colorfast and machine washable.",
        {"Fabric": "100% Combed Cotton", "Thread Count": "144 TC", "Size": "Queen (90 x 100 inches)"},
        "Solimo Retails",
        ["https://images.unsplash.com/photo-1505693416388-ac5ce068fe85?w=800"]
    ),
    (
        "cat-3", "Home & Kitchen", "Pigeon Stainless Steel 24-Piece Flatware Cutlery Set with Stand", "Pigeon",
        649, 1295, 4.2, 8200,
        "Mirror-polished food-grade stainless steel cutlery set comprising 6 dinner spoons, 6 dessert spoons, 6 forks and 6 teaspoons with revolving stand.",
        {"Material": "18/8 Food-Grade Stainless Steel", "Pieces": "24 Pcs + 1 Revolving Stand", "Finish": "Mirror Polish"},
        "Stovekraft Official",
        ["https://images.unsplash.com/photo-1556911220-e15b29be8c8f?w=800"]
    ),
    (
        "cat-3", "Home & Kitchen", "Wipro Coral 16W Batten Smart LED Light with Remote", "Wipro",
        999, 1690, 4.3, 5200,
        "Tunable white and color light batten controllable via smartphone or included infrared remote control. Voice control compatible with Alexa.",
        {"Wattage": "16 Watts", "Length": "4 Feet", "Colors": "Warm to Cool White + RGB"},
        "Wipro Lighting",
        ["https://images.unsplash.com/photo-1550524514-9b6999b19e27?w=800"]
    ),
    (
        "cat-3", "Home & Kitchen", "Milton Pro Cook Granite Induction Frying Pan 24cm", "Milton",
        949, 1495, 4.4, 7600,
        "3-layer non-stick granite coating free from PFOA and harmful heavy metals. Induction and gas stove compatible with soft-touch Bakelite handle.",
        {"Diameter": "24 cm", "Coating": "Granite 3-Layer Non-Stick", "PFOA Free": "100% Non-Toxic"},
        "Milton Official Store",
        ["https://images.unsplash.com/photo-1584269600464-37b1b58a9fe7?w=800"]
    ),
    (
        "cat-3", "Home & Kitchen", "IKEA Frakta Extra Large Storage Bag Blue (Pack of 3)", "IKEA",
        499, 799, 4.8, 19000,
        "Durable polypropylene heavy-duty storage and moving bag. Holds up to 25kg, folds completely flat when empty, easy to clean with water.",
        {"Capacity": "71 Litres each", "Material": "100% Polypropylene", "Count": "Pack of 3 Bags"},
        "IKEA Official Store",
        ["https://images.unsplash.com/photo-1584917865442-de89df76afd3?w=800"]
    ),
    (
        "cat-3", "Home & Kitchen", "AGARO Regency Multi-Function Electric Kettle 1.8L Double Wall", "AGARO",
        1399, 2199, 4.5, 6800,
        "1500W rapid boil kettle with food-grade 304 stainless steel interior and cool-touch outer plastic wall to prevent accidental burns.",
        {"Capacity": "1.8 Litres", "Power": "1500 Watts", "Interior": "304 Food-Grade Stainless Steel", "Safety": "Auto-Cutoff & Boil Dry Protection"},
        "Appario Retail",
        ["https://images.unsplash.com/photo-1517668808822-9ebb02ae2a0e?w=800"]
    ),
    (
        "cat-3", "Home & Kitchen", "Prestige Tru-Edge Laser Cut Stainless Steel Kitchen Knife Set 4-Piece", "Prestige",
        799, 1295, 4.4, 8900,
        "Precision laser cut stainless steel knives with contoured ergonomic grip handles. Includes Chef knife, Utility knife, Paring knife and Wooden block.",
        {"Blades": "High-Carbon Stainless Steel", "Includes": "3 Knives + Solid Wooden Block", "Care": "Dishwasher Safe"},
        "Prestige Official Store",
        ["https://images.unsplash.com/photo-1584269600464-37b1b58a9fe7?w=800"]
    ),
    (
        "cat-3", "Home & Kitchen", "Scotch-Brite Easy Sweeper Plus Mop with Dry and Wet Wipes", "Scotch-Brite",
        999, 1450, 4.3, 11400,
        "360-degree rotating mop head reaches under low furniture effortlessly. Electrostatic dry wipes trap hair and dust, wet wipes degrease floors.",
        {"Head": "360 Degree Swivel Head", "Includes": "1 Mop + 5 Dry Sheets + 4 Wet Sheets", "Handle": "Extendable Aluminum"},
        "Solimo Retails",
        ["https://images.unsplash.com/photo-1558317374-067fb5f30001?w=800"]
    ),
    (
        "cat-3", "Home & Kitchen", "Kuber Industries Non-Woven Foldable Saree Wardrobe Organizer (Pack of 6)", "Kuber",
        549, 999, 4.2, 14200,
        "Breathable moisture-resistant non-woven fabric with transparent clear window to identify clothes without opening. Heavy-duty zipper closure.",
        {"Count": "Set of 6 Organizers", "Capacity": "Holds 8-10 sarees each", "Closure": "Premium Dual Zipper"},
        "Solimo Retails",
        ["https://images.unsplash.com/photo-1584917865442-de89df76afd3?w=800"]
    ),
    (
        "cat-3", "Home & Kitchen", "Milton Executive Stainless Steel Insulated Tiffin Box with Jacket", "Milton",
        1049, 1495, 4.6, 16400,
        "Set of 3 round leakproof microwave-safe stainless steel containers nestled inside an insulated zippered soft fabric carrying pouch with spoon pocket.",
        {"Containers": "3 Stainless Steel Containers (280ml each)", "Jacket": "Thermal Insulated Fabric", "Leakproof": "Yes, 100%"},
        "Milton Official Store",
        ["https://images.unsplash.com/photo-1602143407151-7111542de6e8?w=800"]
    ),
    (
        "cat-3", "Home & Kitchen", "Cello Kleeno Microfiber Floor Cleaning Spin Mop with Bucket", "Cello",
        1499, 2499, 4.3, 13100,
        "Durable plastic bucket with stainless steel wringer basket and 360-degree super absorbent microfiber mop head with telescopic stainless steel handle.",
        {"Wringer": "Stainless Steel Spin Basket", "Heads": "2 Microfiber Refills Included", "Handle": "Extendable Stainless Steel"},
        "Solimo Retails",
        ["https://images.unsplash.com/photo-1558317374-067fb5f30001?w=800"]
    ),
    (
        "cat-3", "Home & Kitchen", "AmazonBasics Heavy Duty Microfiber Cleaning Cloths (Pack of 24)", "AmazonBasics",
        899, 1400, 4.7, 26800,
        "Ultra-soft, non-abrasive microfiber cloths will not scratch paints, coats or other surfaces. Cleans with or without chemical cleaners, lint-free.",
        {"Count": "24 Microfiber Cloths", "Dimensions": "30 x 40 cm", "Absorbency": "Absorbs up to 8x its weight in water"},
        "Solimo Retails",
        ["https://images.unsplash.com/photo-1558317374-067fb5f30001?w=800"]
    ),

    # ---------------- BEAUTY & PERSONAL CARE (26 products) ----------------
    (
        "cat-4", "Beauty & Personal Care", "COSRX Advanced Snail 96 Mucin Power Essence 100ml", "COSRX",
        1199, 1450, 4.7, 24100,
        "Formulated with 96.3% Snail Secretion Filtrate to soothe damaged skin, replenish hydration, and restore a youthful luminous radiance.",
        {"Volume": "100 ml", "Skin Type": "Dry, Dull, Sensitive Skin", "Key Ingredient": "96.3% Snail Mucin"},
        "The Derma Co Store",
        ["https://images.unsplash.com/photo-1620916566398-39f1143ab7be?w=800"]
    ),
    (
        "cat-4", "Beauty & Personal Care", "Paula's Choice 2% BHA Liquid Salicylic Acid Exfoliant 118ml", "Paula's Choice",
        2700, 3100, 4.8, 16200,
        "Award-winning leave-on liquid exfoliant that unclogs enlarged pores, smooths wrinkles, evens out skin tone, and gently sheds dead skin cells.",
        {"Volume": "118 ml", "Active Ingredient": "2% Salicylic Acid BHA", "Benefit": "Blackhead and Pore Reduction"},
        "Minimalist Official Store",
        ["https://images.unsplash.com/photo-1608248597359-009947743d5c?w=800"]
    ),
    (
        "cat-4", "Beauty & Personal Care", "La Roche-Posay Anthelios Invisible Fluid Sunscreen SPF 50+", "La Roche-Posay",
        1850, 2200, 4.8, 8900,
        "Ultra-light non-greasy broad spectrum UVA/UVB protection with Netlock technology. Invisible finish on all skin tones, water and sweat resistant.",
        {"SPF": "50+ PA++++", "Volume": "50 ml", "Texture": "Ultra-Light Invisible Fluid"},
        "Minimalist Official Store",
        ["https://images.unsplash.com/photo-1598440947619-2c35fc9aa908?w=800"]
    ),
    (
        "cat-4", "Beauty & Personal Care", "CeraVe Hydrating Facial Cleanser for Normal to Dry Skin 237ml", "CeraVe",
        999, 1250, 4.7, 31000,
        "Developed with dermatologists, formulated with 3 essential ceramides and hyaluronic acid to cleanse and hydrate without disrupting protective skin barrier.",
        {"Volume": "237 ml", "Ceramides": "1, 3, 6-II", "Non-Comedogenic": "Yes, Fragrance-Free"},
        "Minimalist Official Store",
        ["https://images.unsplash.com/photo-1556228720-195a672e8a03?w=800"]
    ),
    (
        "cat-4", "Beauty & Personal Care", "Neutrogena Hydro Boost Water Gel Face Moisturizer 50g", "Neutrogena",
        799, 1050, 4.6, 28400,
        "Instantly quenches dry skin and keeps it looking smooth, supple and hydrated day after day. Absorbs quickly with unique lightweight oil-free gel formula.",
        {"Weight": "50g", "Texture": "Water Gel", "Key Ingredient": "Purified Hyaluronic Acid"},
        "Appario Retail",
        ["https://images.unsplash.com/photo-1556228720-195a672e8a03?w=800"]
    ),
    (
        "cat-4", "Beauty & Personal Care", "Plum Green Tea Alcohol-Free Pore Clarifying Face Toner 200ml", "Plum",
        335, 390, 4.4, 18200,
        "100% vegan alcohol-free toner enriched with green tea extracts, glycolic acid, and glycerin to combat acne, shrink pores and control sebum.",
        {"Volume": "200 ml", "Alcohol Free": "100%", "Target": "Acne-Prone Oily Skin"},
        "Mamaearth Official Store",
        ["https://images.unsplash.com/photo-1608248597359-009947743d5c?w=800"]
    ),
    (
        "cat-4", "Beauty & Personal Care", "Forest Essentials Kashmiri Saffron Delicate Facial Cleanser 200ml", "Forest Essentials",
        1550, 1750, 4.8, 4800,
        "Purifying Ayurvedic cleanser with pure Kashmiri saffron infusion, neem bark extract, and sweet almond oil that purifies without stripping moisture.",
        {"Volume": "200 ml", "Ingredients": "Kashmiri Saffron, Neem, Kewda", "Ayurvedic": "100% Certified Natural"},
        "Sashtri Healthcare Ltd",
        ["https://images.unsplash.com/photo-1556228720-195a672e8a03?w=800"]
    ),
    (
        "cat-4", "Beauty & Personal Care", "Dyson Supersonic Hair Dryer Iron/Fuchsia with 5 Styling Attachments", "Dyson",
        34900, 39900, 4.9, 3900,
        "Engineered to protect hair from extreme heat damage with intelligent heat control. Fast drying and precision styling powered by Dyson digital motor V9.",
        {"Motor": "Dyson V9 110,000 RPM", "Attachments": "5 Magnetic Attachments", "Heat Settings": "4 Precise Heat Levels"},
        "Appario Retail",
        ["https://images.unsplash.com/photo-1522337360788-8b13dee7a37e?w=800"]
    ),
    (
        "cat-4", "Beauty & Personal Care", "Olaplex No. 3 Hair Perfector Repairing Treatment 100ml", "Olaplex",
        2950, 3200, 4.7, 14900,
        "Global best-selling at-home bond builder that repairs broken disulfide bonds caused by chemical processing, thermal styling and mechanical damage.",
        {"Volume": "100 ml", "Technology": "Patented Bis-Aminopropyl Diglycol Dimaleate", "For": "All Damaged Hair Types"},
        "Appario Retail",
        ["https://images.unsplash.com/photo-1527799820374-dcf8d9d4a388?w=800"]
    ),
    (
        "cat-4", "Beauty & Personal Care", "Moroccanoil Original Treatment Argan Oil 100ml", "Moroccanoil",
        3330, 3800, 4.8, 9200,
        "Infused with antioxidant-rich argan oil and shine-boosting vitamins. Detangles, speeds up blow-drying time, and boosts radiant shine by 118%.",
        {"Volume": "100 ml", "Key Ingredient": "Pure Argan Oil", "Benefit": "Frizz Control and Conditioning"},
        "Appario Retail",
        ["https://images.unsplash.com/photo-1527799820374-dcf8d9d4a388?w=800"]
    ),
    (
        "cat-4", "Beauty & Personal Care", "Braun Series 9 Pro Electric Shaver with SmartCare Center", "Braun",
        24999, 32999, 4.8, 2200,
        "World's most efficient electric shaver with 5 shaving elements and ProLift trimmer that gently cuts tough 1, 3, or 7-day beards without irritation.",
        {"Elements": "5 Shaving Elements with ProLift Trimmer", "Sonic Technology": "40,000 Cutting Actions/Min", "Center": "5-in-1 SmartCare Cleaning Station"},
        "Philips Personal Care",
        ["https://images.unsplash.com/photo-1585751119414-ef2636f8aede?w=800"]
    ),
    (
        "cat-4", "Beauty & Personal Care", "Oral-B Pro 3 3000 CrossAction Electric Rechargeable Toothbrush", "Oral-B",
        3499, 5999, 4.6, 8900,
        "360-degree visible gum pressure sensor alerts if brushing too hard. Oscillating-rotating-pulsating 3D action removes up to 100% more plaque.",
        {"Action": "3D Cleaning Technology", "Sensor": "Visible Gum Pressure Sensor", "Battery": "Over 2 Weeks Per Charge"},
        "Appario Retail",
        ["https://images.unsplash.com/photo-1559591937-e1032397e594?w=800"]
    ),
    (
        "cat-4", "Beauty & Personal Care", "Bombay Shaving Company 6-in-1 Charcoal Shaving & Grooming Kit", "Bombay Shaving Company",
        1299, 2150, 4.5, 6700,
        "Complete precision shaving kit featuring black metal razor, synthetic badger shaving brush, pre-shave scrub, shaving cream, post-shave balm, and towel.",
        {"Contents": "Razor, Shaving Brush, Pre-Shave Scrub, Shaving Cream, Balm, Towel", "Active": "Activated Bamboo Charcoal"},
        "Beardo Grooming",
        ["https://images.unsplash.com/photo-1585751119414-ef2636f8aede?w=800"]
    ),
    (
        "cat-4", "Beauty & Personal Care", "Beardo Dark Side Eau De Parfum for Men Long-Lasting 100ml", "Beardo",
        899, 1499, 4.4, 11400,
        "Intense masculine fragrance blending fresh citrus top notes of lemon and grapefruit with rich woody cedarwood and amber base notes.",
        {"Volume": "100 ml", "Fragrance Type": "Eau De Parfum (EDP)", "Longevity": "Up to 12 Hours"},
        "Beardo Grooming",
        ["https://images.unsplash.com/photo-1592945403244-b3fbafd7f539?w=800"]
    ),
    (
        "cat-4", "Beauty & Personal Care", "M.A.C Retro Matte Lipstick - Ruby Woo (Vivid Blue-Red)", "M.A.C",
        1950, 2200, 4.8, 16800,
        "The universally flattering iconic shade with intense color payoff and a zero-shine ultra-matte finish. Long-wearing formula lasts up to 8 hours.",
        {"Shade": "Ruby Woo (Blue-Red)", "Finish": "Retro Matte", "Weight": "3g"},
        "Lakmé Official Store",
        ["https://images.unsplash.com/photo-1586495777744-4413f21062fa?w=800"]
    ),
    (
        "cat-4", "Beauty & Personal Care", "Maybelline New York Lash Sensational Sky High Waterproof Mascara", "Maybelline",
        599, 799, 4.6, 34200,
        "Full volume and limitless length impact from every angle. Exclusive Flex Tower mascara brush bends to volumize and extend every single lash.",
        {"Volume": "6 ml", "Finish": "Waterproof Limitless Length", "Brush": "Flex Tower Silicone Wand"},
        "Lakmé Official Store",
        ["https://images.unsplash.com/photo-1596462502278-27bfdc403348?w=800"]
    ),
    (
        "cat-4", "Beauty & Personal Care", "Lakme Absolute Skin Natural Mousse Matte Foundation 25g", "Lakme",
        675, 875, 4.4, 14100,
        "Feather-light mousse texture with SPF 8 sun protection blends effortlessly into skin, delivering a flawless natural matte finish lasting 16 hours.",
        {"Weight": "25g", "SPF": "SPF 8", "Finish": "Feather-light Mousse Matte"},
        "Lakmé Official Store",
        ["https://images.unsplash.com/photo-1522337360788-8b13dee7a37e?w=800"]
    ),
    (
        "cat-4", "Beauty & Personal Care", "L'Oreal Paris Infallible 24H Fresh Wear Powder Foundation", "L'Oreal",
        999, 1399, 4.5, 9400,
        "Covers like a liquid foundation and mattifies like a powder. Waterproof, sweat-proof, and transfer-resistant for up to 24 hours of comfort.",
        {"Weight": "9g", "Coverage": "Full Buildable Coverage", "Wear Time": "Up to 24 Hours"},
        "L'Oreal India",
        ["https://images.unsplash.com/photo-1522337360788-8b13dee7a37e?w=800"]
    ),
    (
        "cat-4", "Beauty & Personal Care", "NIVEA Soft Light Moisturizing Cream with Vitamin E & Jojoba Oil 300ml", "NIVEA",
        349, 499, 4.6, 42000,
        "Fast-absorbing light moisturizing cream that refreshes skin with invigorating scent. Infused with Vitamin E and Jojoba Oil for face, hands and body.",
        {"Volume": "300 ml", "Enriched With": "Jojoba Oil and Vitamin E", "Formula": "Non-Greasy Light Texture"},
        "Nivea Official Store",
        ["https://images.unsplash.com/photo-1556228720-195a672e8a03?w=800"]
    ),
    (
        "cat-4", "Beauty & Personal Care", "Mamaearth Onion Shampoo with Onion and Plant Keratin 400ml", "Mamaearth",
        419, 499, 4.3, 38900,
        "Formulated with rich red onion seed oil extract and plant keratin to strengthen hair shafts, reduce hair fall, and restore natural shine.",
        {"Volume": "400 ml", "Toxins": "Sulfate and Paraben Free", "Benefit": "Hair Fall Control"},
        "Mamaearth Official Store",
        ["https://images.unsplash.com/photo-1527799820374-dcf8d9d4a388?w=800"]
    ),
    (
        "cat-4", "Beauty & Personal Care", "Gillette Fusion5 ProGlide Men's Razor with FlexBall Technology", "Gillette",
        699, 899, 4.7, 19400,
        "Features 5 anti-friction blades for a shave you barely feel. FlexBall technology responds to contours and gets virtually every hair effortlessly.",
        {"Blades": "5 Anti-Friction Blades", "Technology": "FlexBall Contour Handle", "Lubrastrip": "Enhanced with Mineral Oil"},
        "Appario Retail",
        ["https://images.unsplash.com/photo-1585751119414-ef2636f8aede?w=800"]
    ),
    (
        "cat-4", "Beauty & Personal Care", "Tresemme Keratin Smooth Heat Protection Hair Spray 200ml", "Tresemme",
        499, 650, 4.5, 7800,
        "Shields hair from thermal styling heat up to 450°F / 230°C. Infused with keratin and marula oil for 72 hours of frizz control and salon shine.",
        {"Volume": "200 ml", "Heat Protection": "Up to 230°C / 450°F", "Benefit": "72H Frizz Resistance"},
        "L'Oreal India",
        ["https://images.unsplash.com/photo-1527799820374-dcf8d9d4a388?w=800"]
    ),
    (
        "cat-4", "Beauty & Personal Care", "Cetaphil Gentle Skin Cleanser for All Skin Types 250ml", "Cetaphil",
        599, 725, 4.7, 26500,
        "Creamy non-foaming formula with hydrating glycerin, niacinamide, and panthenol to cleanse away dirt and makeup without stripping natural moisture.",
        {"Volume": "250 ml", "Dermatologist Tested": "Yes, for Sensitive Skin", "Formula": "Soap-Free & Fragrance-Free"},
        "Minimalist Official Store",
        ["https://images.unsplash.com/photo-1556228720-195a672e8a03?w=800"]
    ),
    (
        "cat-4", "Beauty & Personal Care", "Biotique Bio Kelp Protein Shampoo for Falling Hair 400ml", "Biotique",
        299, 430, 4.2, 14200,
        "Invigorating botanical blend of pure kelp, natural proteins, peppermint oil, and mint leaf extract to gently cleanse hair and invigorate scalp.",
        {"Volume": "400 ml", "Key Herb": "Pure Kelp Seaweed", "Therapy": "Ayurvedic Hair Growth Stimulation"},
        "Sashtri Healthcare Ltd",
        ["https://images.unsplash.com/photo-1527799820374-dcf8d9d4a388?w=800"]
    ),
    (
        "cat-4", "Beauty & Personal Care", "Kama Ayurveda Pure Rose Water Face Mist 200ml", "Kama Ayurveda",
        1395, 1550, 4.8, 6200,
        "Steam-distilled from the petals of luxurious Kannauj roses. Natural astringent that balances and restores skin pH while tightening enlarged pores.",
        {"Volume": "200 ml", "Distillation": "Steam Distilled Kannauj Roses", "Alcohol Free": "100% Pure Floral Water"},
        "Sashtri Healthcare Ltd",
        ["https://images.unsplash.com/photo-1608248597359-009947743d5c?w=800"]
    ),
    (
        "cat-4", "Beauty & Personal Care", "Faces Canada Magneteyes Kajal Deep Black 0.35g", "Faces Canada",
        159, 249, 4.4, 21800,
        "Waterproof and smudge-proof kajal enriched with almond oil and Vitamin E. Delivers intense jet-black definition that stays intact for 24 hours.",
        {"Weight": "0.35g", "Pigmentation": "Intense Jet Black", "Longevity": "24H Smudge-Proof"},
        "Lakmé Official Store",
        ["https://images.unsplash.com/photo-1596462502278-27bfdc403348?w=800"]
    ),

    # ---------------- SPORTS & FITNESS (26 products) ----------------
    (
        "cat-5", "Sports & Fitness", "Bowflex SelectTech 552 Adjustable Dumbbells (Pair)", "Bowflex",
        28990, 39990, 4.9, 3100,
        "Replaces 15 sets of weights. Adjusts from 5 to 52.5 lbs (2.5 to 24 kg) in 2.5 lb increments with a simple turn of a dial. Space-efficient design.",
        {"Weight Range": "5 to 52.5 lbs (2.5 to 24 kg)", "Adjustments": "15 Weight Settings Per Dumbbell", "Tray": "Storage Trays Included"},
        "Boldfit Official Store",
        ["https://images.unsplash.com/photo-1584735935682-2f2b69dff9d2?w=800"]
    ),
    (
        "cat-5", "Sports & Fitness", "Fitkit by Cult FT100 Series 3.25HP Peak Motorized Treadmill", "Fitkit",
        21999, 42000, 4.3, 4200,
        "Quiet 3.25HP peak DC motor with manual 3-level incline, max speed 14 km/h, shock-absorbing anti-skid running deck, and Cult.fit app free coaching.",
        {"Motor": "3.25 HP Peak", "Max Speed": "14 km/h", "Max User Weight": "110 KG", "Foldable": "Hydraulic Soft-Drop"},
        "Boldfit Official Store",
        ["https://images.unsplash.com/photo-1540497077202-7c8a3999166f?w=800"]
    ),
    (
        "cat-5", "Sports & Fitness", "Slovic Heavy Resistance Bands Set of 5 with Door Anchor", "Slovic",
        899, 1699, 4.6, 9200,
        "100% natural Malaysian latex bands offering cumulative resistance from 10 to 150 lbs. Includes 2 cushioned foam handles, ankle straps and carry bag.",
        {"Resistance": "10 to 150 lbs Stackable", "Material": "100% Natural Malaysian Latex", "Accessories": "Door Anchor, Handles, Ankle Straps"},
        "Boldfit Official Store",
        ["https://images.unsplash.com/photo-1598971861713-54ad16a7e72e?w=800"]
    ),
    (
        "cat-5", "Sports & Fitness", "USI Universal Heavy Duty 4-inch Leather Powerlifting Belt", "USI Universal",
        1899, 2999, 4.7, 3400,
        "Heavy-duty top-grain oil-tanned leather powerlifting belt with double-prong stainless steel roller buckle for maximum intra-abdominal pressure during squats.",
        {"Material": "Top-Grain Saddle Leather", "Width": "4 inches Uniform", "Buckle": "Heavy Double-Prong Steel"},
        "Strauss Official Store",
        ["https://images.unsplash.com/photo-1584735935682-2f2b69dff9d2?w=800"]
    ),
    (
        "cat-5", "Sports & Fitness", "Reebok Professional Aerobic Step Platform with Non-Slip Deck", "Reebok",
        6499, 8999, 4.8, 2900,
        "The original studio step platform with three adjustable height settings (15, 20, 25 cm). Textured non-slip bubble surface and non-skid rubber feet.",
        {"Height Levels": "15 cm, 20 cm, 25 cm", "Max Load": "110 KG", "Surface": "Textured Grip Deck"},
        "Puma Sports India",
        ["https://images.unsplash.com/photo-1518611012118-696072aa579a?w=800"]
    ),
    (
        "cat-5", "Sports & Fitness", "Cockatoo Rubber Hexagonal Dumbbell Pair 10kg x 2", "Cockatoo",
        2999, 4999, 4.5, 6800,
        "Cast iron core encased in heavy-duty natural rubber that prevents floor damage and rolling. Ergonomically contoured knurled chrome steel handle.",
        {"Weight": "10 KG each (20 KG Pair)", "Shape": "Anti-Roll Hexagonal", "Grip": "Knurled Solid Steel"},
        "Kobo Fitness Essentials",
        ["https://images.unsplash.com/photo-1584735935682-2f2b69dff9d2?w=800"]
    ),
    (
        "cat-5", "Sports & Fitness", "MRF Genius Grand Edition English Willow Cricket Bat Full Size", "MRF",
        14999, 19999, 4.8, 1400,
        "Selected grade 1 English willow cricket bat designed in collaboration with international batsmen. Massive edges, curved blade, and superb balance.",
        {"Willow": "Grade 1 English Willow", "Handle": "Singapore Cane 12-Piece", "Weight": "1180 to 1220 grams"},
        "Freewill Sports Pvt Ltd",
        ["https://images.unsplash.com/photo-1531415074968-036ba1b575da?w=800"]
    ),
    (
        "cat-5", "Sports & Fitness", "Cosco Omega Football FIFA Basic Approved Match Ball Size 5", "Cosco",
        1499, 2199, 4.6, 5200,
        "Hand-stitched PU synthetic leather match ball with latex bladder for optimal air retention. FIFA certified for official tournament play.",
        {"Size": "Size 5 Match Ball", "Certification": "FIFA Basic Approved", "Panels": "32 Hand-Stitched Panels"},
        "Cosco Sports India",
        ["https://images.unsplash.com/photo-1579952363873-27f3bade9f55?w=800"]
    ),
    (
        "cat-5", "Sports & Fitness", "Spalding TF-1000 Classic Indoor Basketball Size 7", "Spalding",
        3499, 4999, 4.8, 3800,
        "Exclusive ZK microfiber composite leather cover with deep pebbling and shooter's seams for total moisture management and precision ball control.",
        {"Size": "Official Size 7 (29.5 inches)", "Cover": "ZK Microfiber Composite", "Use": "Indoor Tournament"},
        "Freewill Sports Pvt Ltd",
        ["https://images.unsplash.com/photo-1546519638-68e109498ffc?w=800"]
    ),
    (
        "cat-5", "Sports & Fitness", "Li-Ning G-Force 3900 Superlight Carbon Badminton Racket", "Li-Ning",
        2499, 4290, 4.5, 7800,
        "Crafted with High Tensile Slim Shaft and Aerotec Beam System for lightning-fast smashes and defensive maneuvering. Max string tension 30 lbs.",
        {"Weight": "W3 (85-87g)", "Material": "High Tensile Carbon Fiber", "Tension": "Up to 30 lbs"},
        "Yonex Official Store",
        ["https://images.unsplash.com/photo-1626224583764-f87db24ac4ea?w=800"]
    ),
    (
        "cat-5", "Sports & Fitness", "Speedo Fastskin Pure Focus Mirror Competition Swimming Goggles", "Speedo",
        2999, 4299, 4.7, 1900,
        "Engineered with world-class swimmers for 5% drag reduction. Hydroscopic curved lens profile for maximum peripheral vision and anti-fog clarity.",
        {"Lens": "Mirrored Hydroscopic Anti-Fog", "Nose Bridge": "Hybrid Ergonomic", "Approval": "World Aquatics (FINA) Approved"},
        "Puma Sports India",
        ["https://images.unsplash.com/photo-1530549387789-4c1017266635?w=800"]
    ),
    (
        "cat-5", "Sports & Fitness", "Nivia Carbonite 3.0 TPU Moulded Football Stud Shoes", "Nivia",
        899, 1399, 4.3, 8900,
        "High-shear synthetic leather upper with TPU embossed graphic detailing and rigid TPU soleplate with 14 conical studs for explosive pitch traction.",
        {"Upper": "PVC Synthetic Leather", "Sole": "TPU Moulded Studs", "Ground": "Firm Ground / Grass"},
        "Nivia Official Store",
        ["https://images.unsplash.com/photo-1511556532299-8f662fc26c06?w=800"]
    ),
    (
        "cat-5", "Sports & Fitness", "Stiga Pro Carbon Table Tennis Racket 7-Ply Blade", "Stiga",
        3499, 5299, 4.7, 2400,
        "High performance ping pong paddle featuring 7-ply ultra-lightweight balsa blade with dual carbon technology layers and ITTF approved S5 rubber.",
        {"Speed": "100", "Spin": "100", "Control": "80", "Approval": "ITTF Tournament Approved"},
        "Cosco Sports India",
        ["https://images.unsplash.com/photo-1534158914592-062992fbe900?w=800"]
    ),
    (
        "cat-5", "Sports & Fitness", "Dymatize ISO 100 Hydrolyzed 100% Whey Protein Isolate Gourmet Chocolate 5 lb", "Dymatize",
        8499, 10999, 4.9, 14200,
        "Fast-absorbing hydrolyzed whey protein isolate with 25g protein, 5.5g BCAAs, and less than 1g sugar and fat per serving. Banned substance tested.",
        {"Protein": "25g Hydrolyzed Isolate", "Weight": "5 lb (2.3 kg)", "Flavour": "Gourmet Chocolate"},
        "Boldfit Official Store",
        ["https://images.unsplash.com/photo-1579722821273-0f6c7d44362f?w=800"]
    ),
    (
        "cat-5", "Sports & Fitness", "MuscleBlaze Super Gainer XXL High Calorie Mass Gainer Powder 3kg", "MuscleBlaze",
        2299, 3499, 4.4, 18500,
        "High-calorie weight gainer shake providing 1123 calories, 45g protein, and 224g complex carbohydrates per day to pack on solid lean muscle mass.",
        {"Calories": "1123 kcal/day", "Protein": "45g Complex Matrix", "Carbs": "224g Clean Carbs", "Weight": "3 kg (6.6 lb)"},
        "Boldfit Official Store",
        ["https://images.unsplash.com/photo-1579722821273-0f6c7d44362f?w=800"]
    ),
    (
        "cat-5", "Sports & Fitness", "Cellucor C4 Original Explosive Pre-Workout Powder Fruit Punch 30 Servings", "Cellucor",
        1899, 2699, 4.6, 9200,
        "America's #1 selling pre-workout with 150mg caffeine, 1.6g CarnoSyn Beta-Alanine, and 1g Creatine Nitrate for explosive energy, endurance and pumps.",
        {"Servings": "30 Servings", "Active Ingredients": "Caffeine, Beta-Alanine, Creatine Nitrate", "Flavour": "Fruit Punch"},
        "Boldfit Official Store",
        ["https://images.unsplash.com/photo-1579722821273-0f6c7d44362f?w=800"]
    ),
    (
        "cat-5", "Sports & Fitness", "BlenderBottle Pro40 Stainless Steel Insulated Protein Shaker Cup 40oz", "BlenderBottle",
        1799, 2499, 4.8, 11400,
        "Vacuum-insulated double-wall stainless steel shaker keeps drinks icy cold for 24 hours. Includes surgical-grade 316 stainless steel BlenderBall wire whisk.",
        {"Capacity": "40 oz (1180 ml)", "Insulation": "Double-Wall Vacuum SS", "Whisk": "Patented 316 Surgical Steel Ball"},
        "Boldfit Official Store",
        ["https://images.unsplash.com/photo-1579722821273-0f6c7d44362f?w=800"]
    ),
    (
        "cat-5", "Sports & Fitness", "CamelBak Podium Chill Insulated Bike Water Bottle 21oz", "CamelBak",
        1299, 1899, 4.7, 4300,
        "Aerogel double-wall insulation keeps water cold twice as long as normal bottles. Self-sealing Jet Valve delivers high flow without leaks or spills.",
        {"Capacity": "21 oz (620 ml)", "Valve": "Self-Sealing High-Flow Jet Valve", "BPA Free": "100% Free of BPA, BPS & BPF"},
        "Freewill Sports Pvt Ltd",
        ["https://images.unsplash.com/photo-1523362628745-0c100150b504?w=800"]
    ),
    (
        "cat-5", "Sports & Fitness", "Gatorade Thirst Quencher Electrolyte Powder Mix Lemon Lime 51oz", "Gatorade",
        1499, 1999, 4.8, 12800,
        "Proven rehydration formula trusted by elite athletes worldwide. Replenishes critical electrolytes lost in sweat and fuels muscles with carbohydrates.",
        {"Yield": "Makes 6 Gallons (22.7 Litres)", "Flavour": "Lemon Lime", "Electrolytes": "Sodium, Potassium, Magnesium"},
        "Tata Consumer Products",
        ["https://images.unsplash.com/photo-1544816155-12df9643f363?w=800"]
    ),
    (
        "cat-5", "Sports & Fitness", "Boldfit Cotton Elastic Knee Support Compression Cap for Gym & Running", "Boldfit",
        499, 999, 4.4, 21500,
        "4-way stretch circular knit compression sleeve provides 360-degree joint stabilization and heat retention for arthritis, meniscus tears and squats.",
        {"Material": "Breathable Nylon-Spandex Elastic", "Compression": "360 Degree Joint Stabilizer", "Pack": "Pair of 2 Sleeves"},
        "Boldfit Official Store",
        ["https://images.unsplash.com/photo-1598971861713-54ad16a7e72e?w=800"]
    ),
    (
        "cat-5", "Sports & Fitness", "Kobo Anti-Burst Gym Exercise Swiss Ball 65cm with Quick Foot Pump", "Kobo",
        799, 1499, 4.3, 7600,
        "Extra thick professional PVC construction with honeycomb structure that slowly deflates if punctured. Supports up to 250kg for yoga and core workouts.",
        {"Diameter": "65 cm", "Max Load": "250 KG Anti-Burst", "Pump": "Quick-Action Foot Pump Included"},
        "Kobo Fitness Essentials",
        ["https://images.unsplash.com/photo-1518611012118-696072aa579a?w=800"]
    ),
    (
        "cat-5", "Sports & Fitness", "Strauss Pro Heavy Speed Skipping Rope with Ball Bearings", "Strauss",
        349, 799, 4.5, 14800,
        "360-degree smooth ball bearing mechanism ensures tangle-free ultra-fast rotation for double-unders, boxing footwork, and high-intensity cardio.",
        {"Cable": "Steel Wire Coated with PVC", "Bearings": "Dual 360-degree Ball Bearings", "Length": "3 Meters Adjustable"},
        "Strauss Official Store",
        ["https://images.unsplash.com/photo-1598971861713-54ad16a7e72e?w=800"]
    ),
    (
        "cat-5", "Sports & Fitness", "Boldfit Anti-Skid Yoga Mat 6mm Thick with Carrying Strap", "Boldfit",
        799, 1599, 4.4, 18200,
        "Dual-sided textured non-slip surface provides excellent grip on wooden floors and tiles. Eco-friendly high density EVA foam cushions knees and spine.",
        {"Thickness": "6 mm High Density", "Dimensions": "183 x 61 cm", "Strap": "Free Carrying Strap Included"},
        "Boldfit Official Store",
        ["https://images.unsplash.com/photo-1545205597-3d9d02c29597?w=800"]
    ),
    (
        "cat-5", "Sports & Fitness", "Yonex Mavis 350 Nylon Shuttlecocks Green Cap (Pack of 6)", "Yonex",
        999, 1390, 4.7, 36000,
        "Precision manufactured to deliver quick recovery and stable flight trajectory identical to natural feather shuttlecocks with 4x durability.",
        {"Material": "Natural Cork Base + Nylon Skirt", "Speed": "Slow / Green Cap", "Pack": "Tube of 6 Shuttlecocks"},
        "Yonex Official Store",
        ["https://images.unsplash.com/photo-1626224583764-f87db24ac4ea?w=800"]
    ),
    (
        "cat-5", "Sports & Fitness", "Nivia Storm Football Match Rubber Ball Size 5", "Nivia",
        449, 650, 4.3, 29000,
        "Classic multi-color 32-panel rubber molded football with tough butyl bladder. Highly resistant to rough asphalt, concrete ground, and turf.",
        {"Construction": "Rubber Molded 32 Panels", "Size": "Size 5", "Durability": "All-Terrain Hard Ground"},
        "Nivia Official Store",
        ["https://images.unsplash.com/photo-1579952363873-27f3bade9f55?w=800"]
    ),
    (
        "cat-5", "Sports & Fitness", "Cosco Light Tennis Cricket Tennis Balls Heavy Weight (Pack of 6)", "Cosco",
        499, 750, 4.5, 14200,
        "High quality woolen felt outer shell with deep seam stitching and pressurized rubber core providing consistent bounce for gully and tournament cricket.",
        {"Pack": "Pack of 6 Balls", "Weight": "Heavy Tennis Grade", "Core": "Pressurized Rubber"},
        "Cosco Sports India",
        ["https://images.unsplash.com/photo-1531415074968-036ba1b575da?w=800"]
    ),

    # ---------------- BOOKS & STATIONERY (26 products) ----------------
    (
        "cat-6", "Books & Stationery", "Thinking, Fast and Slow by Daniel Kahneman (Paperback)", "Daniel Kahneman",
        449, 599, 4.8, 38400,
        "Nobel Memorial Prize winner Daniel Kahneman takes us on a groundbreaking tour of the mind, explaining the two systems that drive the way we think.",
        {"Author": "Daniel Kahneman", "Pages": "512", "Genre": "Behavioral Economics & Psychology"},
        "Penguin Official Store",
        ["https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=800"]
    ),
    (
        "cat-6", "Books & Stationery", "Deep Work: Rules for Focused Success in a Distracted World", "Cal Newport",
        349, 499, 4.7, 28100,
        "Wall Street Journal business bestseller demonstrating that deep work is a superpower in our increasingly competitive knowledge economy.",
        {"Author": "Cal Newport", "Pages": "304", "Topic": "Productivity & Focus"},
        "Penguin Official Store",
        ["https://images.unsplash.com/photo-1544947950-fa07a98d237f?w=800"]
    ),
    (
        "cat-6", "Books & Stationery", "Can't Hurt Me: Master Your Mind and Defy the Odds", "David Goggins",
        499, 699, 4.9, 52000,
        "For David Goggins, childhood was a nightmare. Through self-discipline, mental toughness, and hard work, he transformed himself into a Navy SEAL icon.",
        {"Author": "David Goggins", "Format": "Paperback", "Category": "Memoir & Mental Toughness"},
        "BookWorm India",
        ["https://images.unsplash.com/photo-1495446815901-a7297e633e8d?w=800"]
    ),
    (
        "cat-6", "Books & Stationery", "Outliers: The Story of Success by Malcolm Gladwell", "Malcolm Gladwell",
        399, 550, 4.6, 21900,
        "In this stunning book, Malcolm Gladwell explores what makes high achievers different, introducing the famous 10,000-hour rule of mastery.",
        {"Author": "Malcolm Gladwell", "Pages": "336", "Language": "English"},
        "Penguin Official Store",
        ["https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=800"]
    ),
    (
        "cat-6", "Books & Stationery", "The 7 Habits of Highly Effective People 30th Anniversary Edition", "Stephen R. Covey",
        499, 699, 4.8, 41200,
        "One of the most inspiring and impactful books ever written. Stephen Covey's timeless holistic approach solves personal and professional problems.",
        {"Author": "Stephen R. Covey", "Pages": "432", "Binding": "Paperback"},
        "Pearson Official Store",
        ["https://images.unsplash.com/photo-1544947950-fa07a98d237f?w=800"]
    ),
    (
        "cat-6", "Books & Stationery", "Zero to One: Notes on Startups, or How to Build the Future", "Peter Thiel",
        380, 499, 4.7, 34500,
        "Legendary entrepreneur and investor Peter Thiel shows how we can find singular ways to create new things and build monopolistic breakthrough companies.",
        {"Author": "Peter Thiel with Blake Masters", "Pages": "224", "Topic": "Entrepreneurship & Innovation"},
        "Penguin Official Store",
        ["https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=800"]
    ),
    (
        "cat-6", "Books & Stationery", "Man's Search for Meaning by Viktor E. Frankl", "Viktor E. Frankl",
        249, 350, 4.8, 39800,
        "Psychiatrist Viktor Frankl's memoir of surviving Nazi death camps and how logotherapy teaches that spiritual survival rests on finding meaning in suffering.",
        {"Author": "Viktor E. Frankl", "Pages": "160", "Topic": "Philosophy & Psychology"},
        "BookWorm India",
        ["https://images.unsplash.com/photo-1495446815901-a7297e633e8d?w=800"]
    ),
    (
        "cat-6", "Books & Stationery", "Dune (Deluxe Hardcover Collector's Edition) by Frank Herbert", "Frank Herbert",
        999, 1499, 4.9, 18500,
        "The definitive science fiction masterpiece set on the desert planet Arrakis. Includes custom illustrated endpapers, gilded edges, and poster map.",
        {"Author": "Frank Herbert", "Binding": "Deluxe Hardcover", "Genre": "Epic Science Fiction"},
        "Penguin Official Store",
        ["https://images.unsplash.com/photo-1544947950-fa07a98d237f?w=800"]
    ),
    (
        "cat-6", "Books & Stationery", "The Alchemist 25th Anniversary Edition by Paulo Coelho", "Paulo Coelho",
        299, 399, 4.7, 78000,
        "The enchanting story of Santiago, an Andalusian shepherd boy who yearns to travel in search of a worldly treasure in the Egyptian pyramids.",
        {"Author": "Paulo Coelho", "Pages": "208", "Theme": "Personal Legend & Destiny"},
        "HarperCollins India",
        ["https://images.unsplash.com/photo-1495446815901-a7297e633e8d?w=800"]
    ),
    (
        "cat-6", "Books & Stationery", "1984 by George Orwell (Centennial Collector's Edition)", "George Orwell",
        249, 350, 4.8, 46000,
        "Orwell's terrifying portrait of totalitarianism, Big Brother, and the erasure of individual truth in the superstate of Oceania. Essential literature.",
        {"Author": "George Orwell", "Pages": "328", "Category": "Classic Dystopian Fiction"},
        "Penguin Official Store",
        ["https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=800"]
    ),
    (
        "cat-6", "Books & Stationery", "Project Hail Mary by Andy Weir (Bestselling Sci-Fi)", "Andy Weir",
        449, 599, 4.9, 31200,
        "A lone astronaut must save the earth from disaster in this incredible new science-based space survival thriller from the author of The Martian.",
        {"Author": "Andy Weir", "Pages": "496", "Format": "Paperback"},
        "BookWorm India",
        ["https://images.unsplash.com/photo-1544947950-fa07a98d237f?w=800"]
    ),
    (
        "cat-6", "Books & Stationery", "Norwegian Wood by Haruki Murakami (Vintage Classics)", "Haruki Murakami",
        399, 550, 4.7, 24600,
        "A magnificent coming-of-age story blending nostalgia, love, and grief in 1960s Tokyo, scored to the melancholy music of the Beatles.",
        {"Author": "Haruki Murakami", "Pages": "400", "Translator": "Jay Rubin"},
        "Penguin Official Store",
        ["https://images.unsplash.com/photo-1495446815901-a7297e633e8d?w=800"]
    ),
    (
        "cat-6", "Books & Stationery", "Parker Sonnet Stainless Steel Gold Trim Medium Nib Fountain Pen", "Parker",
        4999, 7500, 4.8, 2800,
        "Assembled by hand with 17 individual pieces. Brushed stainless steel barrel with gleaming 23k gold plated clip and trim. Includes ink converter.",
        {"Nib": "Stainless Steel Gold Finish M-Nib", "Ink System": "Cartridge / Converter", "Body": "Brushed Stainless Steel"},
        "Classmate Official Store",
        ["https://images.unsplash.com/photo-1583485088034-697b5bc54ccd?w=800"]
    ),
    (
        "cat-6", "Books & Stationery", "Moleskine Classic Hardcover Ruled Notebook Large Black 240 Pages", "Moleskine",
        1850, 2400, 4.8, 11400,
        "Bound in oilcloth-covered cardboard with rounded corners, acid-free ivory pages, bookmark ribbon, elastic closure, and expandable inner rear pocket.",
        {"Size": "Large (13 x 21 cm)", "Pages": "240 Acid-Free Ivory Pages", "Ruling": "Ruled / Lined"},
        "Classmate Official Store",
        ["https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=800"]
    ),
    (
        "cat-6", "Books & Stationery", "Faber-Castell Polychromos Artist Coloured Pencils Tin of 36", "Faber-Castell",
        4499, 5999, 4.9, 5600,
        "Valued internationally by professionals for unmatched lightfastness, break-resistant thick 3.8mm leads, soft oil-based buttery blendability.",
        {"Count": "36 Professional Colors", "Lead Diameter": "3.8 mm Oil-Based", "Case": "Protective Metal Tin"},
        "Faber-Castell Official Store",
        ["https://images.unsplash.com/photo-1513542789411-b6a5d4f31634?w=800"]
    ),
    (
        "cat-6", "Books & Stationery", "Staedtler Pigment Liner Micron Fineliner Pen Set of 6 Assorted", "Staedtler",
        799, 1190, 4.7, 14200,
        "Lightfast, indelible waterproof pigment ink fineliners with long metal-clad tips designed for technical drafting, Zentangle art, and urban sketching.",
        {"Line Widths": "0.05, 0.1, 0.2, 0.3, 0.5, 0.8 mm", "Ink": "Waterproof Pigment Black", "Cap Off": "Can be left uncapped for 18h"},
        "Faber-Castell Official Store",
        ["https://images.unsplash.com/photo-1583485088034-697b5bc54ccd?w=800"]
    ),
    (
        "cat-6", "Books & Stationery", "Winsor & Newton Cotman Watercolour Studio Set 24 Half Pans", "Winsor & Newton",
        2499, 3600, 4.8, 4100,
        "Formulated with fine art pigments for excellent tinting strength, color transparency, and working properties. Palette box with integrated mixing wells.",
        {"Paints": "24 Assorted Half Pans", "Grade": "Fine Art Cotman Series", "Box": "Molded Plastic Studio Box"},
        "Faber-Castell Official Store",
        ["https://images.unsplash.com/photo-1513542789411-b6a5d4f31634?w=800"]
    ),
    (
        "cat-6", "Books & Stationery", "Classmate Pulse 6-Subject Spiral Notebook Single Ruled 300 Pages", "Classmate",
        180, 240, 4.5, 34000,
        "High quality elemental chlorine-free paper with 6 colorful movable divider sheets. Perforated pages for clean tearing and rust-free spiral wire.",
        {"Pages": "300 Pages Single Ruled", "Dividers": "6 Re-arrangeable Color Index Tabs", "Paper": "Ozone-Treated Eco-Paper"},
        "Classmate Official Store",
        ["https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=800"]
    ),
    (
        "cat-6", "Books & Stationery", "Casio FX-991CW ClassWiz Non-Programmable Scientific Calculator", "Casio",
        1595, 1795, 4.8, 29000,
        "Features high-definition Natural Textbook 4-gradation display with over 540 functions including spreadsheet, matrix, and QR code visualization.",
        {"Functions": "540+ Mathematical Functions", "Display": "Natural Textbook Display", "Power": "Solar + Battery Backup"},
        "Appario Retail",
        ["https://images.unsplash.com/photo-1587829741301-dc798b83add3?w=800"]
    ),
    (
        "cat-6", "Books & Stationery", "Pilot V7 Hi-Tecpoint Rollerball Liquid Ink Pen Black (Pack of 3)", "Pilot",
        210, 270, 4.6, 42000,
        "Unique 0.7mm multi-dimple tip provides smooth skip-free writing. Pure liquid ink controller guarantees uniform ink flow to the last drop.",
        {"Tip Size": "0.7 mm Fine", "Ink Type": "Pure Liquid Ink", "Pack": "3 Pens Black Ink"},
        "Classmate Official Store",
        ["https://images.unsplash.com/photo-1583485088034-697b5bc54ccd?w=800"]
    ),
    (
        "cat-6", "Books & Stationery", "Brustro Artists Wiro Watercolour Journal Cold Pressed 300 GSM A5", "Brustro",
        449, 650, 4.7, 8200,
        "Heavyweight 300 GSM 25% cotton chlorine-free cold pressed textured paper. Acid-free pages prevent fading and yellowing over decades.",
        {"Weight": "300 GSM Heavyweight", "Size": "A5 (14.8 x 21 cm)", "Sheets": "30 Sheets (60 Pages)"},
        "Faber-Castell Official Store",
        ["https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=800"]
    ),
    (
        "cat-6", "Books & Stationery", "Camlin Kokuyo Artist Water Colour Cakes 24 Shades Tin Box", "Camlin",
        275, 350, 4.4, 18900,
        "Concentrated rich pigment color cakes with outstanding brilliance and transparency. Includes mixing palette inside lid and a round hog hair brush.",
        {"Colors": "24 Vibrant Shades", "Form": "Dry Cake with Brush", "Packaging": "Durable Metal Tin"},
        "Classmate Official Store",
        ["https://images.unsplash.com/photo-1513542789411-b6a5d4f31634?w=800"]
    ),
    (
        "cat-6", "Books & Stationery", "Kangaro Stapler No. 10 with 1000 Staples Pack", "Kangaro",
        85, 120, 4.6, 48000,
        "All-metal robust steel mechanism with quick-loading magazine and integrated rear staple remover. Binds up to 20 sheets cleanly.",
        {"Capacity": "Staples up to 20 Sheets", "Staple Size": "No. 10", "Pins Included": "Box of 1000 Staples"},
        "Classmate Official Store",
        ["https://images.unsplash.com/photo-1583485088034-697b5bc54ccd?w=800"]
    ),
    (
        "cat-6", "Books & Stationery", "Scotch 3M Transparent Packaging Tape 2-inch x 65 Meters (Pack of 2)", "3M",
        199, 320, 4.5, 14200,
        "Industrial strength heavy-duty carton sealing tape with high shear acrylic adhesive that withstands moisture and temperature fluctuations.",
        {"Width": "48 mm (2 inches)", "Length": "65 Meters each roll", "Pack": "Pack of 2 Rolls"},
        "Solimo Retails",
        ["https://images.unsplash.com/photo-1583485088034-697b5bc54ccd?w=800"]
    ),
    (
        "cat-6", "Books & Stationery", "Faber-Castell Textliner 38 Pastel Highlighters (Wallet of 6)", "Faber-Castell",
        180, 240, 4.6, 21200,
        "Soft aesthetic pastel highlighters with chisel tips allowing 3 different line widths (1, 2 and 5mm). Water-based ink will not bleed through notebook pages.",
        {"Colors": "6 Aesthetic Pastel Shades", "Tip": "Chisel Tip (1, 2, 5mm)", "Ink": "Smudge-Proof Water Based"},
        "Faber-Castell Official Store",
        ["https://images.unsplash.com/photo-1583485088034-697b5bc54ccd?w=800"]
    ),
    (
        "cat-6", "Books & Stationery", "Solo Heavy Duty Clear Book Display File 40 Pockets A4 Size", "Solo",
        225, 320, 4.5, 9600,
        "Stiff polypropylene cover with 40 clear anti-glare copysafe pockets. Keeps certificates, documents and presentation sheets pristine without punching.",
        {"Pockets": "40 Transparent Sheet Protectors", "Size": "A4 Size", "Closure": "Thumb Cut Spine Label"},
        "Classmate Official Store",
        ["https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=800"]
    ),

    # ---------------- GROCERY & GOURMET (26 products) ----------------
    (
        "cat-7", "Grocery & Gourmet", "India Gate Classic Super Basmati Rice 5kg Aged Premium Grain", "India Gate",
        799, 1150, 4.7, 34200,
        "Exotic aroma, sweet taste, and extra-long slender grains that elongate up to two times their original length after cooking. Aged for two full years.",
        {"Weight": "5 kg", "Aging": "2 Years Naturally Aged", "Type": "Extra Long Grain Basmati"},
        "Tata Consumer Products",
        ["https://images.unsplash.com/photo-1586201375761-83865001e31c?w=800"]
    ),
    (
        "cat-7", "Grocery & Gourmet", "Figaro 100% Pure Extra Virgin Olive Oil Tin 1 Litre Cold Pressed", "Figaro",
        1199, 1699, 4.8, 18900,
        "Imported Spanish extra virgin olive oil extracted purely from the first cold pressing of olives. Free from trans-fats and chemical additives.",
        {"Volume": "1000 ml", "Processing": "First Cold Pressed", "Origin": "Spain"},
        "Adani Wilmar",
        ["https://images.unsplash.com/photo-1474979266404-7eaacbcd87c5?w=800"]
    ),
    (
        "cat-7", "Grocery & Gourmet", "Fortune Sunlite Refined Sunflower Oil 5 Litre Can", "Fortune",
        649, 850, 4.5, 41000,
        "Light and clear cooking oil enriched with Vitamins A and D. Features high smoke point ideal for frying, sautéing and authentic Indian curries.",
        {"Volume": "5 Litres", "Vitamins": "Fortified with Vit A & D", "Type": "Refined Sunflower Oil"},
        "Adani Wilmar",
        ["https://images.unsplash.com/photo-1474979266404-7eaacbcd87c5?w=800"]
    ),
    (
        "cat-7", "Grocery & Gourmet", "Aashirvaad Select 100% Sharbati Whole Wheat Atta 5kg", "Aashirvaad",
        299, 360, 4.7, 38000,
        "Made from golden Sharbati wheat grains harvested in the fertile plains of Sehore, Madhya Pradesh. Delivers softer, fluffier rotis that stay fresh longer.",
        {"Weight": "5 kg", "Wheat": "100% MP Sharbati Whole Wheat", "Fiber": "Zero Maida / High Dietary Fiber"},
        "Aashirvaad Official Store",
        ["https://images.unsplash.com/photo-1509440159596-0249088772ff?w=800"]
    ),
    (
        "cat-7", "Grocery & Gourmet", "Tata Salt Vacuum Evaporated Iodized Salt 1kg (Pack of 4)", "Tata Salt",
        100, 120, 4.8, 68000,
        "India's most trusted vacuum-evaporated table salt ensuring purity, hygiene, and the recommended daily iodine dosage for mental health.",
        {"Total Weight": "4 kg (4 x 1kg)", "Iodine": "Guaranteed Iodine Content", "Purity": "Vacuum Evaporated Pure"},
        "Tata Consumer Products",
        ["https://images.unsplash.com/photo-1518110925495-5fe2fda0442c?w=800"]
    ),
    (
        "cat-7", "Grocery & Gourmet", "Happilo 100% Natural Premium California Raw Almonds 1kg Value Pack", "Happilo",
        849, 1399, 4.7, 28400,
        "Handpicked crunchy California non-GMO raw almonds rich in healthy mono-unsaturated fats, dietary fiber, plant protein, and natural antioxidant Vitamin E.",
        {"Weight": "1000g (1 kg)", "Grade": "Premium California Whole", "Preservatives": "Zero Added Preservatives"},
        "Happilo Official Store",
        ["https://images.unsplash.com/photo-1508061252966-f72fb9b5d278?w=800"]
    ),
    (
        "cat-7", "Grocery & Gourmet", "Nutraj Premium California Walnut Kernels Halves 500g", "Nutraj",
        549, 899, 4.6, 16200,
        "Vacuum-packed light-colored crispy walnut halves rich in Omega-3 fatty acids (ALA) to support heart health, memory, and cognitive sharpness.",
        {"Weight": "500g", "Nutrient": "Rich in Omega-3 Fatty Acids", "Form": "Whole Halves / Shelled"},
        "Happilo Official Store",
        ["https://images.unsplash.com/photo-1508061252966-f72fb9b5d278?w=800"]
    ),
    (
        "cat-7", "Grocery & Gourmet", "Urban Platter Organic Raw Black Chia Seeds 500g", "Urban Platter",
        349, 550, 4.6, 9400,
        "Superfood powerhouse packed with soluble fiber, plant protein, and calcium. Forms a gel in water, smoothies, yogurts, and morning oatmeal bowls.",
        {"Weight": "500g", "Diet": "Keto, Vegan & Gluten-Free", "Certifications": "100% Organic Certified"},
        "Happilo Official Store",
        ["https://images.unsplash.com/photo-1518110925495-5fe2fda0442c?w=800"]
    ),
    (
        "cat-7", "Grocery & Gourmet", "Dabur Himalayan 100% Pure Raw Organic Forest Honey 500g Glass Jar", "Dabur",
        299, 450, 4.7, 21800,
        "Naturally collected from wild forest hives in the pristine Himalayan valleys. NMR-tested for zero adulteration and free from artificial sugar syrups.",
        {"Weight": "500g", "Purity": "100% NMR Tested Pure", "Origin": "Pristine Himalayan Foothills"},
        "ITC Limited",
        ["https://images.unsplash.com/photo-1587049352846-4a222e784d38?w=800"]
    ),
    (
        "cat-7", "Grocery & Gourmet", "Lindt Excellence 85% Cocoa Extra Dark Chocolate Bar 100g", "Lindt",
        275, 350, 4.8, 14200,
        "Masterfully crafted by Swiss Master Chocolatiers. Full-bodied rich cocoa profile with roasted hazelnut and tobacco notes, low sugar.",
        {"Weight": "100g", "Cocoa": "85% Pure Dark Cocoa", "Origin": "Switzerland"},
        "Happilo Official Store",
        ["https://images.unsplash.com/photo-1549007994-cb92caebd54b?w=800"]
    ),
    (
        "cat-7", "Grocery & Gourmet", "Hershey's Exotic Dark Chocolate Blueberry & Acai 100g (Pack of 2)", "Hershey's",
        240, 300, 4.5, 8900,
        "Silky dark chocolate enrobing luscious whole dried blueberry and acai berry centers. A luxurious balance of rich cocoa and sweet-tart fruit.",
        {"Total Weight": "200g (2 x 100g)", "Flavor": "Blueberry & Acai Fruit Core", "Type": "Exotic Dark Chocolate"},
        "Happilo Official Store",
        ["https://images.unsplash.com/photo-1549007994-cb92caebd54b?w=800"]
    ),
    (
        "cat-7", "Grocery & Gourmet", "Blue Tokai Coffee Roasters Vienna Roast Arabica Grounds 250g", "Blue Tokai",
        450, 520, 4.9, 12600,
        "100% specialty grade Indian Arabica roasted dark to perfection. Tasting notes of cocoa, toasted walnuts, and oaky caramel with thick crema.",
        {"Weight": "250g", "Roast Level": "Dark (Vienna Roast)", "Grind": "Medium-Fine (Moka Pot / Aeropress)"},
        "Tata Consumer Products",
        ["https://images.unsplash.com/photo-1514432324607-a09d9b4aefdd?w=800"]
    ),
    (
        "cat-7", "Grocery & Gourmet", "Twinings Pure Camomile Herbal Infusion Tea Bags 25s", "Twinings",
        340, 425, 4.6, 9100,
        "Naturally caffeine-free herbal infusion made from pure whole camomile flower heads to soothe your nervous system and promote deep restful sleep.",
        {"Quantity": "25 Foil-Wrapped Tea Bags", "Caffeine": "100% Naturally Decaf", "Benefit": "Calming Sleep Aid"},
        "Tata Tea Official Store",
        ["https://images.unsplash.com/photo-1576092768241-dec231879fc3?w=800"]
    ),
    (
        "cat-7", "Grocery & Gourmet", "Kellogg's Real Almond & Honey Crunchy Muesli 1kg", "Kellogg's",
        499, 699, 4.6, 26800,
        "Multi-grain cereal packed with 5 nutritious grains (wheat, corn, oats, rice, barley), crispy sliced almonds, and a touch of golden natural honey.",
        {"Weight": "1000g (1 kg)", "Grains": "5 Nutritious Grains", "Source": "High Fiber & Vitamin B"},
        "Tata Consumer Products",
        ["https://images.unsplash.com/photo-1517673132405-a56a62b18caf?w=800"]
    ),
    (
        "cat-7", "Grocery & Gourmet", "Bagrry's 100% Whole Rolled Oats 1kg Jumbo Flakes", "Bagrry's",
        229, 325, 4.6, 31000,
        "100% imported Australian wholegrain oats with high beta-glucan soluble fiber that helps reduce blood cholesterol and keeps stomach full for hours.",
        {"Weight": "1 kg Jumbo Flakes", "Soluble Fiber": "Beta-Glucan Enriched", "Processing": "Steamed and Rolled Whole"},
        "Tata Consumer Products",
        ["https://images.unsplash.com/photo-1517673132405-a56a62b18caf?w=800"]
    ),
    (
        "cat-7", "Grocery & Gourmet", "Monin Gourmet Salted Caramel Syrup 1 Litre Glass Bottle", "Monin",
        899, 1150, 4.8, 4200,
        "Authentic French flavoring syrup combining sweet buttery caramel notes with a hint of Mediterranean sea salt. Perfect for iced coffees and frappes.",
        {"Volume": "1000 ml", "Origin": "France", "Application": "Cocktails, Iced Latte, Desserts"},
        "Happilo Official Store",
        ["https://images.unsplash.com/photo-1514432324607-a09d9b4aefdd?w=800"]
    ),
    (
        "cat-7", "Grocery & Gourmet", "Barilla Penne Rigate No. 73 Italian Durum Wheat Pasta 500g", "Barilla",
        185, 260, 4.7, 18900,
        "Italy's favorite pasta brand. Made from 100% non-GMO selected durum wheat semolina, holding sauces brilliantly with ridged al dente texture.",
        {"Weight": "500g", "Grain": "100% Durum Wheat Semolina", "Cook Time": "11 Minutes to Al Dente"},
        "Tata Consumer Products",
        ["https://images.unsplash.com/photo-1551183053-bf91a1d81141?w=800"]
    ),
    (
        "cat-7", "Grocery & Gourmet", "Tata Sampann Unpolished Toor Dal Arhar Dal 1kg", "Tata Sampann",
        175, 215, 4.6, 42500,
        "Unpolished toor dal that undergoes no artificial water, oil, or stone polishing, retaining natural wholesome nutrients and authentic pulse flavor.",
        {"Weight": "1 kg", "Polishing": "100% Unpolished Natural", "Nutrients": "High Protein & Iron"},
        "Tata Sampann Official Store",
        ["https://images.unsplash.com/photo-1518110925495-5fe2fda0442c?w=800"]
    ),
    (
        "cat-7", "Grocery & Gourmet", "Saffola Gold Pro Healthy Lifestyle Blended Cooking Oil 5L Can", "Saffola",
        789, 995, 4.6, 36000,
        "Dual seed blend of 80% Rice Bran Oil and 20% Sunflower Oil featuring LOSORB technology that absorbs up to 33% less oil in deep fried foods.",
        {"Volume": "5 Litres", "Technology": "LOSORB Less Absorption", "Antioxidants": "High Natural Oryzanol"},
        "Saffola Official Store",
        ["https://images.unsplash.com/photo-1474979266404-7eaacbcd87c5?w=800"]
    ),
    (
        "cat-7", "Grocery & Gourmet", "Kissan Fresh Tomato Ketchup 1kg Squeezy Spouch", "Kissan",
        125, 160, 4.5, 48000,
        "Made from 100% real ripe sun-kissed juicy tomatoes. Thick and tangy ketchup loved across Indian households for samosas, fries, and burgers.",
        {"Weight": "1 kg Squeezy Pouch", "Ingredients": "100% Real Tomatoes", "Packaging": "Convenient Spout Pouch"},
        "Kissan Official Store",
        ["https://images.unsplash.com/photo-1589733955941-5eeaf752f6dd?w=800"]
    ),
    (
        "cat-7", "Grocery & Gourmet", "Maggi 2-Minute Masala Instant Noodles (Pack of 12 x 70g)", "Maggi",
        168, 192, 4.8, 85000,
        "The undisputed king of comfort food. Irresistible blend of 10 choicest roasted spices with iron fortification in every slurp-worthy bowl.",
        {"Weight": "840g (12 x 70g Cakes)", "Flavour": "Authentic Masala Magic", "Cook Time": "2 Minutes"},
        "ITC Limited",
        ["https://images.unsplash.com/photo-1569718212165-3a8278d5f624?w=800"]
    ),
    (
        "cat-7", "Grocery & Gourmet", "Cadbury Dairy Milk Silk Chocolate Bar 150g (Pack of 3)", "Cadbury",
        495, 525, 4.8, 62000,
        "Impossibly smooth, velvety, and creamy milk chocolate crafted with a glass and a half of pure milk. Melts delightfully on the tongue.",
        {"Total Weight": "450g (3 x 150g)", "Texture": "Silky Smooth Melt-in-Mouth", "Type": "Premium Milk Chocolate"},
        "ITC Limited",
        ["https://images.unsplash.com/photo-1549007994-cb92caebd54b?w=800"]
    ),
    (
        "cat-7", "Grocery & Gourmet", "Brooke Bond Red Label Tea 1kg Natural Care with 5 Herbs", "Brooke Bond",
        499, 620, 4.6, 32000,
        "Premium CTC black tea blend infused with Ashwagandha, Tulsi, Mulethi, Cardamom and Ginger to boost natural immunity and relieve fatigue.",
        {"Weight": "1000g (1 kg)", "Herbs": "Tulsi, Ginger, Mulethi, Cardamom, Ashwagandha", "Type": "CTC Leaf Tea"},
        "Tata Tea Official Store",
        ["https://images.unsplash.com/photo-1576092768241-dec231879fc3?w=800"]
    ),
    (
        "cat-7", "Grocery & Gourmet", "Epigamia Greek Yogurt Natural 400g High Protein", "Epigamia",
        150, 180, 4.7, 9800,
        "Thick and creamy strained Greek yogurt boasting 8g of protein per serving with zero added refined sugars, starch, or preservatives.",
        {"Weight": "400g Tub", "Protein": "8g Protein per 100g", "Live Cultures": "Probiotic Gut Friendly"},
        "Tata Consumer Products",
        ["https://images.unsplash.com/photo-1517673132405-a56a62b18caf?w=800"]
    ),
    (
        "cat-7", "Grocery & Gourmet", "Haldiram's Nagpur Bhujia Sev Crispy Snack 1kg", "Haldiram's",
        260, 310, 4.7, 54000,
        "Iconic crispy spicy extruded snack made from moth bean flour, chickpea flour and signature aromatic spices fried in healthy vegetable oil.",
        {"Weight": "1000g (1 kg)", "Dietary": "100% Vegetarian", "Flavour": "Authentic Bikaneri Spicy Bhujia"},
        "ITC Limited",
        ["https://images.unsplash.com/photo-1569718212165-3a8278d5f624?w=800"]
    ),
    (
        "cat-7", "Grocery & Gourmet", "Paper Boat Alphonso Aamras Mango Juice 1 Litre Tetra Pak (Pack of 2)", "Paper Boat",
        220, 260, 4.6, 28000,
        "Thick authentic mango pulp drink made from 45% ripe Alphonso and Ratnagiri mango puree without artificial preservatives or GMOs.",
        {"Volume": "2 Litres (2 x 1000ml)", "Fruit Content": "45% Alphonso Pulp", "Preservatives": "Zero Added Preservatives"},
        "Tata Consumer Products",
        ["https://images.unsplash.com/photo-1544816155-12df9643f363?w=800"]
    ),

    # ---------------- TOYS & BABY CARE (25 products) ----------------
    (
        "cat-8", "Toys & Baby Care", "LEGO Creator 3in1 Mighty Dinosaurs 31058 Building Kit", "LEGO",
        1399, 1799, 4.8, 18900,
        "Build a ferocious T-Rex with bright orange eyes, posable joints and open mouth with sharp teeth. Rebuilds into a Triceratops or a Pterodactyl.",
        {"Pieces": "174 Pieces", "Age Group": "7-12 Years", "Models": "T-Rex, Triceratops, Pterodactyl"},
        "LEGO Official Store",
        ["https://images.unsplash.com/photo-1587654780291-39c9404d746b?w=800"]
    ),
    (
        "cat-8", "Toys & Baby Care", "LEGO Star Wars Millennium Falcon 75257 Model Starship", "LEGO",
        14999, 18999, 4.9, 4200,
        "Iconic freighter ship featuring rotating top and bottom gun turrets, 2 spring-loaded shooters, opening cockpit, and 7 Star Wars minifigures.",
        {"Pieces": "1351 Pieces", "Minifigures": "Finn, Chewbacca, Lando, C-3PO, Boolio, D-O, BB-8", "Series": "Star Wars The Rise of Skywalker"},
        "LEGO Official Store",
        ["https://images.unsplash.com/photo-1587654780291-39c9404d746b?w=800"]
    ),
    (
        "cat-8", "Toys & Baby Care", "Hot Wheels 10-Car Pack Die-Cast Toy Vehicles Assortment", "Hot Wheels",
        1299, 1799, 4.8, 32000,
        "Authentic 1:64 scale die-cast vehicles with realistic details and eye-catching decos. Perfect collection starter for automobile enthusiasts.",
        {"Scale": "1:64 Die-Cast Scale", "Vehicle Count": "10 Cars Included", "Material": "Metal and Non-Toxic ABS"},
        "Hot Wheels Official Store",
        ["https://images.unsplash.com/photo-1594787318286-3d835c1d207f?w=800"]
    ),
    (
        "cat-8", "Toys & Baby Care", "Nerf Elite 2.0 Commander RD-6 Dart Blaster with 12 Darts", "Nerf",
        1199, 1599, 4.6, 14200,
        "Features a 6-dart rotating drum and tactical rails to customize for any battle. Slam-fire action fires all 6 darts in rapid succession up to 90 feet.",
        {"Drum Capacity": "6 Rotating Darts", "Darts Included": "12 Official Nerf Elite Darts", "Range": "Fires up to 27 Meters (90 Feet)"},
        "Funskool Official Store",
        ["https://images.unsplash.com/photo-1587654780291-39c9404d746b?w=800"]
    ),
    (
        "cat-8", "Toys & Baby Care", "Barbie Malibu House 2-Story Dollhouse with 6 Rooms & 25 Accessories", "Barbie",
        7999, 10999, 4.7, 6100,
        "Two-story playset opens to reveal kitchen, dining room, living room, bedroom, bathroom, and outdoor patio with transforming flip-wall furniture.",
        {"Rooms": "6 Play Spaces on 2 Stories", "Accessories": "25+ Furnishings and Decors", "Foldable": "Folds Flat for Storage"},
        "Funskool Official Store",
        ["https://images.unsplash.com/photo-1587654780291-39c9404d746b?w=800"]
    ),
    (
        "cat-8", "Toys & Baby Care", "Rubik's Connected Smart Bluetooth 3x3 Speed Cube", "Rubik's",
        3499, 4999, 4.8, 3800,
        "Smart magnetic cube connects via Bluetooth to your smartphone. Tracks your turns in real time, teaches solving algorithms, and lets you battle globally.",
        {"Connectivity": "Bluetooth 5.0 Low Energy", "Sensors": "6-Axis Tracking Sensors", "App": "Rubik's Connected iOS & Android"},
        "Funskool Official Store",
        ["https://images.unsplash.com/photo-1591991731833-b4807cf7ef94?w=800"]
    ),
    (
        "cat-8", "Toys & Baby Care", "Smartivity Mechanical Hydraulic Crane DIY STEM Science Toy Kit", "Smartivity",
        799, 1199, 4.6, 9200,
        "Educational construction kit teaches hydraulic pressure, rack-and-pinion movement, and mechanics using syringe cylinders and eco-friendly engineered wood.",
        {"Age": "8 Years and Above", "Material": "Eco-Friendly Laser Cut Engineered Pine Wood", "Principle": "Pascal's Law of Hydraulics"},
        "Funskool Official Store",
        ["https://images.unsplash.com/photo-1587654780291-39c9404d746b?w=800"]
    ),
    (
        "cat-8", "Toys & Baby Care", "Pampers All Round Protection Diaper Pants XL 56 Count", "Pampers",
        999, 1399, 4.7, 45000,
        "Ultra-absorbent Magic Gel core locks away wetness for up to 12 hours of dry comfort. Anti-rash lotion with Aloe Vera soothes delicate baby skin.",
        {"Size": "Extra Large (XL - 12 to 17 kg)", "Count": "56 Diaper Pants", "Feature": "360-Degree Stretchy Cotton Waistband"},
        "Pampers Official Store",
        ["https://images.unsplash.com/photo-1515488042361-ee00e0ddd4e4?w=800"]
    ),
    (
        "cat-8", "Toys & Baby Care", "Huggies Nature Care Diaper Pants Monthly Box Large 72 Count", "Huggies",
        1149, 1599, 4.6, 28000,
        "Infused with natural organic ingredients and Vitamin E. Bubble-bed technology provides cloud-like softness preventing red marks and skin irritation.",
        {"Size": "Large (L - 9 to 14 kg)", "Count": "72 Diapers Monthly Box", "Absorption": "Bubble-Bed 12-Hour Protection"},
        "Babyhug Official Store",
        ["https://images.unsplash.com/photo-1515488042361-ee00e0ddd4e4?w=800"]
    ),
    (
        "cat-8", "Toys & Baby Care", "Sebamed Baby Cleansing Bar pH 5.5 for Delicate Skin 150g", "Sebamed",
        375, 450, 4.8, 18900,
        "100% soap-free and alkali-free cleansing bar formulated with physiological pH 5.5 to support development of baby's natural protective acid mantle.",
        {"Weight": "150g", "pH Value": "pH 5.5 Clinically Proven", "Free From": "0% Parabens, Phthalates & Soap"},
        "Babyhug Official Store",
        ["https://images.unsplash.com/photo-1515488042361-ee00e0ddd4e4?w=800"]
    ),
    (
        "cat-8", "Toys & Baby Care", "Chicco Natural Sensation Baby Massage Oil with Sweet Almond 200ml", "Chicco",
        549, 699, 4.7, 12400,
        "Deeply nourishes and hydrates delicate baby skin without leaving an oily film. Contains Sweet Almond Oil, Rice Bran Oil, and Vitamin E.",
        {"Volume": "200 ml", "Ingredients": "Sweet Almond & Rice Bran Oils", "Hypoallergenic": "Clinically Tested on Sensitive Skin"},
        "Babyhug Official Store",
        ["https://images.unsplash.com/photo-1515488042361-ee00e0ddd4e4?w=800"]
    ),
    (
        "cat-8", "Toys & Baby Care", "Philips Avent Natural Response Baby Feeding Bottle 260ml", "Philips Avent",
        799, 1095, 4.8, 14200,
        "Natural Response nipple releases milk only when the baby actively drinks, just like at the breast. Anti-colic valve designed to reduce colic and discomfort.",
        {"Capacity": "260 ml (9 oz)", "Nipple Flow": "Flow 3 Nipple Included", "Safety": "100% BPA-Free Polypropylene"},
        "Philips Official Store",
        ["https://images.unsplash.com/photo-1515488042361-ee00e0ddd4e4?w=800"]
    ),
    (
        "cat-8", "Toys & Baby Care", "Dr. Brown's Options+ Anti-Colic Wide-Neck Bottles 270ml (Pack of 2)", "Dr. Brown's",
        1399, 1899, 4.7, 8600,
        "Clinically proven internal vent system prevents air bubbles from mixing with milk, preserving essential nutrients and preventing painful infant gas.",
        {"Capacity": "270 ml each (Pack of 2)", "Vent": "Internal Green Anti-Colic Vent", "Nipple": "Breast-Like Silicone"},
        "Babyhug Official Store",
        ["https://images.unsplash.com/photo-1515488042361-ee00e0ddd4e4?w=800"]
    ),
    (
        "cat-8", "Toys & Baby Care", "LuvLap Sunshine Baby Stroller with Multi-Recline & Reversible Handlebar", "LuvLap",
        4999, 7499, 4.5, 16200,
        "Certified European Standard EN 1888 safety stroller with 3-position seat recline, 5-point safety harness, 360-degree swivel front wheels with brakes.",
        {"Safety": "EN 1888 European Standard", "Harness": "5-Point Safety Belt", "Weight Limit": "Up to 15 KG (0-3 Years)"},
        "R for Rabbit Official Store",
        ["https://images.unsplash.com/photo-1591991731833-b4807cf7ef94?w=800"]
    ),
    (
        "cat-8", "Toys & Baby Care", "R for Rabbit Chocolate Ride Baby Car Seat ECE R44/04 Certified", "R for Rabbit",
        3899, 5999, 4.7, 8400,
        "Crash tested and certified under stringent European safety standard ECE R44/04. Multi-stage convertible seat adapts from infant to toddler (0-25 kg).",
        {"Certification": "ECE R44/04 European Safety", "Group": "Group 0+, 1, 2 (0-25 KG)", "Recline": "3-Position Recline"},
        "R for Rabbit Official Store",
        ["https://images.unsplash.com/photo-1591991731833-b4807cf7ef94?w=800"]
    ),
    (
        "cat-8", "Toys & Baby Care", "Fisher-Price Deluxe Kick & Play Piano Baby Gym Playmat", "Fisher-Price",
        2899, 3999, 4.8, 19400,
        "4 ways to play as baby grows: Lay & play, Tummy time, Sit & play, and Take along. Removable light-up piano keys play songs and teach colors and numbers.",
        {"Modes": "Smart Stages Technology", "Includes": "Gym Mat, Piano, 5 Activity Hanging Toys", "Batteries": "3 AA Included"},
        "Funskool Official Store",
        ["https://images.unsplash.com/photo-1515488042361-ee00e0ddd4e4?w=800"]
    ),
    (
        "cat-8", "Toys & Baby Care", "Baybee Foldable Wooden Baby Crib Cot with Rocking Function", "Baybee",
        8499, 12999, 4.6, 3200,
        "Crafted from premium New Zealand pine wood with smooth non-toxic rounded corners. Converts easily into a soothing gentle baby cradle rocker.",
        {"Material": "Natural New Zealand Pine Wood", "Mobility": "360-degree Lockable Wheels", "Mosquito Net": "Full Coverage Net Included"},
        "R for Rabbit Official Store",
        ["https://images.unsplash.com/photo-1515488042361-ee00e0ddd4e4?w=800"]
    ),
    (
        "cat-8", "Toys & Baby Care", "Pigeon Silicone Baby Teether & Gum Soother BPA-Free", "Pigeon",
        199, 299, 4.6, 24000,
        "Soft textured food-grade silicone teether gently massages sensitive teething gums. Easy-to-grasp ring handle sized perfectly for baby's little hands.",
        {"Material": "100% Food-Grade Silicone", "Sterilization": "Boiling / Steam Sterilizer Safe", "BPA": "Zero BPA"},
        "Babyhug Official Store",
        ["https://images.unsplash.com/photo-1515488042361-ee00e0ddd4e4?w=800"]
    ),
    (
        "cat-8", "Toys & Baby Care", "Funskool Giggles Stacking Barrels Nesting Toy Set", "Funskool",
        299, 449, 4.7, 18500,
        "Set of 5 vibrantly colored nesting barrels that fit inside one another or stack into a tower, fostering spatial awareness and hand-eye coordination.",
        {"Pieces": "5 Nesting / Stacking Barrels", "Age": "12 Months+", "Safety": "Non-Toxic Child-Safe ABS"},
        "Funskool Official Store",
        ["https://images.unsplash.com/photo-1596461404969-9ae70f2830c1?w=800"]
    ),
    (
        "cat-8", "Toys & Baby Care", "Mee Mee Breathable Baby Carrier with Lumbar Support 4-in-1", "Mee Mee",
        1799, 2799, 4.4, 9100,
        "4 ergonomic carrying positions: Inward front facing, Outward front facing, Kangaroo position, and Backpack mode. Cushioned head and lumbar support.",
        {"Positions": "4-in-1 Ergonomic Modes", "Weight": "For Babies 3.5 to 12 KG", "Padding": "Air-Mesh Lumbar Support"},
        "Babyhug Official Store",
        ["https://images.unsplash.com/photo-1515488042361-ee00e0ddd4e4?w=800"]
    ),
    (
        "cat-8", "Toys & Baby Care", "Johnson's Baby Top-to-Toe Gentle Wash 500ml with Pump", "Johnson's",
        345, 450, 4.6, 38000,
        "No More Tears hypoallergenic formula cleanses both fine baby hair and delicate newborn skin without dryness. Free from parabens and sulfates.",
        {"Volume": "500 ml Pump Bottle", "Formula": "No More Tears Tested", "pH": "Balanced for Infant Skin"},
        "Babyhug Official Store",
        ["https://images.unsplash.com/photo-1515488042361-ee00e0ddd4e4?w=800"]
    ),
    (
        "cat-8", "Toys & Baby Care", "Himalaya Baby Lotion with Almond & Olive Oil 400ml", "Himalaya",
        240, 310, 4.5, 46000,
        "Ayurvedic formulation blending cold-pressed almond oil, olive oil, and licorice to maintain suppleness and prevent skin chapping during all seasons.",
        {"Volume": "400 ml", "Key Ingredients": "Olive Oil, Almond Oil, Licorice", "Safety": "Clinically Mildness Proven"},
        "Sashtri Healthcare Ltd",
        ["https://images.unsplash.com/photo-1515488042361-ee00e0ddd4e4?w=800"]
    ),
    (
        "cat-8", "Toys & Baby Care", "Funskool Monopoly Deluxe Classic Family Board Game", "Funskool",
        899, 1299, 4.7, 34000,
        "The world's favorite family board game. Buy, sell, trade and scheme your way to riches. Includes classic tokens, title deed cards, houses and hotels.",
        {"Players": "2 to 6 Players", "Age": "8 Years+", "Includes": "GameBoard, Tokens, Play Money, Cards"},
        "Funskool Official Store",
        ["https://images.unsplash.com/photo-1610890716171-6b1bb98ffd09?w=800"]
    ),
    (
        "cat-8", "Toys & Baby Care", "Wipro Baby Soft Touch Ultra-Sensitive Water Wipes (Pack of 3 x 72)", "Wipro",
        399, 599, 4.7, 16400,
        "Made with 99% pure pharmaceutical-grade deionized water and organic aloe vera. Hypoallergenic, unscented, and 3x thicker than regular wipes.",
        {"Wipes Count": "216 Wipes (3 Packs x 72)", "Water Content": "99% Pure Water", "Chemicals": "Zero Alcohol, Fragrance & Parabens"},
        "Babyhug Official Store",
        ["https://images.unsplash.com/photo-1515488042361-ee00e0ddd4e4?w=800"]
    ),
    (
        "cat-8", "Toys & Baby Care", "Sunbaby Universal High Chair for Baby Feeding with Adjustable Tray", "Sunbaby",
        2799, 4200, 4.5, 5800,
        "Sturdy steel frame baby high chair with 3-position adjustable removable food tray, 5-point safety harness, and stain-resistant wipe-clean seat cushion.",
        {"Safety": "5-Point Harness with Footrest", "Tray": "Dishwasher-Safe Removable Tray", "Age Limit": "6 Months to 3 Years (Up to 20 KG)"},
        "R for Rabbit Official Store",
        ["https://images.unsplash.com/photo-1591991731833-b4807cf7ef94?w=800"]
    ),
]


def seed_to_300():
    current_count = Product.objects.count()
    print(f"Current product count in database: {current_count}")
    
    needed = 300 - current_count
    print(f"Products needed to reach 300: {needed}")

    if needed <= 0:
        print("Catalog already has 300 or more products!")
        return

    # Check blueprints count
    print(f"Available blueprints: {len(NEW_PRODUCTS)}")
    items_to_add = NEW_PRODUCTS[:needed]

    stores = list(Store.objects.all())
    added = 0

    for cat_id, cat_name, title, brand, price, orig_price, rating, rev_count, desc, specs, seller, img_list in items_to_add:
        uid = uuid.uuid4().hex[:8]
        p_id = f"prod-bulk-{uid}"
        slug_base = title.lower().replace(" ", "-").replace("(", "").replace(")", "").replace(",", "").replace("/", "-")
        slug = f"{slug_base[:120]}-{uid}"
        discount = int(((orig_price - price) / max(1, orig_price)) * 100)
        stock_qty = random.randint(30, 220)
        cost_p = round(price * 0.72, 2)

        p = Product.objects.create(
            id=p_id,
            name=title,
            slug=slug,
            category=cat_name,
            categoryId=cat_id,
            brand=brand,
            price=float(price),
            originalPrice=float(orig_price),
            discount=discount,
            rating=float(rating),
            reviewCount=rev_count,
            stock=stock_qty,
            stockStatus="In Stock",
            featured=random.choice([True, False]),
            bestSeller=rating >= 4.7,
            newArrival=random.choice([True, False]),
            images=img_list,
            description=desc,
            specifications=specs,
            seller=seller,
            createdAt="2026-10-15",
            costPrice=cost_p,
            autoRestock=True,
            reorderLevel=5,
            restockQty=25
        )
        added += 1

        # Populate StoreInventory across stores for hyperlocal discovery
        for idx, store in enumerate(stores):
            store_qty = max(2, (stock_qty // max(1, len(stores))) + (idx % 4) * 2)
            StoreInventory.objects.update_or_create(
                store=store,
                product=p,
                defaults={
                    'id': f"inv-{store.id}-{p.id}",
                    'availableQuantity': store_qty,
                    'reservedQuantity': 0,
                    'storePrice': float(price),
                    'isAvailable': True,
                }
            )

    # Synchronize category counters
    for cat in Category.objects.all():
        cat.productCount = Product.objects.filter(category=cat.name).count()
        cat.save(update_fields=['productCount'])

    new_total = Product.objects.count()
    print(f"Successfully added {added} new products.")
    print(f"New total products in AutoCart catalog: {new_total}")
    print("\nProduct count by category:")
    for cat in Category.objects.all():
        print(f" - {cat.name}: {cat.productCount} products")


if __name__ == '__main__':
    seed_to_300()
