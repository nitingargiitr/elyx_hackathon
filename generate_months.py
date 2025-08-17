import os
import json
import random
import requests
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Configuration - choose your preferred free API
USE_HUGGINGFACE = os.getenv("USE_HUGGINGFACE", "true").lower() == "true"
USE_GROQ = os.getenv("USE_GROQ", "false").lower() == "true"
USE_GEMINI = os.getenv("USE_GEMINI", "false").lower() == "true"

DATA_DIR = Path("elyx_conversations")
DATA_DIR.mkdir(exist_ok=True)

# ------------------------------
# Hugging Face API (FREE - No API key needed for basic models)
# ------------------------------
def generate_with_huggingface(month, start_date, end_date):
    try:
        # Using free Hugging Face Inference API
        API_URL = "https://api-inference.huggingface.co/models/microsoft/DialoGPT-large"
        
        prompt = f"""Generate a realistic WhatsApp health team conversation for {month} 2025.
        
Team: Rohan (patient), Dr. Warren (doctor), Ruby (coach), Carla (nutritionist), Neel (diagnostics), Rachel (physio), Advik (analyst).

Create 40-50 realistic messages about:
- HRV monitoring (specific numbers like 45ms, 62ms)
- Blood tests and glucose readings
- Sleep quality metrics
- Recovery scores (70-95%)
- Protocol updates (v2, v3)
- Lifestyle tips and adjustments

Format as JSON array: [{{"timestamp": "2025-04-15 09:30:00", "sender": "Name", "text": "message"}}]

Messages should be spread from {start_date} to {end_date} with natural conversation flow."""

        # Alternative: Use a simple HTTP request to free models
        try:
            # Method 1: Try Hugging Face free inference
            headers = {"Authorization": f"Bearer {os.getenv('HUGGINGFACE_API_KEY', '')}"} if os.getenv('HUGGINGFACE_API_KEY') else {}
            
            payload = {
                "inputs": prompt,
                "parameters": {
                    "max_new_tokens": 2000,
                    "temperature": 0.8,
                    "do_sample": True
                }
            }
            
            response = requests.post(API_URL, headers=headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    generated_text = result[0].get('generated_text', '')
                    return parse_conversation_json(generated_text)
            
        except Exception as e:
            print(f"Hugging Face API error: {e}")
        
        # Fallback to enhanced rule-based if API fails
        return generate_enhanced_rule_based(month, start_date, end_date)
        
    except Exception as e:
        print(f"Hugging Face generation error: {e}")
        return generate_enhanced_rule_based(month, start_date, end_date)

# ------------------------------
# Groq API (FREE - Fast inference with Llama models)
# ------------------------------
def generate_with_groq(month, start_date, end_date):
    try:
        # Groq provides free API access to Llama models
        import groq
        
        client = groq.Groq(api_key=os.getenv("GROQ_API_KEY"))
        
        prompt = f"""Create a realistic WhatsApp health optimization team conversation for {month} 2025.

TEAM MEMBERS:
- Rohan: Patient sharing health data and concerns
- Dr. Warren: Lead physician providing medical insights
- Ruby: Health coach with lifestyle guidance
- Carla: Nutritionist with meal and supplement advice
- Neel: Lab specialist interpreting test results
- Rachel: Physiotherapist with movement guidance
- Advik: Data analyst tracking HRV and biometrics

CONVERSATION THEMES:
- HRV readings (35-75ms range)
- Sleep quality scores (6-9 hours, deep sleep %)
- Recovery percentages (65-95%)
- Blood glucose readings (80-120 mg/dL)
- Lab results (CRP, cortisol, etc.)
- Protocol adjustments (v2, v3 updates)
- Travel impact on metrics
- Supplement timing and dosages

Generate 45-55 realistic messages between {start_date} and {end_date}.
Return ONLY a valid JSON array with this exact format:
[{{"timestamp": "YYYY-MM-DD HH:MM:SS", "sender": "Name", "text": "message content"}}]

Make conversations feel natural with:
- Specific numeric health data
- Professional medical discussions
- Casual supportive messages
- Follow-up questions and responses
- Realistic timing throughout the day"""

        response = client.chat.completions.create(
            model="llama3-70b-8192",  # Free tier model
            messages=[
                {"role": "system", "content": "You are an expert at creating realistic health team conversations. Generate authentic WhatsApp-style messages with specific health data."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.8,
            max_tokens=3000
        )
        
        content = response.choices[0].message.content
        return parse_conversation_json(content)
        
    except Exception as e:
        print(f"Groq API error: {e}")
        return generate_enhanced_rule_based(month, start_date, end_date)

# ------------------------------
# Google Gemini API (FREE tier available)
# ------------------------------
def generate_with_gemini(month, start_date, end_date):
    try:
        import google.generativeai as genai
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        
        prompt = f"""Generate a realistic WhatsApp health optimization team conversation for {month} 2025.

Team: Rohan (patient), Dr. Warren (physician), Ruby (coach), Carla (nutritionist), Neel (diagnostics), Rachel (physio), Advik (analyst).

Create 45-55 authentic messages covering:
- HRV monitoring (specific values: 38ms, 67ms, etc.)
- Sleep metrics (hours, deep sleep %, REM)
- Recovery scores (percentage values)
- Blood work results (glucose, inflammation markers)
- Protocol updates and adjustments
- Lifestyle optimization tips
- Travel and stress impact discussions

Distribute messages naturally from {start_date} to {end_date}.
Return valid JSON: [{{"timestamp": "YYYY-MM-DD HH:MM:SS", "sender": "Name", "text": "message"}}]

Make it feel like a real health team WhatsApp group with professional yet friendly tone."""
        
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        
        return parse_conversation_json(response.text)
        
    except Exception as e:
        print(f"Gemini API error: {e}")
        return generate_enhanced_rule_based(month, start_date, end_date)

# ------------------------------
# JSON parsing helper
# ------------------------------
def parse_conversation_json(content):
    try:
        # Clean up common formatting issues
        content = content.strip()
        
        # Handle markdown code blocks
        if "```json" in content:
            start = content.find("```json") + 7
            end = content.find("```", start)
            content = content[start:end].strip()
        elif "```" in content:
            start = content.find("```") + 3
            end = content.find("```", start)
            content = content[start:end].strip()
        
        # Try to find JSON array in the content
        if "[" in content and "]" in content:
            start = content.find("[")
            end = content.rfind("]") + 1
            json_content = content[start:end]
            
            return json.loads(json_content)
        
        return []
        
    except json.JSONDecodeError as e:
        print(f"JSON parsing error: {e}")
        return []

# ------------------------------
# Enhanced rule-based fallback (no API needed)
# ------------------------------
def generate_enhanced_rule_based(month, start_date, end_date):
    participants = [
        {"name": "Rohan", "role": "patient"},
        {"name": "Dr. Warren", "role": "doctor"},
        {"name": "Ruby", "role": "coach"},
        {"name": "Carla", "role": "nutritionist"},
        {"name": "Neel", "role": "diagnostics"},
        {"name": "Rachel", "role": "physio"},
        {"name": "Advik", "role": "analyst"}
    ]
    
    # Categorized realistic messages
    patient_messages = [
        "HRV dropped to {hrv}ms this morning, feeling stressed about the project deadline 😟",
        "Recovery score is {recovery}% today, much better than yesterday!",
        "Sleep was only {sleep} hours last night, kept waking up",
        "Glucose reading 2hrs post-meal: {glucose} mg/dL, is this okay?",
        "Feeling great today! Energy levels are through the roof 💪",
        "Travel day tomorrow, any tips for maintaining my routine?",
        "Morning workout felt really hard, should I reduce intensity?",
    ]
    
    doctor_messages = [
        "Your recent blood panel shows CRP at {crp} mg/L, within normal range 👍",
        "Let's schedule your OGTT for next week. Fast for 12 hours beforehand.",
        "Protocol v{version} update: adjusting your magnesium dosage to {dose}mg",
        "Based on your cortisol pattern, try meditation before 10 AM",
        "Your lipid profile has improved significantly since last month",
        "Consider reducing caffeine intake after 2 PM for better sleep quality",
    ]
    
    coach_messages = [
        "Great job maintaining consistency! Your 7-day average HRV is trending up 📈",
        "Remember to do your breathing exercise before the big presentation",
        "Your stress management is improving - I can see it in the data",
        "Let's focus on recovery this week, dial back intensity by 20%",
        "Perfect timing on your meals yesterday, glucose stayed stable",
    ]
    
    nutritionist_messages = [
        "Try adding {food} to your breakfast for sustained energy",
        "Your post-workout meal timing is perfect - keep it up!",
        "Consider swapping the afternoon snack for nuts and berries",
        "Hydration looks low today, aim for 2.5L with electrolytes",
        "Great choice on the salmon last night - omega-3s will help recovery",
    ]
    
    diagnostics_messages = [
        "Lab results are in: {marker} levels look excellent",
        "Your inflammatory markers are trending downward - great progress",
        "Vitamin D is at {level} ng/mL, let's increase supplementation",
        "Thyroid function normal, TSH at {tsh} mIU/L",
        "Follow-up bloodwork scheduled for {date}",
    ]
    
    physio_messages = [
        "Your movement quality has improved! Keep up the mobility work",
        "Try the new hip flexor stretch I sent - 2 minutes each side",
        "Your shoulder impingement is resolving well",
        "Remember to activate glutes before your run tomorrow",
        "Posture looking much better during our video call 👍",
    ]
    
    analyst_messages = [
        "Your HRV trend shows a {trend}% improvement over 30 days",
        "Sleep efficiency is up to {efficiency}% - best month yet!",
        "Recovery correlation with sleep duration is strong (r={correlation})",
        "Your stress response pattern is becoming more resilient",
        "Data suggests optimal training window is {time} for your chronotype",
    ]
    
    quick_responses = ["Thanks! 👍", "Perfect", "Got it", "Will do", "Great news!", "Noted", "On it!"]
    
    # Generate messages
    data = []
    current = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")
    
    while current <= end:
        # 1-4 messages per day
        daily_count = random.randint(1, 4)
        
        for _ in range(daily_count):
            participant = random.choice(participants)
            sender = participant["name"]
            role = participant["role"]
            
            # Select message based on role
            if role == "patient":
                templates = patient_messages + quick_responses
            elif role == "doctor":
                templates = doctor_messages + quick_responses
            elif role == "coach":
                templates = coach_messages + quick_responses
            elif role == "nutritionist":
                templates = nutritionist_messages + quick_responses
            elif role == "diagnostics":
                templates = diagnostics_messages + quick_responses
            elif role == "physio":
                templates = physio_messages + quick_responses
            elif role == "analyst":
                templates = analyst_messages + quick_responses
            else:
                templates = quick_responses
            
            template = random.choice(templates)
            
            # Fill in template variables with realistic values
            message = template.format(
                hrv=random.randint(35, 75),
                recovery=random.randint(65, 95),
                sleep=round(random.uniform(5.5, 8.5), 1),
                glucose=random.randint(80, 120),
                crp=round(random.uniform(0.5, 2.0), 1),
                version=random.randint(2, 4),
                dose=random.choice([200, 300, 400]),
                food=random.choice(["Greek yogurt", "oatmeal", "avocado", "berries"]),
                marker=random.choice(["B12", "Iron", "Folate"]),
                level=random.randint(30, 80),
                tsh=round(random.uniform(1.0, 3.0), 1),
                date=f"April {random.randint(15, 30)}",
                trend=random.randint(5, 25),
                efficiency=random.randint(82, 94),
                correlation=round(random.uniform(0.6, 0.9), 2),
                time=random.choice(["9-11 AM", "2-4 PM", "6-8 AM"])
            )
            
            # Realistic timing
            hour = random.choices(
                range(24),
                weights=[1,1,1,1,1,2,4,8,10,12,15,15,12,10,8,6,4,3,2,1,1,1,1,1]
            )[0]
            
            timestamp = current.replace(
                hour=hour,
                minute=random.randint(0, 59),
                second=random.randint(0, 59)
            )
            
            data.append({
                "timestamp": timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                "sender": sender,
                "text": message
            })
        
        current += timedelta(days=1)
    
    # Sort chronologically
    data.sort(key=lambda x: x["timestamp"])
    
    # Ensure we have a good number of messages
    if len(data) < 40:
        # Add some more messages if needed
        additional = 40 - len(data)
        for _ in range(additional):
            participant = random.choice(participants)
            message = random.choice(quick_responses)
            base_time = random.choice(data)["timestamp"]
            timestamp = datetime.strptime(base_time, "%Y-%m-%d %H:%M:%S") + timedelta(minutes=random.randint(1, 60))
            
            data.append({
                "timestamp": timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                "sender": participant["name"],
                "text": message
            })
        
        data.sort(key=lambda x: x["timestamp"])
    
    return data[:50]  # Limit to 50 messages

def save_month(month, start_date, end_date):
    print(f"🚀 Generating conversation for {month}...")
    
    if USE_GROQ:
        print("📡 Using Groq API (Free Llama models)...")
        data = generate_with_groq(month, start_date, end_date)
    elif USE_GEMINI:
        print("📡 Using Google Gemini API...")
        data = generate_with_gemini(month, start_date, end_date)
    elif USE_HUGGINGFACE:
        print("📡 Using Hugging Face API...")
        data = generate_with_huggingface(month, start_date, end_date)
    else:
        print("🔧 Using enhanced rule-based generation...")
        data = generate_enhanced_rule_based(month, start_date, end_date)
    
    # Fallback if no data generated
    if not data or len(data) < 10:
        print("⚠️ API generated insufficient data, using enhanced fallback...")
        data = generate_enhanced_rule_based(month, start_date, end_date)
    
    # Save data
    path = DATA_DIR / f"{month.lower()}_conversations.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Saved {len(data)} messages to {path}")
    
    # Preview
    print(f"\n📱 Preview of {month} conversation:")
    for msg in data[:3]:
        print(f"[{msg['timestamp']}] {msg['sender']}: {msg['text']}")
    if len(data) > 3:
        print(f"... and {len(data)-3} more messages")
    print()

if __name__ == "__main__":
    # Generate comprehensive dataset
    months_data = [
        ("January", "2025-01-01", "2025-01-31"),
        ("February", "2025-02-01", "2025-02-28"),
        ("March", "2025-03-01", "2025-03-31"),
        ("April", "2025-04-01", "2025-04-30"),
        ("May", "2025-05-01", "2025-05-31"),
        ("June", "2025-06-01", "2025-06-30"),
    ]
    
    print("🎯 Health Chat Generator - Free API Edition")
    print("=" * 50)
    
    for month, start, end in months_data:
        save_month(month, start, end)
    
    print("🎉 All conversations generated successfully!")
    print(f"📁 Check the '{DATA_DIR}' folder for your JSON files")