"""
General Agent - Handles general queries and serves as fallback
"""

from typing import List, Any
from .base_agent import BaseAgent
from ..tools.search_tool import CalculatorTool, DateTimeTool

class GeneralAgent(BaseAgent):
    """
    General purpose agent that handles various types of queries
    """
    
    def __init__(self):
        # General-purpose tools
        tools = [
            CalculatorTool(),
            DateTimeTool()
        ]
        
        super().__init__(
            name="GeneralAgent",
            description="""
            I am a general assistant agent. I can help you with:
            - Mathematical calculations and problem solving
            - Date and time information
            - General questions and conversations
            - Providing explanations and assistance
            - Serving as a helpful assistant for various tasks
            
            I'm here to help when other specialized agents aren't the best fit for your query.
            """,
            tools=tools,
            model_name="gpt-3.5-turbo",
            temperature=0.7  # Higher temperature for more conversational responses
        )
        
        # Math-related keywords
        self.math_keywords = [
            'calculate', 'compute', 'math', 'mathematics', 'equation',
            'solve', 'add', 'subtract', 'multiply', 'divide', 'percentage',
            'percent', 'sum', 'total', 'average', 'mean'
        ]
        
        # Time-related keywords
        self.time_keywords = [
            'time', 'date', 'today', 'now', 'current', 'when',
            'day', 'month', 'year', 'hour', 'minute', 'clock'
        ]
        
        # General conversation keywords
        self.conversation_keywords = [
            'hello', 'hi', 'hey', 'thanks', 'thank you', 'help',
            'please', 'can you', 'would you', 'how are you'
        ]
    
    def can_handle_query(self, query: str) -> float:
        """
        Determine if this agent can handle the query
        
        Args:
            query: The user query
            
        Returns:
            Confidence score (0.0 to 1.0)
        """
        query_lower = query.lower()
        confidence = 0.0
        
        # Check for math keywords
        math_score = sum(0.2 for keyword in self.math_keywords if keyword in query_lower)
        confidence += min(math_score, 0.8)
        
        # Check for time keywords
        time_score = sum(0.2 for keyword in self.time_keywords if keyword in query_lower)
        confidence += min(time_score, 0.8)
        
        # Check for conversation keywords
        conversation_score = sum(0.1 for keyword in self.conversation_keywords if keyword in query_lower)
        confidence += min(conversation_score, 0.5)
        
        # Check for mathematical expressions
        if self._contains_math_expression(query):
            confidence += 0.6
        
        # Base confidence for general queries (fallback agent)
        if confidence == 0.0:
            confidence = 0.3  # Always willing to try as fallback
        
        # Cap the score at 1.0
        return min(confidence, 1.0)
    
    def _contains_math_expression(self, query: str) -> bool:
        """
        Check if the query contains mathematical expressions
        
        Args:
            query: The user query
            
        Returns:
            True if math expression is detected
        """
        import re
        
        # Look for mathematical patterns
        math_patterns = [
            r'\d+\s*[\+\-\*\/]\s*\d+',  # Basic arithmetic
            r'\d+\s*%',  # Percentages
            r'[\+\-\*\/\(\)]',  # Math operators
            r'\d+\.\d+',  # Decimal numbers
        ]
        
        for pattern in math_patterns:
            if re.search(pattern, query):
                return True
        
        return False
    
    def _is_greeting(self, query: str) -> bool:
        """
        Check if the query is a greeting
        
        Args:
            query: The user query
            
        Returns:
            True if it's a greeting
        """
        greetings = [
            'hello', 'hi', 'hey', 'good morning', 'good afternoon',
            'good evening', 'how are you', 'what\'s up'
        ]
        
        query_lower = query.lower().strip()
        return any(greeting in query_lower for greeting in greetings)
    
    def _is_time_query(self, query: str) -> bool:
        """
        Check if the query is asking for time/date information
        
        Args:
            query: The user query
            
        Returns:
            True if time/date is requested
        """
        time_indicators = [
            'what time', 'current time', 'what date', 'today',
            'now', 'current date', 'day is it', 'time is it'
        ]
        
        query_lower = query.lower()
        return any(indicator in query_lower for indicator in time_indicators)
    
    def _is_math_query(self, query: str) -> bool:
        """
        Check if the query is asking for mathematical calculation
        
        Args:
            query: The user query
            
        Returns:
            True if math calculation is requested
        """
        return (
            self._contains_math_expression(query) or
            any(keyword in query.lower() for keyword in self.math_keywords)
        )
