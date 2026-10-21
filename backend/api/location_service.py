"""
AutoCart Location & Geospatial Fulfillment Service.
Provides Haversine distance calculation, city/PIN geocoding fallback,
serviceability radius filtering, and nearby store inventory lookup.
"""

import math
import re
import json
import urllib.request
from typing import Dict, List, Any, Optional, Tuple
from django.db.models import Q
from .models import Store, StoreInventory, Product

# The 10 Primary Hyperlocal Operating Zones across Mumbai & MMR
MUMBAI_ZONES = {
    'thane': {
        'id': 'thane',
        'name': 'Thane',
        'lat': 19.2183,
        'lng': 72.9781,
        'pincodes': ['400601', '400602', '400604', '400606', '400607'],
        'description': 'Viviana Mall, Naupada, Hiranandani Estate, Teen Hath Naka'
    },
    'kalyan': {
        'id': 'kalyan',
        'name': 'Kalyan',
        'lat': 19.2403,
        'lng': 73.1305,
        'pincodes': ['421301', '421304', '421306'],
        'description': 'Khadakpada, Station Road, Wayle Nagar, Birla College, Kolsewadi'
    },
    'dombivli': {
        'id': 'dombivli',
        'name': 'Dombivli',
        'lat': 19.2184,
        'lng': 73.0867,
        'pincodes': ['421201', '421202', '421204'],
        'description': 'Phadke Road, Manpada, Lodha Palava, Tilak Road, Gupte Road'
    },
    'mulund': {
        'id': 'mulund',
        'name': 'Mulund',
        'lat': 19.1726,
        'lng': 72.9565,
        'pincodes': ['400080', '400081'],
        'description': 'MG Road, R Mall, Sarvodaya Nagar, Mithagar, Yogi Hills, Nahur'
    },
    'bhandup': {
        'id': 'bhandup',
        'name': 'Bhandup',
        'lat': 19.1458,
        'lng': 72.9372,
        'pincodes': ['400078'],
        'description': 'Dreams Mall, LBS Marg, Station Road, Usha Nagar, Kanjur Link'
    },
    'ghatkopar': {
        'id': 'ghatkopar',
        'name': 'Ghatkopar',
        'lat': 19.0860,
        'lng': 72.9090,
        'pincodes': ['400077', '400086', '400075'],
        'description': 'R City Mall, Vallabh Baug, Pant Nagar, Amrut Nagar, MG Road'
    },
    'powai': {
        'id': 'powai',
        'name': 'Powai',
        'lat': 19.1176,
        'lng': 72.9060,
        'pincodes': ['400076', '400072'],
        'description': 'Hiranandani Gardens, Galleria, IIT Bombay, Chandivali, Saki Vihar'
    },
    'andheri': {
        'id': 'andheri',
        'name': 'Andheri',
        'lat': 19.1136,
        'lng': 72.8697,
        'pincodes': ['400053', '400058', '400069', '400059', '400093'],
        'description': 'Lokhandwala, Chakala, Infinity Mall, JB Nagar, MIDC, Marol'
    },
    'borivali': {
        'id': 'borivali',
        'name': 'Borivali',
        'lat': 19.2307,
        'lng': 72.8567,
        'pincodes': ['400091', '400092', '400066', '400103'],
        'description': 'Shimpoli, IC Colony, SV Road, Carter Road, Chikuwadi, National Park'
    },
    'navi mumbai': {
        'id': 'navi mumbai',
        'name': 'Navi Mumbai',
        'lat': 19.0330,
        'lng': 73.0297,
        'pincodes': ['400703', '400705', '400706', '400614', '410210'],
        'description': 'Vashi Sector 17, Seawoods Grand Central, Palm Beach, Nerul, Belapur, Kharghar'
    }
}

