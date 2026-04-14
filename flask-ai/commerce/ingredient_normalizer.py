"""
Ingredient Normalizer Module
=============================
Parses raw ingredient text (e.g. "2 cups chopped onions") into structured data.
Handles fractions, adjectives, plurals, and unit extraction.
"""

import re
import logging

logger = logging.getLogger(__name__)

# ─── Adjectives to Strip ──────────────────────────────────────────────────────
# These words describe preparation, not the ingredient itself
ADJECTIVES_TO_STRIP = [
    "chopped", "diced", "minced", "sliced", "grated", "shredded",
    "crushed", "ground", "powdered", "dried", "fresh", "frozen",
    "whole", "halved", "quartered", "peeled", "deseeded", "seeded",
    "boneless", "skinless", "cooked", "uncooked", "raw", "roasted",
    "toasted", "blanched", "boiled", "steamed", "fried", "sautéed",
    "melted", "softened", "chilled", "warm", "hot", "cold",
    "large", "medium", "small", "big", "tiny", "thick", "thin",
    "ripe", "unripe", "organic", "finely", "roughly", "coarsely",
    "thinly", "thickly", "freshly", "lightly", "heavily",
    "packed", "loosely", "firmly", "heaped", "level", "rounded",
    "optional", "to taste", "as needed", "for garnish", "for serving",
]

# ─── Known Units ──────────────────────────────────────────────────────────────
KNOWN_UNITS = [
    "kg", "kilogram", "kilograms",
    "g", "gram", "grams",
    "mg", "milligram", "milligrams",
    "l", "liter", "liters", "litre", "litres",
    "ml", "milliliter", "milliliters", "millilitre", "millilitres",
    "cup", "cups",
    "tbsp", "tablespoon", "tablespoons",
    "tsp", "teaspoon", "teaspoons",
    "oz", "ounce", "ounces",
    "lb", "pound", "pounds",
    "pint", "pints",
    "quart", "quarts",
    "gallon", "gallons",
    "piece", "pieces", "pcs",
    "unit", "units",
    "clove", "cloves",
    "bunch", "bunches",
    "slice", "slices",
    "pinch", "pinches",
    "dash", "dashes",
    "handful", "handfuls",
    "sprig", "sprigs",
    "head", "heads",
    "stalk", "stalks",
    "leaf", "leaves",
    "can", "cans",
    "packet", "packets",
    "box", "boxes",
    "bag", "bags",
    "bottle", "bottles",
    "jar", "jars",
    "dozen", "dozens",
    "stick", "sticks",
    "cube", "cubes",
]

# ─── Fraction Mapping ─────────────────────────────────────────────────────────
UNICODE_FRACTIONS = {
    "½": 0.5, "⅓": 0.333, "⅔": 0.667,
    "¼": 0.25, "¾": 0.75,
    "⅕": 0.2, "⅖": 0.4, "⅗": 0.6, "⅘": 0.8,
    "⅙": 0.167, "⅚": 0.833,
    "⅛": 0.125, "⅜": 0.375, "⅝": 0.625, "⅞": 0.875,
}

# ─── Plural → Singular Mapping ────────────────────────────────────────────────
IRREGULAR_PLURALS = {
    "tomatoes": "tomato",
    "potatoes": "potato",
    "onions": "onion",
    "garlic": "garlic",  # already singular
    "leaves": "leaf",
    "berries": "berry",
    "cherries": "cherry",
    "chillies": "chili",
    "chilies": "chili",
    "chilis": "chili",
}


