import json
from utils.normalizer import normalize_ingredient, normalize_ingredient_list


def load_recipes():
    """Load recipes from JSON file"""
    try:
        with open('data/recipes.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('recipes', [])
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        return []


def load_substitutes():
    """Load ingredient substitutes from JSON file"""
    try:
        with open('data/substitutes.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('substitutes', {})
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        return {}


def calculate_match_score(user_ingredients, recipe):
    """
    IMPROVED: Calculate how well user ingredients match a recipe
    Now prioritizes recipes that can be made with what user has
    """
    # Extract all recipe ingredients
    mandatory = [normalize_ingredient(i['name']) for i in recipe['ingredients']['mandatory']]
    optional = [normalize_ingredient(i['name']) for i in recipe['ingredients']['optional']]
    
    mandatory_set = set(mandatory)
    optional_set = set(optional)
    user_set = set(user_ingredients)
    
    # Calculate matches
    matched_mandatory = user_set & mandatory_set
    matched_optional = user_set & optional_set
    matched_total = matched_mandatory | matched_optional
    
    missing_mandatory = mandatory_set - user_set
    missing_optional = optional_set - user_set
    
    # NEW SCORING LOGIC
    # Base score: How many of user's ingredients are used
    total_recipe_ingredients = len(mandatory_set) + len(optional_set)
    
    if total_recipe_ingredients == 0:
        match_percentage = 0
    else:
        # Calculate what % of the recipe the user can make
        ingredient_coverage = (len(matched_total) / total_recipe_ingredients) * 100
        
        # HUGE bonus if ALL mandatory ingredients are met
        if len(missing_mandatory) == 0:
            mandatory_bonus = 50  # Big boost!
        else:
            # Penalty for each missing mandatory ingredient
            mandatory_penalty = len(missing_mandatory) * 15
            mandatory_bonus = -mandatory_penalty
        
        # Small bonus for optional matches
        optional_bonus = len(matched_optional) * 5
        
        # Calculate final score
        match_percentage = ingredient_coverage + mandatory_bonus + optional_bonus
        match_percentage = max(0, min(100, match_percentage))  # Clamp between 0-100
    
    return {
        'score': round(match_percentage, 1),
        'matched': list(matched_total),
        'missing_mandatory': list(missing_mandatory),
        'missing_optional': list(missing_optional),
        'has_all_mandatory': len(missing_mandatory) == 0,
        'can_make_now': len(missing_mandatory) == 0  # NEW: Can user make this right now?
    }


def find_matching_recipes(user_ingredients, dietary_filter=None, min_score=0):
    """
    IMPROVED: Find recipes that match user ingredients
    Now shows recipes even with just 1-2 ingredients
    """
    # Normalize user ingredients
    user_ingredients = normalize_ingredient_list(user_ingredients)
    
    # Load recipes
    recipes = load_recipes()
    
    if not recipes:
        return []
    
    # Calculate matches for each recipe
    results = []
    for recipe in recipes:
        # Apply dietary filter
        if dietary_filter and recipe['type'] != dietary_filter:
            continue
        
        match_info = calculate_match_score(user_ingredients, recipe)
        
        # CHANGED: Show ALL recipes, even with low scores
        # Users can see what they're missing
        result = {
            **recipe,
            'match_info': match_info
        }
        results.append(result)
    
    # Sort by:
    # 1. Can make NOW (all mandatory met) - these come first
    # 2. Then by match score
    results.sort(key=lambda x: (
        x['match_info']['can_make_now'],  # True comes before False
        x['match_info']['score']
    ), reverse=True)
    
    return results


def get_substitutes_for_ingredient(ingredient):
    """Get substitutes for a given ingredient"""
    substitutes_db = load_substitutes()
    normalized = normalize_ingredient(ingredient)
    return substitutes_db.get(normalized, [])