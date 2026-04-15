import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import json
import os

router = APIRouter(prefix="/api/weather", tags=["Weather"])
WEATHER_CACHE_FILE = "data/weather_cache.json"

class WeatherResponse(BaseModel):
    temperature: float
    condition: str
    city: str
    is_cached: bool = False
    prediction: str = ""

@router.get("/", response_model=WeatherResponse)
async def get_weather(lat: float = 28.6139, lon: float = 77.2090, city: str = "New Delhi"):
    """
    Fetch live weather from Open-Meteo (Free, No API Key needed).
    Returns temperature, condition, and optional simple prediction.
    Falls back to backend cache if API fails.
    """
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
    
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(url)
        resp.raise_for_status()
        data = resp.json()
        current = data.get("current_weather", {})
        
        # WMO Weather interpretation codes
        weather_code = current.get("weathercode", 0)
        cond = "☀️ Clear" if weather_code <= 1 else "☁️ Cloudy" if weather_code <= 3 else "🌧️ Rain"
        temp = current.get("temperature", 0.0)
        
        # Load local history for basic prediction mapping
        history = []
        os.makedirs("data", exist_ok=True)
        if os.path.exists(WEATHER_CACHE_FILE):
            try:
                with open(WEATHER_CACHE_FILE, "r", encoding="utf-8") as f:
                    cache_content = json.load(f)
                    if isinstance(cache_content, dict):
                        history = cache_content.get("history", [])
            except:
                pass
                
        # Update history (keep last 3)
        history.append(temp)
        if len(history) > 3:
            history = history[-3:]
            
        prediction = ""
        # Simple AI-based prediction logic (average)
        if len(history) == 3:
            avg_temp = sum(history) / 3
            trend = "warming up" if temp > avg_temp else "cooling down"
            prediction = f"Trend: {trend}. Avg was {avg_temp:.1f}°C."
            
        result = {
            "temperature": temp,
            "condition": cond,
            "city": city,
            "is_cached": False,
            "prediction": prediction
        }
        
        # Save to cache
        with open(WEATHER_CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump({"history": history, "last_result": result}, f)
            
        return result
        
    except Exception as e:
        # 1. API Failure Fallback
        if os.path.exists(WEATHER_CACHE_FILE):
            try:
                with open(WEATHER_CACHE_FILE, "r", encoding="utf-8") as f:
                    cache_content = json.load(f)
                    last = cache_content.get("last_result", {})
                    if last:
                        last["is_cached"] = True
                        last["prediction"] = "Serving from backend cache due to API error."
                        return last
            except:
                pass
        raise HTTPException(status_code=503, detail="Weather service unavailable and no cache.")
