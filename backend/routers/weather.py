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
    forecast_3h: dict = {}
    daily_forecast: list = []

@router.get("/", response_model=WeatherResponse)
async def get_weather(lat: float = 28.6139, lon: float = 77.2090, city: str = "New Delhi"):
    """
    Fetch live weather from Open-Meteo (Free, No API Key needed).
    Returns temperature, condition, 3-hour forecast, and 7-day forecast.
    Falls back to backend cache if API fails.
    """
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true&hourly=temperature_2m,weathercode&daily=weathercode,temperature_2m_max,temperature_2m_min&timezone=auto"
    
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(url)
        resp.raise_for_status()
        data = resp.json()
        current = data.get("current_weather", {})
        
        # WMO Weather interpretation codes function
        def get_cond(code):
            return "☀️ Clear" if code <= 1 else "☁️ Cloudy" if code <= 3 else "🌧️ Rain"

        weather_code = current.get("weathercode", 0)
        cond = get_cond(weather_code)
        temp = current.get("temperature", 0.0)
        
        # +3 Hours Forecast
        forecast_3h = {}
        try:
            hourly = data.get("hourly", {})
            current_time = current.get("time") # e.g., "2023-10-27T14:00"
            if current_time and "time" in hourly:
                times = hourly["time"]
                if current_time in times:
                    idx = times.index(current_time)
                    target_idx = idx + 3
                    if target_idx < len(times):
                        forecast_3h = {
                            "time": times[target_idx],
                            "temperature": hourly["temperature_2m"][target_idx],
                            "condition": get_cond(hourly["weathercode"][target_idx])
                        }
        except Exception as e:
            pass

        # Daily Forecast
        daily_forecast = []
        try:
            daily = data.get("daily", {})
            if "time" in daily:
                for i in range(min(7, len(daily["time"]))):
                    daily_forecast.append({
                        "date": daily["time"][i],
                        "max_temp": daily["temperature_2m_max"][i],
                        "min_temp": daily["temperature_2m_min"][i],
                        "condition": get_cond(daily["weathercode"][i])
                    })
        except Exception as e:
            pass
        
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
            "prediction": prediction,
            "forecast_3h": forecast_3h,
            "daily_forecast": daily_forecast
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
