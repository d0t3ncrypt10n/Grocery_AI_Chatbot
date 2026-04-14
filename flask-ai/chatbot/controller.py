"""
Chatbot Controller Module
=========================
Central routing hub for all chatbot intents. Receives parsed NLP results,
orchestrates calls to product matcher, session manager, and Node.js backend,
and composes the final response sent to the frontend.
"""

import os
import logging
import requests

from ai.gemini_service import process_with_gemini, is_available as gemini_available
from ai.nlp_fallback import process_natural_language
from commerce.ingredient_normalizer import normalize_ingredient_list
from commerce.product_matcher import match_products_for_ingredients, search_single_product
from chatbot.session_manager import (
    get_session, update_session, add_to_conversation,
    set_suggested_products, set_pending_cart_items,
    get_session_context,
)

logger = logging.getLogger(__name__)

NODE_BACKEND_URL = os.getenv("NODE_BACKEND_URL", "http://localhost:4000")


def process_message(user_id, message):
    """
    Main entry point: process a user's chat message and return a response.
    
    Args:
        user_id: Unique user identifier.
        message: The user's message text.
    
    Returns:
        dict: Complete response for the frontend:
        {
            "text": str (bot's reply text),
            "intent": str,
            "products": [] (product cards to display),
            "cart_items": [] (items added to cart, if any),
            "actions": [] (quick action buttons),
            "show_cart": bool (whether to open the cart sidebar),
        }
    """
    # Record user message in session
    add_to_conversation(user_id, "user", message)

    # ── Step 1: NLP Processing (Gemini with fallback) ──────────────────────
    session_context = get_session_context(user_id)
    nlp_result = None

    if gemini_available():
        nlp_result = process_with_gemini(message, session_context)

    if nlp_result is None:
        nlp_result = process_natural_language(message)

    intent = nlp_result.get("intent", "UNKNOWN")
    logger.info(f"[{user_id}] Intent: {intent} | Message: '{message[:50]}...'")

    # Update session with current intent
    update_session(user_id, {"last_intent": intent})

    # ── Step 2: Route to Intent Handler ────────────────────────────────────
    handler = INTENT_HANDLERS.get(intent, _handle_unknown)
    response = handler(user_id, nlp_result)

    # Record bot response in session
    add_to_conversation(user_id, "bot", response.get("text", ""))

    return response


# ─── Intent Handlers ──────────────────────────────────────────────────────────

