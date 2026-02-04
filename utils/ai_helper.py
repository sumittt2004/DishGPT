import json
import os
from typing import List, Dict, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Try to import Google Gemini
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    print("⚠️ Google Generative AI not installed. Run: pip install google-generativeai")


def initialize_gemini():
    """Initialize Gemini AI with API key"""
    if not GEMINI_AVAILABLE:
        print("❌ Gemini library not available")
        return None
    
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("❌ GEMINI_API_KEY not found in .env file")
        return None
    
    try:
        genai.configure(api_key=api_key)
        # Try multiple model names in order of preference
        model_names = [
            'gemini-pro',           # Standard Gemini Pro
            'models/gemini-pro',    # With models/ prefix
            'gemini-1.0-pro'        # Alternative name
        ]
        
        model = None
        for model_name in model_names:
            try:
                model = genai.GenerativeModel(model_name)
                print(f"✅ Gemini initialized successfully with model: {model_name}")
                return model
            except Exception as e:
                print(f"⚠️ Failed to load {model_name}: {e}")
                continue
        
        if not model:
            print("❌ Could not initialize any Gemini model")
            return None
            
    except Exception as e:
        print(f"❌ Gemini initialization error: {e}")
        return None


def generate_ai_recipes(
    user_ingredients: List[str],
    dietary_filter: Optional[str] = None,
    num_recipes: int = 2
) -> List[Dict]:
    """
    Generate recipes using Google Gemini AI
    
    Args:
        user_ingredients: List of ingredients the user has
        dietary_filter: 'veg' or 'non-veg' or None
        num_recipes: Number of recipes to generate
        
    Returns:
        List of recipe dictionaries
    """
    
    print(f"\n🤖 AI Recipe Generation Started")
    print(f"   Ingredients: {user_ingredients}")
    print(f"   Dietary Filter: {dietary_filter}")
    
    # Initialize Gemini
    model = initialize_gemini()
    
    if not model:
        print("❌ AI model not available - skipping AI generation")
        return []
    
    # Create prompt
    prompt = create_recipe_prompt(user_ingredients, dietary_filter, num_recipes)
    
    print(f"📝 Sending prompt to AI...")
    
    try:
        # Call Gemini API
        response = model.generate_content(prompt)
        
        print(f"✅ AI Response received!")
        print(f"   Raw response length: {len(response.text)} characters")
        
        # Parse response
        recipes = parse_ai_response(response.text)
        
        print(f"📊 Parsed {len(recipes)} recipes from AI response")
        
        # Validate recipes
        valid_recipes = []
        for i, recipe in enumerate(recipes):
            if validate_recipe(recipe):
                print(f"   ✅ Recipe {i+1}: {recipe.get('name', 'Unknown')} - Valid")
                valid_recipes.append(recipe)
            else:
                print(f"   ❌ Recipe {i+1}: Invalid structure")
        
        return valid_recipes[:num_recipes]
        
    except Exception as e:
        print(f"❌ AI generation error: {str(e)}")
        import traceback
        traceback.print_exc()
        return []


def create_recipe_prompt(user_ingredients: List[str], dietary_filter: Optional[str] = None, num_recipes: int = 2) -> str:
    """
    Create optimized prompt for AI recipe generation
    """
    
    ingredients_str = ", ".join(user_ingredients)
    
    dietary_instruction = ""
    if dietary_filter == "veg":
        dietary_instruction = "\nIMPORTANT: All recipes MUST be VEGETARIAN (no meat, fish, or eggs)."
    elif dietary_filter == "non-veg":
        dietary_instruction = "\nRecipes can include meat, fish, or eggs."
    
    prompt = f"""You are a professional chef. Create {num_recipes} delicious, practical recipes using these ingredients: {ingredients_str}
{dietary_instruction}

RULES:
1. Use AS MANY of the user's ingredients as possible
2. Assume basic pantry items exist: salt, pepper, oil, water, sugar
3. Keep additional ingredients to MAX 3-4 items
4. Recipes must be realistic and cookable
5. Instructions must be clear step-by-step

CRITICAL: Return ONLY valid JSON in this EXACT format with NO additional text, NO markdown, NO code blocks:

{{
  "recipes": [
    {{
      "id": 100,
      "name": "Creative Recipe Name",
      "cuisine": "Asian/Indian/Italian/Continental/etc",
      "type": "veg",
      "prep_time": "10 mins",
      "cook_time": "15 mins",
      "servings": 2,
      "ingredients": {{
        "mandatory": [
          {{"name": "ingredient1", "amount": "200g", "category": "protein"}},
          {{"name": "ingredient2", "amount": "1 cup", "category": "grain"}}
        ],
        "optional": [
          {{"name": "ingredient3", "amount": "1 tsp", "category": "spice"}}
        ]
      }},
      "substitutes": {{
        "ingredient1": ["substitute1", "substitute2"]
      }},
      "instructions": [
        "Step 1: Do this specific action",
        "Step 2: Do that specific action",
        "Step 3: Continue with details"
      ],
      "tags": ["quick", "easy"],
      "difficulty": "easy"
    }}
  ]
}}

Generate {num_recipes} complete recipes now:"""
    
    return prompt


def parse_ai_response(response_text: str) -> List[Dict]:
    """
    Parse AI response and extract recipes
    """
    
    try:
        # Clean the response
        text = response_text.strip()
        
        print(f"🔍 Parsing AI response...")
        print(f"   First 200 chars: {text[:200]}")
        
        # Remove markdown code blocks if present
        if '```json' in text:
            text = text.split('```json')[1].split('```')[0]
            print(f"   Removed ```json markers")
        elif '```' in text:
            text = text.split('```')[1].split('```')[0]
            print(f"   Removed ``` markers")
        
        text = text.strip()
        
        # Find JSON object
        start_idx = text.find('{')
        end_idx = text.rfind('}') + 1
        
        if start_idx == -1 or end_idx == 0:
            print(f"❌ No JSON found in response")
            return []
        
        json_str = text[start_idx:end_idx]
        
        print(f"   Extracted JSON length: {len(json_str)} chars")
        
        # Parse JSON
        data = json.loads(json_str)
        
        recipes = data.get('recipes', [])
        print(f"   Found {len(recipes)} recipes in JSON")
        
        return recipes
        
    except json.JSONDecodeError as e:
        print(f"❌ JSON parse error: {e}")
        print(f"   Failed to parse: {text[:500]}")
        return []
    except Exception as e:
        print(f"❌ Parse error: {e}")
        return []


def validate_recipe(recipe: Dict) -> bool:
    """
    Validate that a recipe has all required fields
    """
    
    required_fields = ['name', 'cuisine', 'type', 'ingredients', 'instructions']
    
    # Check all required fields exist
    for field in required_fields:
        if field not in recipe:
            print(f"   Missing field: {field}")
            return False
    
    # Check ingredients structure
    if 'mandatory' not in recipe.get('ingredients', {}):
        print(f"   Missing mandatory ingredients")
        return False
    
    # Check instructions is a list
    if not isinstance(recipe.get('instructions'), list):
        print(f"   Instructions not a list")
        return False
    
    # Check recipe type is valid
    if recipe.get('type') not in ['veg', 'non-veg']:
        print(f"   Invalid type: {recipe.get('type')}")
        return False
    
    return True