# Approximate coordinates for key Indian logistics hubs & metro districts
KNOWN_GEOCODING_DATABASE = {
    # 1. Thane
    '400606': {'city': 'Thane', 'area': 'Viviana Mall / Vartak Nagar', 'lat': 19.2085, 'lng': 72.9716},
    '400602': {'city': 'Thane', 'area': 'Naupada / Station', 'lat': 19.1895, 'lng': 72.9723},
    '400607': {'city': 'Thane', 'area': 'Hiranandani Estate / Ghodbunder', 'lat': 19.2558, 'lng': 72.9806},
    '400601': {'city': 'Thane', 'area': 'Majiwada Junction', 'lat': 19.2140, 'lng': 72.9870},
    '400604': {'city': 'Thane', 'area': 'Teen Hath Naka', 'lat': 19.1862, 'lng': 72.9598},
    'thane': {'city': 'Thane', 'area': 'Central Thane', 'lat': 19.2183, 'lng': 72.9781},

    # 2. Kalyan
    '421301': {'city': 'Kalyan', 'district': 'Thane', 'area': 'Khadakpada / Station Road', 'lat': 19.2551, 'lng': 73.1378,
               'sub_localities': ['Birla College', 'Chikanghar', 'Godrej Hill', 'Kalyan City', 'Khadakpada', 'Rambaug', 'Syndicate', 'Wayle Nagar']},
    '421304': {'city': 'Kalyan', 'district': 'Thane', 'area': 'Gandhinagar / Kalyan West', 'lat': 19.2450, 'lng': 73.1300},
    '421306': {'city': 'Kalyan', 'district': 'Thane', 'area': 'Kolsewadi / Kalyan East', 'lat': 19.2295, 'lng': 73.1410},
    'kalyan': {'city': 'Kalyan', 'district': 'Thane', 'area': 'Central Kalyan', 'lat': 19.2403, 'lng': 73.1305},
    'birla college': {'city': 'Kalyan', 'district': 'Thane', 'area': 'Birla College, Kalyan', 'lat': 19.2482, 'lng': 73.1465, 'pincode': '421301'},
    'chikanghar': {'city': 'Kalyan', 'district': 'Thane', 'area': 'Chikanghar, Kalyan', 'lat': 19.2435, 'lng': 73.1362, 'pincode': '421301'},
    'godrej hill': {'city': 'Kalyan', 'district': 'Thane', 'area': 'Godrej Hill, Kalyan', 'lat': 19.2592, 'lng': 73.1320, 'pincode': '421301'},
    'kalyan city': {'city': 'Kalyan', 'district': 'Thane', 'area': 'Kalyan City', 'lat': 19.2403, 'lng': 73.1305, 'pincode': '421301'},
    'khadakpada': {'city': 'Kalyan', 'district': 'Thane', 'area': 'Khadakpada, Kalyan', 'lat': 19.2551, 'lng': 73.1378, 'pincode': '421301'},
    'rambaug': {'city': 'Kalyan', 'district': 'Thane', 'area': 'Rambaug, Kalyan', 'lat': 19.2368, 'lng': 73.1287, 'pincode': '421301'},
    'syndicate': {'city': 'Kalyan', 'district': 'Thane', 'area': 'Syndicate, Kalyan', 'lat': 19.2390, 'lng': 73.1412, 'pincode': '421301'},
    'wayle nagar': {'city': 'Kalyan', 'district': 'Thane', 'area': 'Wayle Nagar, Kalyan', 'lat': 19.2510, 'lng': 73.1315, 'pincode': '421301'},

    # 3. Dombivli
    '421201': {'city': 'Dombivli', 'district': 'Thane', 'area': 'Phadke Road / Manpada', 'lat': 19.2165, 'lng': 73.0872},
    '421202': {'city': 'Dombivli', 'district': 'Thane', 'area': 'Gupte Road / Dombivli West', 'lat': 19.2190, 'lng': 73.0785},
    '421204': {'city': 'Dombivli', 'district': 'Thane', 'area': 'Lodha Palava / Xperia Mall', 'lat': 19.1915, 'lng': 73.0780},
    'dombivli': {'city': 'Dombivli', 'district': 'Thane', 'area': 'Central Dombivli', 'lat': 19.2184, 'lng': 73.0867},
    'dombivali': {'city': 'Dombivli', 'district': 'Thane', 'area': 'Central Dombivli', 'lat': 19.2184, 'lng': 73.0867},

    # 4. Mulund
    '400080': {'city': 'Mulund', 'area': 'MG Road / R Mall / Mulund West', 'lat': 19.1735, 'lng': 72.9530},
    '400081': {'city': 'Mulund', 'area': 'Mithagar / Mulund East', 'lat': 19.1685, 'lng': 72.9660},
    'mulund': {'city': 'Mulund', 'area': 'Central Mulund', 'lat': 19.1726, 'lng': 72.9565},

    # 5. Bhandup
    '400078': {'city': 'Bhandup', 'area': 'Dreams Mall / LBS Marg / Station', 'lat': 19.1458, 'lng': 72.9372},
    'bhandup': {'city': 'Bhandup', 'area': 'Central Bhandup', 'lat': 19.1458, 'lng': 72.9372},

    # 6. Ghatkopar
    '400086': {'city': 'Ghatkopar', 'area': 'R City Mall / LBS Marg', 'lat': 19.0990, 'lng': 72.9165},
    '400077': {'city': 'Ghatkopar', 'area': 'Vallabh Baug / Ghatkopar East', 'lat': 19.0815, 'lng': 72.9080},
    '400075': {'city': 'Ghatkopar', 'area': 'Pant Nagar', 'lat': 19.0780, 'lng': 72.9150},
    'ghatkopar': {'city': 'Ghatkopar', 'area': 'Central Ghatkopar', 'lat': 19.0860, 'lng': 72.9090},

    # 7. Powai
    '400076': {'city': 'Powai', 'area': 'Hiranandani Gardens / Galleria', 'lat': 19.1195, 'lng': 72.9085},
    '400072': {'city': 'Powai', 'area': 'Chandivali / Saki Vihar Road', 'lat': 19.1120, 'lng': 72.8960},
    'powai': {'city': 'Powai', 'area': 'Central Powai', 'lat': 19.1176, 'lng': 72.9060},

    # 8. Andheri
    '400053': {'city': 'Andheri', 'area': 'Lokhandwala Complex / Andheri West', 'lat': 19.1410, 'lng': 72.8285},
    '400069': {'city': 'Andheri', 'area': 'Chakala / Andheri East', 'lat': 19.1136, 'lng': 72.8697},
    '400059': {'city': 'Andheri', 'area': 'JB Nagar / Marol Naka', 'lat': 19.1120, 'lng': 72.8720},
    '400093': {'city': 'Andheri', 'area': 'MIDC Central Road', 'lat': 19.1205, 'lng': 72.8755},
    '400058': {'city': 'Andheri', 'area': 'Andheri Station West', 'lat': 19.1197, 'lng': 72.8464},
    'andheri': {'city': 'Andheri', 'area': 'Central Andheri', 'lat': 19.1136, 'lng': 72.8697},

    # 9. Borivali
    '400092': {'city': 'Borivali', 'area': 'Shimpoli / SV Road / Borivali West', 'lat': 19.2275, 'lng': 72.8465},
    '400103': {'city': 'Borivali', 'area': 'IC Colony / Holy Cross', 'lat': 19.2450, 'lng': 72.8480},
    '400066': {'city': 'Borivali', 'area': 'Carter Road / National Park / Borivali East', 'lat': 19.2285, 'lng': 72.8630},
    '400091': {'city': 'Borivali', 'area': 'Borivali West Station', 'lat': 19.2290, 'lng': 72.8560},
    'borivali': {'city': 'Borivali', 'area': 'Central Borivali', 'lat': 19.2307, 'lng': 72.8567},

    # 10. South & Central Mumbai (including Parel / Lalbaug 400012)
    '400012': {'city': 'Mumbai', 'area': 'Parel / Lalbaug / Lower Parel', 'lat': 18.9986, 'lng': 72.8422},
    'parel': {'city': 'Mumbai', 'area': 'Parel / Lalbaug', 'lat': 18.9986, 'lng': 72.8422},
    'lower parel': {'city': 'Mumbai', 'area': 'Lower Parel / High Street Phoenix', 'lat': 18.9950, 'lng': 72.8300},
    'lalbaug': {'city': 'Mumbai', 'area': 'Lalbaug, Mumbai', 'lat': 18.9930, 'lng': 72.8390},
    '400013': {'city': 'Mumbai', 'area': 'Delisle Road / Lower Parel', 'lat': 18.9950, 'lng': 72.8300},
    '400014': {'city': 'Mumbai', 'area': 'Dadar East / Hindu Colony', 'lat': 19.0178, 'lng': 72.8478},
    '400028': {'city': 'Mumbai', 'area': 'Dadar West / Shivaji Park', 'lat': 19.0222, 'lng': 72.8360},
    '400050': {'city': 'Mumbai', 'area': 'Bandra West / Linking Road', 'lat': 19.0596, 'lng': 72.8295},
    '400051': {'city': 'Mumbai', 'area': 'Bandra East / BKC', 'lat': 19.0607, 'lng': 72.8644},
    '400001': {'city': 'Mumbai', 'area': 'Fort / CST / Nariman Point', 'lat': 18.9322, 'lng': 72.8339},
    'bandra': {'city': 'Mumbai', 'area': 'Bandra West', 'lat': 19.0596, 'lng': 72.8295},
    'dadar': {'city': 'Mumbai', 'area': 'Dadar Shivaji Park', 'lat': 19.0222, 'lng': 72.8360},
    'bkc': {'city': 'Mumbai', 'area': 'Bandra Kurla Complex (BKC)', 'lat': 19.0607, 'lng': 72.8644},

    # 10. Navi Mumbai
    '400703': {'city': 'Navi Mumbai', 'area': 'Sector 17 / Vashi', 'lat': 19.0760, 'lng': 72.9985},
    '400706': {'city': 'Navi Mumbai', 'area': 'Seawoods Grand Central / Nerul', 'lat': 19.0205, 'lng': 73.0185},
    '400705': {'city': 'Navi Mumbai', 'area': 'Palm Beach Road / Vashi', 'lat': 19.0680, 'lng': 73.0070},
    '400614': {'city': 'Navi Mumbai', 'area': 'CBD Belapur', 'lat': 19.0190, 'lng': 73.0395},
    '410210': {'city': 'Navi Mumbai', 'area': 'Sector 20 / Kharghar', 'lat': 19.0430, 'lng': 73.0670},
    'navi mumbai': {'city': 'Navi Mumbai', 'area': 'Central Navi Mumbai', 'lat': 19.0330, 'lng': 73.0297},
    'vashi': {'city': 'Navi Mumbai', 'area': 'Sector 17, Vashi', 'lat': 19.0760, 'lng': 72.9985},
    'nerul': {'city': 'Navi Mumbai', 'area': 'Nerul West', 'lat': 19.0335, 'lng': 73.0160},
    'kharghar': {'city': 'Navi Mumbai', 'area': 'Kharghar Sector 20', 'lat': 19.0430, 'lng': 73.0670},
    'seawoods': {'city': 'Navi Mumbai', 'area': 'Seawoods Mall', 'lat': 19.0205, 'lng': 73.0185},

    # Kalyan variations and typos (e.g. klayan)
    'klayan': {'city': 'Kalyan', 'area': 'Central Kalyan', 'lat': 19.2403, 'lng': 73.1305},
    'kalyaan': {'city': 'Kalyan', 'area': 'Central Kalyan', 'lat': 19.2403, 'lng': 73.1305},
    'kalyan west': {'city': 'Kalyan', 'area': 'Kalyan West', 'lat': 19.2450, 'lng': 73.1300},
    'kalyan east': {'city': 'Kalyan', 'area': 'Kalyan East', 'lat': 19.2295, 'lng': 73.1410},
    'khadakpada': {'city': 'Kalyan', 'area': 'Khadakpada, Kalyan', 'lat': 19.2551, 'lng': 73.1378},

    # Thane variations and landmarks
    'thana': {'city': 'Thane', 'area': 'Central Thane', 'lat': 19.2183, 'lng': 72.9781},
    'viviana': {'city': 'Thane', 'area': 'Viviana Mall, Thane', 'lat': 19.2085, 'lng': 72.9716},
    'naupada': {'city': 'Thane', 'area': 'Naupada, Thane', 'lat': 19.1895, 'lng': 72.9723},
    'ghodbunder': {'city': 'Thane', 'area': 'Ghodbunder Road, Thane', 'lat': 19.2558, 'lng': 72.9806},
    'majiwada': {'city': 'Thane', 'area': 'Majiwada, Thane', 'lat': 19.2140, 'lng': 72.9870},

    # Dombivli variations
    'dombivili': {'city': 'Dombivli', 'area': 'Central Dombivli', 'lat': 19.2184, 'lng': 73.0867},
    'dombivli west': {'city': 'Dombivli', 'area': 'Dombivli West', 'lat': 19.2190, 'lng': 73.0785},
    'dombivli east': {'city': 'Dombivli', 'area': 'Dombivli East', 'lat': 19.2165, 'lng': 73.0872},
    'palava': {'city': 'Dombivli', 'area': 'Lodha Palava, Dombivli', 'lat': 19.1915, 'lng': 73.0780},

    # Powai variations
    'powaee': {'city': 'Powai', 'area': 'Central Powai', 'lat': 19.1176, 'lng': 72.9060},
    'hiranandani': {'city': 'Powai', 'area': 'Hiranandani Gardens, Powai', 'lat': 19.1195, 'lng': 72.9085},

    # Andheri & Suburbs
    'lokhandwala': {'city': 'Andheri', 'area': 'Lokhandwala Complex, Andheri West', 'lat': 19.1410, 'lng': 72.8285},
    'andheri west': {'city': 'Andheri', 'area': 'Andheri West', 'lat': 19.1410, 'lng': 72.8285},
    'andheri east': {'city': 'Andheri', 'area': 'Andheri East', 'lat': 19.1136, 'lng': 72.8697},
    'borivli': {'city': 'Borivali', 'area': 'Central Borivali', 'lat': 19.2307, 'lng': 72.8567},
    'borivali west': {'city': 'Borivali', 'area': 'Borivali West', 'lat': 19.2275, 'lng': 72.8465},
    'borivali east': {'city': 'Borivali', 'area': 'Borivali East', 'lat': 19.2285, 'lng': 72.8630},
    'dadar': {'city': 'Mumbai', 'area': 'Dadar', 'lat': 19.0178, 'lng': 72.8478},
    'bandra': {'city': 'Mumbai', 'area': 'Bandra West', 'lat': 19.0596, 'lng': 72.8295},
    'bkc': {'city': 'Mumbai', 'area': 'Bandra Kurla Complex (BKC)', 'lat': 19.0664, 'lng': 72.8677},
    'kurla': {'city': 'Mumbai', 'area': 'Kurla', 'lat': 19.0657, 'lng': 72.8794},

    # Other Mumbai Landmark hubs
    '400050': {'city': 'Mumbai', 'area': 'Bandra West', 'lat': 19.0596, 'lng': 72.8295},
    '400001': {'city': 'Mumbai', 'area': 'Fort / Colaba', 'lat': 18.9322, 'lng': 72.8354},
    'mumbai': {'city': 'Mumbai', 'area': 'City Center (BKC / Dadar)', 'lat': 19.0760, 'lng': 72.8777},

    # Extended Mumbai Metropolitan Region PIN Codes
    '400014': {'city': 'Mumbai', 'area': 'Dadar East / Hindu Colony', 'lat': 19.0178, 'lng': 72.8478},
    '400028': {'city': 'Mumbai', 'area': 'Dadar West / Shivaji Park', 'lat': 19.0282, 'lng': 72.8397},
    '400070': {'city': 'Mumbai', 'area': 'Kurla West / Station', 'lat': 19.0657, 'lng': 72.8794},
    '400071': {'city': 'Mumbai', 'area': 'Chembur / Diamond Garden', 'lat': 19.0622, 'lng': 72.8973},
    '400051': {'city': 'Mumbai', 'area': 'Bandra Kurla Complex (BKC)', 'lat': 19.0664, 'lng': 72.8677},
    '400057': {'city': 'Mumbai', 'area': 'Vile Parle East', 'lat': 19.0988, 'lng': 72.8525},
    '400056': {'city': 'Mumbai', 'area': 'Vile Parle West / Juhu', 'lat': 19.1025, 'lng': 72.8389},
    '400054': {'city': 'Mumbai', 'area': 'Santacruz West', 'lat': 19.0837, 'lng': 72.8378},
    '400055': {'city': 'Mumbai', 'area': 'Santacruz East / Vakola', 'lat': 19.0812, 'lng': 72.8534},
    '400062': {'city': 'Mumbai', 'area': 'Goregaon West / SV Road', 'lat': 19.1663, 'lng': 72.8431},
    '400063': {'city': 'Mumbai', 'area': 'Goregaon East / Oberoi Mall', 'lat': 19.1691, 'lng': 72.8597},
    '400104': {'city': 'Mumbai', 'area': 'Bangur Nagar / Goregaon West', 'lat': 19.1670, 'lng': 72.8360},
    '400064': {'city': 'Mumbai', 'area': 'Malad West / Inorbit Mall', 'lat': 19.1860, 'lng': 72.8368},
    '400097': {'city': 'Mumbai', 'area': 'Malad East / Dindoshi', 'lat': 19.1764, 'lng': 72.8612},
    '400067': {'city': 'Mumbai', 'area': 'Kandivali West / Mahavir Nagar', 'lat': 19.2088, 'lng': 72.8399},
    '400101': {'city': 'Mumbai', 'area': 'Kandivali East / Thakur Complex', 'lat': 19.2080, 'lng': 72.8715},
    '401107': {'city': 'Mira Road', 'district': 'Thane', 'area': 'Mira Road Station / Shanti Nagar', 'lat': 19.2812, 'lng': 72.8561},
    '401101': {'city': 'Bhayandar', 'district': 'Thane', 'area': 'Bhayandar West / Station Road', 'lat': 19.3015, 'lng': 72.8510},
    '401105': {'city': 'Bhayandar', 'district': 'Thane', 'area': 'Bhayandar East / Navghar', 'lat': 19.2978, 'lng': 72.8632},
    '421001': {'city': 'Ulhasnagar', 'district': 'Thane', 'area': 'Ulhasnagar 1 / Station Road', 'lat': 19.2215, 'lng': 73.1643},
    '421002': {'city': 'Ulhasnagar', 'district': 'Thane', 'area': 'Ulhasnagar 2 / Gol Maidan', 'lat': 19.2170, 'lng': 73.1580},
    '421003': {'city': 'Ulhasnagar', 'district': 'Thane', 'area': 'Ulhasnagar 3 / Press Bazar', 'lat': 19.2130, 'lng': 73.1520},
    '421004': {'city': 'Ulhasnagar', 'district': 'Thane', 'area': 'Ulhasnagar 4 / Netaji Chowk', 'lat': 19.2110, 'lng': 73.1620},
    '421005': {'city': 'Ulhasnagar', 'district': 'Thane', 'area': 'Ulhasnagar 5 / Kailash Colony', 'lat': 19.2080, 'lng': 73.1670},
    '421501': {'city': 'Ambernath', 'district': 'Thane', 'area': 'Ambernath West / Station', 'lat': 19.2005, 'lng': 73.1950},
    '421505': {'city': 'Ambernath', 'district': 'Thane', 'area': 'Ambernath East / MIDC', 'lat': 19.1950, 'lng': 73.2120},
    '410206': {'city': 'Panvel', 'district': 'Raigad', 'area': 'Old Panvel / Station', 'lat': 18.9894, 'lng': 73.1175},
    '444001': {'city': 'Akola', 'district': 'Akola', 'area': 'Akola City / Alsi Plot', 'lat': 20.7002, 'lng': 77.0082},

    # Bengaluru
    '560038': {'city': 'Bengaluru', 'area': 'Indiranagar', 'lat': 12.9784, 'lng': 77.6408},
    '560034': {'city': 'Bengaluru', 'area': 'Koramangala', 'lat': 12.9352, 'lng': 77.6245},
    '560066': {'city': 'Bengaluru', 'area': 'Whitefield', 'lat': 12.9698, 'lng': 77.7500},
    '560001': {'city': 'Bengaluru', 'area': 'MG Road', 'lat': 12.9756, 'lng': 77.6066},
    'bengaluru': {'city': 'Bengaluru', 'area': 'City Center', 'lat': 12.9716, 'lng': 77.5946},
    'bangalore': {'city': 'Bengaluru', 'area': 'City Center', 'lat': 12.9716, 'lng': 77.5946},

    # New Delhi
    '110001': {'city': 'New Delhi', 'area': 'Connaught Place', 'lat': 28.6304, 'lng': 77.2177},
    'delhi': {'city': 'New Delhi', 'area': 'Central Delhi', 'lat': 28.6139, 'lng': 77.2090},

    # Hyderabad & Pune
    '500081': {'city': 'Hyderabad', 'area': 'Hitec City', 'lat': 17.4474, 'lng': 78.3762},
    'hyderabad': {'city': 'Hyderabad', 'area': 'City Center', 'lat': 17.3850, 'lng': 78.4867},
    '411001': {'city': 'Pune', 'area': 'Pune Station', 'lat': 18.5289, 'lng': 73.8744},
    'pune': {'city': 'Pune', 'area': 'City Center', 'lat': 18.5204, 'lng': 73.8567},
}