def _handle_get_recipe(user_id, nlp_result):
    """Handle GET_RECIPE intent — extract ingredients + match products."""
    dish_name = nlp_result.get("dish_name", "the dish")
    servings = nlp_result.get("servings", 2)
    raw_ingredients = nlp_result.get("ingredients", [])

    # Update session
    update_session(user_id, {"last_dish": dish_name})

    if not raw_ingredients:
        return {
            "text": f"I'd love to help you make {dish_name}, but I couldn't determine the ingredients. Could you try rephrasing?",
            "intent": "GET_RECIPE",
            "products": [],
            "actions": [],
            "show_cart": False,
        }

    # Normalize ingredients
    normalized = normalize_ingredient_list(raw_ingredients)
    logger.info(f"[{user_id}] Normalized {len(normalized)} ingredients for {dish_name}")

    # Match products from database
    matched_results = match_products_for_ingredients(normalized)

    # Build product cards for frontend
    products = []
    pending_items = []
    unavailable = []

    for result in matched_results:
        ingredient_name = result["ingredient_name"]
        status = result["status"]
        matched = result.get("matched_products", [])

        if status == "found" and matched:
            best = matched[0]
            product_card = {
                "id": best.get("id"),
                "name": best.get("name", ingredient_name),
                "price": best.get("price", 0),
                "unit": best.get("unit", ""),
                "stock": best.get("stock", 0),
                "category": best.get("category", ""),
                "image_url": best.get("image_url", ""),
                "match_type": best.get("match_type", "exact"),
                "ingredient_name": ingredient_name,
                "quantity_needed": result.get("quantity_needed", 1),
                "quantity_unit": result.get("unit", "units"),
                "alternatives": matched[1:] if len(matched) > 1 else [],
            }
            products.append(product_card)
            pending_items.append({
                "product_id": best.get("id"),
                "name": best.get("name"),
                "quantity": 1,  # Default to 1 unit of the product
                "price": best.get("price", 0),
            })

        elif status == "substitute_available" and matched:
            best = matched[0]
            product_card = {
                "id": best.get("id"),
                "name": best.get("name", ingredient_name),
                "price": best.get("price", 0),
                "unit": best.get("unit", ""),
                "stock": best.get("stock", 0),
                "category": best.get("category", ""),
                "image_url": best.get("image_url", ""),
                "match_type": "substitute",
                "substitute_for": ingredient_name,
                "ingredient_name": ingredient_name,
                "quantity_needed": result.get("quantity_needed", 1),
                "quantity_unit": result.get("unit", "units"),
                "alternatives": matched[1:] if len(matched) > 1 else [],
                "note": result.get("substitute_reason", ""),
            }
            products.append(product_card)
            pending_items.append({
                "product_id": best.get("id"),
                "name": best.get("name"),
                "quantity": 1,
                "price": best.get("price", 0),
            })

        elif status == "out_of_stock":
            unavailable.append(ingredient_name)

        else:
            unavailable.append(ingredient_name)

    # Store in session for "add all" command
    set_suggested_products(user_id, products)
    set_pending_cart_items(user_id, pending_items)

    # Compose response text
    text_parts = [nlp_result.get("message", f"Here's what you need to make **{dish_name}** for {servings} people!")]

    if products:
        text_parts.append(f"\n\nI found **{len(products)} products** for you:")

    if unavailable:
        text_parts.append(f"\n\n⚠️ Couldn't find: {', '.join(unavailable)}")

    # Build actions
    actions = []
    if pending_items:
        actions.append({"label": "🛒 Add All to Cart", "action": "ADD_ALL"})
    actions.append({"label": "🔄 Show Alternatives", "action": "SHOW_ALTERNATIVES"})

    return {
        "text": "".join(text_parts),
        "intent": "GET_RECIPE",
        "products": products,
        "actions": actions,
        "show_cart": False,
    }


def _handle_add_to_cart(user_id, nlp_result):
    """Handle ADD_TO_CART intent — add a specific item to cart."""
    item_name = nlp_result.get("item_name", "")
    quantity = nlp_result.get("item_quantity", 1)

    if not item_name:
        return {
            "text": "What would you like to add to your cart?",
            "intent": "ADD_TO_CART",
            "products": [],
            "actions": [],
            "show_cart": False,
        }

    # Find the product
    product = search_single_product(item_name)

    if not product:
        return {
            "text": f"Sorry, I couldn't find **{item_name}** in our store. Try searching with a different name.",
            "intent": "ADD_TO_CART",
            "products": [],
            "actions": [{"label": "🔍 Search Products", "action": "SHOW_PRODUCTS"}],
            "show_cart": False,
        }

    if product.get("stock", 0) <= 0:
        return {
            "text": f"**{product['name']}** is currently out of stock.",
            "intent": "ADD_TO_CART",
            "products": [product],
            "actions": [{"label": "🔄 Show Alternatives", "action": "SHOW_ALTERNATIVES"}],
            "show_cart": False,
        }

    # Add to cart via Node.js backend
    cart_result = _add_to_cart_api(user_id, product["id"], quantity)

    if cart_result:
        return {
            "text": f"✅ Added **{product['name']}** (×{quantity}) to your cart!",
            "intent": "ADD_TO_CART",
            "products": [product],
            "cart_items": cart_result.get("items", []),
            "actions": [],
            "show_cart": True,
        }
    else:
        return {
            "text": f"There was a problem adding {item_name} to your cart. Please try again.",
            "intent": "ADD_TO_CART",
            "products": [product],
            "actions": [{"label": "🔁 Retry", "action": "ADD_TO_CART"}],
            "show_cart": False,
        }


