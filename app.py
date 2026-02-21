"""
StyleSense – AI Fashion Advisor (Premium Edition - Fixed)
Enhanced with Stability AI Image-to-Image generation, batch processing, and advanced caching
Optimized for paid Gemini API tier and Stability AI REST API
"""

import streamlit as st
from google import genai
from google.genai import types
import groq
from PIL import Image
import os
import json
import base64
from io import BytesIO
from urllib.parse import urlencode
import time
from functools import lru_cache
from datetime import datetime, timedelta
import requests

# ============================================================================
# CONFIGURATION & CONSTANTS
# ============================================================================

# Currency map for different countries
CURRENCY_MAP = {
    "United States": {"symbol": "$", "code": "USD"},
    "India": {"symbol": "₹", "code": "INR"},
    "United Kingdom": {"symbol": "£", "code": "GBP"},
    "Eurozone": {"symbol": "€", "code": "EUR"},
    "Japan": {"symbol": "¥", "code": "JPY"},
    "Canada": {"symbol": "C$", "code": "CAD"},
    "Australia": {"symbol": "A$", "code": "AUD"},
}

# Color suggestions based on country, season, and occasion
COLOR_SUGGESTIONS = {
    "India": {
        "Summer": {
            "Casual": ["White", "Light Blue", "Cream", "Pastel Yellow"],
            "Wedding": ["Gold", "Red", "Maroon", "Emerald Green"],
            "Party": ["Bright Pink", "Purple", "Electric Blue", "Gold"],
            "Office": ["Navy Blue", "White", "Beige", "Light Gray"],
            "Festival": ["Red", "Gold", "Orange", "Multicolor"],
            "Date": ["Coral", "Peach", "Soft Pink", "Lavender"],
            "Traditional": ["Red", "Gold", "Maroon", "Deep Purple"],
            "Vacation": ["Turquoise", "Coral", "White", "Pastel Green"],
        },
        "Winter": {
            "Casual": ["Burgundy", "Navy", "Gray", "Mustard"],
            "Wedding": ["Gold", "Deep Red", "Maroon", "Royal Blue"],
            "Party": ["Black", "Gold", "Deep Purple", "Maroon"],
            "Office": ["Navy", "Gray", "Black", "Charcoal"],
            "Festival": ["Red", "Gold", "Orange", "Deep Purple"],
            "Date": ["Burgundy", "Deep Pink", "Plum", "Navy"],
            "Traditional": ["Red", "Gold", "Maroon", "Deep Purple"],
            "Vacation": ["Camel", "Burgundy", "Navy", "Gray"],
        },
        "Spring": {
            "Casual": ["Pastel Pink", "Mint Green", "Sky Blue", "Peach"],
            "Wedding": ["Gold", "Red", "Emerald", "Coral"],
            "Party": ["Bright Pink", "Purple", "Gold", "Turquoise"],
            "Office": ["Light Blue", "White", "Beige", "Sage Green"],
            "Festival": ["Orange", "Yellow", "Red", "Gold"],
            "Date": ["Soft Pink", "Lavender", "Peach", "Mint"],
            "Traditional": ["Red", "Gold", "Orange", "Maroon"],
            "Vacation": ["Turquoise", "Coral", "Mint", "Peach"],
        },
        "Autumn": {
            "Casual": ["Burnt Orange", "Olive Green", "Rust", "Chocolate"],
            "Wedding": ["Gold", "Deep Red", "Maroon", "Emerald"],
            "Party": ["Deep Purple", "Maroon", "Gold", "Black"],
            "Office": ["Brown", "Navy", "Gray", "Olive"],
            "Festival": ["Orange", "Red", "Gold", "Brown"],
            "Date": ["Rust", "Burgundy", "Deep Pink", "Plum"],
            "Traditional": ["Red", "Gold", "Maroon", "Orange"],
            "Vacation": ["Camel", "Rust", "Olive", "Brown"],
        },
        "Monsoon": {
            "Casual": ["Navy", "Gray", "Dark Green", "Charcoal"],
            "Wedding": ["Gold", "Red", "Maroon", "Royal Blue"],
            "Party": ["Deep Purple", "Black", "Gold", "Maroon"],
            "Office": ["Navy", "Gray", "Black", "Dark Green"],
            "Festival": ["Red", "Gold", "Orange", "Purple"],
            "Date": ["Deep Pink", "Plum", "Navy", "Burgundy"],
            "Traditional": ["Red", "Gold", "Maroon", "Purple"],
            "Vacation": ["Navy", "Gray", "Dark Green", "Charcoal"],
        },
    },
    "United States": {
        "Summer": {
            "Casual": ["White", "Light Blue", "Pastel", "Neutral"],
            "Wedding": ["White", "Blush", "Gold", "Navy"],
            "Party": ["Bright Colors", "Metallics", "Bold", "Neon"],
            "Office": ["Navy", "White", "Beige", "Gray"],
            "Festival": ["Bright", "Colorful", "Vibrant", "Pastels"],
            "Date": ["Pink", "Coral", "Peach", "Lavender"],
            "Traditional": ["Navy", "White", "Red", "Gold"],
            "Vacation": ["Turquoise", "Coral", "White", "Pastels"],
        },
        "Winter": {
            "Casual": ["Black", "Gray", "Burgundy", "Navy"],
            "Wedding": ["White", "Ivory", "Gold", "Navy"],
            "Party": ["Black", "Gold", "Burgundy", "Deep Purple"],
            "Office": ["Black", "Gray", "Navy", "Charcoal"],
            "Festival": ["Red", "Gold", "Green", "Silver"],
            "Date": ["Burgundy", "Deep Red", "Black", "Gold"],
            "Traditional": ["Navy", "White", "Red", "Gold"],
            "Vacation": ["Camel", "Gray", "Navy", "Black"],
        },
        "Spring": {
            "Casual": ["Pastel", "Mint", "Pink", "Yellow"],
            "Wedding": ["White", "Blush", "Gold", "Sage"],
            "Party": ["Bright", "Colorful", "Metallics", "Pastels"],
            "Office": ["Light Blue", "White", "Beige", "Sage"],
            "Festival": ["Bright", "Colorful", "Pastels", "Vibrant"],
            "Date": ["Pink", "Lavender", "Peach", "Mint"],
            "Traditional": ["Navy", "White", "Red", "Gold"],
            "Vacation": ["Turquoise", "Coral", "Mint", "Peach"],
        },
        "Autumn": {
            "Casual": ["Burnt Orange", "Brown", "Rust", "Olive"],
            "Wedding": ["Gold", "Burgundy", "Ivory", "Rust"],
            "Party": ["Deep Purple", "Maroon", "Gold", "Black"],
            "Office": ["Brown", "Navy", "Gray", "Olive"],
            "Festival": ["Orange", "Red", "Gold", "Brown"],
            "Date": ["Rust", "Burgundy", "Deep Red", "Plum"],
            "Traditional": ["Navy", "White", "Red", "Gold"],
            "Vacation": ["Camel", "Rust", "Olive", "Brown"],
        },
    },
    "United Kingdom": {
        "Summer": {
            "Casual": ["White", "Pastel", "Light Blue", "Cream"],
            "Wedding": ["White", "Blush", "Gold", "Navy"],
            "Party": ["Black", "Gold", "Metallics", "Bold"],
            "Office": ["Navy", "White", "Gray", "Beige"],
            "Festival": ["Bright", "Colorful", "Pastels", "Vibrant"],
            "Date": ["Pink", "Coral", "Lavender", "Peach"],
            "Traditional": ["Navy", "White", "Red", "Gold"],
            "Vacation": ["Turquoise", "Coral", "White", "Pastels"],
        },
        "Winter": {
            "Casual": ["Black", "Gray", "Navy", "Burgundy"],
            "Wedding": ["White", "Ivory", "Gold", "Navy"],
            "Party": ["Black", "Gold", "Deep Purple", "Burgundy"],
            "Office": ["Black", "Gray", "Navy", "Charcoal"],
            "Festival": ["Red", "Gold", "Green", "Silver"],
            "Date": ["Burgundy", "Deep Red", "Black", "Gold"],
            "Traditional": ["Navy", "White", "Red", "Gold"],
            "Vacation": ["Camel", "Gray", "Navy", "Black"],
        },
        "Spring": {
            "Casual": ["Pastel", "Mint", "Pink", "Lavender"],
            "Wedding": ["White", "Blush", "Gold", "Sage"],
            "Party": ["Bright", "Colorful", "Metallics", "Pastels"],
            "Office": ["Light Blue", "White", "Beige", "Sage"],
            "Festival": ["Bright", "Colorful", "Pastels", "Vibrant"],
            "Date": ["Pink", "Lavender", "Peach", "Mint"],
            "Traditional": ["Navy", "White", "Red", "Gold"],
            "Vacation": ["Turquoise", "Coral", "Mint", "Peach"],
        },
        "Autumn": {
            "Casual": ["Burnt Orange", "Brown", "Rust", "Olive"],
            "Wedding": ["Gold", "Burgundy", "Ivory", "Rust"],
            "Party": ["Deep Purple", "Maroon", "Gold", "Black"],
            "Office": ["Brown", "Navy", "Gray", "Olive"],
            "Festival": ["Orange", "Red", "Gold", "Brown"],
            "Date": ["Rust", "Burgundy", "Deep Red", "Plum"],
            "Traditional": ["Navy", "White", "Red", "Gold"],
            "Vacation": ["Camel", "Rust", "Olive", "Brown"],
        },
    },
}

