"""
Product Matcher Module
======================
Matches normalized ingredients to real products in the Node.js backend database.
Uses a 4-step matching pipeline: exact → fuzzy → category → suggestions.
Includes smart substitution logic for out-of-stock items.
"""

import os
import logging
import requests
from utils.fuzzy_match import combined_fuzzy_search, find_best_match

logger = logging.getLogger(__name__)

NODE_BACKEND_URL = os.getenv("NODE_BACKEND_URL", "http://localhost:4000")

# ─── Smart Substitution Map ──────────────────────────────────────────────────
# Maps ingredients to potential substitutes when original is unavailable
SUBSTITUTION_MAP = {
    "paneer": ["tofu", "cottage cheese", "halloumi"],
    "butter": ["margarine", "ghee", "cooking oil"],
    "cream": ["coconut cream", "yogurt", "milk"],
    "milk": ["almond milk", "soy milk", "coconut milk"],
    "chicken": ["tofu", "paneer", "mushroom"],
    "ghee": ["butter", "cooking oil", "olive oil"],
    "yogurt": ["cream", "sour cream", "buttermilk"],
    "rice": ["quinoa", "couscous", "bulgur wheat"],
    "wheat flour": ["almond flour", "rice flour", "chickpea flour"],
    "cheese": ["paneer", "nutritional yeast", "tofu"],
    "eggs": ["tofu", "banana", "flax seeds"],
    "fish": ["tofu", "chicken", "mushroom"],
    "soy sauce": ["tamari", "coconut aminos", "worcestershire sauce"],
    "olive oil": ["cooking oil", "coconut oil", "avocado oil"],
    "lemon": ["lime", "vinegar", "citric acid"],
    "tomato": ["tomato sauce", "tomato paste", "canned tomato"],
    "onion": ["shallot", "spring onion", "leek"],
    "bell pepper": ["capsicum", "jalapeno", "green chili"],
    "pasta": ["noodles", "rice", "zucchini"],
}


def match_products_for_ingredients(normalized_ingredients):
    """
    Match a list of normalized ingredients to products from the database.
    
    Args:
        normalized_ingredients: List of dicts with {name, quantity, unit} from normalizer.
    
    Returns:
        list: List of dicts with matched product info:
        [
            {
                "ingredient_name": str,
                "quantity_needed": float,
                "unit": str,
                "matched_products": [
                    {
                        "id": int,
                        "name": str,
                        "price": float,
                        "unit": str,
                        "stock": int,
                        "category": str,
                        "image_url": str,
                        "match_type": str ("exact"|"fuzzy"|"category"|"substitute"),
                        "match_score": float
                    }
                ],
                "status": str ("found"|"out_of_stock"|"not_found"|"substitute_available"),
                "substitute_reason": str (optional)
            }
        ]
    """
    results = []

    for ingredient in normalized_ingredients:
        name = ingredient.get("name", "")
        quantity = ingredient.get("quantity", 1)
        unit = ingredient.get("unit", "units")

        if not name:
            continue

        result = {
            "ingredient_name": name,
            "quantity_needed": quantity,
            "unit": unit,
            "matched_products": [],
            "status": "not_found",
        }

        # ── Step 1: Exact Match ────────────────────────────────────────────
        products = _search_products(name, mode="exact")
        if products:
            in_stock = [p for p in products if p.get("stock", 0) > 0]
            if in_stock:
                result["matched_products"] = _tag_products(in_stock[:3], "exact", 100)
                result["status"] = "found"
                results.append(result)
                continue
            else:
                # Found but out of stock
                result["matched_products"] = _tag_products(products[:3], "exact", 100)
                result["status"] = "out_of_stock"
                # Try to find substitutes
                subs = _find_substitutes(name)
                if subs:
                    result["matched_products"].extend(subs)
                    result["status"] = "substitute_available"
                    result["substitute_reason"] = f"{name} is out of stock"
                results.append(result)
                continue

        # ── Step 2: Fuzzy Match (LIKE search) ──────────────────────────────
        products = _search_products(name, mode="fuzzy")
        if products:
            # Use fuzzy scoring to rank results
            product_names = [p.get("name", "") for p in products]
            fuzzy_results = combined_fuzzy_search(name, product_names, threshold=60, limit=3)

            if fuzzy_results:
                matched = []
                for fr in fuzzy_results:
                    idx = fr["index"]
                    if idx < len(products):
                        product = products[idx].copy()
                        product["match_type"] = "fuzzy"
                        product["match_score"] = fr["score"]
                        matched.append(product)

                in_stock = [p for p in matched if p.get("stock", 0) > 0]
                if in_stock:
                    result["matched_products"] = in_stock[:3]
                    result["status"] = "found"
                else:
                    result["matched_products"] = matched[:3]
                    result["status"] = "out_of_stock"
                    subs = _find_substitutes(name)
                    if subs:
                        result["matched_products"].extend(subs)
                        result["status"] = "substitute_available"
                        result["substitute_reason"] = f"{name} is out of stock"

                results.append(result)
                continue

        # ── Step 3: Category Fallback ──────────────────────────────────────
        category = _guess_category(name)
        if category:
            products = _search_products(category, mode="category")
            if products:
                # Score by relevance to original ingredient name
                product_names = [p.get("name", "") for p in products]
                fuzzy_results = combined_fuzzy_search(name, product_names, threshold=30, limit=3)

                if fuzzy_results:
                    matched = []
                    for fr in fuzzy_results:
                        idx = fr["index"]
                        if idx < len(products):
                            product = products[idx].copy()
                            product["match_type"] = "category"
                            product["match_score"] = fr["score"]
                            matched.append(product)
                    result["matched_products"] = matched[:3]
                    result["status"] = "found"
                    results.append(result)
                    continue

        # ── Step 4: Substitutes as Last Resort ─────────────────────────────
        subs = _find_substitutes(name)
        if subs:
            result["matched_products"] = subs
            result["status"] = "substitute_available"
            result["substitute_reason"] = f"Couldn't find {name} - here are some alternatives"
        else:
            result["status"] = "not_found"

        results.append(result)

    return results