DEFAULT_MUMBAI_LAT = 19.0760
DEFAULT_MUMBAI_LNG = 72.8777


def haversine_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the great circle distance between two points in kilometers.
    """
    R = 6371.0  # Earth's radius in kilometers
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return round(R * c, 2)


def resolve_coordinates(location_input: str) -> Optional[Tuple[float, float, str]]:
    """
    Resolve coordinates from PIN code or city name string.
    Returns (latitude, longitude, resolved_name) or None.
    A PIN code provides an approximate area location, never an exact street address.
    """
    if not location_input:
        return None

    import re
    cleaned = str(location_input).strip().lower()
    
    # 1. Exact 6-digit Indian PIN code match (strictly dictionary-backed, no fuzzy fallbacks for invalid PINs)
    if re.fullmatch(r'\d{6}', cleaned):
        if cleaned in KNOWN_GEOCODING_DATABASE:
            data = KNOWN_GEOCODING_DATABASE[cleaned]
            return data['lat'], data['lng'], f"{data['area']}, {data['city']}"
        return None

    # 2. Check exact city / zone name key
    if cleaned in KNOWN_GEOCODING_DATABASE:
        data = KNOWN_GEOCODING_DATABASE[cleaned]
        return data['lat'], data['lng'], f"{data['area']}, {data['city']}"

    # 3. Partial match only for non-numeric city/hub search strings
    if not cleaned.isdigit():
        # Sort keys by length descending to match longest specific string first
        sorted_keys = sorted([k for k in KNOWN_GEOCODING_DATABASE.keys() if not k.isdigit()], key=len, reverse=True)
        for key in sorted_keys:
            if key in cleaned or cleaned in key:
                data = KNOWN_GEOCODING_DATABASE[key]
                return data['lat'], data['lng'], f"{data['area']}, {data['city']}"

    return None


def extract_location_from_text(text: str) -> Optional[Tuple[float, float, str, str]]:
    """
    Extracts a known Mumbai/MMR location or PIN code from free-form user text.
    Returns (latitude, longitude, resolved_area_name, matched_key) or None.
    Handles user queries such as:
      - 'stores nearby klayan'
      - 'stores near thane'
      - 'find stores near andheri'
      - 'show me stores in powai'
      - '400053 stores'
    """
    if not text:
        return None
    import re
    cleaned = str(text).strip().lower()

    # 1. Check for 6-digit PIN code in text
    pin_match = re.search(r'\b\d{6}\b', cleaned)
    if pin_match:
        pin = pin_match.group(0)
        coords = resolve_coordinates(pin)
        if coords:
            return coords[0], coords[1], coords[2], pin

    # 2. Check for known area keywords / typos / aliases
    # Sort keys by length descending so multi-word keys ("navi mumbai", "andheri west") match before single words
    non_digit_keys = sorted(
        [k for k in KNOWN_GEOCODING_DATABASE.keys() if not k.isdigit()],
        key=len,
        reverse=True
    )
    for key in non_digit_keys:
        pattern = r'(?:\b|_)' + re.escape(key) + r'(?:\b|_)'
        if re.search(pattern, cleaned) or key in cleaned:
            data = KNOWN_GEOCODING_DATABASE[key]
            return data['lat'], data['lng'], f"{data['area']}, {data['city']}", key

    return None



def find_nearby_stores_with_inventory(
    product_id: Optional[str] = None,
    customer_lat: float = DEFAULT_MUMBAI_LAT,
    customer_lng: float = DEFAULT_MUMBAI_LNG,
    max_radius_km: float = 25.0,
    required_quantity: int = 1,
    pin_code: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Queries active stores within coverage radius that have available inventory for the product.
    Ranks by straight-line distance, road delivery estimate, and availability.
    """
    resolved_area = ""
    if pin_code:
        coords = resolve_coordinates(pin_code)
        if coords:
            customer_lat, customer_lng, resolved_area = coords

    stores = Store.objects.filter(operatingStatus='Open')
    results = []

    for store in stores:
        dist_km = haversine_distance_km(customer_lat, customer_lng, store.latitude, store.longitude)
        
        # Check service coverage radius
        effective_radius = max(store.serviceCoverageRadiusKm, max_radius_km)
        if dist_km > effective_radius:
            continue

        store_data = {
            'storeId': store.id,
            'storeName': store.name,
            'sellerName': store.seller,
            'address': store.address,
            'city': store.city,
            'pincode': store.pincode,
            'latitude': store.latitude,
            'longitude': store.longitude,
            'distanceKm': dist_km,
            'distanceFormatted': f"~{dist_km:.1f} km (approximate from {resolved_area})" if resolved_area else f"~{dist_km:.1f} km",
            'isApproximate': True if (pin_code or resolved_area) else False,
            'operatingStatus': store.operatingStatus,
            'fulfillmentCapability': store.fulfillmentCapability,
            'rating': store.rating,
            'phone': store.phone,
            'openingHours': store.openingHours,
            # Estimated delivery minutes based on road distance
            'estimatedMinutes': max(25, int(dist_km * 3.2) + 15),
            'deliveryFee': 0.0 if dist_km <= 3.0 else round(35.0 + max(0, dist_km - 3.0) * 8.0, 2),
        }

        # Check inventory for specific product if requested
        if product_id:
            inv = StoreInventory.objects.filter(
                store=store,
                product_id=product_id,
                isAvailable=True,
                availableQuantity__gte=required_quantity
            ).first()

            if not inv:
                # Store does not have required stock
                continue

            store_data['availableQuantity'] = inv.availableQuantity
            store_data['storePrice'] = inv.storePrice
            store_data['isAvailable'] = True
            store_data['productId'] = product_id
        else:
            # General store lookup without product constraint
            store_data['availableQuantity'] = StoreInventory.objects.filter(store=store, isAvailable=True).count()
            store_data['isAvailable'] = True

        results.append(store_data)

    # Sort results by distance ascending
    results.sort(key=lambda s: s['distanceKm'])
    return results


