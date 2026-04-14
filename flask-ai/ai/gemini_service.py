"""
Gemini Service Module
=====================
Integrates with Google's Gemini API for intelligent NLP processing.
Handles intent detection, ingredient extraction, and recipe generation.
Falls back gracefully if the API is unavailable.
"""

import os
import json
import logging

logger = logging.getLogger(__name__)

# ─── Gemini API Setup ─────────────────────────────────────────────────────────
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash-preview-04-17")
gemini_available = False
client = None

try:
    if GEMINI_API_KEY:
        from google import genai
        from google.genai import types
        client = genai.Client(api_key=GEMINI_API_KEY)
        gemini_available = True
        logger.info("Gemini API initialized successfully")
    else:
        logger.warning("GEMINI_API_KEY not set — Gemini features disabled")
except ImportError:
    logger.warning("google-genai package not installed — Gemini features disabled")
except Exception as e:
    logger.error(f"Error initializing Gemini API: {e}")


# ─── System Prompt ────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """You are an AI grocery shopping assistant. Analyze the user's message and extract structured information.

Return a JSON object with the following structure:

{
  "intent": "<one of the intents below>",
  "dish_name": "<name of the dish if applicable>",
  "servings": <number of servings, default 2>,
  "ingredients": [
    {
      "name": "<ingredient name>",
      "quantity": <numeric amount>,
      "unit": "<measurement unit>"
    }
  ],
  "item_name": "<single item name if adding/removing one item>",
  "item_quantity": <quantity for single item>,
  "item_unit": "<unit for single item>",
  "budget": <budget amount if budget mode>,
  "currency": "<currency symbol>",
  "search_query": "<product search query>",
  "clarification_needed": "<question to ask user if input is ambiguous>",
  "message": "<friendly response text to show the user>"
}

INTENTS:
- GET_RECIPE: User wants to cook something (e.g. "make butter chicken for 4 people", "how to cook pasta")
  → Extract dish_name, servings, and list all ingredients with quantities
- ADD_TO_CART: User wants to add a specific product (e.g. "add 2kg onions to cart")
  → Extract item_name, item_quantity, item_unit
- ADD_ALL: User wants to add all previously suggested items (e.g. "add all", "add everything")
  → No additional fields needed
- SHOW_PRODUCTS: User wants to search/browse products (e.g. "show me vegetables", "what dairy do you have")
  → Extract search_query or category
- REPLACE_ITEM: User wants to swap an item (e.g. "replace paneer with tofu")
  → Extract item_name (original) and replacement item
- REMOVE_ITEM: User wants to remove from cart (e.g. "remove onions")
  → Extract item_name
- BUDGET_MODE: User wants to shop within a budget (e.g. "make a meal under ₹200")
  → Extract budget, currency, and optionally dish_name
- SHOW_CART: User wants to see their cart
- CLEAR_CART: User wants to empty their cart
- GREETING: User is saying hello
- HELP: User needs help understanding commands
- UNKNOWN: Cannot determine intent → set clarification_needed

RULES:
1. For GET_RECIPE, ALWAYS provide a complete ingredient list with realistic quantities for the given servings.
2. Singularize ingredient names (e.g. "onions" → "onion").
3. Use standard units: g, kg, ml, l, cups, tbsp, tsp, pieces, units.
4. If servings not specified, default to 2.
5. If the input is ambiguous, set intent to UNKNOWN and provide a clarification question.
6. Always include a friendly "message" field with a natural response.
7. For Indian dishes, use Indian ingredient names (e.g. "ghee", "garam masala").

Only return valid JSON. No markdown, no explanation, just the JSON object."""


def process_with_gemini(user_input, session_context=None):
    """
    Process user input using Gemini API for intent detection and entity extraction.
    
    Args:
        user_input: The user's message text.
        session_context: Optional dict with conversation context from session manager.
    
    Returns:
        dict: Parsed result with intent, ingredients, etc.
        None: If Gemini is unavailable or fails (caller should use fallback).
    """
    if not gemini_available or not client:
        logger.info("Gemini not available, returning None for fallback")
        return None

    try:
        # Build context-aware prompt
        context_info = ""
        if session_context:
            if session_context.get("last_dish"):
                context_info += f"\nContext: User was previously looking at '{session_context['last_dish']}'."
            if session_context.get("suggested_products"):
                product_names = [p.get("name", "") for p in session_context["suggested_products"][:5]]
                context_info += f"\nPreviously suggested products: {', '.join(product_names)}"
            if session_context.get("pending_cart_items"):
                pending = [p.get("name", "") for p in session_context["pending_cart_items"][:5]]
                context_info += f"\nPending cart items: {', '.join(pending)}"

        full_prompt = f"{SYSTEM_PROMPT}{context_info}\n\nUser input: {user_input}"

        from google.genai import types

        contents = [
            types.Content(
                role="user",
                parts=[types.Part.from_text(text=full_prompt)],
            ),
        ]

        generate_config = types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0.3,  # Low temperature for more consistent structured output
        )

        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=contents,
            config=generate_config,
        )

        # Parse the JSON response
        response_text = response.text.strip()

        # Handle potential markdown code fences
        if response_text.startswith("```"):
            lines = response_text.split("\n")
            # Remove first and last lines (code fences)
            response_text = "\n".join(lines[1:-1])

        result = json.loads(response_text)

        # Validate required fields
        if "intent" not in result:
            result["intent"] = "UNKNOWN"
        if "message" not in result:
            result["message"] = "I processed your request."

        # Ensure ingredients is always a list
        if "ingredients" not in result:
            result["ingredients"] = []

        logger.info(f"Gemini parsed intent: {result['intent']} for input: '{user_input[:50]}...'")
        return result

    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse Gemini JSON response: {e}")
        logger.error(f"Raw response: {response_text[:200] if 'response_text' in dir() else 'N/A'}")
        return None

    except Exception as e:
        logger.error(f"Gemini API error: {e}")
        return None


def is_available():
    """Check if Gemini API is configured and available."""
    return gemini_available and client is not None
