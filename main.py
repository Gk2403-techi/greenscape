from fastapi import FastAPI, Request, Form, UploadFile, File
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional, Dict, Any
import shutil
import os
import random
import urllib.parse
import re
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import google.generativeai as genai

# Load plant database
with open("plants.json", "r") as f:
    PLANT_DATA = json.load(f)["plants"]

load_dotenv()

# --- CONFIGURATION ---
# Using the key provided
try:
    genai.configure(api_key="AIzaSyCTpzb1KIOB0sgQr5q-7RpTu6kZc-uoqY8")
    HAS_GEMINI = True
except:
    HAS_GEMINI = False

app = FastAPI()

# Setup Directories
os.makedirs("static", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Register Jinja Filter (Crucial for Frontend State)
templates.env.filters["tojson"] = lambda x: json.dumps(x) if x else "null"

# --- DATA STORES ---
APPOINTMENTS = []  # In-memory storage for appointments

MATERIAL_TIERS = {
    "Economy": {
        "hardscape": {"name": "Concrete Pavers", "price": 8.0, "unit": "sqft"},
        "softscape": {"name": "Standard Mulch", "price": 3.5, "unit": "bag"},
        "lighting":  {"name": "Solar Path Stakes", "price": 8.0, "unit": "each"}
    },
    "Standard": {
        "hardscape": {"name": "Limestone Pavers", "price": 15.0, "unit": "sqft"},
        "softscape": {"name": "Hardwood Mulch", "price": 5.0, "unit": "bag"},
        "lighting":  {"name": "LED Low Voltage", "price": 25.0, "unit": "each"}
    },
    "Premium": {
        "hardscape": {"name": "Imported Granite", "price": 28.0, "unit": "sqft"},
        "softscape": {"name": "River Rock", "price": 12.0, "unit": "bag"},
        "lighting":  {"name": "Smart App System", "price": 60.0, "unit": "each"}
    }
}

LABOR_RATES = {
    "General": {"rate": 40.0, "type": "General Labor"},
    "Specialist": {"rate": 85.0, "type": "Masonry/Technical"},
}

CURRENCY_RATES = { 
    "USD": {"symbol": "$", "rate": 1.0}, 
    "EUR": {"symbol": "€", "rate": 0.92}, 
    "INR": {"symbol": "₹", "rate": 83.0} 
}

# Soil & Climate Knowledge Base
SOIL_KNOWLEDGE_BASE = {
    "Clay": {"advice": "Clay retains moisture. We selected deep-rooting plants to break compaction.", "amendment": "Gypsum"},
    "Sandy": {"advice": "Sandy soil drains fast. We selected drought-resistant species.", "amendment": "Peat Moss"},
    "Loam": {"advice": "Loam is ideal. Supports a lush, dense garden layout.", "amendment": "Compost"}
}

# --- HELPER FUNCTIONS ---
def get_season_from_zip(zip_code):
    """
    Simple season mapping based on US zip code regions.
    In a real app, this would use a weather API.
    """
    try:
        zip_int = int(zip_code[:3])  # First 3 digits
        if 100 <= zip_int <= 199:  # Northeast
            return "Spring"  # Assuming current season; in reality, use date
        elif 200 <= zip_int <= 399:  # Southeast
            return "Spring"
        elif 400 <= zip_int <= 599:  # Midwest
            return "Spring"
        elif 600 <= zip_int <= 799:  # Southwest
            return "Spring"
        elif 800 <= zip_int <= 999:  # West
            return "Spring"
        else:
            return "Spring"
    except:
        return "Spring"

def get_climate_from_zip(zip_code):
    """
    Determine climate based on zip code.
    """
    try:
        zip_int = int(zip_code[:3])
        if 100 <= zip_int <= 199:  # Northeast
            return "Temperate"
        elif 200 <= zip_int <= 399:  # Southeast
            return "Subtropical"
        elif 400 <= zip_int <= 599:  # Midwest
            return "Continental"
        elif 600 <= zip_int <= 799:  # Southwest
            return "Arid"
        elif 800 <= zip_int <= 999:  # West
            return "Mediterranean"
        else:
            return "Temperate"
    except:
        return "Temperate"

def generate_image_url(prompt):
    """
    Tries Google Imagen -> Falls back to Pollinations.ai
    """
    filename = f"static/render_{random.randint(1000,9999)}.png"
    
    # 1. Try Google Imagen (If available on key)
    if HAS_GEMINI:
        try:
            model = genai.ImageGenerationModel('imagen-3.0-generate-001')
            response = model.generate_images(
                prompt=prompt, number_of_images=1,
                safety_filter_level="block_only_high",
                aspect_ratio="16:9"
            )
            response[0].save(filename)
            return f"/{filename}"
        except:
            pass # Fail silently to fallback

    # 2. Fallback: Pollinations.ai (Reliable)
    encoded = urllib.parse.quote(prompt)
    seed = random.randint(1, 99999)
    return f"https://image.pollinations.ai/prompt/{encoded}?width=1280&height=720&seed={seed}&model=flux&nologo=true"

# --- NLP ENGINE (Virtual Assistant) ---
class NaturalLanguageProcessor:
    @staticmethod
    def parse(message: str, current_state: dict):
        msg = message.lower()
        changes = {}
        response = ""

        # Numerical Parsing
        numbers = re.findall(r'\d+', msg.replace(',', ''))
        
        # Intent Recognition
        if "size" in msg or "sqft" in msg:
            if numbers: changes['dimensions'] = int(numbers[0]); response = f"Recalculating for **{numbers[0]} sqft**."
        elif "budget" in msg:
            if numbers: changes['user_budget'] = int(numbers[0]); response = f"Budget limit set to **{numbers[0]}**."
        elif "pool" in msg: changes['water_feature'] = "Swimming Pool"; response = "Added a **Swimming Pool** to the layout."
        elif "cheap" in msg: changes['quality_tier'] = "Economy"; response = "Switched to **Economy** materials."
        elif "premium" in msg: changes['quality_tier'] = "Premium"; response = "Upgraded to **Premium** materials."
        
        # Soil/Climate Advice Intent
        elif "soil" in msg or "advice" in msg:
            soil = current_state.get('soil', 'Loam')
            info = SOIL_KNOWLEDGE_BASE.get(soil, SOIL_KNOWLEDGE_BASE['Loam'])
            response = f"**Soil Analysis:** {info['advice']} Recommended amendment: {info['amendment']}."

        # Fallback Chat using Gemini Text (if available) or Rules
        if not response:
            try:
                model = genai.GenerativeModel('gemini-1.5-flash')
                chat = model.generate_content(f"You are a garden architect. Reply briefly to: {message}")
                response = chat.text
            except:
                response = "I can modify the **Budget**, **Size**, **Materials**, or explain the **Soil**. What do you need?"
            
        return changes, response

# --- CALCULATION ENGINE ---
def calculate_plan_logic(state: dict):
    # Safe Defaults
    dims = int(state.get('dimensions', 1000))
    tier_name = state.get('quality_tier', 'Standard')
    tier = MATERIAL_TIERS.get(tier_name, MATERIAL_TIERS["Standard"])
    curr = CURRENCY_RATES.get(state.get('currency', 'USD'), CURRENCY_RATES["USD"])
    
    persona = state.get('user_persona', 'Homeowner')
    water_feature = state.get('water_feature', 'None')
    soil = state.get('soil', 'Loam')
    
    # Ratios
    ratios = {"hardscape": 0.3, "softscape": 0.5}
    if persona == "Farmer": ratios = {"hardscape": 0.05, "softscape": 0.95}
    elif persona == "Architect" or persona == "Landscaping Business": ratios = {"hardscape": 0.4, "softscape": 0.4}

    hard_area = int(dims * ratios["hardscape"])
    soft_area = int(dims * ratios["softscape"])
    
    # BOM Generation
    bom = []
    
    # Hardscape
    h_cost = hard_area * tier["hardscape"]["price"]
    bom.append({"name": tier["hardscape"]["name"], "qty": hard_area, "unit": tier["hardscape"]["unit"], "rate": tier["hardscape"]["price"], "total": h_cost})
    
    # Softscape
    mulch_qty = max(1, int(soft_area / 15))
    s_cost = mulch_qty * tier["softscape"]["price"]
    bom.append({"name": tier["softscape"]["name"], "qty": mulch_qty, "unit": tier["softscape"]["unit"], "rate": tier["softscape"]["price"], "total": s_cost})
    
    # Special Items
    special_cost = 0
    special_name = "Design Fee"
    if water_feature == "Swimming Pool": special_name = "Pool Install"; special_cost = 15000
    elif water_feature == "Koi Pond": special_name = "Pond Install"; special_cost = 5000
    elif persona == "Farmer": special_name = "Irrigation System"; special_cost = 2500
    
    bom.append({"name": special_name, "qty": 1, "unit": "lot", "rate": special_cost, "total": special_cost})

    # Labor
    labor_hours = int(dims / 20)
    l_cost = labor_hours * LABOR_RATES["General"]["rate"]
    
    # Totals
    grand_total_raw = sum([x['total'] for x in bom]) + l_cost
    
    # Formatting
    sym, rate = curr['symbol'], curr['rate']
    formatted_bom = [{**x, "rate": f"{sym}{int(x['rate']*rate)}", "total": f"{sym}{int(x['total']*rate):,}"} for x in bom]
    
    total_display = f"{sym}{int(grand_total_raw * rate):,}"
    try: budget_limit = int(state.get('user_budget', 100000))
    except: budget_limit = 100000
    
    budget_status = "Within Budget" if (grand_total_raw * rate) <= budget_limit else "Over Budget"
    status_color = "text-neon-lime" if (grand_total_raw * rate) <= budget_limit else "text-red-400"

    # Seasonal Plant Recommendations
    zip_code = state.get('zip_code', '00000')
    climate = state.get('climate', get_climate_from_zip(zip_code))
    maintenance_level = state.get('maintenance_level', 'Medium')
    current_season = get_season_from_zip(zip_code)

    # Filter plants based on season, soil, and maintenance level
    recommended_plants = []
    for plant in PLANT_DATA:
        if not (plant['season'] == current_season or plant['season'] == 'Evergreen'):
            continue
        if soil not in plant['soil_types']:
            continue
        # Simple maintenance filter: low maintenance if level is Low, etc.
        if maintenance_level == 'Low':
            # Prefer plants with less frequent maintenance
            if 'drought tolerant' in plant['maintenance']['watering'].lower() or 'minimal' in plant['maintenance']['pruning'].lower():
                recommended_plants.append(plant)
        elif maintenance_level == 'High':
            # Include all
            recommended_plants.append(plant)
        else:  # Medium
            recommended_plants.append(plant)

    # Select 3-5 plants randomly
    selected_plants = random.sample(recommended_plants, min(5, len(recommended_plants))) if recommended_plants else []

    # Maintenance Schedules
    maintenance_schedule = []
    for plant in selected_plants:
        maintenance_schedule.append({
            "plant": plant['name'],
            "watering": plant['maintenance']['watering'],
            "pruning": plant['maintenance']['pruning'],
            "fertilizing": plant['maintenance']['fertilizing']
        })

    # AI Visuals
    render_prompt = (
        f"photorealistic 3d aerial render of {state.get('project_type')}, "
        f"designed for {persona}, featuring {water_feature} and {tier['hardscape']['name']} pathways, "
        f"on {soil} soil, {state.get('style')} style, {state.get('terrain')} terrain, highly detailed"
    )

    return {
        "cost": total_display,
        "budget_status": budget_status,
        "status_color": status_color,
        "bom": formatted_bom,
        "url_3d": generate_image_url(render_prompt),
        "url_2d": generate_image_url(f"2D technical blueprint for {state.get('project_type')}"),
        "recommended_plants": selected_plants,
        "maintenance_schedule": maintenance_schedule,
        "current_season": current_season,
        "state": state
    }

# --- ROUTES ---
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "result": None, "current_state": None, "bulk_plans": None})

