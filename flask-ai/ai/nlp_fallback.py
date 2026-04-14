"""
NLP Fallback Module
===================
Regex and keyword-based NLP processing as fallback when Gemini API is unavailable.
Ported and enhanced from the original grocery.py pattern matching logic.
"""

import re
import logging

logger = logging.getLogger(__name__)

# ─── Common Indian Recipes with Ingredients ───────────────────────────────────
# Used as fallback when Gemini is not available for ingredient extraction
RECIPE_DATABASE = {
    "butter chicken": [
        {"name": "chicken", "quantity": 500, "unit": "g"},
        {"name": "butter", "quantity": 50, "unit": "g"},
        {"name": "onion", "quantity": 2, "unit": "pieces"},
        {"name": "tomato", "quantity": 3, "unit": "pieces"},
        {"name": "cream", "quantity": 100, "unit": "ml"},
        {"name": "garlic", "quantity": 6, "unit": "cloves"},
        {"name": "ginger", "quantity": 1, "unit": "pieces"},
        {"name": "garam masala", "quantity": 1, "unit": "tbsp"},
        {"name": "turmeric", "quantity": 0.5, "unit": "tsp"},
        {"name": "chili powder", "quantity": 1, "unit": "tsp"},
        {"name": "cumin", "quantity": 1, "unit": "tsp"},
        {"name": "yogurt", "quantity": 100, "unit": "g"},
        {"name": "cooking oil", "quantity": 2, "unit": "tbsp"},
        {"name": "salt", "quantity": 1, "unit": "tsp"},
    ],
    "pasta": [
        {"name": "pasta", "quantity": 250, "unit": "g"},
        {"name": "tomato", "quantity": 3, "unit": "pieces"},
        {"name": "onion", "quantity": 1, "unit": "pieces"},
        {"name": "garlic", "quantity": 4, "unit": "cloves"},
        {"name": "olive oil", "quantity": 2, "unit": "tbsp"},
        {"name": "bell pepper", "quantity": 1, "unit": "pieces"},
        {"name": "mushroom", "quantity": 100, "unit": "g"},
        {"name": "cheese", "quantity": 50, "unit": "g"},
        {"name": "black pepper", "quantity": 0.5, "unit": "tsp"},
        {"name": "salt", "quantity": 1, "unit": "tsp"},
        {"name": "oregano", "quantity": 1, "unit": "tsp"},
    ],
    "biryani": [
        {"name": "rice", "quantity": 500, "unit": "g"},
        {"name": "chicken", "quantity": 500, "unit": "g"},
        {"name": "onion", "quantity": 3, "unit": "pieces"},
        {"name": "yogurt", "quantity": 200, "unit": "g"},
        {"name": "tomato", "quantity": 2, "unit": "pieces"},
        {"name": "ginger", "quantity": 1, "unit": "pieces"},
        {"name": "garlic", "quantity": 8, "unit": "cloves"},
        {"name": "green chili", "quantity": 3, "unit": "pieces"},
        {"name": "ghee", "quantity": 3, "unit": "tbsp"},
        {"name": "garam masala", "quantity": 1, "unit": "tbsp"},
        {"name": "turmeric", "quantity": 0.5, "unit": "tsp"},
        {"name": "cumin", "quantity": 1, "unit": "tsp"},
        {"name": "bay leaves", "quantity": 2, "unit": "pieces"},
        {"name": "cardamom", "quantity": 3, "unit": "pieces"},
        {"name": "cinnamon", "quantity": 1, "unit": "pieces"},
        {"name": "salt", "quantity": 2, "unit": "tsp"},
        {"name": "cooking oil", "quantity": 3, "unit": "tbsp"},
    ],
    "dal": [
        {"name": "lentils", "quantity": 200, "unit": "g"},
        {"name": "onion", "quantity": 1, "unit": "pieces"},
        {"name": "tomato", "quantity": 2, "unit": "pieces"},
        {"name": "garlic", "quantity": 4, "unit": "cloves"},
        {"name": "ginger", "quantity": 1, "unit": "pieces"},
        {"name": "turmeric", "quantity": 0.5, "unit": "tsp"},
        {"name": "cumin", "quantity": 1, "unit": "tsp"},
        {"name": "ghee", "quantity": 1, "unit": "tbsp"},
        {"name": "salt", "quantity": 1, "unit": "tsp"},
        {"name": "chili powder", "quantity": 0.5, "unit": "tsp"},
    ],
    "paneer tikka": [
        {"name": "paneer", "quantity": 250, "unit": "g"},
        {"name": "yogurt", "quantity": 100, "unit": "g"},
        {"name": "bell pepper", "quantity": 2, "unit": "pieces"},
        {"name": "onion", "quantity": 1, "unit": "pieces"},
        {"name": "garam masala", "quantity": 1, "unit": "tsp"},
        {"name": "turmeric", "quantity": 0.5, "unit": "tsp"},
        {"name": "chili powder", "quantity": 1, "unit": "tsp"},
        {"name": "cooking oil", "quantity": 2, "unit": "tbsp"},
        {"name": "salt", "quantity": 1, "unit": "tsp"},
        {"name": "lemon", "quantity": 1, "unit": "pieces"},
    ],
    "omelette": [
        {"name": "eggs", "quantity": 3, "unit": "pieces"},
        {"name": "onion", "quantity": 1, "unit": "pieces"},
        {"name": "tomato", "quantity": 1, "unit": "pieces"},
        {"name": "green chili", "quantity": 1, "unit": "pieces"},
        {"name": "salt", "quantity": 0.5, "unit": "tsp"},
        {"name": "black pepper", "quantity": 0.25, "unit": "tsp"},
        {"name": "butter", "quantity": 1, "unit": "tbsp"},
    ],
    "fried rice": [
        {"name": "rice", "quantity": 300, "unit": "g"},
        {"name": "eggs", "quantity": 2, "unit": "pieces"},
        {"name": "onion", "quantity": 1, "unit": "pieces"},
        {"name": "carrot", "quantity": 1, "unit": "pieces"},
        {"name": "bell pepper", "quantity": 1, "unit": "pieces"},
        {"name": "garlic", "quantity": 4, "unit": "cloves"},
        {"name": "soy sauce", "quantity": 2, "unit": "tbsp"},
        {"name": "cooking oil", "quantity": 3, "unit": "tbsp"},
        {"name": "salt", "quantity": 1, "unit": "tsp"},
        {"name": "black pepper", "quantity": 0.5, "unit": "tsp"},
    ],
    "chapati": [
        {"name": "wheat flour", "quantity": 250, "unit": "g"},
        {"name": "salt", "quantity": 0.5, "unit": "tsp"},
        {"name": "ghee", "quantity": 1, "unit": "tbsp"},
    ],
}