def search_single_product(query):
    """
    Search for a single product by name. Used for ADD_TO_CART intent.
    
    Args:
        query: Product name to search for.
    
    Returns:
        dict: Best matching product, or None if not found.
    """
    # Try exact match first
    products = _search_products(query, mode="exact")
    if products:
        in_stock = [p for p in products if p.get("stock", 0) > 0]
        if in_stock:
            return in_stock[0]
        return products[0]

    # Try fuzzy match
    products = _search_products(query, mode="fuzzy")
    if products:
        product_names = [p.get("name", "") for p in products]
        fuzzy = find_best_match(query, product_names, threshold=65, limit=1)
        if fuzzy:
            return products[fuzzy[0]["index"]]

    return None


def _search_products(query, mode="exact"):
    """
    Search products via the Node.js backend API.
    
    Args:
        query: Search term.
        mode: "exact", "fuzzy", or "category".
    
    Returns:
        list: Product dicts from the API, or empty list on error.
    """
    try:
        params = {"q": query, "mode": mode}
        if mode == "category":
            params = {"category": query}

        response = requests.get(
            f"{NODE_BACKEND_URL}/products/search",
            params=params,
            timeout=5,
        )

        if response.status_code == 200:
            data = response.json()
            return data.get("products", [])
        else:
            logger.warning(f"Product search returned {response.status_code}: {response.text[:100]}")
            return []

    except requests.exceptions.ConnectionError:
        logger.error(f"Cannot connect to Node.js backend at {NODE_BACKEND_URL}")
        return []
    except requests.exceptions.Timeout:
        logger.error("Product search timed out")
        return []
    except Exception as e:
        logger.error(f"Product search error: {e}")
        return []


def _tag_products(products, match_type, score):
    """Add match_type and match_score to product dicts."""
    for p in products:
        p["match_type"] = match_type
        p["match_score"] = score
    return products


def _find_substitutes(ingredient_name):
    """
    Find substitute products for an ingredient.
    
    Args:
        ingredient_name: The ingredient that's unavailable.
    
    Returns:
        list: Substitute product dicts, or empty list.
    """
    name_lower = ingredient_name.lower()
    substitute_names = SUBSTITUTION_MAP.get(name_lower, [])

    substitutes = []
    for sub_name in substitute_names:
        products = _search_products(sub_name, mode="fuzzy")
        if products:
            in_stock = [p for p in products if p.get("stock", 0) > 0]
            if in_stock:
                product = in_stock[0].copy()
                product["match_type"] = "substitute"
                product["match_score"] = 50
                product["substitute_for"] = ingredient_name
                substitutes.append(product)
                if len(substitutes) >= 2:
                    break

    return substitutes


def _guess_category(ingredient_name):
    """
    Guess the product category for an ingredient name.
    Used for category-level fallback searches.
    """
    name = ingredient_name.lower()

    category_keywords = {
        "vegetables": [
            "onion", "tomato", "potato", "carrot", "spinach", "cabbage",
            "cauliflower", "broccoli", "mushroom", "pepper", "capsicum",
            "eggplant", "cucumber", "peas", "corn", "garlic", "ginger",
            "lettuce", "celery", "zucchini", "bean", "lentil",
        ],
        "dairy": [
            "milk", "butter", "cream", "cheese", "paneer", "yogurt",
            "curd", "ghee", "condensed milk", "buttermilk",
        ],
        "grains": [
            "rice", "flour", "wheat", "pasta", "bread", "oats",
            "semolina", "noodle", "cereal", "cornstarch",
        ],
        "spices": [
            "turmeric", "cumin", "coriander", "chili", "pepper",
            "garam masala", "cinnamon", "cardamom", "clove", "nutmeg",
            "oregano", "basil", "thyme", "rosemary", "bay leaf",
            "paprika", "saffron", "mustard", "fennel", "salt",
        ],
        "proteins": [
            "chicken", "egg", "fish", "tofu", "lentil", "chickpea",
            "kidney bean", "soya", "prawn", "shrimp", "mutton", "lamb",
        ],
        "oils_sauces": [
            "oil", "olive oil", "cooking oil", "soy sauce", "vinegar",
            "tomato sauce", "ketchup", "mayonnaise", "mustard sauce",
        ],
    }

    for category, keywords in category_keywords.items():
        for keyword in keywords:
            if keyword in name:
                return category

    return None
