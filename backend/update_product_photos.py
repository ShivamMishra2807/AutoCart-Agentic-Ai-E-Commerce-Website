"""
Script to ensure all 300 products in AutoCart have rich, high-resolution multi-angle photos (3 photos each).
Maps each product by category and subcategory keywords to curated, crystal-clear Unsplash product photos.
"""
import os
import sys
import random
import re

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'autocart_core.settings')
import django
django.setup()

from api.models import Product, Category

# Rich library of high-resolution Unsplash photo pools categorized by product types
IMAGE_POOLS = {
    # ---------------- ELECTRONICS ----------------
    "laptop": [
        "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=800&q=80",
        "https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=800&q=80",
        "https://images.unsplash.com/photo-1588872657578-7efd1f1555ed?w=800&q=80",
        "https://images.unsplash.com/photo-1593642632823-8f785ba67e45?w=800&q=80",
        "https://images.unsplash.com/photo-1541807084-5c52b6b3adef?w=800&q=80",
        "https://images.unsplash.com/photo-1525547719571-a2d4ac8945e2?w=800&q=80"
    ],
    "monitor": [
        "https://images.unsplash.com/photo-1527443224154-c4a3942d3acf?w=800&q=80",
        "https://images.unsplash.com/photo-1547119957-637f8679db1e?w=800&q=80",
        "https://images.unsplash.com/photo-1593784991095-a205069470b6?w=800&q=80"
    ],
    "keyboard": [
        "https://images.unsplash.com/photo-1587829741301-dc798b83add3?w=800&q=80",
        "https://images.unsplash.com/photo-1595225476474-87563907a212?w=800&q=80",
        "https://images.unsplash.com/photo-1615663245857-ac93bb7c39e7?w=800&q=80"
    ],
    "mouse": [
        "https://images.unsplash.com/photo-1615663245857-ac93bb7c39e7?w=800&q=80",
        "https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?w=800&q=80",
        "https://images.unsplash.com/photo-1587829741301-dc798b83add3?w=800&q=80"
    ],
    "headphones": [
        "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=800&q=80",
        "https://images.unsplash.com/photo-1484704849700-f032a568e944?w=800&q=80",
        "https://images.unsplash.com/photo-1546435770-a3e426bf472b?w=800&q=80",
        "https://images.unsplash.com/photo-1583394838336-acd977736f90?w=800&q=80"
    ],
    "earbuds": [
        "https://images.unsplash.com/photo-1590658268037-6bf12165a8df?w=800&q=80",
        "https://images.unsplash.com/photo-1600294037681-c80b4cb5b434?w=800&q=80",
        "https://images.unsplash.com/photo-1572536147248-ac59a8abfa4b?w=800&q=80"
    ],
    "speaker": [
        "https://images.unsplash.com/photo-1545454675-3531b543be5d?w=800&q=80",
        "https://images.unsplash.com/photo-1608043152269-423dbba4e7e1?w=800&q=80",
        "https://images.unsplash.com/photo-1508700115892-45ecd05ae2ad?w=800&q=80"
    ],
    "phone": [
        "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=800&q=80",
        "https://images.unsplash.com/photo-1598327105666-5b89351aff97?w=800&q=80",
        "https://images.unsplash.com/photo-1565849904461-04a58ad377e0?w=800&q=80",
        "https://images.unsplash.com/photo-1610945265064-0e34e5519bbf?w=800&q=80",
        "https://images.unsplash.com/photo-1695048133142-1a20484d2569?w=800&q=80"
    ],
    "tablet": [
        "https://images.unsplash.com/photo-1544244015-0df4b3ffc6b0?w=800&q=80",
        "https://images.unsplash.com/photo-1561154464-82e9adf32764?w=800&q=80",
        "https://images.unsplash.com/photo-1512499617640-c74ae3a79d37?w=800&q=80"
    ],
    "smartwatch": [
        "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=800&q=80",
        "https://images.unsplash.com/photo-1508685096489-7aacd43bd3b1?w=800&q=80",
        "https://images.unsplash.com/photo-1546868871-7041f2a55e12?w=800&q=80"
    ],
    "camera": [
        "https://images.unsplash.com/photo-1516035069371-29a1b244cc32?w=800&q=80",
        "https://images.unsplash.com/photo-1526170375885-4d8ecf77b99f?w=800&q=80",
        "https://images.unsplash.com/photo-1508614589041-895b88991e3e?w=800&q=80"
    ],
    "electronics_general": [
        "https://images.unsplash.com/photo-1550009158-9ebf69173e03?w=800&q=80",
        "https://images.unsplash.com/photo-1609592424350-0255b768a44c?w=800&q=80",
        "https://images.unsplash.com/photo-1622445268096-7787f739fcfa?w=800&q=80"
    ],

    # ---------------- FASHION ----------------
    "shirt": [
        "https://images.unsplash.com/photo-1602810318383-e386cc2a3ccf?w=800&q=80",
        "https://images.unsplash.com/photo-1598033129183-c4f50c736f10?w=800&q=80",
        "https://images.unsplash.com/photo-1586363104862-3a5e2ab60d99?w=800&q=80"
    ],
    "jacket": [
        "https://images.unsplash.com/photo-1576995853123-5a10305d93c0?w=800&q=80",
        "https://images.unsplash.com/photo-1507679799987-c73779587ccf?w=800&q=80",
        "https://images.unsplash.com/photo-1544441893-675973e31985?w=800&q=80"
    ],
    "kurta": [
        "https://images.unsplash.com/photo-1610030469983-98e550d6193c?w=800&q=80",
        "https://images.unsplash.com/photo-1583391733956-3750e0ff4e8b?w=800&q=80",
        "https://images.unsplash.com/photo-1572804013309-59a88b7e92f1?w=800&q=80"
    ],
    "jeans": [
        "https://images.unsplash.com/photo-1541099649105-f69ad21f3246?w=800&q=80",
        "https://images.unsplash.com/photo-1582418702059-97ebafb35d09?w=800&q=80",
        "https://images.unsplash.com/photo-1542272604-787c3835535d?w=800&q=80"
    ],
    "shoes": [
        "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=800&q=80",
        "https://images.unsplash.com/photo-1608231387042-66d1773070a5?w=800&q=80",
        "https://images.unsplash.com/photo-1595950653106-6c9ebd614d3a?w=800&q=80",
        "https://images.unsplash.com/photo-1525966222134-fcfa99b8ae77?w=800&q=80",
        "https://images.unsplash.com/photo-1614252235316-8c857d38b5f4?w=800&q=80",
        "https://images.unsplash.com/photo-1587563871167-1ee9c731aefb?w=800&q=80"
    ],
    "watch": [
        "https://images.unsplash.com/photo-1524805444758-089113d48a6d?w=800&q=80",
        "https://images.unsplash.com/photo-1522335789203-aabd1fc54bc9?w=800&q=80",
        "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=800&q=80"
    ],
    "sunglasses": [
        "https://images.unsplash.com/photo-1511499767150-a48a237f0083?w=800&q=80",
        "https://images.unsplash.com/photo-1572635196237-14b3f281503f?w=800&q=80",
        "https://images.unsplash.com/photo-1508296695146-257a814070b4?w=800&q=80"
    ],
    "bag": [
        "https://images.unsplash.com/photo-1584917865442-de89df76afd3?w=800&q=80",
        "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=800&q=80",
        "https://images.unsplash.com/photo-1627123424574-724758594e93?w=800&q=80"
    ],
    "fashion_general": [
        "https://images.unsplash.com/photo-1445205170230-053b83016050?w=800&q=80",
        "https://images.unsplash.com/photo-1490481651871-ab68de25d43d?w=800&q=80",
        "https://images.unsplash.com/photo-1469334031218-e382a71b716b?w=800&q=80"
    ],

    # ---------------- HOME & KITCHEN ----------------
    "kitchen_appliance": [
        "https://images.unsplash.com/photo-1556911220-e15b29be8c8f?w=800&q=80",
        "https://images.unsplash.com/photo-1584269600464-37b1b58a9fe7?w=800&q=80",
        "https://images.unsplash.com/photo-1585670149967-b4f4da88cc9f?w=800&q=80",
        "https://images.unsplash.com/photo-1517668808822-9ebb02ae2a0e?w=800&q=80"
    ],
    "cookware": [
        "https://images.unsplash.com/photo-1584269600464-37b1b58a9fe7?w=800&q=80",
        "https://images.unsplash.com/photo-1556911220-e15b29be8c8f?w=800&q=80",
        "https://images.unsplash.com/photo-1614707267537-b85aaf00c4b7?w=800&q=80"
    ],
    "home_clean": [
        "https://images.unsplash.com/photo-1558317374-067fb5f30001?w=800&q=80",
        "https://images.unsplash.com/photo-1585771724684-38269d6639fd?w=800&q=80",
        "https://images.unsplash.com/photo-1550524514-9b6999b19e27?w=800&q=80"
    ],
    "home_bedding": [
        "https://images.unsplash.com/photo-1505693416388-ac5ce068fe85?w=800&q=80",
        "https://images.unsplash.com/photo-1584100936595-c0654b55a2e2?w=800&q=80",
        "https://images.unsplash.com/photo-1580481077195-c3a821a58875?w=800&q=80"
    ],

    # ---------------- BEAUTY & PERSONAL CARE ----------------
    "skincare": [
        "https://images.unsplash.com/photo-1620916566398-39f1143ab7be?w=800&q=80",
        "https://images.unsplash.com/photo-1608248597359-009947743d5c?w=800&q=80",
        "https://images.unsplash.com/photo-1556228720-195a672e8a03?w=800&q=80",
        "https://images.unsplash.com/photo-1598440947619-2c35fc9aa908?w=800&q=80"
    ],
    "haircare": [
        "https://images.unsplash.com/photo-1527799820374-dcf8d9d4a388?w=800&q=80",
        "https://images.unsplash.com/photo-1522337360788-8b13dee7a37e?w=800&q=80",
        "https://images.unsplash.com/photo-1608248597359-009947743d5c?w=800&q=80"
    ],
    "grooming": [
        "https://images.unsplash.com/photo-1585751119414-ef2636f8aede?w=800&q=80",
        "https://images.unsplash.com/photo-1592945403244-b3fbafd7f539?w=800&q=80",
        "https://images.unsplash.com/photo-1559591937-e1032397e594?w=800&q=80"
    ],
    "makeup": [
        "https://images.unsplash.com/photo-1586495777744-4413f21062fa?w=800&q=80",
        "https://images.unsplash.com/photo-1596462502278-27bfdc403348?w=800&q=80",
        "https://images.unsplash.com/photo-1522337360788-8b13dee7a37e?w=800&q=80"
    ],

    # ---------------- SPORTS & FITNESS ----------------
    "gym": [
        "https://images.unsplash.com/photo-1584735935682-2f2b69dff9d2?w=800&q=80",
        "https://images.unsplash.com/photo-1540497077202-7c8a3999166f?w=800&q=80",
        "https://images.unsplash.com/photo-1598971861713-54ad16a7e72e?w=800&q=80",
        "https://images.unsplash.com/photo-1518611012118-696072aa579a?w=800&q=80"
    ],
    "sports_gear": [
        "https://images.unsplash.com/photo-1531415074968-036ba1b575da?w=800&q=80",
        "https://images.unsplash.com/photo-1579952363873-27f3bade9f55?w=800&q=80",
        "https://images.unsplash.com/photo-1546519638-68e109498ffc?w=800&q=80",
        "https://images.unsplash.com/photo-1626224583764-f87db24ac4ea?w=800&q=80",
        "https://images.unsplash.com/photo-1530549387789-4c1017266635?w=800&q=80",
        "https://images.unsplash.com/photo-1511556532299-8f662fc26c06?w=800&q=80"
    ],
    "nutrition": [
        "https://images.unsplash.com/photo-1579722821273-0f6c7d44362f?w=800&q=80",
        "https://images.unsplash.com/photo-1523362628745-0c100150b504?w=800&q=80",
        "https://images.unsplash.com/photo-1544816155-12df9643f363?w=800&q=80"
    ],
    "yoga": [
        "https://images.unsplash.com/photo-1545205597-3d9d02c29597?w=800&q=80",
        "https://images.unsplash.com/photo-1518611012118-696072aa579a?w=800&q=80",
        "https://images.unsplash.com/photo-1598971861713-54ad16a7e72e?w=800&q=80"
    ],

    # ---------------- BOOKS & STATIONERY ----------------
    "book": [
        "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=800&q=80",
        "https://images.unsplash.com/photo-1544947950-fa07a98d237f?w=800&q=80",
        "https://images.unsplash.com/photo-1495446815901-a7297e633e8d?w=800&q=80"
    ],
    "stationery": [
        "https://images.unsplash.com/photo-1583485088034-697b5bc54ccd?w=800&q=80",
        "https://images.unsplash.com/photo-1513542789411-b6a5d4f31634?w=800&q=80",
        "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=800&q=80"
    ],

    # ---------------- GROCERY & GOURMET ----------------
    "grocery": [
        "https://images.unsplash.com/photo-1586201375761-83865001e31c?w=800&q=80",
        "https://images.unsplash.com/photo-1474979266404-7eaacbcd87c5?w=800&q=80",
        "https://images.unsplash.com/photo-1509440159596-0249088772ff?w=800&q=80",
        "https://images.unsplash.com/photo-1518110925495-5fe2fda0442c?w=800&q=80",
        "https://images.unsplash.com/photo-1508061252966-f72fb9b5d278?w=800&q=80",
        "https://images.unsplash.com/photo-1587049352846-4a222e784d38?w=800&q=80",
        "https://images.unsplash.com/photo-1549007994-cb92caebd54b?w=800&q=80",
        "https://images.unsplash.com/photo-1514432324607-a09d9b4aefdd?w=800&q=80",
        "https://images.unsplash.com/photo-1576092768241-dec231879fc3?w=800&q=80",
        "https://images.unsplash.com/photo-1517673132405-a56a62b18caf?w=800&q=80",
        "https://images.unsplash.com/photo-1551183053-bf91a1d81141?w=800&q=80",
        "https://images.unsplash.com/photo-1569718212165-3a8278d5f624?w=800&q=80",
        "https://images.unsplash.com/photo-1589733955941-5eeaf752f6dd?w=800&q=80"
    ],

    # ---------------- TOYS & BABY CARE ----------------
    "toy": [
        "https://images.unsplash.com/photo-1587654780291-39c9404d746b?w=800&q=80",
        "https://images.unsplash.com/photo-1594787318286-3d835c1d207f?w=800&q=80",
        "https://images.unsplash.com/photo-1591991731833-b4807cf7ef94?w=800&q=80",
        "https://images.unsplash.com/photo-1596461404969-9ae70f2830c1?w=800&q=80",
        "https://images.unsplash.com/photo-1610890716171-6b1bb98ffd09?w=800&q=80"
    ],
    "baby_care": [
        "https://images.unsplash.com/photo-1515488042361-ee00e0ddd4e4?w=800&q=80",
        "https://images.unsplash.com/photo-1596461404969-9ae70f2830c1?w=800&q=80",
        "https://images.unsplash.com/photo-1587654780291-39c9404d746b?w=800&q=80"
    ]
}