@app.post("/generate", response_class=HTMLResponse)
async def generate_plan(
    request: Request,
    user_persona: str = Form(...), project_type: str = Form(...), style: str = Form(...),
    quality_tier: str = Form(...), user_budget: int = Form(...), dimensions: int = Form(...),
    soil: str = Form(...), currency: str = Form(...), file: UploadFile = File(...),
    terrain: str = Form(...), usage: str = Form(...), privacy: str = Form(...), water_feature: str = Form(...),
    zip_code: str = Form(...), climate: str = Form(...), maintenance_level: str = Form(...),
    bulk_mode: str = Form("off")
):
    filename = f"static/upload_{random.randint(1000,9999)}.jpg"
    with open(filename, "wb") as buffer: shutil.copyfileobj(file.file, buffer)

    state = {
        "user_persona": user_persona, "project_type": project_type, "style": style,
        "quality_tier": quality_tier, "user_budget": user_budget, "dimensions": dimensions,
        "soil": soil, "currency": currency, "terrain": terrain, "usage": usage,
        "privacy": privacy, "water_feature": water_feature, "original_image": filename,
        "zip_code": zip_code, "climate": climate, "maintenance_level": maintenance_level
    }

    if bulk_mode == "on":
        # Generate 3-5 variations
        bulk_plans = []
        styles = ["Modern", "Traditional", "Rustic", "Minimalist"]
        tiers = ["Economy", "Standard", "Premium"]
        for i in range(3):
            variation_state = state.copy()
            variation_state['style'] = random.choice(styles)
            variation_state['quality_tier'] = random.choice(tiers)
            variation_state['user_budget'] = int(state['user_budget']) + random.randint(-5000, 5000)  # Slight budget variation
            plan = calculate_plan_logic(variation_state)
            bulk_plans.append(plan)
        return templates.TemplateResponse("index.html", {
            "request": request, "result": None, "bulk_plans": bulk_plans, "current_state": state, "persona": user_persona
        })

    plan = calculate_plan_logic(state)
    return templates.TemplateResponse("index.html", {
        "request": request, "result": True, **plan, "current_state": state, "persona": user_persona
    })