# Shopping platform search URL patterns
SHOPPING_PLATFORMS = {
    "amazon": {
        "base_url": "https://www.amazon.in/s",
        "query_param": "k",
        "price_filter": "&rh=p_36:{min}-{max}",
    },
    "flipkart": {
        "base_url": "https://www.flipkart.com/search",
        "query_param": "q",
        "price_filter": "&p[]=facets.price_range.from:{min}&p[]=facets.price_range.to:{max}",
    },
    "ajio": {
        "base_url": "https://www.ajio.com/search",
        "query_param": "text",
        "price_filter": "&minPrice={min}&maxPrice={max}",
    },
    "meesho": {
        "base_url": "https://www.meesho.com/search",
        "query_param": "q",
        "price_filter": "&minPrice={min}&maxPrice={max}",
    },
}

# ============================================================================
# STABILITY AI IMAGE GENERATION FUNCTIONS
# ============================================================================

def generate_image_with_stability_ai(reference_image_bytes, costume_description, api_key, strength=0.7):
    """
    Generate an image using Stability AI's Image-to-Image API.
    
    Args:
        reference_image_bytes: The reference image as bytes
        costume_description: Text description of the desired costume/outfit
        api_key: Stability AI API key
        strength: How much influence the reference image has (0.0 to 1.0)
    
    Returns:
        PIL Image or None if generation fails
    """
    try:
        # Prepare the request
        url = "https://api.stability.ai/v2beta/stable-image/generate/core"
        
        headers = {
            "authorization": f"Bearer {api_key}",
            "accept": "image/*"
        }
        
        # Prepare the files for multipart/form-data
        files = {
            "image": ("reference_image.png", reference_image_bytes, "image/png"),
        }
        
        data = {
            "prompt": costume_description,
            "mode": "image-to-image",
            "strength": strength,
            "output_format": "png"
        }
        
        # Make the API request
        response = requests.post(url, headers=headers, files=files, data=data, timeout=60)
        
        if response.status_code == 200:
            # Return the generated image as PIL Image
            return Image.open(BytesIO(response.content))
        else:
            st.warning(f"Stability AI API error: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        st.error(f"Error generating image with Stability AI: {e}")
        return None


def generate_image_with_stability_sd35(reference_image_bytes, costume_description, api_key, strength=0.7, model="sd3.5-large"):
    """
    Generate an image using Stability AI's Stable Diffusion 3.5 Image-to-Image API.
    
    Args:
        reference_image_bytes: The reference image as bytes
        costume_description: Text description of the desired costume/outfit
        api_key: Stability AI API key
        strength: How much influence the reference image has (0.0 to 1.0)
        model: Model to use (sd3.5-large, sd3.5-large-turbo, sd3.5-medium, sd3.5-flash)
    
    Returns:
        PIL Image or None if generation fails
    """
    try:
        # Prepare the request
        url = "https://api.stability.ai/v2beta/stable-image/generate/sd3"
        
        headers = {
            "authorization": f"Bearer {api_key}",
            "accept": "image/*"
        }
        
        # Prepare the files for multipart/form-data
        files = {
            "image": ("reference_image.png", reference_image_bytes, "image/png"),
        }
        
        data = {
            "prompt": costume_description,
            "mode": "image-to-image",
            "model": model,
            "strength": strength,
            "output_format": "png"
        }
        
        # Make the API request
        response = requests.post(url, headers=headers, files=files, data=data, timeout=60)
        
        if response.status_code == 200:
            # Return the generated image as PIL Image
            return Image.open(BytesIO(response.content))
        else:
            st.warning(f"Stability AI SD3.5 API error: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        st.error(f"Error generating image with Stability AI SD3.5: {e}")
        return None


# ============================================================================
# UTILITY FUNCTIONS WITH CACHING
# ============================================================================

@lru_cache(maxsize=128)
def get_currency_symbol(country):
    """Get currency symbol based on country (cached)."""
    return CURRENCY_MAP.get(country, {"symbol": "$"})["symbol"]


@lru_cache(maxsize=256)
def get_color_suggestions(country, season, occasion):
    """Get color suggestions based on country, season, and occasion (cached)."""
    if country in COLOR_SUGGESTIONS:
        if season in COLOR_SUGGESTIONS[country]:
            if occasion in COLOR_SUGGESTIONS[country][season]:
                return tuple(COLOR_SUGGESTIONS[country][season][occasion])
    return ("Blue", "Black", "White", "Gray")


def generate_shopping_url(product_name, platform, budget_min, budget_max):
    """Generate shopping URL for a product on a specific platform."""
    if platform not in SHOPPING_PLATFORMS:
        return None
    
    platform_config = SHOPPING_PLATFORMS[platform]
    base_url = platform_config["base_url"]
    query_param = platform_config["query_param"]
    
    # Build URL with query parameter
    url = f"{base_url}?{query_param}={urlencode({'': product_name}).split('=')[1]}"
    
    # Add price filter if available
    if "price_filter" in platform_config:
        price_filter = platform_config["price_filter"].format(min=budget_min, max=budget_max)
        url += price_filter
    
    return url


def generate_shopping_urls(product_name, budget_min, budget_max):
    """Generate shopping URLs for a product across multiple platforms."""
    urls = {}
    for platform in SHOPPING_PLATFORMS.keys():
        urls[platform] = generate_shopping_url(product_name, platform, budget_min, budget_max)
    return urls


# ============================================================================
# STREAMLIT PAGE CONFIGURATION
# ============================================================================

st.set_page_config(layout="wide", page_title="StyleSense – AI Fashion Advisor (Premium)")

# Initialize session state for color selection
if "selected_color" not in st.session_state:
    st.session_state.selected_color = None

# --- API Configuration ---
try:
    from dotenv import load_dotenv
    load_dotenv()
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    STABILITY_API_KEY = os.getenv("STABILITY_API_KEY")
    
    # Initialize clients
    client = genai.Client(api_key=GEMINI_API_KEY)
    groq_client = groq.Groq(api_key=GROQ_API_KEY)
    
    # Premium model configuration
    # Note: Use model strings without 'models/' prefix for google-genai 0.5.0
    VISION_MODEL = "gemini-1.5-pro"  
    IMAGE_GEN_MODEL = "gemini-3-pro-image-preview"  
    GROQ_MODEL = "llama-3.3-70b-versatile"

except ImportError:
    st.error("The `google-genai` library is missing. Please install it with `pip install google-genai`")
    st.stop()
except Exception as e:
    st.error(f"API key configuration failed: {e}")
    st.stop()

# --- UI Styling ---
st.markdown('''
<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=Roboto:wght@300;400&display=swap');

    .stApp {
        background-color: #FDFBF7; /* Soft, elegant off-white */
    }

    h1, h2, h3, .st-emotion-cache-10trblm e1nzilvr1, .st-emotion-cache-1avcm0n e1nzilvr2, .st-emotion-cache-1c7y2kd e1f1d6gn0{
        font-family: 'Playfair Display', serif;
        color: #2C3A47; /* Muted, sophisticated dark blue */
    }

    .st-emotion-cache-1y4p8pa {
        padding-top: 2rem;
    }

    .st-b7, .st-emotion-cache-1v0mbdj e115fcil1, .st-emotion-cache-1r6slb0 e115fcil2, .st-emotion-cache-1kyxreq e115fcil2 {
        border-radius: 8px;
        border: 1px solid #EAEAEA;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    }

    .stButton>button {
        border-radius: 8px;
        background-color: #2C3A47;
        color: white;
        border: none;
        padding: 12px 24px;
        font-family: 'Roboto', sans-serif;
        font-weight: 400;
        transition: background-color 0.3s ease;
    }

    .stButton>button:hover {
        background-color: #475C7A;
    }

    .outfit-card {
        background: #FFFFFF;
        border-radius: 12px;
        padding: 2em;
        box-shadow: 0 10px 30px -15px rgba(0, 0, 0, 0.1);
        margin: 1.5em 0;
        border: 1px solid #F0F0F0;
    }

    .premium-badge {
        background: #2C3A47;
        color: white;
        padding: 0.6em 1.2em;
        border-radius: 50px;
        display: inline-block;
        font-family: 'Roboto', sans-serif;
        font-weight: 300;
        letter-spacing: 1px;
        text-transform: uppercase;
        font-size: 0.8em;
        margin-bottom: 1em;
    }

    .st-emotion-cache-10trblm e1nzilvr1, .st-emotion-cache-1avcm0n e1nzilvr2 {
        border-bottom: 2px solid #2C3A47;
    }

</style>
''', unsafe_allow_html=True)

# ============================================================================
# MAIN APPLICATION
# ============================================================================

st.markdown("<h1 style=\'text-align: center; color: #2C3A47;\'>StyleSense</h1>", unsafe_allow_html=True)
st.markdown("<p style=\'text-align: center; font-family: Roboto, sans-serif; color: #475C7A; margin-bottom: 0.5rem;\'>Your Personal AI Fashion Advisor</p>", unsafe_allow_html=True)
st.markdown("<div class=\'premium-badge\' style=\'text-align: center; margin: 0 auto 2rem auto;\'>✨ Premium Edition with Stability AI & 3D Nano Banana Pro</div>", unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.markdown("<h2 style=\'text-align: center;\'>Your Profile</h2>", unsafe_allow_html=True)
    
    with st.expander("Personal Details", expanded=True):
        gender = st.selectbox("Gender", ["Male", "Female", "Other"])
        age = st.select_slider("Age Range", options=['Baby (0–3)', 'Child (4–12)', 'Teen (13–19)', 'Adult (20–40)', 'Mature (40+)'])
        height = st.number_input("Height (cm)", min_value=50, max_value=250, value=170)
        body_size = st.select_slider("Body Size", options=['XS', 'S', 'M', 'L', 'XL', 'XXL'])
        skin_tone_manual = st.selectbox("Skin Tone", ["Fair", "Medium", "Dusky", "Dark"])
        fav_color = st.text_input("Favorite Color (optional)")

    with st.expander("Location & Occasion", expanded=True):
        country = st.selectbox("Country", list(CURRENCY_MAP.keys()))
        season = st.selectbox("Season", ["Summer", "Winter", "Spring", "Autumn", "Monsoon"])
        occasion = st.selectbox("Occasion", ["Casual", "Wedding", "Party", "Office", "Festival", "Date", "Traditional", "Vacation"])
        time_of_occasion = st.selectbox("Time of Occasion", ["Morning", "Afternoon", "Evening", "Night"])
        currency_symbol = get_currency_symbol(country)
        budget = st.slider(f"Budget Range ({currency_symbol})", min_value=50, max_value=5000, value=(100, 500))

    # --- Color Suggestions with Proper State Management ---
    st.markdown("<h3 style=\'text-align: center;\'>Color Suggestions</h3>", unsafe_allow_html=True)
    suggested_colors = get_color_suggestions(country, season, occasion)
    
    st.write(f"**Suggested colors for {season} {occasion} in {country}:**")
    
    # Display color suggestions as buttons with state
    color_cols = st.columns(len(suggested_colors))
    for idx, color in enumerate(suggested_colors):
        with color_cols[idx]:
            if st.button(color, key=f"color_{idx}", use_container_width=True):
                st.session_state.selected_color = color
                st.rerun()
    
    # Display selected color
    if st.session_state.selected_color:
        st.success(f"✨ Selected Color: **{st.session_state.selected_color}**")
    
    # Allow user to type custom color
    st.write("Or type your own color:")
    custom_color = st.text_input("Custom Color", key="custom_color_input")
    
    if custom_color:
        st.session_state.selected_color = custom_color
        st.success(f"✨ Selected Color: **{custom_color}**")
    
    # Final color selection logic
    final_color = st.session_state.selected_color if st.session_state.selected_color else fav_color

    uploaded_image = st.file_uploader("📸 Upload Your Image", type=['png', 'jpg', 'jpeg'])
    
    # Premium options
    st.markdown("<h3 style=\'text-align: center;\'>Premium Options</h3>", unsafe_allow_html=True)
    num_outfits = st.slider("Number of Outfit Variations", min_value=1, max_value=5, value=1)
    image_resolution = st.selectbox("Image Resolution", ["1K", "2K", "4K"], index=1)
    use_3d_render = st.checkbox("Generate 3D Renders (Nano Banana Pro)", value=True)
    use_stability_ai = st.checkbox("Use Stability AI for Reference-Based Generation", value=True)
    
    # Stability AI model selection
    if use_stability_ai:
        stability_model = st.selectbox(
            "Stability AI Model",
            ["core", "sd3.5-large", "sd3.5-large-turbo", "sd3.5-medium", "sd3.5-flash"],
            help="Select the model for image generation. SD3.5 models offer better quality but may be slower."
        )
        stability_strength = st.slider(
            "Reference Image Strength",
            min_value=0.0,
            max_value=1.0,
            value=0.7,
            step=0.1,
            help="Higher values preserve more of the reference image. Lower values allow more creative freedom."
        )

if st.button("Generate Outfit(s)", use_container_width=True):
    if uploaded_image is None:
        st.warning("Please upload an image to generate an outfit.")
    else:
        with st.spinner("🎨 Generating your personalized style..."):
            try:
                # --- AI Workflow ---
                # Step 1: Enhanced Gemini 2.0 Pro Vision Analysis
                image_bytes = uploaded_image.getvalue()
                image = Image.open(BytesIO(image_bytes))
                
                vision_prompt = """Analyze this image in detail:
                1. Determine the user's approximate skin tone (Fair, Medium, Dusky, Dark)
                2. Analyze body shape and proportions
                3. Identify current clothing style and preferences
                4. Note any distinctive features or style elements
                Provide a comprehensive analysis for fashion recommendations."""
                
                vision_analysis = "User provided image for styling."
                try:
                    st.info("🔍 Analyzing your image...")
                    vision_response = client.models.generate_content(
                        model=VISION_MODEL,
                        contents=[vision_prompt, image]
                    )
                    vision_analysis = vision_response.text
                    st.success("✅ Image analysis complete!")
                except Exception as vision_err:
                    st.warning(f"Vision analysis note: {vision_err}. Proceeding with user input only.")

                # Step 2: Generate Multiple Outfit Recommendations
                outfits_data = []
                
                st.info(f"📝 Generating {num_outfits} outfit recommendation(s)...")
                
                for outfit_num in range(num_outfits):
                    groq_prompt = f'''
                    Generate outfit recommendation #{outfit_num + 1} in JSON format for:
                    - Gender: {gender}
                    - Age: {age}
                    - Location: {country}, {season}
                    - Occasion: {occasion} at {time_of_occasion}
                    - Physical Details: {height}cm, {body_size}, {skin_tone_manual} skin tone
                    - Color Preference: {final_color if final_color else "No preference"}
                    - Budget: {currency_symbol}{budget[0]} - {currency_symbol}{budget[1]}
                    - Image Analysis: {vision_analysis}

                    Provide JSON with:
                    {{
                        "outfit_description": "Detailed outfit description",
                        "fabric_recommendation": "Suggested fabrics",
                        "suitability_reason": "Why this outfit suits the user",
                        "accessories_suggestion": "Recommended accessories",
                        "product_recommendations": [
                            {{"product_name": "Top", "estimated_price": "200", "category": "top"}},
                            {{"product_name": "Bottom", "estimated_price": "300", "category": "bottom"}},
                            {{"product_name": "Shoes", "estimated_price": "150", "category": "shoes"}},
                            {{"product_name": "Accessory", "estimated_price": "100", "category": "accessory"}}
                        ]
                    }}
                    '''
                    
                    try:
                        groq_response = groq_client.chat.completions.create(
                            messages=[{"role": "user", "content": groq_prompt}],
                            model=GROQ_MODEL,
                            temperature=0.7,
                            max_tokens=1024,
                            top_p=1,
                            stream=False,
                            response_format={"type": "json_object"}
                        )
                        recommendations = groq_response.choices[0].message.content
                        recommendations_json = json.loads(recommendations)
                        outfits_data.append(recommendations_json)
                    except Exception as groq_err:
                        st.warning(f"Outfit {outfit_num + 1} generation error: {groq_err}")

                st.success(f"✅ Generated {len(outfits_data)} outfit(s)!")

                # Step 3: Generate Images with Stability AI or Nano Banana Pro
                generated_images = []
                
                if use_stability_ai and STABILITY_API_KEY and len(outfits_data) > 0:
                    st.info("🎨 Generating outfit images with Stability AI...")
                    
                    for outfit_idx, outfit_rec in enumerate(outfits_data):
                        # Create detailed prompt for Stability AI
                        stability_prompt = f'''
                        Create a professional fashion outfit image based on this description:
                        
                        {outfit_rec["outfit_description"]}
                        
                        Details:
                        - Fabrics: {outfit_rec["fabric_recommendation"]}
                        - Accessories: {outfit_rec["accessories_suggestion"]}
                        - Color: {final_color if final_color else "neutral"}
                        - Style: Professional, polished, fashion-forward
                        - Background: Clean, minimalist white background
                        - Lighting: Professional studio lighting
                        '''
                        
                        try:
                            st.info(f"Generating outfit {outfit_idx + 1}/{len(outfits_data)} with Stability AI...")
                            
                            if stability_model.startswith("sd3.5"):
                                # Use SD3.5 model
                                generated_image = generate_image_with_stability_sd35(
                                    image_bytes,
                                    stability_prompt,
                                    STABILITY_API_KEY,
                                    strength=stability_strength,
                                    model=stability_model
                                )
                            else:
                                # Use Core model
                                generated_image = generate_image_with_stability_ai(
                                    image_bytes,
                                    stability_prompt,
                                    STABILITY_API_KEY,
                                    strength=stability_strength
                                )
                            
                            if generated_image:
                                generated_images.append(generated_image)
                                st.success(f"✅ Outfit {outfit_idx + 1} generated!")
                            else:
                                generated_images.append(None)
                                st.warning(f"⚠️ Could not generate outfit {outfit_idx + 1}")
                                
                        except Exception as img_err:
                            st.warning(f"Image generation for outfit {outfit_idx + 1}: {img_err}")
                            generated_images.append(None)
                
                elif use_3d_render and len(outfits_data) > 0:
                    st.info("🎨 Generating 3D fashion renders with Nano Banana Pro...")
                    
                    for outfit_idx, outfit_rec in enumerate(outfits_data):
                        # 3D Isometric Fashion Render Prompt
                        image_gen_prompt = f'''
                        Create a stunning 3D isometric fashion render showing a full-body model.
                        
                        Model Details:
                        - Gender: {gender}
                        - Age: {age}
                        - Skin tone: {skin_tone_manual}
                        - Height: {height}cm
                        - Body size: {body_size}
                        
                        Outfit Details:
                        - Description: {outfit_rec["outfit_description"]}
                        - Fabrics: {outfit_rec["fabric_recommendation"]}
                        - Accessories: {outfit_rec["accessories_suggestion"]}
                        
                        Scene Requirements:
                        - 3D isometric perspective (45° angle)
                        - Professional lighting with soft shadows
                        - Clean, minimalist background
                        - High-fidelity detail preservation
                        - Fashion magazine quality
                        - Render style: 3D miniature fashion scene
                        - Color palette: Emphasize {final_color if final_color else "neutral tones"}
                        
                        Style: Luxurious, professional 3D fashion illustration
                        '''
                        
                        try:
                            st.info(f"Rendering outfit {outfit_idx + 1}/{len(outfits_data)}...")
                            
                            # Optimized for google-genai 0.5.0 and paid tier
                            # Explicitly set response_modalities=["IMAGE"] to trigger image generation
                            image_response = client.models.generate_content(
                                model=IMAGE_GEN_MODEL,
                                contents=[image_gen_prompt],
                                config=types.GenerateContentConfig(
                                    response_modalities=["IMAGE"]
                                )
                            )
                            
                            # Extract generated image from inline_data parts
                            image_found = False
                            if hasattr(image_response, 'parts'):
                                for part in image_response.parts:
                                    if hasattr(part, 'inline_data') and part.inline_data:
                                        try:
                                            image_data = part.inline_data.data
                                            pil_image = Image.open(BytesIO(image_data))
                                            generated_images.append(pil_image)
                                            image_found = True
                                            st.success(f"✅ Outfit {outfit_idx + 1} rendered!")
                                            break
                                        except Exception as convert_err:
                                            st.warning(f"Could not process image data: {convert_err}")
                            
                            if not image_found:
                                st.warning(f"No image data found for outfit {outfit_idx + 1}")
                                generated_images.append(None)
                                
                        except Exception as img_err:
                            st.warning(f"Image generation for outfit {outfit_idx + 1}: {img_err}")
                            generated_images.append(None)
                else:
                    generated_images = [None] * len(outfits_data)

                # --- Display Results ---
                st.success("✨ All outfits ready!")
                
                with col2:
                    st.markdown("<h2 style=\'text-align: center;\'>Your Personalized Outfits</h2>", unsafe_allow_html=True)
                    
                    for outfit_idx, (outfit_rec, gen_image) in enumerate(zip(outfits_data, generated_images)):
                        st.markdown(f'<div class="outfit-card">', unsafe_allow_html=True)
                        st.markdown(f"<h3 style=\'text-align: center;\'>Outfit #{outfit_idx + 1}</h3>", unsafe_allow_html=True)
                        
                        if gen_image:
                            try:
                                st.image(gen_image, caption=f"Generated Outfit - {outfit_idx + 1}", use_container_width=True)
                            except Exception as display_err:
                                st.warning(f"Could not display image: {display_err}")
                        else:
                            st.info("📸 Visual recommendation based on your profile")
                        
                        st.write(f"**Outfit Description:**\n{outfit_rec.get('outfit_description', 'N/A')}")
                        st.write(f"**Why it suits you:**\n{outfit_rec.get('suitability_reason', 'N/A')}")
                        
                        col_fabric, col_accessories = st.columns(2)
                        with col_fabric:
                            st.write(f"**Fabric:** {outfit_rec.get('fabric_recommendation', 'N/A')}")
                        with col_accessories:
                            st.write(f"**Accessories:** {outfit_rec.get('accessories_suggestion', 'N/A')}")
                        
                        st.markdown("<h3 style=\'text-align: center;\'>Shop The Look</h3>", unsafe_allow_html=True)
                        for item in outfit_rec.get("product_recommendations", []):
                            try:
                                product_name = item.get("product_name", "Product")
                                price = item.get("estimated_price", "0")
                                
                                st.write(f"**{product_name}** ({currency_symbol}{price})")
                                
                                # Generate shopping links
                                shopping_urls = generate_shopping_urls(product_name, budget[0], budget[1])
                                
                                # Display shopping links
                                link_cols = st.columns(4)
                                platforms = ["amazon", "flipkart", "ajio", "meesho"]
                                for idx, platform in enumerate(platforms):
                                    with link_cols[idx]:
                                        if shopping_urls[platform]:
                                            st.markdown(f"[{platform.capitalize()}]({shopping_urls[platform]})", unsafe_allow_html=True)
                                
                                st.write("---")
                            except Exception as e:
                                st.warning(f"Error displaying product: {e}")
                        
                        st.markdown('</div>', unsafe_allow_html=True)

            except Exception as e:
                st.error(f"An error occurred: {e}")
                import traceback
                st.error(traceback.format_exc())

st.markdown("""
<style>
    .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background-color: #FDFBF7;
        color: #888888;
        text-align: center;
        padding: 10px;
        font-family: 'Roboto', sans-serif;
        font-size: 0.8em;
        border-top: 1px solid #EAEAEA;
    }
</style>
<div class="footer">
    Powered by Google Gemini, Groq, Stability AI & StyleSense AI Fashion Advisor © 2026
</div>
""", unsafe_allow_html=True)