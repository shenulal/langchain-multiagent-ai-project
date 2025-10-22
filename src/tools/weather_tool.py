"""
Weather API tool for fetching weather information
"""

import os
import aiohttp
from typing import Dict, Any, Optional
from langchain.tools import BaseTool
from pydantic import BaseModel, Field
from loguru import logger

class WeatherInput(BaseModel):
    """Input schema for weather tool"""
    location: str = Field(description="City name or location to get weather for")
    units: str = Field(default="metric", description="Units for temperature (metric, imperial, kelvin)")

class WeatherTool(BaseTool):
    """Tool for fetching current weather information"""
    
    name: str = "get_weather"
    description: str = """
    Get current weather information for a specific location.
    Use this tool when users ask about weather conditions, temperature, or forecast.
    Input should be a location (city name, city and country, etc.).
    """
    args_schema = WeatherInput
    
    def __init__(self):
        super().__init__()
        self.api_key = os.getenv("WEATHER_API_KEY")
        self.base_url = "http://api.openweathermap.org/data/2.5"
    
    async def _arun(self, location: str, units: str = "metric") -> str:
        """Async implementation of the weather tool"""
        try:
            if not self.api_key:
                return "Weather API key not configured. Please set WEATHER_API_KEY environment variable."
            
            # Fetch current weather
            current_weather = await self._fetch_current_weather(location, units)
            
            if not current_weather:
                return f"Could not fetch weather information for {location}. Please check the location name."
            
            # Format the response
            response = self._format_weather_response(current_weather, location)
            
            logger.info(f"Weather data fetched for {location}")
            return response
            
        except Exception as e:
            logger.error(f"Error fetching weather for {location}: {str(e)}")
            return f"Error fetching weather information: {str(e)}"
    
    def _run(self, location: str, units: str = "metric") -> str:
        """Sync implementation (not recommended for async apps)"""
        import asyncio
        return asyncio.run(self._arun(location, units))
    
    async def _fetch_current_weather(self, location: str, units: str) -> Optional[Dict[str, Any]]:
        """Fetch current weather from OpenWeatherMap API"""
        try:
            url = f"{self.base_url}/weather"
            params = {
                "q": location,
                "appid": self.api_key,
                "units": units
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        return await response.json()
                    elif response.status == 404:
                        logger.warning(f"Location not found: {location}")
                        return None
                    else:
                        logger.error(f"Weather API error: {response.status}")
                        return None
                        
        except Exception as e:
            logger.error(f"Error calling weather API: {str(e)}")
            return None
    
    def _format_weather_response(self, weather_data: Dict[str, Any], location: str) -> str:
        """Format weather data into a readable response"""
        try:
            main = weather_data.get("main", {})
            weather = weather_data.get("weather", [{}])[0]
            wind = weather_data.get("wind", {})
            
            temp = main.get("temp", "N/A")
            feels_like = main.get("feels_like", "N/A")
            humidity = main.get("humidity", "N/A")
            pressure = main.get("pressure", "N/A")
            
            description = weather.get("description", "N/A").title()
            wind_speed = wind.get("speed", "N/A")
            
            # Determine temperature unit
            unit_symbol = "°C" if weather_data.get("units") != "imperial" else "°F"
            
            response = f"""
Current Weather for {location}:

🌡️ Temperature: {temp}{unit_symbol} (feels like {feels_like}{unit_symbol})
🌤️ Conditions: {description}
💧 Humidity: {humidity}%
🌬️ Wind Speed: {wind_speed} m/s
📊 Pressure: {pressure} hPa
            """.strip()
            
            return response
            
        except Exception as e:
            logger.error(f"Error formatting weather response: {str(e)}")
            return f"Weather data received but could not format properly: {str(e)}"

class WeatherForecastTool(BaseTool):
    """Tool for fetching weather forecast"""
    
    name: str = "get_weather_forecast"
    description: str = """
    Get 5-day weather forecast for a specific location.
    Use this tool when users ask about future weather or forecast.
    Input should be a location (city name, city and country, etc.).
    """
    args_schema = WeatherInput
    
    def __init__(self):
        super().__init__()
        self.api_key = os.getenv("WEATHER_API_KEY")
        self.base_url = "http://api.openweathermap.org/data/2.5"
    
    async def _arun(self, location: str, units: str = "metric") -> str:
        """Async implementation of the forecast tool"""
        try:
            if not self.api_key:
                return "Weather API key not configured. Please set WEATHER_API_KEY environment variable."
            
            # Fetch forecast
            forecast_data = await self._fetch_forecast(location, units)
            
            if not forecast_data:
                return f"Could not fetch forecast for {location}. Please check the location name."
            
            # Format the response
            response = self._format_forecast_response(forecast_data, location)
            
            logger.info(f"Forecast data fetched for {location}")
            return response
            
        except Exception as e:
            logger.error(f"Error fetching forecast for {location}: {str(e)}")
            return f"Error fetching forecast: {str(e)}"
    
    def _run(self, location: str, units: str = "metric") -> str:
        """Sync implementation"""
        import asyncio
        return asyncio.run(self._arun(location, units))
    
    async def _fetch_forecast(self, location: str, units: str) -> Optional[Dict[str, Any]]:
        """Fetch forecast from OpenWeatherMap API"""
        try:
            url = f"{self.base_url}/forecast"
            params = {
                "q": location,
                "appid": self.api_key,
                "units": units
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        return await response.json()
                    elif response.status == 404:
                        logger.warning(f"Location not found: {location}")
                        return None
                    else:
                        logger.error(f"Forecast API error: {response.status}")
                        return None
                        
        except Exception as e:
            logger.error(f"Error calling forecast API: {str(e)}")
            return None
    
    def _format_forecast_response(self, forecast_data: Dict[str, Any], location: str) -> str:
        """Format forecast data into a readable response"""
        try:
            forecasts = forecast_data.get("list", [])[:5]  # Get first 5 forecasts
            
            if not forecasts:
                return f"No forecast data available for {location}"
            
            response = f"5-Day Weather Forecast for {location}:\n\n"
            
            for i, forecast in enumerate(forecasts):
                main = forecast.get("main", {})
                weather = forecast.get("weather", [{}])[0]
                
                temp = main.get("temp", "N/A")
                description = weather.get("description", "N/A").title()
                
                response += f"Day {i+1}: {temp}°C - {description}\n"
            
            return response.strip()
            
        except Exception as e:
            logger.error(f"Error formatting forecast response: {str(e)}")
            return f"Forecast data received but could not format properly: {str(e)}"
