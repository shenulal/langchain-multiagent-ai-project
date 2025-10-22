"""
Weather Agent - Specialized for weather-related queries
"""

import re
from typing import List, Any
from .base_agent import BaseAgent
from ..tools.weather_tool import WeatherTool, WeatherForecastTool

class WeatherAgent(BaseAgent):
    """
    Specialized agent for handling weather-related queries
    """
    
    def __init__(self):
        # Weather-related tools
        tools = [
            WeatherTool(),
            WeatherForecastTool()
        ]
        
        super().__init__(
            name="WeatherAgent",
            description="""
            I am a weather specialist agent. I can help you with:
            - Current weather conditions for any location
            - Weather forecasts for the next few days
            - Temperature, humidity, wind speed, and other weather data
            - Weather-related advice and information
            
            I have access to real-time weather data from reliable sources.
            """,
            tools=tools,
            model_name="gpt-3.5-turbo",
            temperature=0.3  # Lower temperature for more factual responses
        )
        
        # Weather-related keywords for query classification
        self.weather_keywords = [
            'weather', 'temperature', 'rain', 'snow', 'sunny', 'cloudy',
            'forecast', 'humidity', 'wind', 'storm', 'hot', 'cold',
            'degrees', 'celsius', 'fahrenheit', 'precipitation', 'climate',
            'meteorology', 'atmospheric', 'barometric', 'pressure'
        ]
        
        # Location indicators
        self.location_patterns = [
            r'\bin\s+([A-Za-z\s,]+)',
            r'\bat\s+([A-Za-z\s,]+)',
            r'\bfor\s+([A-Za-z\s,]+)',
            r'([A-Za-z\s,]+)\s+weather',
            r'weather\s+in\s+([A-Za-z\s,]+)'
        ]
    
    def can_handle_query(self, query: str) -> float:
        """
        Determine if this agent can handle the weather query
        
        Args:
            query: The user query
            
        Returns:
            Confidence score (0.0 to 1.0)
        """
        query_lower = query.lower()
        
        # Check for weather keywords
        weather_score = 0.0
        for keyword in self.weather_keywords:
            if keyword in query_lower:
                weather_score += 0.2
        
        # Boost score if location is mentioned
        location_mentioned = any(
            re.search(pattern, query_lower) 
            for pattern in self.location_patterns
        )
        
        if location_mentioned:
            weather_score += 0.3
        
        # Check for forecast-specific terms
        forecast_terms = ['forecast', 'tomorrow', 'next week', 'upcoming', 'future']
        if any(term in query_lower for term in forecast_terms):
            weather_score += 0.2
        
        # Cap the score at 1.0
        return min(weather_score, 1.0)
    
    def _extract_location(self, query: str) -> str:
        """
        Extract location from the query
        
        Args:
            query: The user query
            
        Returns:
            Extracted location or default
        """
        query_lower = query.lower()
        
        # Try different patterns to extract location
        for pattern in self.location_patterns:
            match = re.search(pattern, query_lower)
            if match:
                location = match.group(1).strip()
                # Clean up the location
                location = re.sub(r'[^\w\s,]', '', location)
                if location and len(location) > 1:
                    return location.title()
        
        # Default location if none found
        return "New York"
    
    def _is_forecast_query(self, query: str) -> bool:
        """
        Determine if the query is asking for a forecast
        
        Args:
            query: The user query
            
        Returns:
            True if forecast is requested
        """
        forecast_indicators = [
            'forecast', 'tomorrow', 'next', 'upcoming', 'future',
            'will be', 'going to be', 'expect', 'prediction',
            'days', 'week', 'weekend'
        ]
        
        query_lower = query.lower()
        return any(indicator in query_lower for indicator in forecast_indicators)