def choose_best_pool(product: Product):
    name_low = (product.name or '').lower()
    cat_low = (product.category or '').lower()
    desc_low = (product.description or '').lower()
    full_text = f"{name_low} {cat_low} {desc_low}"

    # Electronics
    if any(k in full_text for k in ('laptop', 'macbook', 'notebook', 'thinkpad', 'zenbook', 'spectre')):
        return IMAGE_POOLS['laptop']
    if any(k in full_text for k in ('monitor', 'ultrawide', 'display', 'screen', 'curved qled')):
        return IMAGE_POOLS['monitor']
    if any(k in full_text for k in ('keyboard', 'keychron', 'mechanical switch')):
        return IMAGE_POOLS['keyboard']
    if any(k in full_text for k in ('mouse', 'gaming mouse', 'optical sensor', 'trackball')):
        return IMAGE_POOLS['mouse']
    if any(k in full_text for k in ('headphone', 'over-ear', 'wh-1000xm', 'anc headphones')):
        return IMAGE_POOLS['headphones']
    if any(k in full_text for k in ('earbuds', 'tws', 'airpods', 'buds', 'in-ear')):
        return IMAGE_POOLS['earbuds']
    if any(k in full_text for k in ('speaker', 'soundbar', 'bluetooth speaker', 'audio')):
        return IMAGE_POOLS['speaker']
    if any(k in full_text for k in ('phone', 'smartphone', 'galaxy s', 'iphone', 'pixel', 'oneplus', 'iqoo')):
        return IMAGE_POOLS['phone']
    if any(k in full_text for k in ('tablet', 'ipad', 'tab', 'stylus')):
        return IMAGE_POOLS['tablet']
    if any(k in full_text for k in ('smartwatch', 'smart watch', 'apple watch', 'colorfit')):
        return IMAGE_POOLS['smartwatch']
    if any(k in full_text for k in ('camera', 'drone', 'action cam', 'gopro', 'alpha 7', 'dji')):
        return IMAGE_POOLS['camera']

    # Fashion
    if any(k in full_text for k in ('kurta', 'kurti', 'anarkali', 'saree', 'ethnic', 'lehenga', 'dupatta')):
        return IMAGE_POOLS['kurta']
    if any(k in full_text for k in ('shirt', 'polo', 't-shirt', 'top', 'blouse')):
        return IMAGE_POOLS['shirt']
    if any(k in full_text for k in ('jacket', 'blazer', 'coat', 'trench')):
        return IMAGE_POOLS['jacket']
    if any(k in full_text for k in ('jean', 'denim', 'trouser', 'pant', 'chino')):
        return IMAGE_POOLS['jeans']
    if any(k in full_text for k in ('shoe', 'sneaker', 'derby', 'boot', 'sandal', 'footwear', 'pegasus', 'smash')):
        return IMAGE_POOLS['shoes']
    if any(k in full_text for k in ('sunglasses', 'aviator', 'shades', 'eyewear')):
        return IMAGE_POOLS['sunglasses']
    if any(k in full_text for k in ('watch', 'analog watch', 'quartz')):
        return IMAGE_POOLS['watch']
    if any(k in full_text for k in ('bag', 'backpack', 'wallet', 'tote', 'rucksack', 'purse')):
        return IMAGE_POOLS['bag']

    # Home & Kitchen
    if any(k in full_text for k in ('fryer', 'cooker', 'mixer', 'grinder', 'coffee', 'blender', 'purifier', 'kettle', 'otg', 'induction')):
        return IMAGE_POOLS['kitchen_appliance']
    if any(k in full_text for k in ('skillet', 'pan', 'cookware', 'bowl', 'dinner set', 'cutlery', 'tiffin', 'knife')):
        return IMAGE_POOLS['cookware']
    if any(k in full_text for k in ('vacuum', 'mop', 'cleaner', 'air purifier', 'light', 'batten')):
        return IMAGE_POOLS['home_clean']
    if any(k in full_text for k in ('pillow', 'mattress', 'bedsheet', 'bed', 'chair', 'organizer')):
        return IMAGE_POOLS['home_bedding']

    # Beauty & Personal Care
    if any(k in full_text for k in ('serum', 'exfoliant', 'sunscreen', 'cleanser', 'moisturizer', 'cream', 'toner', 'skincare')):
        return IMAGE_POOLS['skincare']
    if any(k in full_text for k in ('shampoo', 'hair', 'argan', 'dryer', 'supersonic', 'olaplex')):
        return IMAGE_POOLS['haircare']
    if any(k in full_text for k in ('shaver', 'trimmer', 'razor', 'perfume', 'parfum', 'grooming', 'shaving', 'toothbrush')):
        return IMAGE_POOLS['grooming']
    if any(k in full_text for k in ('lipstick', 'mascara', 'foundation', 'kajal', 'eyeliner', 'makeup', 'mousse')):
        return IMAGE_POOLS['makeup']

    # Sports & Fitness
    if any(k in full_text for k in ('dumbbell', 'treadmill', 'resistance band', 'powerlifting', 'aerobic', 'weight', 'gym')):
        return IMAGE_POOLS['gym']
    if any(k in full_text for k in ('cricket', 'football', 'basketball', 'badminton', 'racket', 'goggles', 'stud', 'tennis', 'shuttlecock')):
        return IMAGE_POOLS['sports_gear']
    if any(k in full_text for k in ('whey', 'protein', 'gainer', 'pre-workout', 'shaker', 'hydration', 'electrolyte')):
        return IMAGE_POOLS['nutrition']
    if any(k in full_text for k in ('yoga', 'mat', 'swiss ball', 'skipping rope')):
        return IMAGE_POOLS['yoga']

    # Books & Stationery
    if any(k in full_text for k in ('book', 'habits', 'dune', 'alchemist', 'author', 'pages', 'history', 'money', 'work')):
        return IMAGE_POOLS['book']
    if any(k in full_text for k in ('pen', 'pencil', 'notebook', 'colour', 'journal', 'calculator', 'highlighter', 'stationery')):
        return IMAGE_POOLS['stationery']

    # Grocery & Gourmet
    if 'grocery' in cat_low or any(k in full_text for k in ('rice', 'oil', 'atta', 'salt', 'almond', 'walnut', 'chia', 'honey', 'chocolate', 'coffee', 'tea', 'muesli', 'oats', 'syrup', 'pasta', 'dal', 'ketchup', 'maggi', 'noodle', 'snack')):
        return IMAGE_POOLS['grocery']

    # Toys & Baby Care
    if any(k in full_text for k in ('lego', 'hot wheels', 'nerf', 'barbie', 'cube', 'rubik', 'toy', 'game', 'board game')):
        return IMAGE_POOLS['toy']
    if any(k in full_text for k in ('baby', 'diaper', 'pampers', 'huggies', 'stroller', 'pram', 'crib', 'bottle', 'carrier', 'wipes')):
        return IMAGE_POOLS['baby_care']

    # Default category fallback
    if 'electron' in cat_low:
        return IMAGE_POOLS['electronics_general']
    if 'fashion' in cat_low:
        return IMAGE_POOLS['fashion_general']
    if 'home' in cat_low:
        return IMAGE_POOLS['kitchen_appliance']
    if 'beauty' in cat_low:
        return IMAGE_POOLS['skincare']
    if 'sports' in cat_low:
        return IMAGE_POOLS['gym']
    if 'book' in cat_low:
        return IMAGE_POOLS['book']
    if 'toy' in cat_low or 'baby' in cat_low:
        return IMAGE_POOLS['toy']

    return IMAGE_POOLS['electronics_general']