def normalize_ingredient(raw_text):
    """
    Parse a raw ingredient string into structured data.
    
    Args:
        raw_text: Raw ingredient text, e.g. "2 cups chopped onions"
    
    Returns:
        dict: {
            "name": str (cleaned, singular ingredient name),
            "quantity": float (numeric amount),
            "unit": str (measurement unit),
            "original": str (the original input text)
        }
    """
    if not raw_text or not raw_text.strip():
        return {"name": "", "quantity": 0, "unit": "units", "original": raw_text}

    original = raw_text.strip()
    text = original.lower().strip()

    # Remove parenthetical notes like "(about 200g)" or "(optional)"
    text = re.sub(r"\([^)]*\)", "", text).strip()

    # ── Step 1: Extract Quantity ───────────────────────────────────────────
    quantity = 1.0
    quantity_found = False

    # Check for unicode fractions first (e.g. "½ cup")
    for frac_char, frac_val in UNICODE_FRACTIONS.items():
        if frac_char in text:
            # Check for whole number + fraction (e.g. "1½")
            whole_match = re.search(rf"(\d+)\s*{re.escape(frac_char)}", text)
            if whole_match:
                quantity = float(whole_match.group(1)) + frac_val
                text = text.replace(whole_match.group(0), "").strip()
            else:
                quantity = frac_val
                text = text.replace(frac_char, "").strip()
            quantity_found = True
            break

    if not quantity_found:
        # Check for "X/Y" fractions (e.g. "1/2 cup")
        frac_match = re.match(r"^(\d+)\s+(\d+)/(\d+)\s+(.+)", text)
        if frac_match:
            whole = float(frac_match.group(1))
            num = float(frac_match.group(2))
            den = float(frac_match.group(3))
            quantity = whole + (num / den) if den != 0 else whole
            text = frac_match.group(4)
            quantity_found = True
        else:
            frac_match2 = re.match(r"^(\d+)/(\d+)\s+(.+)", text)
            if frac_match2:
                num = float(frac_match2.group(1))
                den = float(frac_match2.group(2))
                quantity = num / den if den != 0 else 1.0
                text = frac_match2.group(3)
                quantity_found = True

    if not quantity_found:
        # Check for decimal or whole number at the start
        num_match = re.match(r"^(\d+\.?\d*)\s*(.+)", text)
        if num_match:
            quantity = float(num_match.group(1))
            text = num_match.group(2)
            quantity_found = True

    # ── Step 2: Extract Unit ───────────────────────────────────────────────
    unit = "units"
    text = text.strip()

    # Sort units by length (longest first) to match "tablespoons" before "table"
    sorted_units = sorted(KNOWN_UNITS, key=len, reverse=True)

    for known_unit in sorted_units:
        # Match unit at the beginning of the remaining text
        pattern = rf"^{re.escape(known_unit)}(?:\s+of\s+|\s+)"
        match = re.match(pattern, text, re.IGNORECASE)
        if match:
            unit = known_unit
            text = text[match.end():].strip()
            break
        # Also check for unit without following text (e.g. the text IS just the unit)
        if text == known_unit:
            unit = known_unit
            text = ""
            break

    # Remove leading "of" if present (e.g. after unit extraction)
    text = re.sub(r"^of\s+", "", text).strip()

    # ── Step 3: Clean Ingredient Name ──────────────────────────────────────
    name = text

    # Remove adjectives
    for adj in ADJECTIVES_TO_STRIP:
        # Word boundary matching to avoid stripping parts of words
        name = re.sub(rf"\b{re.escape(adj)}\b", "", name, flags=re.IGNORECASE)

    # Clean up whitespace
    name = re.sub(r"\s+", " ", name).strip()

    # Remove leading/trailing punctuation
    name = name.strip(" ,.-;:'\"")

    # ── Step 4: Singularize ────────────────────────────────────────────────
    name = _singularize(name)

    # ── Step 5: Final Cleanup ──────────────────────────────────────────────
    # Capitalize properly
    name = name.strip()

    # If name is empty after all processing, use the original text
    if not name:
        name = original.strip()

    return {
        "name": name,
        "quantity": round(quantity, 2),
        "unit": unit,
        "original": original,
    }


def normalize_ingredient_list(ingredients):
    """
    Normalize a list of ingredient dicts or strings.
    
    Args:
        ingredients: List of either:
            - strings (raw text like "2 cups onions")
            - dicts with at least a "name" field (from Gemini output)
    
    Returns:
        list: List of normalized ingredient dicts.
    """
    normalized = []

    for item in ingredients:
        if isinstance(item, str):
            # Raw text string
            result = normalize_ingredient(item)
            normalized.append(result)
        elif isinstance(item, dict):
            # Already structured — just clean the name
            name = item.get("name", "")
            quantity = item.get("quantity", item.get("amount", 1))
            unit = item.get("unit", "units")

            # Clean the name
            clean_name = _clean_name(name)
            clean_name = _singularize(clean_name)

            normalized.append({
                "name": clean_name,
                "quantity": round(float(quantity), 2),
                "unit": unit,
                "original": name,
            })
        else:
            logger.warning(f"Unexpected ingredient format: {type(item)} — {item}")

    return normalized


def _clean_name(name):
    """Remove adjectives and clean up an ingredient name."""
    text = name.lower().strip()
    for adj in ADJECTIVES_TO_STRIP:
        text = re.sub(rf"\b{re.escape(adj)}\b", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\s+", " ", text).strip()
    text = text.strip(" ,.-;:'\"")
    return text


def _singularize(name):
    """
    Convert a plural ingredient name to singular.
    Uses irregular plural mapping first, then applies basic English rules.
    """
    name = name.lower().strip()

    # Check irregular plurals first
    if name in IRREGULAR_PLURALS:
        return IRREGULAR_PLURALS[name]

    # Basic English pluralization rules (in reverse)
    if name.endswith("ies") and len(name) > 4:
        # "berries" → "berry" (but not "series")
        return name[:-3] + "y"
    elif name.endswith("ves"):
        # "leaves" → "leaf"
        return name[:-3] + "f"
    elif name.endswith("oes") and name not in ("shoes", "does"):
        return name[:-2]  # "tomatoes" → "tomato"
    elif name.endswith("ses") or name.endswith("xes") or name.endswith("zes"):
        return name[:-2]  # "boxes" → "box"
    elif name.endswith("s") and not name.endswith("ss") and len(name) > 2:
        return name[:-1]  # "onions" → "onion"

    return name