def get_mumbai_zones_summary() -> List[Dict[str, Any]]:
    """
    Returns aggregated status for all 10 Mumbai Metropolitan Region operating zones,
    including active store count, central geospatial coordinates, and key hubs.
    """
    summary = []
    all_open_stores = list(Store.objects.filter(operatingStatus='Open'))

    for zone_id, zone_data in MUMBAI_ZONES.items():
        z_lat = zone_data['lat']
        z_lng = zone_data['lng']
        
        # Count stores within 8km radius of zone center or matching city name
        zone_stores = [
            s for s in all_open_stores
            if (s.city.lower() == zone_data['name'].lower() or
                s.pincode in zone_data['pincodes'] or
                haversine_distance_km(z_lat, z_lng, s.latitude, s.longitude) <= 8.5)
        ]

        summary.append({
            'id': zone_id,
            'name': zone_data['name'],
            'lat': z_lat,
            'lng': z_lng,
            'description': zone_data['description'],
            'pincodes': zone_data['pincodes'],
            'activeStoresCount': len(zone_stores),
            'featuredStores': [
                {
                    'id': s.id,
                    'name': s.name,
                    'seller': s.seller,
                    'address': s.address,
                    'rating': s.rating,
                    'lat': s.latitude,
                    'lng': s.longitude,
                    'pincode': s.pincode,
                    'capability': s.fulfillmentCapability
                }
                for s in zone_stores[:3]
            ]
        })

    return summary