def update_all_photos():
    # 1. First fix legacy empty-category items p-t1, p-t10, p-t20
    legacy_items = Product.objects.filter(id__in=['p-t1', 'p-t10', 'p-t20'])
    for p in legacy_items:
        p.category = 'Fashion'
        p.categoryId = 'cat-2'
        p.brand = 'Biba'
        p.seller = 'Biba Apparels'
        p.description = f"{p.name} - Premium breathable cotton ethnic kurta crafted for comfort, style and everyday festive elegance."
        p.specifications = {"Fabric": "Pure Cotton", "Fit": "Regular Fit", "Sleeve": "Long Sleeve", "Care": "Hand Wash"}
        p.save()
    print("Fixed legacy items (p-t1, p-t10, p-t20) with valid category and metadata.")

    # 2. Update photos across all 300 products
    all_products = list(Product.objects.all())
    updated_count = 0

    for p in all_products:
        pool = choose_best_pool(p)
        current_imgs = [img for img in (p.images or []) if img and str(img).startswith('http')]

        # Pick 3 distinctive images
        new_imgs = []
        if current_imgs:
            new_imgs.append(current_imgs[0])

        # Fill remaining spots from the chosen pool
        for img in pool:
            if img not in new_imgs and len(new_imgs) < 3:
                new_imgs.append(img)

        # If pool was smaller than 3, borrow from backup in category
        if len(new_imgs) < 3:
            for b_pool in IMAGE_POOLS.values():
                for img in b_pool:
                    if img not in new_imgs and len(new_imgs) < 3:
                        new_imgs.append(img)

        p.images = new_imgs
        p.save(update_fields=['images'])
        updated_count += 1

    print(f"Successfully updated photos for all {updated_count} products!")
    
    # 3. Synchronize category counters again
    for cat in Category.objects.all():
        cat.productCount = Product.objects.filter(category=cat.name).count()
        cat.save(update_fields=['productCount'])

    # 4. Verify results
    zero_images = Product.objects.filter(images=[]).count()
    one_image = sum(1 for p in Product.objects.all() if len(p.images or []) == 1)
    two_images = sum(1 for p in Product.objects.all() if len(p.images or []) == 2)
    three_or_more = sum(1 for p in Product.objects.all() if len(p.images or []) >= 3)

    print("\nPhoto Distribution Across 300 Products:")
    print(f" - Products with 0 images: {zero_images}")
    print(f" - Products with 1 image:  {one_image}")
    print(f" - Products with 2 images: {two_images}")
    print(f" - Products with 3+ images: {three_or_more}")


if __name__ == '__main__':
    update_all_photos()
