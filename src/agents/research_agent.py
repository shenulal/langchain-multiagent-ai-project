"""
Research Agent - Specialized for information gathering and research
"""

import re
from typing import List, Any
from .base_agent import BaseAgent
from ..tools.search_tool import WebSearchTool
from ..tools.news_tool import NewsTool, TopHeadlinesTool

class ResearchAgent(BaseAgent):
    """
    Specialized agent for research and information gathering
    """
    
    def __init__(self):
        # Research-related tools
        tools = [
            WebSearchTool(),
            NewsTool(),
            TopHeadlinesTool()
        ]
        
        super().__init__(
            name="ResearchAgent",
            description="""
            I am a research specialist agent. I can help you with:
            - Finding information on any topic through web search
            - Getting the latest news and current events
            - Researching facts, statistics, and detailed information
            - Providing comprehensive answers based on multiple sources
            - Finding recent developments and updates on topics
            
            I have access to web search and news APIs to provide current information.
            """,
            tools=tools,
            model_name="gpt-3.5-turbo",
            temperature=0.4  # Balanced temperature for research
        )
        
        # Research-related keywords
        self.research_keywords = [
            'search', 'find', 'research', 'information', 'facts', 'data',
            'statistics', 'study', 'report', 'analysis', 'details',
            'explain', 'what is', 'who is', 'how does', 'why does',
            'tell me about', 'learn about', 'know about'
        ]
        
        # News-related keywords
        self.news_keywords = [
            'news', 'latest', 'recent', 'current', 'today', 'headlines',
            'breaking', 'update', 'happening', 'events', 'developments',
            'announcement', 'report', 'story', 'article'
        ]
        
        # Question patterns
        self.question_patterns = [
            r'^what\s+is\s+',
            r'^who\s+is\s+',
            r'^how\s+does\s+',
            r'^why\s+does\s+',
            r'^when\s+did\s+',
            r'^where\s+is\s+',
            r'tell\s+me\s+about',
            r'explain\s+',
            r'find\s+information',
            r'search\s+for'
        ]
    
    def can_handle_query(self, query: str) -> float:
        """
        Determine if this agent can handle the research query
        
        Args:
            query: The user query
            
        Returns:
            Confidence score (0.0 to 1.0)
        """
        query_lower = query.lower()
        confidence = 0.0
        
        # Check for research keywords
        for keyword in self.research_keywords:
            if keyword in query_lower:
                confidence += 0.15
        
        # Check for news keywords
        for keyword in self.news_keywords:
            if keyword in query_lower:
                confidence += 0.2
        
        # Check for question patterns
        for pattern in self.question_patterns:
            if re.search(pattern, query_lower):
                confidence += 0.3
                break
        
        # Boost for specific research indicators
        research_indicators = [
            'information about', 'details about', 'facts about',
            'research on', 'study of', 'analysis of'
        ]
        
        for indicator in research_indicators:
            if indicator in query_lower:
                confidence += 0.25
        
        # Check if it's a factual question
        if query.strip().endswith('?'):
            confidence += 0.1
        
        # Cap the score at 1.0
        return min(confidence, 1.0)
    
    def _is_news_query(self, query: str) -> bool:
        """
        Determine if the query is asking for news
        
        Args:
            query: The user query
            
        Returns:
            True if news is requested
        """
        query_lower = query.lower()
        
        news_indicators = [
            'news', 'latest', 'recent', 'current events', 'headlines',
            'breaking', 'today', 'happening now', 'updates'
        ]
        
        return any(indicator in query_lower for indicator in news_indicators)
    
    def _extract_search_topic(self, query: str) -> str:
        """
        Extract the main topic from a search query
        
        Args:
            query: The user query
            
        Returns:
            Cleaned search topic
        """
        # Remove common question words and phrases
        clean_query = query.lower()
        
        # Remove question starters
        question_starters = [
            'what is', 'who is', 'how does', 'why does', 'when did',
            'where is', 'tell me about', 'explain', 'find information about',
            'search for', 'look up', 'research'
        ]
        
        for starter in question_starters:
            clean_query = clean_query.replace(starter, '').strip()
        
        # Remove question marks and extra spaces
        clean_query = clean_query.replace('?', '').strip()
        clean_query = ' '.join(clean_query.split())
        
        return clean_query if clean_query else query
    
    def _categorize_news_query(self, query: str) -> str:
        """
        Categorize news query to determine the appropriate category
        
        Args:
            query: The user query
            
        Returns:
            News category
        """
        query_lower = query.lower()
        
        categories = {
            'business': ['business', 'economy', 'finance', 'market', 'stock', 'company'],
            'technology': ['technology', 'tech', 'ai', 'computer', 'software', 'internet'],
            'health': ['health', 'medical', 'medicine', 'disease', 'healthcare'],
            'science': ['science', 'research', 'discovery', 'study', 'scientific'],
            'sports': ['sports', 'football', 'basketball', 'soccer', 'game', 'team'],
            'entertainment': ['entertainment', 'movie', 'music', 'celebrity', 'film']
        }
        
        for category, keywords in categories.items():
            if any(keyword in query_lower for keyword in keywords):
                return category
        
        return 'general'