class ChatRequest(BaseModel):
    message: str
    current_state: Dict[str, Any]

@app.post("/chat")
async def chat_response(data: ChatRequest):
    changes, reply = NaturalLanguageProcessor.parse(data.message, data.current_state)
    new_state = data.current_state.copy()
    new_state.update(changes)
    new_plan = calculate_plan_logic(new_state)
    return JSONResponse({"reply": reply, "updated": bool(changes), "new_plan": new_plan})

@app.post("/schedule")
async def schedule_appointment(
    name: str = Form(...),
    email: str = Form(...),
    phone: str = Form(...),
    date: str = Form(...),
    message: Optional[str] = Form("No message provided.")
):
    """
    Handles the consultation schedule form submission and sends an email notification.
    """
    try:
        # --- Set up email credentials from environment variables ---
        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        # WARNING: Storing credentials directly in code is a security risk.
        # For better security, please use a .env file as recommended below.
        sender_email = "krishnangopi353@gmail.com"
        sender_password = "zvpx dfpa ppbd uifm"
        admin_email = "krishnangopi353@gmail.com" # Admin notification recipient

        # --- 1. Create a single email for both admin and user ---
        recipients = [admin_email, email]
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = ", ".join(recipients)
        msg['Subject'] = f"GreenScape Consultation Request Details ({name})"

        body = f"""
        A new consultation request has been submitted. This email serves as a notification for the admin and a confirmation copy for the user.

        --- Submitted Details ---

        Name: {name}
        Email: {email}
        Phone: {phone}
        Preferred Date: {date}
        Message:
        {message}
        """
        msg.attach(MIMEText(body, 'plain'))

        # --- Send the email ---
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, recipients, msg.as_string())

        return JSONResponse(status_code=200, content={"message": "Thank you! Your consultation request has been sent."})

    except smtplib.SMTPAuthenticationError:
        print("SMTP Authentication Error. Check credentials or app-specific password settings.")
        return JSONResponse(status_code=500, content={"message": "Authentication failure."})
    except Exception as e:
        print(f"An error occurred: {e}")
        return JSONResponse(status_code=500, content={"message": "An error occurred."})

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return JSONResponse(content={})