def _handle_add_all(user_id, nlp_result):
    """Handle ADD_ALL intent — add all pending items to cart."""
    session = get_session(user_id)
    pending = session.get("pending_cart_items", [])

    if not pending:
        return {
            "text": "There are no pending items to add. Try searching for a recipe first!",
            "intent": "ADD_ALL",
            "products": [],
            "actions": [],
            "show_cart": False,
        }

    # Batch add to cart via Node.js backend
    products_to_add = []
    for item in pending:
        if item.get("product_id"):
            products_to_add.append({
                "product_id": item["product_id"],
                "quantity": item.get("quantity", 1),
            })

    if not products_to_add:
        return {
            "text": "No valid products to add to cart.",
            "intent": "ADD_ALL",
            "products": [],
            "actions": [],
            "show_cart": False,
        }

    cart_result = _add_all_to_cart_api(user_id, products_to_add)

    if cart_result:
        # Clear pending items from session
        set_pending_cart_items(user_id, [])

        return {
            "text": f"✅ Added **{len(products_to_add)} items** to your cart!",
            "intent": "ADD_ALL",
            "products": [],
            "cart_items": cart_result.get("items", []),
            "actions": [],
            "show_cart": True,
        }
    else:
        return {
            "text": "There was a problem adding items to your cart. Please try again.",
            "intent": "ADD_ALL",
            "products": [],
            "actions": [{"label": "🔁 Retry", "action": "ADD_ALL"}],
            "show_cart": False,
        }


def _handle_show_products(user_id, nlp_result):
    """Handle SHOW_PRODUCTS intent — search and display products."""
    query = nlp_result.get("search_query", "")

    if not query:
        return {
            "text": "What products are you looking for?",
            "intent": "SHOW_PRODUCTS",
            "products": [],
            "actions": [],
            "show_cart": False,
        }

    # Search products
    try:
        response = requests.get(
            f"{NODE_BACKEND_URL}/products/search",
            params={"q": query, "mode": "fuzzy"},
            timeout=5,
        )

        if response.status_code == 200:
            data = response.json()
            products = data.get("products", [])

            if products:
                # Store for potential "add all"
                pending = [
                    {"product_id": p["id"], "name": p["name"], "quantity": 1, "price": p.get("price", 0)}
                    for p in products[:10]
                ]
                set_suggested_products(user_id, products[:10])
                set_pending_cart_items(user_id, pending)

                return {
                    "text": f"Found **{len(products)}** products matching **{query}**:",
                    "intent": "SHOW_PRODUCTS",
                    "products": products[:10],
                    "actions": [
                        {"label": "🛒 Add All to Cart", "action": "ADD_ALL"},
                    ],
                    "show_cart": False,
                }
            else:
                return {
                    "text": f"No products found matching **{query}**. Try a different search term.",
                    "intent": "SHOW_PRODUCTS",
                    "products": [],
                    "actions": [],
                    "show_cart": False,
                }
        else:
            return {
                "text": "Sorry, there was an issue searching for products.",
                "intent": "SHOW_PRODUCTS",
                "products": [],
                "actions": [],
                "show_cart": False,
            }

    except Exception as e:
        logger.error(f"Product search error: {e}")
        return {
            "text": "Sorry, I couldn't search for products right now. Please try again.",
            "intent": "SHOW_PRODUCTS",
            "products": [],
            "actions": [],
            "show_cart": False,
        }