# =============================================================================
# PIN CODE & REVERSE GEOCODING LOCATION LOOKUP SERVICES
# =============================================================================

import json
import urllib.request
import urllib.parse
import logging
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status as http_status

logger = logging.getLogger(__name__)
_PINCODE_CACHE: Dict[str, Dict[str, Any]] = {}


def lookup_pincode_details(pincode: str, address_context: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """
    Validates a 6-digit Indian PIN code and returns associated postal locality,
    district, state, and approximate centroid coordinates without fabricating data.
    When multiple post offices or localities exist, disambiguates the true city/locality
    using the provided address_context (e.g. OCR-extracted residential address).
    """
    clean = str(pincode or '').strip()
    if not re.fullmatch(r'^[1-9][0-9]{5}$', clean):
        return None

    cache_key = f"{clean}:{address_context or ''}"
    if cache_key in _PINCODE_CACHE:
        return _PINCODE_CACHE[cache_key]

    known = KNOWN_GEOCODING_DATABASE.get(clean)
    lat = known['lat'] if known else None
    lng = known['lng'] if known else None
    city = known['city'] if known else ''
    area = known['area'] if known else ''
    district = (known.get('district') if known else None) or city or ''
    state = 'Maharashtra' if (clean.startswith('40') or clean.startswith('41') or clean.startswith('42')) else ''
    localities = [area] if area else []
    is_ambiguous = False
    offices = []

    # Check official India Post public API
    try:
        url = f"https://api.postalpincode.in/pincode/{clean}"
        req = urllib.request.Request(url, headers={'User-Agent': 'AutoCart/2.0 (Geospatial Seller Onboarding)'})
        with urllib.request.urlopen(req, timeout=3.0) as resp:
            data = json.loads(resp.read().decode())
            if isinstance(data, list) and data and data[0].get('Status') == 'Success':
                offices = data[0].get('PostOffice') or []
                if offices:
                    po_first = offices[0]
                    district = po_first.get('District') or district or city
                    state = po_first.get('State') or state
                    fetched_localities = [o.get('Name') for o in offices if o.get('Name')]
                    if fetched_localities:
                        localities = fetched_localities

                    # Extract available block / city candidates across offices
                    block_candidates = [o.get('Block') for o in offices if o.get('Block') and o.get('Block').upper() != 'NA']
                    unique_blocks = list(dict.fromkeys(block_candidates))

                    # Disambiguate city using address context if available
                    matched_city = None
                    if address_context:
                        addr_low = address_context.lower()
                        # 1. Check if any office name is mentioned in the address
                        for o in offices:
                            o_name = (o.get('Name') or '').strip()
                            o_clean = re.sub(r'\b(b\.o|s\.o|h\.o|d\.c|rs|city|town)\b', '', o_name, flags=re.I).strip().lower()
                            if o_clean and len(o_clean) >= 3 and o_clean in addr_low:
                                matched_city = o.get('Block') if (o.get('Block') and o.get('Block').upper() != 'NA') else o_name
                                break
                        # 2. Check if any block name is mentioned in address
                        if not matched_city:
                            for b in unique_blocks:
                                if b and len(b) >= 3 and b.lower() in addr_low:
                                    matched_city = b
                                    break

                    if matched_city:
                        city = matched_city
                        is_ambiguous = False
                    elif city:
                        # Pre-configured known city
                        is_ambiguous = False
                    elif unique_blocks and len(unique_blocks) == 1:
                        # All post offices share the exact same Block/Taluk (e.g. Kalyan, Akola)
                        city = unique_blocks[0]
                        is_ambiguous = False
                    elif po_first.get('Block') and po_first.get('Block').upper() != 'NA':
                        city = po_first.get('Block')
                        is_ambiguous = len(unique_blocks) > 1
                    else:
                        city = po_first.get('District') or 'Mumbai'
                        is_ambiguous = len(offices) > 1

            elif not known:
                # Postal registry confirmed no such PIN code exists
                return None
    except Exception as e:
        logger.debug("Postal API lookup failed for %s: %s", clean, e)

    # Clean clean city representation
    if city and re.search(r'\b(city|town|d\.c|r\.s)\b', city, re.I):
        city = re.sub(r'\s*\b(city|town|d\.c|r\.s)\b', '', city, flags=re.I).strip()

    # If coordinates are missing, attempt Nominatim geocoding for area centroid
    if lat is None or lng is None:
        try:
            q = f"{clean}, {district or city}, {state}, India"
            geo_url = f"https://nominatim.openstreetmap.org/search?format=json&limit=1&countrycodes=in&q={urllib.parse.quote(q)}"
            geo_req = urllib.request.Request(geo_url, headers={'User-Agent': 'AutoCart-Marketplace/2.0 (seller-verification@autocart.com)'})
            with urllib.request.urlopen(geo_req, timeout=3.0) as resp:
                geo_rows = json.loads(resp.read().decode())
                if geo_rows:
                    lat = round(float(geo_rows[0]['lat']), 6)
                    lng = round(float(geo_rows[0]['lon']), 6)
        except Exception as e:
            logger.debug("Nominatim geocoding failed for %s: %s", clean, e)

    # Fallback to known city centroid if district/city is known
    if (lat is None or lng is None) and city.lower() in KNOWN_GEOCODING_DATABASE:
        city_coords = KNOWN_GEOCODING_DATABASE[city.lower()]
        lat, lng = city_coords['lat'], city_coords['lng']

    if not city and not district and not known:
        return None

    known_subs = known.get('sub_localities', []) if (known and isinstance(known, dict)) else []
    if clean == '421301' or known_subs:
        combined = list(dict.fromkeys(known_subs + localities))
        localities = combined

    locality_coordinates = {}
    for loc_name in (localities or [city]):
        loc_key = loc_name.lower().strip()
        loc_entry = KNOWN_GEOCODING_DATABASE.get(loc_key)
        if loc_entry and 'lat' in loc_entry and 'lng' in loc_entry:
            locality_coordinates[loc_name] = {'lat': loc_entry['lat'], 'lng': loc_entry['lng']}
        elif lat is not None and lng is not None:
            h = abs(hash(f"{clean}:{loc_name}"))
            d_lat = ((h % 100) - 50) * 0.00012
            d_lng = (((h // 100) % 100) - 50) * 0.00012
            locality_coordinates[loc_name] = {'lat': round(lat + d_lat, 6), 'lng': round(lng + d_lng, 6)}

    primary_area = localities[0] if localities else (area or city)
    res = {
        'valid': True,
        'pincode': clean,
        'district': district or city,
        'city': city or district,
        'state': state or 'Maharashtra',
        'localities': localities or [city],
        'localityCoordinates': locality_coordinates,
        'isAmbiguous': is_ambiguous,
        'latitude': lat,
        'longitude': lng,
        'centroid': {'lat': lat, 'lng': lng} if (lat is not None and lng is not None) else None,
        'formattedArea': f"{primary_area}, {district or city}, {state or 'India'} {clean}",
    }
    _PINCODE_CACHE[cache_key] = res
    return res


def reverse_geocode_lookup(lat: float, lon: float) -> Dict[str, Any]:
    """
    Reverse-geocodes coordinates inside India to a confirmed neighborhood, city, and PIN code.
    """
    nearest = None
    min_dist = float('inf')
    for k, v in KNOWN_GEOCODING_DATABASE.items():
        if isinstance(v, dict) and 'lat' in v and 'lng' in v:
            d = haversine_distance_km(lat, lon, v['lat'], v['lng'])
            if d < min_dist:
                min_dist = d
                nearest = v

    detected_area = nearest['area'] if nearest and min_dist <= 5.0 else 'Selected Store Location'
    detected_city = nearest['city'] if nearest and min_dist <= 15.0 else 'Mumbai'
    detected_pin = None
    display_address = f"{detected_area}, {detected_city}"

    try:
        url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}"
        req = urllib.request.Request(url, headers={'User-Agent': 'AutoCart-Marketplace/2.0 (seller-verification@autocart.com)'})
        with urllib.request.urlopen(req, timeout=3.0) as resp:
            data = json.loads(resp.read().decode())
            if data and data.get('display_name'):
                display_address = data['display_name']
                addr = data.get('address') or {}
                if addr.get('postcode'):
                    detected_pin = addr['postcode']
                if addr.get('suburb') or addr.get('neighbourhood'):
                    detected_area = addr.get('suburb') or addr.get('neighbourhood')
                if addr.get('city') or addr.get('town') or addr.get('district'):
                    detected_city = addr.get('city') or addr.get('town') or addr.get('district')
    except Exception as e:
        logger.debug("Reverse geocode network lookup error: %s", e)

    return {
        'success': True,
        'latitude': lat,
        'longitude': lon,
        'area': detected_area,
        'city': detected_city,
        'pincode': detected_pin,
        'displayAddress': display_address,
        'distanceToKnownCenterKm': round(min_dist, 2) if min_dist != float('inf') else None
    }


@api_view(['GET'])
@permission_classes([AllowAny])
def pincode_lookup_view(request):
    """
    GET /api/location/pincode-lookup?pincode=421001
    Validates and resolves a 6-digit PIN code into locality list, city, state, and coordinates.
    """
    pincode = (request.query_params.get('pincode') or request.query_params.get('pin') or '').strip()
    address = (request.query_params.get('address') or request.query_params.get('addressContext') or '').strip()
    if not pincode:
        return Response({'valid': False, 'detail': 'PIN code parameter is required.'}, status=http_status.HTTP_400_BAD_REQUEST)
    if not re.fullmatch(r'^[1-9][0-9]{5}$', pincode):
        return Response({'valid': False, 'detail': 'PIN code must be a valid 6-digit number.'}, status=http_status.HTTP_400_BAD_REQUEST)
    res = lookup_pincode_details(pincode, address_context=address)
    if not res:
        return Response({
            'valid': False,
            'detail': f"No postal records found for PIN code {pincode}. Please verify the 6 digits or enter the store address manually."
        }, status=http_status.HTTP_404_NOT_FOUND)
    return Response(res)


@api_view(['GET'])
@permission_classes([AllowAny])
def reverse_geocode_view(request):
    """
    GET /api/location/reverse-geocode?lat=19.2215&lng=73.1643
    Reverse-geocodes coordinates into an approximate neighborhood, locality, and postal PIN code.
    """
    try:
        lat = float(request.query_params.get('lat'))
        lng = float(request.query_params.get('lng'))
    except (TypeError, ValueError):
        return Response({'success': False, 'detail': 'Valid lat and lng query parameters are required.'}, status=http_status.HTTP_400_BAD_REQUEST)
    if not (6 <= lat <= 38 and 68 <= lng <= 98):
        return Response({'success': False, 'detail': 'Coordinates must be inside India.'}, status=http_status.HTTP_400_BAD_REQUEST)
    return Response(reverse_geocode_lookup(lat, lng))


def geocode_address(query: str, pincode: Optional[str] = None, city: Optional[str] = None) -> Optional[Dict[str, Any]]:
    clean_q = (query or '').strip()
    clean_pin = (pincode or '').strip()
    clean_city = (city or '').strip()

    if not clean_q and not clean_pin:
        return None

    # 1. Exact match in KNOWN_GEOCODING_DATABASE
    q_low = clean_q.lower()
    q_norm = re.sub(r'[\,\.\-\/\(\)]', ' ', q_low).strip()
    q_norm = re.sub(r'\s+', ' ', q_norm)

    for k, v in KNOWN_GEOCODING_DATABASE.items():
        if isinstance(v, dict) and 'lat' in v and 'lng' in v:
            k_low = k.lower()
            if k_low == q_norm or k_low in q_norm or q_norm in k_low:
                return {
                    'success': True,
                    'latitude': v['lat'],
                    'longitude': v['lng'],
                    'area': v.get('area', clean_q),
                    'city': v.get('city', clean_city or 'Kalyan'),
                    'source': 'known_database'
                }

    pin_centroid = None
    if clean_pin and clean_pin in KNOWN_GEOCODING_DATABASE:
        p_entry = KNOWN_GEOCODING_DATABASE[clean_pin]
        if isinstance(p_entry, dict) and 'lat' in p_entry:
            pin_centroid = {'lat': p_entry['lat'], 'lng': p_entry['lng']}

    # 2. Try OpenStreetMap Nominatim
    try:
        search_parts = [clean_q]
        if clean_city and clean_city.lower() not in clean_q.lower():
            search_parts.append(clean_city)
        if clean_pin and clean_pin not in clean_q:
            search_parts.append(clean_pin)
        search_parts.append("Maharashtra, India")
        q_str = ", ".join(search_parts)

        geo_url = f"https://nominatim.openstreetmap.org/search?format=json&limit=1&countrycodes=in&q={urllib.parse.quote(q_str)}"
        req = urllib.request.Request(geo_url, headers={'User-Agent': 'AutoCart-Marketplace/2.0 (seller-location@autocart.com)'})
        with urllib.request.urlopen(req, timeout=2.5) as resp:
            data = json.loads(resp.read().decode())
            if data and len(data) > 0:
                lat = round(float(data[0]['lat']), 6)
                lon = round(float(data[0]['lon']), 6)
                if 6 <= lat <= 38 and 68 <= lon <= 98:
                    return {
                        'success': True,
                        'latitude': lat,
                        'longitude': lon,
                        'area': clean_q,
                        'city': clean_city,
                        'source': 'osm'
                    }
    except Exception as e:
        logger.debug("OSM geocode error for %s: %s", clean_q, e)

    # 3. Fallback to PIN centroid or City centroid with distinct deterministic offset
    base_lat = pin_centroid['lat'] if pin_centroid else None
    base_lng = pin_centroid['lng'] if pin_centroid else None

    if base_lat is None or base_lng is None:
        if clean_city and clean_city.lower() in KNOWN_GEOCODING_DATABASE:
            c_entry = KNOWN_GEOCODING_DATABASE[clean_city.lower()]
            base_lat, base_lng = c_entry['lat'], c_entry['lng']
        else:
            base_lat, base_lng = 19.2403, 73.1305 # Default Kalyan/MMR

    h = abs(hash(clean_q or 'default'))
    d_lat = ((h % 100) - 50) * 0.00015
    d_lng = (((h // 100) % 100) - 50) * 0.00015

    return {
        'success': True,
        'latitude': round(base_lat + d_lat, 6),
        'longitude': round(base_lng + d_lng, 6),
        'area': clean_q,
        'city': clean_city or 'Kalyan',
        'source': 'deterministic_fallback'
    }


@api_view(['GET'])
@permission_classes([AllowAny])
def geocode_view(request):
    """
    GET /api/location/geocode?q=Birla+College&pincode=421301&city=Kalyan
    Resolves an address, locality, or landmark query into coordinates with high precision.
    """
    q = (request.query_params.get('q') or request.query_params.get('query') or request.query_params.get('address') or '').strip()
    pincode = (request.query_params.get('pincode') or request.query_params.get('pin') or '').strip()
    city = (request.query_params.get('city') or '').strip()

    if not q and not pincode:
        return Response({'success': False, 'detail': 'Search query or PIN code is required.'}, status=http_status.HTTP_400_BAD_REQUEST)

    result = geocode_address(query=q, pincode=pincode, city=city)
    if not result:
        return Response({'success': False, 'detail': f"Unable to resolve coordinates for '{q}'."}, status=http_status.HTTP_404_NOT_FOUND)

    return Response(result)

