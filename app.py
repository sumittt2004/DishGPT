import streamlit as st
from utils.matcher import find_matching_recipes, get_substitutes_for_ingredient
from utils.normalizer import normalize_ingredient_list
from utils.ai_helper import generate_ai_recipes

# Page configuration
st.set_page_config(
    page_title="DishGPT - Smart Recipe Builder",
    page_icon="🍳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# FIXED CSS - WORKS WITH BOTH LIGHT AND DARK MODE
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap');
    
    .main {
        background-color: #0e1117;
    }
    
    .main-header {
        font-size: 4rem;
        font-weight: 700;
        text-align: center;
        color: #FF6B6B;
        margin-bottom: 0.5rem;
        text-shadow: 0 0 30px rgba(255, 107, 107, 0.5);
    }
    
    .sub-header {
        font-size: 1.4rem;
        text-align: center;
        color: #FFD93D;
        margin-bottom: 2rem;
        font-weight: 500;
    }
    
    /* Recipe Cards */
    .recipe-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.8rem;
        border-radius: 15px;
        margin-bottom: 1.5rem;
        box-shadow: 0 10px 40px rgba(102, 126, 234, 0.3);
        color: white;
    }
    
    .recipe-card h2 {
        color: white !important;
        font-size: 2rem;
        margin-bottom: 1rem;
    }
    
    .ai-badge {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        padding: 0.4rem 1rem;
        border-radius: 20px;
        font-weight: 700;
        font-size: 0.9rem;
        display: inline-block;
        margin-left: 0.5rem;
    }
    
    /* Match Badge */
    .match-badge {
        background: #FFD93D;
        color: #000;
        padding: 0.6rem 1.5rem;
        border-radius: 25px;
        font-size: 1.4rem;
        font-weight: 700;
        display: inline-block;
        box-shadow: 0 4px 15px rgba(255, 217, 61, 0.5);
    }
    
    .can-make-badge {
        background: #6BCF7F;
        color: white;
        padding: 0.6rem 1.5rem;
        border-radius: 25px;
        font-weight: 700;
        font-size: 1.2rem;
        display: inline-block;
        box-shadow: 0 4px 15px rgba(107, 207, 127, 0.5);
    }
    
    /* Ingredient Pills */
    .ing-pill {
        display: inline-block;
        padding: 0.5rem 1.2rem;
        margin: 0.3rem;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.95rem;
    }
    
    .ing-have {
        background: #6BCF7F;
        color: white;
        box-shadow: 0 3px 10px rgba(107, 207, 127, 0.4);
    }
    
    .ing-need-mandatory {
        background: #FF6B6B;
        color: white;
        box-shadow: 0 3px 10px rgba(255, 107, 107, 0.4);
    }
    
    .ing-need-optional {
        background: #FFD93D;
        color: #000;
        box-shadow: 0 3px 10px rgba(255, 217, 61, 0.4);
    }
    
    /* Feature Cards - FIXED */
    .feature-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2.5rem 1.5rem;
        border-radius: 15px;
        text-align: center;
        color: white;
        box-shadow: 0 8px 30px rgba(102, 126, 234, 0.3);
        margin: 1rem 0;
        min-height: 200px;
    }
    
    .feature-box h3 {
        color: white !important;
        font-size: 1.5rem;
        margin: 1rem 0;
    }
    
    .feature-box p {
        color: rgba(255,255,255,0.9);
        font-size: 1.1rem;
    }
    
    .feature-emoji {
        font-size: 3rem;
        margin-bottom: 0.5rem;
    }
    
    /* Section Headers */
    .section-header {
        color: #FFD93D;
        font-size: 2rem;
        font-weight: 700;
        margin: 2rem 0 1rem 0;
        border-bottom: 3px solid #FFD93D;
        padding-bottom: 0.5rem;
    }
    
    /* Info Pills */
    .info-pill {
        background: #667eea;
        color: white;
        padding: 0.4rem 1rem;
        border-radius: 15px;
        display: inline-block;
        margin: 0.2rem;
        font-weight: 600;
    }
    </style>
    """, unsafe_allow_html=True)


def main():
    # Header
    st.markdown('<div class="main-header">🍳 DishGPT</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">✨ Cook delicious meals with what you already have! ✨</div>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown("## 📝 Your Kitchen")
        
        user_input = st.text_area(
            "What ingredients do you have?",
            placeholder="chicken, rice\negg, bread\ntomato, onion",
            height=120,
            help="Enter any ingredients - even just 1 or 2!"
        )
        
        dietary_filter = st.selectbox(
            "🥗 Dietary Preference",
            options=["All Recipes", "Vegetarian Only", "Non-Vegetarian Only"],
            index=0
        )
        
        filter_map = {
            "All Recipes": None,
            "Vegetarian Only": "veg",
            "Non-Vegetarian Only": "non-veg"
        }
        selected_filter = filter_map[dietary_filter]
        
        # AI Toggle
        use_ai = st.checkbox("🤖 Use AI for more recipes", value=True, help="Generate additional recipes using AI")
        
        search_button = st.button("🔍 Find Recipes", use_container_width=True, type="primary")
        
        st.markdown("---")
        st.success("### 💡 How it works\n\n✅ Enter 1+ ingredients\n\n✅ See recipes you can make NOW\n\n✅ Get shopping list for others\n\n✅ Smart substitutes included")
        
        st.markdown("---")
        st.info("### 📊 Database\n\n**18 recipes** loaded!\n\n🤖 **AI:** " + ("Enabled" if use_ai else "Disabled"))
    
    # Main content
    if search_button and user_input.strip():
        ingredients = normalize_ingredient_list(user_input)
        
        if not ingredients:
            st.warning("⚠️ Please enter at least one ingredient!")
            return
        
        # Display entered ingredients
        st.markdown('<div class="section-header">🛒 Your Ingredients</div>', unsafe_allow_html=True)
        
        ing_html = ""
        for ing in ingredients:
            ing_html += f'<span class="ing-pill ing-have">✓ {ing.title()}</span>'
        st.markdown(ing_html, unsafe_allow_html=True)
        
        st.markdown("<br><br>", unsafe_allow_html=True)
        
        # Search database recipes
        with st.spinner("🔎 Searching database recipes..."):
            db_recipes = find_matching_recipes(
                user_ingredients=ingredients,
                dietary_filter=selected_filter,
                min_score=0
            )
        
        # Generate AI recipes if enabled
        ai_recipes = []
        if use_ai:
            with st.spinner("🤖 AI is generating custom recipes for you..."):
                ai_recipes = generate_ai_recipes(
                    user_ingredients=ingredients,
                    dietary_filter=selected_filter,
                    num_recipes=2
                )
                
                if ai_recipes:
                    st.success(f"✨ AI generated {len(ai_recipes)} custom recipe(s)!")
        
        # Combine all recipes
        all_recipes = db_recipes + ai_recipes
        
        if all_recipes:
            # Separate recipes
            can_make = [r for r in all_recipes if r.get('match_info', {}).get('can_make_now', False)]
            need_more = [r for r in all_recipes if not r.get('match_info', {}).get('can_make_now', False)]
            
            if can_make:
                st.markdown(f'<div class="section-header">🎉 Ready to Cook! ({len(can_make)} recipes)</div>', unsafe_allow_html=True)
                for idx, recipe in enumerate(can_make):
                    is_ai = recipe.get('id', 0) >= 100
                    display_recipe_card(recipe, ingredients, idx, can_make_now=True, is_ai_generated=is_ai)
            
            if need_more:
                st.markdown(f'<div class="section-header">🛍️ Need a Few More Items ({len(need_more)} recipes)</div>', unsafe_allow_html=True)
                for idx, recipe in enumerate(need_more[:10]):
                    is_ai = recipe.get('id', 0) >= 100
                    display_recipe_card(recipe, ingredients, idx, can_make_now=False, is_ai_generated=is_ai)
        else:
            st.error("😔 No recipes found with those ingredients!")
            st.info("💡 **Tip:** Try enabling AI or use more common ingredients like rice, egg, chicken, etc.")
    
    elif search_button:
        st.warning("⚠️ Please enter ingredients first!")
    
    else:
        # Welcome screen
        st.markdown("<br>", unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            <div class="feature-box">
                <div class="feature-emoji">🎯</div>
                <h3>Smart Matching</h3>
                <p>Enter 1-2 ingredients and see what you can make right now!</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="feature-box">
                <div class="feature-emoji">🤖</div>
                <h3>AI Powered</h3>
                <p>AI generates custom recipes for ANY ingredient combo!</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div class="feature-box">
                <div class="feature-emoji">👨‍🍳</div>
                <h3>Easy Steps</h3>
                <p>Clear, beginner-friendly cooking instructions</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("<br><br>", unsafe_allow_html=True)
        
        # Example
        st.markdown('<div class="section-header">📚 Try These Examples</div>', unsafe_allow_html=True)
        
        ex_col1, ex_col2, ex_col3 = st.columns(3)
        
        with ex_col1:
            st.info("**Try:** `chicken, rice`\n\n→ Database + AI recipes")
        
        with ex_col2:
            st.info("**Try:** `peanut butter, banana`\n\n→ AI will create recipes!")
        
        with ex_col3:
            st.info("**Try:** `egg, bread`\n\n→ Quick breakfast options")


def display_recipe_card(recipe, user_ingredients, index, can_make_now=False, is_ai_generated=False):
    """Display recipe card"""
    
    # For AI recipes, calculate match info if not present
    if 'match_info' not in recipe:
        from utils.matcher import calculate_match_score
        match_info = calculate_match_score(user_ingredients, recipe)
        recipe['match_info'] = match_info
    else:
        match_info = recipe['match_info']
    
    score = match_info.get('score', 0)
    
    # Card header
    st.markdown(f"""
    <div class="recipe-card">
        <h2>{"✅ " if can_make_now else "🔸 "}{recipe['name']}{' <span class="ai-badge">🤖 AI</span>' if is_ai_generated else ''}</h2>
    </div>
    """, unsafe_allow_html=True)
    
    # Info row
    col1, col2, col3, col4 = st.columns([3, 1, 1, 2])
    
    with col1:
        st.markdown(f"<span class='info-pill'>🌍 {recipe.get('cuisine', 'N/A')}</span> <span class='info-pill'>🥗 {recipe['type'].title()}</span> <span class='info-pill'>📊 {recipe.get('difficulty', 'easy').title()}</span>", unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"⏱️ **{recipe.get('prep_time', 'N/A')}**")
    
    with col3:
        st.markdown(f"🔥 **{recipe.get('cook_time', 'N/A')}**")
    
    with col4:
        if can_make_now:
            st.markdown('<span class="can-make-badge">✓ MAKE IT NOW!</span>', unsafe_allow_html=True)
        else:
            st.markdown(f'<span class="match-badge">{score}% Match</span>', unsafe_allow_html=True)
    
    # Ingredients
    with st.expander("📋 **Ingredients Breakdown**", expanded=can_make_now):
        col_have, col_need = st.columns(2)
        
        with col_have:
            st.markdown("### ✅ You Have")
            matched = match_info.get('matched', [])
            if matched:
                html = ""
                for ing in matched:
                    html += f'<span class="ing-pill ing-have">✓ {ing.title()}</span>'
                st.markdown(html, unsafe_allow_html=True)
            else:
                st.write("_(None)_")
        
        with col_need:
            st.markdown("### 🛒 You Need")
            missing_mandatory = match_info.get('missing_mandatory', [])
            missing_optional = match_info.get('missing_optional', [])
            
            if missing_mandatory:
                st.markdown("**MUST HAVE:**")
                for ing in missing_mandatory:
                    st.markdown(f'<span class="ing-pill ing-need-mandatory">⚠️ {ing.title()}</span>', unsafe_allow_html=True)
                    subs = get_substitutes_for_ingredient(ing)
                    if subs:
                        st.caption(f"   → Or use: {', '.join(subs[:3])}")
            
            if missing_optional:
                st.markdown("**OPTIONAL:**")
                for ing in missing_optional:
                    st.markdown(f'<span class="ing-pill ing-need-optional">○ {ing.title()}</span>', unsafe_allow_html=True)
                    subs = get_substitutes_for_ingredient(ing)
                    if subs:
                        st.caption(f"   → Or: {', '.join(subs[:3])}")
            
            if not missing_mandatory and not missing_optional:
                st.success("🎉 You have everything!")
    
    # Instructions
    with st.expander("👨‍🍳 **Cooking Instructions**"):
        instructions = recipe.get('instructions', [])
        for i, step in enumerate(instructions, 1):
            st.markdown(f"**Step {i}:** {step}")
    
    st.markdown("<br>", unsafe_allow_html=True)


if __name__ == "__main__":
    main()