def _handle_replace_item(user_id, nlp_result):
    """Handle REPLACE_ITEM intent — swap an item in suggestions/cart."""
    original = nlp_result.get("item_name", "")
    replacement = nlp_result.get("replacement", "")

    if not original or not replacement:
        return {
            "text": "Please specify what you'd like to replace and with what. E.g., \"Replace paneer with tofu\"",
            "intent": "REPLACE_ITEM",
            "products": [],
            "actions": [],
            "show_cart": False,
        }

    # Find replacement product
    product = search_single_product(replacement)
    if product:
        return {
            "text": f"🔄 Found **{product['name']}** as a replacement for {original}!",
            "intent": "REPLACE_ITEM",
            "products": [product],
            "actions": [
                {"label": f"🛒 Add {product['name']}", "action": "ADD_TO_CART"},
            ],
            "show_cart": False,
        }
    else:
        return {
            "text": f"Sorry, I couldn't find **{replacement}** in our store.",
            "intent": "REPLACE_ITEM",
            "products": [],
            "actions": [],
            "show_cart": False,
        }


def _handle_remove_item(user_id, nlp_result):
    """Handle REMOVE_ITEM intent — remove an item from cart."""
    item_name = nlp_result.get("item_name", "")

    return {
        "text": f"To remove **{item_name}**, please use the ✕ button in your cart sidebar.",
        "intent": "REMOVE_ITEM",
        "products": [],
        "actions": [],
        "show_cart": True,
    }


def _handle_show_cart(user_id, nlp_result):
    """Handle SHOW_CART intent — show current cart."""
    return {
        "text": "Here's your current cart! 🛒",
        "intent": "SHOW_CART",
        "products": [],
        "actions": [],
        "show_cart": True,
    }


def _handle_clear_cart(user_id, nlp_result):
    """Handle CLEAR_CART intent — clear the cart."""
    try:
        response = requests.delete(
            f"{NODE_BACKEND_URL}/cart/{user_id}",
            timeout=5,
        )
        if response.status_code == 200:
            return {
                "text": "🗑️ Your cart has been cleared!",
                "intent": "CLEAR_CART",
                "products": [],
                "actions": [],
                "show_cart": True,
            }
    except Exception as e:
        logger.error(f"Clear cart error: {e}")

    return {
        "text": "There was a problem clearing your cart. Please try again.",
        "intent": "CLEAR_CART",
        "products": [],
        "actions": [],
        "show_cart": False,
    }


def _handle_budget_mode(user_id, nlp_result):
    """Handle BUDGET_MODE intent — find products within a budget."""
    budget = nlp_result.get("budget", 200)
    currency = nlp_result.get("currency", "₹")

    try:
        # Get all products and filter by budget
        response = requests.get(
            f"{NODE_BACKEND_URL}/products/search",
            params={"q": "", "mode": "fuzzy", "max_price": budget},
            timeout=5,
        )

        if response.status_code == 200:
            data = response.json()
            products = data.get("products", [])

            # Sort by price ascending, pick a diverse set
            products.sort(key=lambda p: p.get("price", 0))

            # Build a budget-friendly basket
            basket = []
            total = 0
            seen_categories = set()
            for p in products:
                price = p.get("price", 0)
                category = p.get("category", "")
                if total + price <= budget and category not in seen_categories:
                    basket.append(p)
                    total += price
                    seen_categories.add(category)
                    if len(basket) >= 8:
                        break

            if basket:
                pending = [
                    {"product_id": p["id"], "name": p["name"], "quantity": 1, "price": p.get("price", 0)}
                    for p in basket
                ]
                set_suggested_products(user_id, basket)
                set_pending_cart_items(user_id, pending)

                return {
                    "text": f"💰 Here's a meal you can make within **{currency}{budget}** (Total: {currency}{total:.0f}):",
                    "intent": "BUDGET_MODE",
                    "products": basket,
                    "actions": [{"label": "🛒 Add All to Cart", "action": "ADD_ALL"}],
                    "show_cart": False,
                }

        return {
            "text": f"Sorry, I couldn't find products within {currency}{budget}. Try a higher budget.",
            "intent": "BUDGET_MODE",
            "products": [],
            "actions": [],
            "show_cart": False,
        }

    except Exception as e:
        logger.error(f"Budget mode error: {e}")
        return {
            "text": "Sorry, there was an error processing your budget request.",
            "intent": "BUDGET_MODE",
            "products": [],
            "actions": [],
            "show_cart": False,
        }


