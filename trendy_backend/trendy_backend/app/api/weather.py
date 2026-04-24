import requests
from fastapi import APIRouter, HTTPException
import os

router = APIRouter(prefix="/api/weather", tags=["weather"])

@router.get("/current/{city}")
async def get_weather(city: str):
    """Get current weather for any city using OpenWeatherMap API"""
    api_key = os.getenv("OPENWEATHER_API_KEY", "demo_key")
    
    # Demo fallback data
    if api_key == "demo_key":
        return {
            "weather": [{"description": "Partly cloudy"}],
            "main": {"temp": 22, "humidity": 65},
            "name": city,
            "sys": {"country": "US"}
        }
    
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            raise HTTPException(status_code=404, detail="Weather data not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/forecast/{city}")
async def get_forecast(city: str):
    """Get 5-day weather forecast"""
    api_key = os.getenv("OPENWEATHER_API_KEY", "demo_key")
    
    if api_key == "demo_key":
        return {
            "list": [
                {"dt": 1700000000, "main": {"temp": 20}, "weather": [{"description": "Sunny"}]},
                {"dt": 1700086400, "main": {"temp": 18}, "weather": [{"description": "Cloudy"}]}
            ]
        }
    
    url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={api_key}&units=metric"
    
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            raise HTTPException(status_code=404, detail="Forecast data not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
