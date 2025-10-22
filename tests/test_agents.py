"""
Test cases for the multi-agent system
"""

import pytest
import asyncio
from unittest.mock import Mock, patch
import os
import sys

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from agents.weather_agent import WeatherAgent
from agents.research_agent import ResearchAgent
from agents.general_agent import GeneralAgent
from agents.coordinator import AgentCoordinator

class TestWeatherAgent:
    """Test cases for WeatherAgent"""
    
    def setup_method(self):
        """Setup for each test method"""
        self.agent = WeatherAgent()
    
    def test_can_handle_weather_queries(self):
        """Test weather query detection"""
        # High confidence queries
        assert self.agent.can_handle_query("What's the weather in London?") > 0.7
        assert self.agent.can_handle_query("Temperature in New York") > 0.5
        assert self.agent.can_handle_query("Will it rain tomorrow?") > 0.5
        
        # Low confidence queries
        assert self.agent.can_handle_query("What is Python programming?") < 0.3
        assert self.agent.can_handle_query("Latest news") < 0.3
    
    def test_location_extraction(self):
        """Test location extraction from queries"""
        assert "London" in self.agent._extract_location("Weather in London")
        assert "New York" in self.agent._extract_location("What's the temperature in New York?")
        assert "Paris" in self.agent._extract_location("Paris weather forecast")
    
    def test_forecast_detection(self):
        """Test forecast query detection"""
        assert self.agent._is_forecast_query("Weather forecast for tomorrow")
        assert self.agent._is_forecast_query("Will it rain next week?")
        assert not self.agent._is_forecast_query("Current weather in London")

class TestResearchAgent:
    """Test cases for ResearchAgent"""
    
    def setup_method(self):
        """Setup for each test method"""
        self.agent = ResearchAgent()
    
    def test_can_handle_research_queries(self):
        """Test research query detection"""
        # High confidence queries
        assert self.agent.can_handle_query("What is artificial intelligence?") > 0.7
        assert self.agent.can_handle_query("Latest news about technology") > 0.7
        assert self.agent.can_handle_query("Tell me about quantum computing") > 0.5
        
        # Low confidence queries
        assert self.agent.can_handle_query("What's the weather?") < 0.3
        assert self.agent.can_handle_query("Calculate 2 + 2") < 0.3
    
    def test_news_query_detection(self):
        """Test news query detection"""
        assert self.agent._is_news_query("Latest news")
        assert self.agent._is_news_query("Current events")
        assert self.agent._is_news_query("Breaking news about AI")
        assert not self.agent._is_news_query("What is machine learning?")
    
    def test_search_topic_extraction(self):
        """Test search topic extraction"""
        assert "artificial intelligence" in self.agent._extract_search_topic("What is artificial intelligence?")
        assert "quantum computing" in self.agent._extract_search_topic("Tell me about quantum computing")
    
    def test_news_categorization(self):
        """Test news category detection"""
        assert self.agent._categorize_news_query("Technology news") == "technology"
        assert self.agent._categorize_news_query("Business updates") == "business"
        assert self.agent._categorize_news_query("Sports scores") == "sports"
        assert self.agent._categorize_news_query("General news") == "general"

class TestGeneralAgent:
    """Test cases for GeneralAgent"""
    
    def setup_method(self):
        """Setup for each test method"""
        self.agent = GeneralAgent()
    
    def test_can_handle_general_queries(self):
        """Test general query detection"""
        # Math queries
        assert self.agent.can_handle_query("Calculate 2 + 2") > 0.5
        assert self.agent.can_handle_query("What is 15% of 100?") > 0.5
        
        # Time queries
        assert self.agent.can_handle_query("What time is it?") > 0.5
        assert self.agent.can_handle_query("Current date") > 0.5
        
        # Greetings
        assert self.agent.can_handle_query("Hello") > 0.3
        assert self.agent.can_handle_query("How are you?") > 0.3
    
    def test_math_expression_detection(self):
        """Test mathematical expression detection"""
        assert self.agent._contains_math_expression("2 + 2")
        assert self.agent._contains_math_expression("15% of 100")
        assert self.agent._contains_math_expression("(5 * 3) / 2")
        assert not self.agent._contains_math_expression("Hello world")
    
    def test_greeting_detection(self):
        """Test greeting detection"""
        assert self.agent._is_greeting("Hello")
        assert self.agent._is_greeting("Hi there")
        assert self.agent._is_greeting("Good morning")
        assert not self.agent._is_greeting("Calculate 2 + 2")
    
    def test_time_query_detection(self):
        """Test time query detection"""
        assert self.agent._is_time_query("What time is it?")
        assert self.agent._is_time_query("Current date")
        assert self.agent._is_time_query("What day is it today?")
        assert not self.agent._is_time_query("Weather forecast")

class TestAgentCoordinator:
    """Test cases for AgentCoordinator"""
    
    def setup_method(self):
        """Setup for each test method"""
        self.coordinator = AgentCoordinator()
    
    @pytest.mark.asyncio
    async def test_coordinator_initialization(self):
        """Test coordinator initialization"""
        # Mock the agent initialization to avoid API calls
        with patch.object(WeatherAgent, 'initialize'), \
             patch.object(ResearchAgent, 'initialize'), \
             patch.object(GeneralAgent, 'initialize'):
            
            await self.coordinator.initialize()
            assert self.coordinator.initialized
            assert len(self.coordinator.agents) == 3
            assert "WeatherAgent" in self.coordinator.agents
            assert "ResearchAgent" in self.coordinator.agents
            assert "GeneralAgent" in self.coordinator.agents
    
    @pytest.mark.asyncio
    async def test_agent_selection(self):
        """Test agent selection logic"""
        # Mock agents
        weather_agent = Mock()
        weather_agent.can_handle_query.return_value = 0.9
        weather_agent.name = "WeatherAgent"
        
        research_agent = Mock()
        research_agent.can_handle_query.return_value = 0.2
        research_agent.name = "ResearchAgent"
        
        general_agent = Mock()
        general_agent.can_handle_query.return_value = 0.3
        general_agent.name = "GeneralAgent"
        
        self.coordinator.agents = {
            "WeatherAgent": weather_agent,
            "ResearchAgent": research_agent,
            "GeneralAgent": general_agent
        }
        
        selected = await self.coordinator._select_agent("Weather in London")
        assert selected == weather_agent
    
    def test_query_history_storage(self):
        """Test query history functionality"""
        # Mock result
        result = {
            "agent_used": "WeatherAgent",
            "execution_time": 1.5
        }
        
        self.coordinator._store_query_history("Test query", result, "user123")
        
        assert len(self.coordinator.query_history) == 1
        assert self.coordinator.query_history[0]["query"] == "Test query"
        assert self.coordinator.query_history[0]["user_id"] == "user123"
    
    def test_get_query_history_filtering(self):
        """Test query history filtering by user"""
        # Add some test history
        self.coordinator.query_history = [
            {"user_id": "user1", "query": "Query 1"},
            {"user_id": "user2", "query": "Query 2"},
            {"user_id": "user1", "query": "Query 3"}
        ]
        
        user1_history = self.coordinator.get_query_history("user1")
        assert len(user1_history) == 2
        
        all_history = self.coordinator.get_query_history()
        assert len(all_history) == 3

if __name__ == "__main__":
    pytest.main([__file__])
