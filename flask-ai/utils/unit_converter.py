"""
Unit Converter Module
====================
Handles conversion between different measurement units for ingredients.
Supports liquid and dry ingredient conversions with category-aware ratios.
"""

# ─── Conversion Tables ────────────────────────────────────────────────────────
# All conversions are relative to a base unit (ml for liquid, grams for dry)

LIQUID_TO_ML = {
    "ml": 1.0,
    "milliliter": 1.0,
    "milliliters": 1.0,
    "l": 1000.0,
    "liter": 1000.0,
    "liters": 1000.0,
    "cup": 236.588,
    "cups": 236.588,
    "tbsp": 14.787,
    "tablespoon": 14.787,
    "tablespoons": 14.787,
    "tsp": 4.929,
    "teaspoon": 4.929,
    "teaspoons": 4.929,
    "fl oz": 29.574,
    "fluid ounce": 29.574,
    "fluid ounces": 29.574,
    "pint": 473.176,
    "pints": 473.176,
    "quart": 946.353,
    "quarts": 946.353,
    "gallon": 3785.41,
    "gallons": 3785.41,
}

DRY_TO_GRAMS = {
    "g": 1.0,
    "gram": 1.0,
    "grams": 1.0,
    "kg": 1000.0,
    "kilogram": 1000.0,
    "kilograms": 1000.0,
    "oz": 28.3495,
    "ounce": 28.3495,
    "ounces": 28.3495,
    "lb": 453.592,
    "pound": 453.592,
    "pounds": 453.592,
    "mg": 0.001,
    "milligram": 0.001,
    "milligrams": 0.001,
}

# Approximate cup-to-gram conversions for common ingredient categories
# These vary by ingredient density, so we use category-level approximations
CUP_TO_GRAMS_BY_CATEGORY = {
    "flour": 120,        # all-purpose flour
    "sugar": 200,        # granulated sugar
    "butter": 227,       # solid butter
    "rice": 185,         # uncooked rice
    "oats": 90,          # rolled oats
    "milk": 245,         # liquid milk (≈ water)
    "cream": 240,
    "oil": 218,
    "honey": 340,
    "salt": 288,
    "spice": 110,        # ground spices average
    "vegetables": 150,   # chopped vegetables average
    "cheese": 113,       # shredded cheese
    "nuts": 140,         # chopped nuts
    "default": 150,      # fallback
}

# Count-based units (no conversion needed, just pass through)
COUNT_UNITS = {
    "unit", "units", "piece", "pieces", "whole",
    "clove", "cloves", "bunch", "bunches",
    "slice", "slices", "pinch", "pinches",
    "dash", "dashes", "handful", "handfuls",
    "sprig", "sprigs", "head", "heads",
    "stalk", "stalks", "leaf", "leaves",
    "can", "cans", "packet", "packets",
    "box", "boxes", "bag", "bags",
    "bottle", "bottles", "jar", "jars",
    "dozen", "dozens",
}


def is_count_unit(unit):
    """Check if a unit is a count-based unit (not convertible)."""
    return unit.lower().strip() in COUNT_UNITS


def is_liquid_unit(unit):
    """Check if a unit is a liquid measurement unit."""
    return unit.lower().strip() in LIQUID_TO_ML


def is_dry_unit(unit):
    """Check if a unit is a dry weight measurement unit."""
    return unit.lower().strip() in DRY_TO_GRAMS


def get_ingredient_category(ingredient_name):
    """
    Determine the category of an ingredient for density-based conversions.
    Returns a key from CUP_TO_GRAMS_BY_CATEGORY.
    """
    name = ingredient_name.lower()

    category_keywords = {
        "flour": ["flour", "maida", "atta", "besan"],
        "sugar": ["sugar", "jaggery", "sweetener"],
        "butter": ["butter", "margarine", "ghee"],
        "rice": ["rice", "basmati", "quinoa"],
        "oats": ["oats", "oatmeal", "muesli"],
        "milk": ["milk"],
        "cream": ["cream", "yogurt", "curd", "dahi"],
        "oil": ["oil"],
        "honey": ["honey", "syrup", "molasses"],
        "salt": ["salt"],
        "spice": [
            "turmeric", "cumin", "coriander", "pepper", "chili",
            "garam masala", "cinnamon", "cardamom", "paprika",
            "oregano", "basil", "thyme", "rosemary",
        ],
        "vegetables": [
            "onion", "tomato", "potato", "carrot", "spinach",
            "cabbage", "cauliflower", "broccoli", "mushroom",
            "bell pepper", "capsicum", "peas", "corn",
        ],
        "cheese": ["cheese", "paneer", "mozzarella", "cheddar", "parmesan"],
        "nuts": ["almond", "cashew", "peanut", "walnut", "pistachio", "nut"],
    }

    for category, keywords in category_keywords.items():
        for keyword in keywords:
            if keyword in name:
                return category

    return "default"


