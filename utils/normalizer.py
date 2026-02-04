import re

def normalize_ingredient(ingredient):
    """
    Normalize ingredient name for better matching
    
    Args:
        ingredient (str): Raw ingredient name
        
    Returns:
        str: Normalized ingredient name
    """
    if not ingredient:
        return ""
    
    # Convert to lowercase
    ingredient = ingredient.lower().strip()
    
    # Remove extra spaces
    ingredient = re.sub(r'\s+', ' ', ingredient)
    
    # Remove common suffixes (plurals, etc.)
    singular_mappings = {
        'tomatoes': 'tomato',
        'potatoes': 'potato',
        'onions': 'onion',
        'carrots': 'carrot',
        'peppers': 'pepper',
        'mushrooms': 'mushroom',
        'beans': 'bean',
        'peas': 'pea',
        'chickpeas': 'chickpea',
        'eggs': 'egg',
        'cloves': 'clove',
        'leaves': 'leaf'
    }
    
    if ingredient in singular_mappings:
        ingredient = singular_mappings[ingredient]
    
    # Remove common words that don't affect matching
    words_to_remove = ['fresh', 'dried', 'raw', 'cooked', 'chopped', 'diced', 
                       'sliced', 'minced', 'whole', 'ground', 'powdered',
                       'large', 'small', 'medium']
    
    for word in words_to_remove:
        ingredient = ingredient.replace(word, '').strip()
    
    # Clean up multiple spaces again
    ingredient = re.sub(r'\s+', ' ', ingredient)
    
    return ingredient


def normalize_ingredient_list(ingredients):
    """
    Normalize a list of ingredients
    
    Args:
        ingredients (list or str): List of ingredients or comma-separated string
        
    Returns:
        list: List of normalized ingredients
    """
    if isinstance(ingredients, str):
        # Split by comma if it's a string
        ingredients = [i.strip() for i in ingredients.split(',')]
    
    # Normalize each ingredient
    normalized = [normalize_ingredient(ing) for ing in ingredients]
    
    # Remove empty strings and duplicates while preserving order
    seen = set()
    result = []
    for ing in normalized:
        if ing and ing not in seen:
            seen.add(ing)
            result.append(ing)
    
    return result