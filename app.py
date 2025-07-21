from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import requests
import logging
import json
import os
from dotenv import load_dotenv
import traceback

# Load environment variables
load_dotenv()

# Import grocery functions with error handling
try:
    from grocery import (get_recipe_ingredients, add_ingredients_to_grocery_list,
                        show_grocery_list, show_pantry, add_to_pantry,
                        remove_from_grocery_list, save_grocery_list,
                        gemini_nlp_analysis, process_natural_language, grocery_list, pantry_items,
                        get_ingredient_image)
except Exception as e:
    # Log the error but continue loading the app
    print(f"Error importing grocery module: {e}")
    traceback.print_exc()
    # Define fallback functions and variables
    grocery_list = {}
    pantry_items = {}
    def process_natural_language(text):
        return {"intent": "unknown"}
    def gemini_nlp_analysis(text):
        return process_natural_language(text)
    # Define other required functions as simple placeholders
    def get_recipe_ingredients(*args, **kwargs):
        return None, None, None
    def add_ingredients_to_grocery_list(*args, **kwargs):
        return []
    def show_grocery_list():
        return "Grocery list functionality unavailable"
    def show_pantry():
        return "Pantry functionality unavailable"
    def add_to_pantry(*args, **kwargs):
        pass
    def remove_from_grocery_list(*args, **kwargs):
        return "Remove functionality unavailable"
    def save_grocery_list(*args, **kwargs):
        return "Save functionality unavailable"
    def get_ingredient_image(*args, **kwargs):
        return None

SPOONACULAR_API_KEY = os.getenv("SPOONACULAR_API_KEY", "7349df0f8e3e45d49294fecf92ed56de")
SPOONACULAR_API_URL = "https://api.spoonacular.com/recipes"

app = Flask(__name__)
CORS(app)  # Allow CORS for all routes

# Configure limiter with a more Vercel-friendly setup
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)

# Configure logging for Vercel
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def load_saved_data():
    """Load grocery list and pantry items from persistent storage"""
    try:
        with open('grocery_data.json', 'r') as f:
            data = json.load(f)
            return data.get('grocery_list', {}), data.get('pantry_items', {})
    except FileNotFoundError:
        return {}, {}
    except Exception as e:
        logger.error(f"Error loading saved data: {e}")
        return {}, {}

# Initialize with saved data if available
try:
    saved_grocery_list, saved_pantry_items = load_saved_data()
    if saved_grocery_list:
        grocery_list.update(saved_grocery_list)
    if saved_pantry_items:
        pantry_items.update(saved_pantry_items)
except Exception as e:
    logger.error(f"Error initializing data: {e}")