def convert(amount, from_unit, to_unit, ingredient_name=""):
    """
    Convert an amount from one unit to another.
    
    Args:
        amount: The numeric amount to convert.
        from_unit: The source unit (e.g. "cups").
        to_unit: The target unit (e.g. "grams").
        ingredient_name: Optional ingredient name for density-aware conversions.
    
    Returns:
        dict with converted amount and unit, or original if conversion not possible.
        {
            "amount": float,
            "unit": str,
            "converted": bool,
            "note": str (optional)
        }
    """
    from_unit = from_unit.lower().strip()
    to_unit = to_unit.lower().strip()

    # Same unit — no conversion needed
    if from_unit == to_unit:
        return {"amount": amount, "unit": to_unit, "converted": False}

    # Count units — cannot convert
    if is_count_unit(from_unit) or is_count_unit(to_unit):
        return {
            "amount": amount,
            "unit": from_unit,
            "converted": False,
            "note": f"Cannot convert between '{from_unit}' and '{to_unit}' (count-based unit)"
        }

    # ── Liquid ↔ Liquid Conversion ──────────────────────────────────────────
    if from_unit in LIQUID_TO_ML and to_unit in LIQUID_TO_ML:
        ml = amount * LIQUID_TO_ML[from_unit]
        converted = ml / LIQUID_TO_ML[to_unit]
        return {"amount": round(converted, 2), "unit": to_unit, "converted": True}

    # ── Dry ↔ Dry Conversion ───────────────────────────────────────────────
    if from_unit in DRY_TO_GRAMS and to_unit in DRY_TO_GRAMS:
        grams = amount * DRY_TO_GRAMS[from_unit]
        converted = grams / DRY_TO_GRAMS[to_unit]
        return {"amount": round(converted, 2), "unit": to_unit, "converted": True}

    # ── Cup (volume) → Grams (weight) — needs ingredient category ──────────
    if from_unit in ("cup", "cups") and to_unit in ("g", "gram", "grams"):
        category = get_ingredient_category(ingredient_name)
        grams_per_cup = CUP_TO_GRAMS_BY_CATEGORY.get(category, 150)
        converted = amount * grams_per_cup
        return {
            "amount": round(converted, 2),
            "unit": "g",
            "converted": True,
            "note": f"Estimated using {category} density ({grams_per_cup}g/cup)"
        }

    # ── Grams → Cups (reverse of above) ───────────────────────────────────
    if from_unit in ("g", "gram", "grams") and to_unit in ("cup", "cups"):
        category = get_ingredient_category(ingredient_name)
        grams_per_cup = CUP_TO_GRAMS_BY_CATEGORY.get(category, 150)
        converted = amount / grams_per_cup
        return {
            "amount": round(converted, 2),
            "unit": "cups",
            "converted": True,
            "note": f"Estimated using {category} density ({grams_per_cup}g/cup)"
        }

    # ── Liquid → Dry or other cross-type (attempt via ml→grams at 1:1) ────
    # Water-like approximation: 1 ml ≈ 1 gram
    if from_unit in LIQUID_TO_ML and to_unit in DRY_TO_GRAMS:
        ml = amount * LIQUID_TO_ML[from_unit]
        converted = ml / DRY_TO_GRAMS[to_unit]
        return {
            "amount": round(converted, 2),
            "unit": to_unit,
            "converted": True,
            "note": "Approximate conversion assuming water-like density"
        }

    if from_unit in DRY_TO_GRAMS and to_unit in LIQUID_TO_ML:
        grams = amount * DRY_TO_GRAMS[from_unit]
        converted = grams / LIQUID_TO_ML[to_unit]
        return {
            "amount": round(converted, 2),
            "unit": to_unit,
            "converted": True,
            "note": "Approximate conversion assuming water-like density"
        }

    # ── Fallback — no conversion possible ──────────────────────────────────
    return {
        "amount": amount,
        "unit": from_unit,
        "converted": False,
        "note": f"No conversion available from '{from_unit}' to '{to_unit}'"
    }


def standardize_unit(unit):
    """
    Standardize a unit string to a canonical form.
    E.g. "tablespoons" → "tbsp", "kilograms" → "kg"
    """
    unit = unit.lower().strip()

    standardizations = {
        "tablespoon": "tbsp", "tablespoons": "tbsp",
        "teaspoon": "tsp", "teaspoons": "tsp",
        "cup": "cups",
        "gram": "g", "grams": "g",
        "kilogram": "kg", "kilograms": "kg",
        "milligram": "mg", "milligrams": "mg",
        "liter": "l", "liters": "l",
        "milliliter": "ml", "milliliters": "ml",
        "ounce": "oz", "ounces": "oz",
        "pound": "lb", "pounds": "lb",
        "fluid ounce": "fl oz", "fluid ounces": "fl oz",
        "piece": "pieces",
        "unit": "units",
        "clove": "cloves",
        "slice": "slices",
        "bunch": "bunches",
        "pinch": "pinches",
        "sprig": "sprigs",
        "head": "heads",
        "stalk": "stalks",
        "leaf": "leaves",
        "can": "cans",
        "packet": "packets",
    }

    return standardizations.get(unit, unit)
