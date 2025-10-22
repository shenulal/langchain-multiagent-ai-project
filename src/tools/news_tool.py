"""
News API tool for fetching latest news
"""

import os
import aiohttp
from typing import Dict, Any, Optional, List
from langchain.tools import BaseTool
from pydantic import BaseModel, Field
from loguru import logger
from datetime import datetime

class NewsInput(BaseModel):
    """Input schema for news tool"""
    query: str = Field(description="Search query for news articles")
    category: str = Field(default="general", description="News category (business, entertainment, general, health, science, sports, technology)")
    country: str = Field(default="us", description="Country code for news (us, gb, ca, etc.)")

class NewsTool(BaseTool):
    """Tool for fetching latest news articles"""
    
    name: str = "get_news"
    description: str = """
    Get latest news articles based on a search query or category.
    Use this tool when users ask about current events, news, or specific topics in the news.
    You can search by keywords or get news from specific categories.
    """
    args_schema = NewsInput
    
    def __init__(self):
        super().__init__()
        self.api_key = os.getenv("NEWS_API_KEY")
        self.base_url = "https://newsapi.org/v2"
    
    async def _arun(self, query: str, category: str = "general", country: str = "us") -> str:
        """Async implementation of the news tool"""
        try:
            if not self.api_key:
                return "News API key not configured. Please set NEWS_API_KEY environment variable."
            
            # Fetch news articles
            articles = await self._fetch_news(query, category, country)
            
            if not articles:
                return f"Could not fetch news for query: {query}"
            
            # Format the response
            response = self._format_news_response(articles, query)
            
            logger.info(f"News data fetched for query: {query}")
            return response
            
        except Exception as e:
            logger.error(f"Error fetching news for query {query}: {str(e)}")
            return f"Error fetching news: {str(e)}"
    
    def _run(self, query: str, category: str = "general", country: str = "us") -> str:
        """Sync implementation"""
        import asyncio
        return asyncio.run(self._arun(query, category, country))
    
    async def _fetch_news(self, query: str, category: str, country: str) -> Optional[List[Dict[str, Any]]]:
        """Fetch news from NewsAPI"""
        try:
            # Use search endpoint if query is provided, otherwise use top headlines
            if query and query.strip():
                url = f"{self.base_url}/everything"
                params = {
                    "q": query,
                    "apiKey": self.api_key,
                    "sortBy": "publishedAt",
                    "pageSize": 5,
                    "language": "en"
                }
            else:
                url = f"{self.base_url}/top-headlines"
                params = {
                    "apiKey": self.api_key,
                    "category": category,
                    "country": country,
                    "pageSize": 5
                }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get("articles", [])
                    else:
                        logger.error(f"News API error: {response.status}")
                        return None
                        
        except Exception as e:
            logger.error(f"Error calling news API: {str(e)}")
            return None
    
    def _format_news_response(self, articles: List[Dict[str, Any]], query: str) -> str:
        """Format news articles into a readable response"""
        try:
            if not articles:
                return f"No news articles found for: {query}"
            
            response = f"Latest News for '{query}':\n\n"
            
            for i, article in enumerate(articles[:5], 1):
                title = article.get("title", "No title")
                description = article.get("description", "No description")
                source = article.get("source", {}).get("name", "Unknown source")
                published_at = article.get("publishedAt", "")
                url = article.get("url", "")
                
                # Format publication date
                if published_at:
                    try:
                        pub_date = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
                        formatted_date = pub_date.strftime("%Y-%m-%d %H:%M")
                    except:
                        formatted_date = published_at
                else:
                    formatted_date = "Unknown date"
                
                response += f"{i}. {title}\n"
                response += f"   Source: {source} | {formatted_date}\n"
                if description:
                    response += f"   {description[:150]}{'...' if len(description) > 150 else ''}\n"
                if url:
                    response += f"   Link: {url}\n"
                response += "\n"
            
            return response.strip()
            
        except Exception as e:
            logger.error(f"Error formatting news response: {str(e)}")
            return f"News data received but could not format properly: {str(e)}"

class TopHeadlinesTool(BaseTool):
    """Tool for fetching top headlines"""
    
    name: str = "get_top_headlines"
    description: str = """
    Get top news headlines from a specific country or category.
    Use this tool when users ask for general news, top stories, or headlines.
    """
    
    def __init__(self):
        super().__init__()
        self.api_key = os.getenv("NEWS_API_KEY")
        self.base_url = "https://newsapi.org/v2"
    
    async def _arun(self, category: str = "general", country: str = "us") -> str:
        """Async implementation of the top headlines tool"""
        try:
            if not self.api_key:
                return "News API key not configured. Please set NEWS_API_KEY environment variable."
            
            # Fetch top headlines
            articles = await self._fetch_top_headlines(category, country)
            
            if not articles:
                return f"Could not fetch top headlines for category: {category}"
            
            # Format the response
            response = self._format_headlines_response(articles, category, country)
            
            logger.info(f"Top headlines fetched for category: {category}")
            return response
            
        except Exception as e:
            logger.error(f"Error fetching top headlines: {str(e)}")
            return f"Error fetching top headlines: {str(e)}"
    
    def _run(self, category: str = "general", country: str = "us") -> str:
        """Sync implementation"""
        import asyncio
        return asyncio.run(self._arun(category, country))
    
    async def _fetch_top_headlines(self, category: str, country: str) -> Optional[List[Dict[str, Any]]]:
        """Fetch top headlines from NewsAPI"""
        try:
            url = f"{self.base_url}/top-headlines"
            params = {
                "apiKey": self.api_key,
                "category": category,
                "country": country,
                "pageSize": 5
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get("articles", [])
                    else:
                        logger.error(f"Headlines API error: {response.status}")
                        return None
                        
        except Exception as e:
            logger.error(f"Error calling headlines API: {str(e)}")
            return None
    
    def _format_headlines_response(self, articles: List[Dict[str, Any]], category: str, country: str) -> str:
        """Format headlines into a readable response"""
        try:
            if not articles:
                return f"No headlines found for category: {category}"
            
            response = f"Top {category.title()} Headlines ({country.upper()}):\n\n"
            
            for i, article in enumerate(articles, 1):
                title = article.get("title", "No title")
                source = article.get("source", {}).get("name", "Unknown source")
                
                response += f"{i}. {title}\n"
                response += f"   Source: {source}\n\n"
            
            return response.strip()
            
        except Exception as e:
            logger.error(f"Error formatting headlines response: {str(e)}")
            return f"Headlines data received but could not format properly: {str(e)}"
