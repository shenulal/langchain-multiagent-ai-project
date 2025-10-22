"""
Web search tool for general information retrieval
"""

import aiohttp
from typing import Dict, Any, Optional, List
from langchain.tools import BaseTool
from pydantic import BaseModel, Field
from loguru import logger
import json

class SearchInput(BaseModel):
    """Input schema for search tool"""
    query: str = Field(description="Search query to find information on the web")
    num_results: int = Field(default=5, description="Number of search results to return")

class WebSearchTool(BaseTool):
    """Tool for performing web searches"""
    
    name: str = "web_search"
    description: str = """
    Search the web for information on any topic.
    Use this tool when users ask questions that require current information,
    facts, or general knowledge that might not be in your training data.
    """
    args_schema = SearchInput
    
    def __init__(self):
        super().__init__()
        # Using DuckDuckGo Instant Answer API (free, no API key required)
        self.search_url = "https://api.duckduckgo.com/"
    
    async def _arun(self, query: str, num_results: int = 5) -> str:
        """Async implementation of the search tool"""
        try:
            # Fetch search results
            results = await self._perform_search(query)
            
            if not results:
                return f"Could not find search results for: {query}"
            
            # Format the response
            response = self._format_search_response(results, query)
            
            logger.info(f"Web search completed for query: {query}")
            return response
            
        except Exception as e:
            logger.error(f"Error performing web search for {query}: {str(e)}")
            return f"Error performing web search: {str(e)}"
    
    def _run(self, query: str, num_results: int = 5) -> str:
        """Sync implementation"""
        import asyncio
        return asyncio.run(self._arun(query, num_results))
    
    async def _perform_search(self, query: str) -> Optional[Dict[str, Any]]:
        """Perform search using DuckDuckGo Instant Answer API"""
        try:
            params = {
                "q": query,
                "format": "json",
                "no_html": "1",
                "skip_disambig": "1"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(self.search_url, params=params) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        logger.error(f"Search API error: {response.status}")
                        return None
                        
        except Exception as e:
            logger.error(f"Error calling search API: {str(e)}")
            return None
    
    def _format_search_response(self, results: Dict[str, Any], query: str) -> str:
        """Format search results into a readable response"""
        try:
            response = f"Search Results for '{query}':\n\n"
            
            # Get instant answer if available
            instant_answer = results.get("InstantAnswer")
            if instant_answer:
                response += f"Quick Answer: {instant_answer}\n\n"
            
            # Get abstract if available
            abstract = results.get("Abstract")
            if abstract:
                response += f"Summary: {abstract}\n"
                abstract_source = results.get("AbstractSource")
                if abstract_source:
                    response += f"Source: {abstract_source}\n"
                response += "\n"
            
            # Get definition if available
            definition = results.get("Definition")
            if definition:
                response += f"Definition: {definition}\n"
                definition_source = results.get("DefinitionSource")
                if definition_source:
                    response += f"Source: {definition_source}\n"
                response += "\n"
            
            # Get related topics
            related_topics = results.get("RelatedTopics", [])
            if related_topics:
                response += "Related Information:\n"
                for i, topic in enumerate(related_topics[:3], 1):
                    if isinstance(topic, dict):
                        text = topic.get("Text", "")
                        if text:
                            response += f"{i}. {text[:200]}{'...' if len(text) > 200 else ''}\n"
                response += "\n"
            
            # If no useful information found
            if not any([instant_answer, abstract, definition, related_topics]):
                response += "No detailed information found. You may want to try a more specific search query.\n"
            
            return response.strip()
            
        except Exception as e:
            logger.error(f"Error formatting search response: {str(e)}")
            return f"Search completed but could not format results properly: {str(e)}"

class CalculatorTool(BaseTool):
    """Tool for performing mathematical calculations"""
    
    name: str = "calculator"
    description: str = """
    Perform mathematical calculations and solve math problems.
    Use this tool when users ask for calculations, math problems, or numerical computations.
    Supports basic arithmetic, percentages, and simple mathematical expressions.
    """
    
    def _run(self, expression: str) -> str:
        """Perform calculation"""
        try:
            # Clean the expression
            expression = expression.strip()
            
            # Basic security check - only allow safe characters
            allowed_chars = set("0123456789+-*/().% ")
            if not all(c in allowed_chars for c in expression):
                return "Invalid characters in expression. Only numbers and basic operators (+, -, *, /, %, parentheses) are allowed."
            
            # Handle percentage
            if "%" in expression:
                expression = expression.replace("%", "/100")
            
            # Evaluate the expression safely
            result = eval(expression)
            
            return f"Result: {result}"
            
        except ZeroDivisionError:
            return "Error: Division by zero"
        except SyntaxError:
            return "Error: Invalid mathematical expression"
        except Exception as e:
            return f"Error calculating: {str(e)}"
    
    async def _arun(self, expression: str) -> str:
        """Async implementation"""
        return self._run(expression)

class DateTimeTool(BaseTool):
    """Tool for getting current date and time information"""
    
    name: str = "get_datetime"
    description: str = """
    Get current date and time information.
    Use this tool when users ask about the current date, time, day of the week, etc.
    """
    
    def _run(self, query: str = "") -> str:
        """Get current date and time"""
        try:
            from datetime import datetime
            import pytz
            
            now = datetime.now()
            utc_now = datetime.utcnow()
            
            response = f"""
Current Date and Time:

Local Time: {now.strftime('%Y-%m-%d %H:%M:%S')}
UTC Time: {utc_now.strftime('%Y-%m-%d %H:%M:%S')}
Day of Week: {now.strftime('%A')}
Month: {now.strftime('%B')}
Year: {now.year}
            """.strip()
            
            return response
            
        except Exception as e:
            return f"Error getting date/time: {str(e)}"
    
    async def _arun(self, query: str = "") -> str:
        """Async implementation"""
        return self._run(query)