@app.route('/api/chat', methods=['POST'])
@limiter.limit("10 per minute")
def chat():
    user_input = request.json.get('message', '').strip()
    if not user_input:
        return jsonify({"error": "Empty message"}), 400

    try:
        # First try with Gemini NLP, fall back to basic pattern matching
        try:
            nlp_result = gemini_nlp_analysis(user_input)
        except Exception as e:
            logger.error(f"Gemini NLP error: {e}")
            nlp_result = process_natural_language(user_input)
            
        response = {
            "intent": nlp_result["intent"],
            "text": "",
            "products": [],
            "productsTitle": "",
            "recipe_image": None,
            "ingredients": []
        }

        if nlp_result["intent"] == "add_recipe":
            food_item = nlp_result.get("food_item", "")
            servings = nlp_result.get("servings", 2)
            ingredients, recipe_title, recipe_image = get_recipe_ingredients(food_item, servings)
            
            if ingredients:
                response["text"] = f"Found recipe: {recipe_title}\nIngredients required for {servings} servings:"
                response["recipe_image"] = recipe_image
                response["recipe_title"] = recipe_title
                
                for ingredient in ingredients:
                    response["ingredients"].append({
                        "name": ingredient["name"],
                        "amount": ingredient["amount"],
                        "unit": ingredient["unit"],
                        "image": ingredient.get("image")
                    })
                    response["text"] += f"\n- {ingredient['amount']:.2f} {ingredient['unit']} of {ingredient['name']}"
                
                added_items = add_ingredients_to_grocery_list(ingredients)
                if added_items:
                    response["text"] += "\n\nAdded to grocery list:"
                    for item in added_items:
                        response["text"] += f"\n- {item}"
            else:
                response["text"] = f"Could not find a recipe for {food_item}."

        elif nlp_result["intent"] == "add_item":
            item = nlp_result.get("item", "")
            amount = nlp_result.get("amount", 1)
            unit = nlp_result.get("unit", "unit")
            image_url = get_ingredient_image(item)
            
            if item in grocery_list:
                grocery_list[item]["amount"] += amount
                if image_url and "image" not in grocery_list[item]:
                    grocery_list[item]["image"] = image_url
                response["text"] = f"Added more {item} to your grocery list."
            else:
                grocery_list[item] = {
                    "amount": amount,
                    "unit": unit,
                    "image": image_url
                }
                response["text"] = f"Added {amount} {unit} of {item} to your grocery list."
            
            response["products"].append({
                "name": item,
                "amount": amount,
                "unit": unit,
                "image": image_url
            })

        elif nlp_result["intent"] == "add_pantry":
            item = nlp_result.get("item", "")
            amount = nlp_result.get("amount", 1)
            unit = nlp_result.get("unit", "unit")
            add_to_pantry(item, amount, unit)
            response["text"] = f"Added {amount} {unit} of {item} to your pantry."
            
            if item in grocery_list:
                if grocery_list[item]["unit"] == unit:
                    if grocery_list[item]["amount"] <= amount:
                        del grocery_list[item]
                        response["text"] += f"\nRemoved {item} from your grocery list since you now have it in your pantry."
                    else:
                        grocery_list[item]["amount"] -= amount
                        response["text"] += f"\nUpdated grocery list: now you need {grocery_list[item]['amount']:.2f} {unit} of {item}."

        elif nlp_result["intent"] == "remove_item":
            item = nlp_result.get("item", "")
            amount = nlp_result.get("amount", None)
            response["text"] = remove_from_grocery_list(item, amount)

        elif nlp_result["intent"] == "show_list":
            response["text"] = show_grocery_list()
            for item, details in grocery_list.items():
                response["products"].append({
                    "name": item,
                    "amount": details["amount"],
                    "unit": details["unit"],
                    "image": details.get("image", None)
                })
            response["productsTitle"] = "Your Grocery List"

        elif nlp_result["intent"] == "show_pantry":
            response["text"] = show_pantry()

        elif nlp_result["intent"] == "save_list":
            response["text"] = save_grocery_list()

        elif nlp_result["intent"] == "exit":
            response["text"] = "Thank you for using the Grocery AI Chatbot! Goodbye!"

        else:
            response["text"] = "I'm not sure what you want to do. Try asking me to add a recipe, add items to your list or pantry, or view your lists."

        return jsonify(response)

    except Exception as e:
        logger.error(f"Error processing chat request: {e}")
        logger.error(traceback.format_exc())
        return jsonify({"error": str(e), "text": "Sorry, there was an error processing your request."}), 500

@app.route('/api/grocery-list', methods=['GET'])
def get_grocery_list():
    return jsonify(grocery_list)

@app.route('/api/pantry', methods=['GET'])
def get_pantry():
    return jsonify(pantry_items)

@app.route('/api/add-to-cart', methods=['POST'])
def add_to_cart():
    try:
        item_data = request.json
        if not item_data:
            return jsonify({"error": "Invalid request data"}), 400

        item = item_data.get('item', '')
        amount = item_data.get('amount', 1)
        unit = item_data.get('unit', 'unit')
        image = item_data.get('image', None)

        if item in grocery_list:
            grocery_list[item]["amount"] += amount
            if image and "image" not in grocery_list[item]:
                grocery_list[item]["image"] = image
        else:
            grocery_list[item] = {"amount": amount, "unit": unit, "image": image}

        return jsonify({"status": "success", "grocery_list": grocery_list})
    except Exception as e:
        logger.error(f"Error adding to cart: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/clear-list', methods=['POST'])
def clear_list():
    try:
        global grocery_list
        grocery_list.clear()
        return jsonify({"status": "success", "message": "Grocery list cleared"})
    except Exception as e:
        logger.error(f"Error clearing list: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/save-data', methods=['POST'])
def save_data():
    """Save grocery list and pantry items to persistent storage"""
    try:
        with open('grocery_data.json', 'w') as f:
            json.dump({
                'grocery_list': grocery_list,
                'pantry_items': pantry_items
            }, f)
        return jsonify({"status": "success", "message": "Data saved successfully"})
    except Exception as e:
        logger.error(f"Error saving data: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/')
def index():
    try:
        return send_from_directory('.', 'index.html')
    except Exception as e:
        logger.error(f"Error serving index: {e}")
        return "Welcome to Grocery AI Chatbot API", 200

@app.route('/Images/<filename>')
def serve_image(filename):
    try:
        return send_from_directory('Images', filename)
    except Exception as e:
        logger.error(f"Error serving image {filename}: {e}")
        return "Image not found", 404

@app.route('/api/test', methods=['GET'])
def test_api():
    return jsonify({"status": "success", "message": "API is working!"})

# Add this back for local testing
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    app.run(debug=debug, host='0.0.0.0', port=port)