def _handle_greeting(user_id, nlp_result):
    """Handle GREETING intent."""
    return {
        "text": nlp_result.get("message", "Hello! 👋 I'm your AI grocery assistant. Tell me what you'd like to cook, or search for products!"),
        "intent": "GREETING",
        "products": [],
        "actions": [
            {"label": "🍳 Cook Something", "action": "GET_RECIPE"},
            {"label": "🔍 Browse Products", "action": "SHOW_PRODUCTS"},
            {"label": "💰 Budget Mode", "action": "BUDGET_MODE"},
        ],
        "show_cart": False,
    }


def _handle_help(user_id, nlp_result):
    """Handle HELP intent."""
    return {
        "text": nlp_result.get("message", "I can help you cook recipes, find products, and manage your cart!"),
        "intent": "HELP",
        "products": [],
        "actions": [
            {"label": "🍳 Cook Something", "action": "GET_RECIPE"},
            {"label": "🔍 Browse Products", "action": "SHOW_PRODUCTS"},
        ],
        "show_cart": False,
    }


def _handle_unknown(user_id, nlp_result):
    """Handle UNKNOWN intent — ask for clarification."""
    clarification = nlp_result.get("clarification_needed", "")
    message = nlp_result.get("message", "I'm not sure what you'd like to do.")

    if clarification:
        message += f"\n\n{clarification}"

    return {
        "text": message,
        "intent": "UNKNOWN",
        "products": [],
        "actions": [
            {"label": "🍳 Cook Something", "action": "GET_RECIPE"},
            {"label": "🔍 Browse Products", "action": "SHOW_PRODUCTS"},
            {"label": "❓ Help", "action": "HELP"},
        ],
        "show_cart": False,
    }


# ─── Intent Handler Map ──────────────────────────────────────────────────────
INTENT_HANDLERS = {
    "GET_RECIPE": _handle_get_recipe,
    "ADD_TO_CART": _handle_add_to_cart,
    "ADD_ALL": _handle_add_all,
    "SHOW_PRODUCTS": _handle_show_products,
    "REPLACE_ITEM": _handle_replace_item,
    "REMOVE_ITEM": _handle_remove_item,
    "SHOW_CART": _handle_show_cart,
    "CLEAR_CART": _handle_clear_cart,
    "BUDGET_MODE": _handle_budget_mode,
    "GREETING": _handle_greeting,
    "HELP": _handle_help,
    "UNKNOWN": _handle_unknown,
    # Backward compatibility with old intents
    "add_recipe": _handle_get_recipe,
    "add_item": _handle_add_to_cart,
    "show_list": _handle_show_cart,
    "remove_item": _handle_remove_item,
}


# ─── Node.js Backend API Helpers ──────────────────────────────────────────────

def _add_to_cart_api(user_id, product_id, quantity):
    """Add a single item to cart via Node.js backend."""
    try:
        response = requests.post(
            f"{NODE_BACKEND_URL}/cart/add",
            json={
                "user_id": user_id,
                "product_id": product_id,
                "quantity": quantity,
            },
            timeout=5,
        )
        if response.status_code in (200, 201):
            return response.json()
        else:
            logger.error(f"Add to cart failed: {response.status_code} {response.text[:100]}")
            return None
    except Exception as e:
        logger.error(f"Add to cart API error: {e}")
        return None


def _add_all_to_cart_api(user_id, products):
    """Batch add items to cart via Node.js backend."""
    try:
        response = requests.post(
            f"{NODE_BACKEND_URL}/cart/add-all",
            json={
                "user_id": user_id,
                "products": products,
            },
            timeout=10,
        )
        if response.status_code in (200, 201):
            return response.json()
        else:
            logger.error(f"Add all to cart failed: {response.status_code} {response.text[:100]}")
            return None
    except Exception as e:
        logger.error(f"Add all to cart API error: {e}")
        return None