def process_natural_language(user_input):
    """
    Process user input using regex patterns to determine intent and extract entities.
    This is the fallback NLP when Gemini is not available.
    
    Args:
        user_input: The user's message text.
    
    Returns:
        dict with intent, entities, and a response message.
    """
    text = user_input.lower().strip()

    # ── GET_RECIPE Intent ──────────────────────────────────────────────────
    recipe_patterns = [
        r"(?:make|cook|prepare|recipe for|how to (?:make|cook|prepare))\s+(.+?)(?:\s+for\s+(\d+)\s*(?:people|person|servings?))?$",
        r"i\s+want\s+to\s+(?:make|cook|prepare)\s+(.+?)(?:\s+for\s+(\d+)\s*(?:people|person|servings?))?$",
        r"(?:get|find|show)\s+(?:me\s+)?(?:a\s+)?recipe\s+(?:for\s+)?(.+?)(?:\s+for\s+(\d+)\s*(?:people|person|servings?))?$",
        r"(?:let'?s|lets)\s+(?:make|cook|prepare)\s+(.+?)(?:\s+for\s+(\d+)\s*(?:people|person|servings?))?$",
    ]

    for pattern in recipe_patterns:
        match = re.search(pattern, text)
        if match:
            dish_name = match.group(1).strip()
            servings = int(match.group(2)) if match.group(2) else 2

            # Try to find ingredients from local database
            ingredients = _get_recipe_ingredients(dish_name, servings)
            message = f"Here are the ingredients for {dish_name} ({servings} servings):" if ingredients else f"I'll help you make {dish_name} for {servings} people!"

            return {
                "intent": "GET_RECIPE",
                "dish_name": dish_name,
                "servings": servings,
                "ingredients": ingredients,
                "message": message,
            }

    # ── ADD_TO_CART Intent ─────────────────────────────────────────────────
    add_patterns = [
        r"add\s+(\d+\.?\d*)\s*(kg|g|ml|l|cups?|tbsp|tsp|pieces?|units?|dozen)?\s*(?:of\s+)?(.+?)(?:\s+to\s+(?:my\s+)?cart)?$",
        r"add\s+(.+?)\s+to\s+(?:my\s+)?cart",
        r"(?:i\s+)?(?:want|need)\s+(\d+\.?\d*)\s*(kg|g|ml|l|cups?|tbsp|tsp|pieces?|units?|dozen)?\s*(?:of\s+)?(.+)",
        r"buy\s+(\d+\.?\d*)\s*(kg|g|ml|l|cups?|tbsp|tsp|pieces?|units?|dozen)?\s*(?:of\s+)?(.+)",
    ]

    for pattern in add_patterns:
        match = re.search(pattern, text)
        if match:
            groups = match.groups()
            if len(groups) == 3 and groups[0] and groups[0].replace(".", "").isdigit():
                quantity = float(groups[0])
                unit = groups[1] or "pieces"
                item_name = groups[2].strip()
            elif len(groups) >= 1:
                item_name = groups[0].strip()
                quantity = 1
                unit = "pieces"
            else:
                continue

            return {
                "intent": "ADD_TO_CART",
                "item_name": item_name,
                "item_quantity": quantity,
                "item_unit": unit,
                "message": f"Adding {quantity} {unit} of {item_name} to your cart.",
            }

    # ── ADD_ALL Intent ─────────────────────────────────────────────────────
    if re.search(r"\b(add\s+all|add\s+everything|add\s+them\s+all|yes\s*,?\s*add\s+all)\b", text):
        return {
            "intent": "ADD_ALL",
            "message": "Adding all suggested items to your cart!",
        }

    # ── REPLACE_ITEM Intent ────────────────────────────────────────────────
    replace_match = re.search(
        r"(?:replace|swap|substitute|switch)\s+(.+?)\s+(?:with|for|by)\s+(.+)", text
    )
    if replace_match:
        return {
            "intent": "REPLACE_ITEM",
            "item_name": replace_match.group(1).strip(),
            "replacement": replace_match.group(2).strip(),
            "message": f"Replacing {replace_match.group(1).strip()} with {replace_match.group(2).strip()}.",
        }

    # ── REMOVE_ITEM Intent ─────────────────────────────────────────────────
    remove_match = re.search(
        r"(?:remove|delete|take out|drop)\s+(.+?)(?:\s+from\s+(?:my\s+)?cart)?$", text
    )
    if remove_match:
        return {
            "intent": "REMOVE_ITEM",
            "item_name": remove_match.group(1).strip(),
            "message": f"Removing {remove_match.group(1).strip()} from your cart.",
        }

    # ── SHOW_PRODUCTS Intent ───────────────────────────────────────────────
    show_match = re.search(
        r"(?:show|search|find|browse|what|list)\s+(?:me\s+)?(?:some\s+)?(.+?)(?:\s+products?)?$", text
    )
    if show_match and any(word in text for word in ["show", "search", "find", "browse", "list", "what"]):
        query = show_match.group(1).strip()
        # Filter out common noise words
        noise = ["do you have", "is available", "are available", "you have"]
        for n in noise:
            query = query.replace(n, "").strip()
        if query:
            return {
                "intent": "SHOW_PRODUCTS",
                "search_query": query,
                "message": f"Searching for {query}...",
            }

    # ── BUDGET_MODE Intent ─────────────────────────────────────────────────
    budget_match = re.search(
        r"(?:make|cook|prepare)?\s*(?:a\s+)?(?:meal|food|dish)?\s*(?:under|within|below|for)\s*[₹$€£]?\s*(\d+)", text
    )
    if budget_match and any(word in text for word in ["under", "within", "below", "budget"]):
        budget = float(budget_match.group(1))
        currency = "₹"
        if "$" in text:
            currency = "$"
        elif "€" in text:
            currency = "€"
        elif "£" in text:
            currency = "£"

        return {
            "intent": "BUDGET_MODE",
            "budget": budget,
            "currency": currency,
            "message": f"Finding a meal within {currency}{budget}...",
        }

    # ── SHOW_CART Intent ───────────────────────────────────────────────────
    if re.search(r"\b(show|view|see|what'?s in)\s*(my\s+)?cart\b", text):
        return {
            "intent": "SHOW_CART",
            "message": "Here's what's in your cart.",
        }

    # ── CLEAR_CART Intent ──────────────────────────────────────────────────
    if re.search(r"\b(clear|empty|reset)\s*(my\s+)?cart\b", text):
        return {
            "intent": "CLEAR_CART",
            "message": "Your cart has been cleared.",
        }

    # ── GREETING Intent ───────────────────────────────────────────────────
    if re.search(r"^(hi|hello|hey|good\s+(morning|afternoon|evening)|howdy|greetings)\b", text):
        return {
            "intent": "GREETING",
            "message": "Hello! 👋 I'm your AI grocery assistant. Tell me what you'd like to cook, or ask me to find products!",
        }

    # ── HELP Intent ────────────────────────────────────────────────────────
    if re.search(r"\b(help|what can you do|how (?:do|does) (?:this|it) work|commands?)\b", text):
        return {
            "intent": "HELP",
            "message": (
                "Here's what I can do:\n"
                "🍳 **Cook something**: \"Make butter chicken for 4 people\"\n"
                "🛒 **Add to cart**: \"Add 2kg onions to cart\"\n"
                "🔍 **Search products**: \"Show me vegetables\"\n"
                "💰 **Budget mode**: \"Make a meal under ₹200\"\n"
                "🔄 **Replace items**: \"Replace paneer with tofu\"\n"
                "📋 **View cart**: \"Show my cart\"\n"
                "🗑️ **Clear cart**: \"Clear my cart\""
            ),
        }

    # ── UNKNOWN Intent ─────────────────────────────────────────────────────
    return {
        "intent": "UNKNOWN",
        "message": "I'm not sure what you'd like to do. Try saying something like \"Make pasta for 4 people\" or \"Add onions to my cart\".",
        "clarification_needed": "Could you rephrase that? I can help you cook recipes, search for products, or manage your cart.",
    }


def _get_recipe_ingredients(dish_name, servings):
    """
    Look up a recipe in the local database and scale ingredients for servings.
    Base recipes are for 2 servings.
    
    Args:
        dish_name: The name of the dish.
        servings: Number of servings to scale to.
    
    Returns:
        list: Scaled ingredients, or empty list if recipe not found.
    """
    # Try exact match first
    base_ingredients = RECIPE_DATABASE.get(dish_name)

    # Try partial match
    if not base_ingredients:
        for recipe_name, ingredients in RECIPE_DATABASE.items():
            if recipe_name in dish_name or dish_name in recipe_name:
                base_ingredients = ingredients
                break

    if not base_ingredients:
        return []

    # Scale for servings (base recipes are for 2 servings)
    scale_factor = servings / 2.0
    scaled = []
    for ing in base_ingredients:
        scaled.append({
            "name": ing["name"],
            "quantity": round(ing["quantity"] * scale_factor, 2),
            "unit": ing["unit"],
        })

    return scaled
