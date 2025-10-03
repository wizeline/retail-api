from typing import Dict, List, Optional

# Zones (3)
ZONES = [
    {
        "id": "HOT",
        "name": "Impulse",
        "type": "impulse",
        "capacity": 15,
        "weight": {"velocity": 0.45, "margin": 0.25, "price": 0.10, "fit": 0.20},
    },
    {
        "id": "WINE",
        "name": "Beverages",
        "type": "beverages",
        "capacity": 12,
        "weight": {"velocity": 0.30, "margin": 0.25, "price": 0.10, "fit": 0.35},
    },
    {
        "id": "PRO",
        "name": "Produce",
        "type": "produce",
        "capacity": 18,
        "weight": {"velocity": 0.25, "margin": 0.15, "price": 0.10, "fit": 0.50},
    },
]

# Products (English)
PRODUCTS = [
    {"id":"P01","name":"Cola 500ml","cat":"beverages","price":1.5,"margin":0.25,"velocity":0.90,"tags":["cold","impulse"]},
    {"id":"P02","name":"Mineral Water 600ml","cat":"beverages","price":1.0,"margin":0.22,"velocity":0.80,"tags":["healthy","cold"]},
    {"id":"P03","name":"Orange Juice 1L","cat":"beverages","price":2.1,"margin":0.28,"velocity":0.65,"tags":["healthy","cold"]},
    {"id":"P04","name":"Whole Milk 1L","cat":"dairy","price":1.6,"margin":0.18,"velocity":0.75,"tags":["basic","cold"]},
    {"id":"P05","name":"Strawberry Yogurt 200g","cat":"dairy","price":0.9,"margin":0.30,"velocity":0.70,"tags":["impulse","cold"]},
    {"id":"P06","name":"Mozzarella Cheese 250g","cat":"dairy","price":3.2,"margin":0.32,"velocity":0.55,"tags":["gourmet","cold"]},
    {"id":"P07","name":"Potato Chips 120g","cat":"snacks","price":1.2,"margin":0.35,"velocity":0.85,"tags":["salty","impulse"]},
    {"id":"P08","name":"Chocolate Bar 50g","cat":"snacks","price":0.8,"margin":0.38,"velocity":0.88,"tags":["sweet","impulse"]},
    {"id":"P09","name":"Granola Bar","cat":"snacks","price":1.0,"margin":0.30,"velocity":0.60,"tags":["healthy"]},
    {"id":"P10","name":"Red Apple (each)","cat":"produce","price":0.5,"margin":0.20,"velocity":0.65,"tags":["healthy","fresh"]},
    {"id":"P11","name":"Banana (each)","cat":"produce","price":0.4,"margin":0.18,"velocity":0.70,"tags":["healthy","fresh"]},
    {"id":"P12","name":"Mixed Veggies Frozen","cat":"frozen","price":2.5,"margin":0.27,"velocity":0.50,"tags":["frozen","healthy"]},
    {"id":"P13","name":"Vanilla Ice Cream 1L","cat":"frozen","price":3.0,"margin":0.33,"velocity":0.72,"tags":["cold","sweet","frozen"]},
    {"id":"P14","name":"Sliced Bread","cat":"bakery","price":1.4,"margin":0.22,"velocity":0.68,"tags":["basic"]},
    {"id":"P15","name":"Croissant","cat":"bakery","price":1.1,"margin":0.28,"velocity":0.58,"tags":["impulse"]},
    {"id":"P16","name":"Detergent 1kg","cat":"household","price":4.0,"margin":0.26,"velocity":0.45,"tags":["home"]},
    {"id":"P17","name":"Liquid Soap 500ml","cat":"personal care","price":2.3,"margin":0.24,"velocity":0.52,"tags":["hygiene"]},
    {"id":"P18","name":"Shampoo 400ml","cat":"personal care","price":3.5,"margin":0.29,"velocity":0.48,"tags":["hygiene"]},
    {"id":"P19","name":"Dog Food 2kg","cat":"pets","price":6.0,"margin":0.20,"velocity":0.35,"tags":["pets"]},
    {"id":"P20","name":"Gourmet Cookies","cat":"gourmet","price":4.2,"margin":0.34,"velocity":0.30,"tags":["gourmet","premium"]},
    {"id":"P21","name":"Mixed Nuts","cat":"snacks","price":2.8,"margin":0.31,"velocity":0.42,"tags":["healthy","premium"]},
    {"id":"P22","name":"Kombucha 330ml","cat":"beverages","price":2.9,"margin":0.36,"velocity":0.28,"tags":["healthy","premium","cold"]},
    {"id":"P23","name":"Lactose-Free Milk 1L","cat":"dairy","price":1.8,"margin":0.20,"velocity":0.60,"tags":["healthy","cold"]},
    {"id":"P24","name":"Frozen Pizza","cat":"frozen","price":5.5,"margin":0.35,"velocity":0.44,"tags":["frozen","impulse"]},
    {"id":"P25","name":"Frozen Cassava","cat":"frozen","price":2.1,"margin":0.23,"velocity":0.40,"tags":["frozen"]},
]

# Hotspots (only used ids)
HOTSPOTS = {
    "HOT":  {"x": 18, "y": 46, "w": 9,  "h": 18},  # Impulse
    "WINE": {"x": 35, "y": 48, "w": 5,  "h": 22},  # Beverages
    "PRO":  {"x": 83, "y": 56, "w": 14, "h": 30},  # Produce
}

# In-memory layouts
LAYOUTS: Dict[str, List[Optional[str]]] = {}

MIN_PRICE = min(p["price"] for p in PRODUCTS)
MAX_PRICE = max(p["price"] for p in PRODUCTS)
