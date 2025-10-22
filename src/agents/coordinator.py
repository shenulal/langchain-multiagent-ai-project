"""
Agent Coordinator - Manages multiple agents and routes queries
"""

import time
import asyncio
from typing import Dict, List, Any, Optional
from loguru import logger

from .base_agent import BaseAgent
from .research_agent import ResearchAgent
from .weather_agent import WeatherAgent
from .general_agent import GeneralAgent

class AgentCoordinator:
    """
    Coordinates multiple agents and routes queries to the most appropriate agent
    """
    
    def __init__(self):
        self.agents: Dict[str, BaseAgent] = {}
        self.query_history: List[Dict[str, Any]] = []
        self.initialized = False
    
    async def initialize(self):
        """Initialize all agents"""
        try:
            logger.info("Initializing Agent Coordinator...")
            
            # Create and initialize agents
            agents_to_create = [
                ResearchAgent(),
                WeatherAgent(),
                GeneralAgent()
            ]
            
            # Initialize all agents concurrently
            initialization_tasks = []
            for agent in agents_to_create:
                initialization_tasks.append(agent.initialize())
                self.agents[agent.name] = agent
            
            await asyncio.gather(*initialization_tasks)
            
            self.initialized = True
            logger.info(f"Agent Coordinator initialized with {len(self.agents)} agents")
            
        except Exception as e:
            logger.error(f"Failed to initialize Agent Coordinator: {str(e)}")
            raise
    
    async def process_query(
        self,
        query: str,
        user_id: str = "default",
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process a query by routing it to the most appropriate agent
        
        Args:
            query: The user query
            user_id: Identifier for the user
            context: Additional context for the query
            
        Returns:
            Dictionary containing response and metadata
        """
        start_time = time.time()
        
        try:
            logger.info(f"Processing query from user {user_id}: {query}")
            
            if not self.initialized:
                raise RuntimeError("Agent Coordinator not initialized")
            
            # Select the best agent for the query
            selected_agent = await self._select_agent(query)
            
            if not selected_agent:
                return {
                    "response": "I'm sorry, I couldn't find an appropriate agent to handle your request.",
                    "agent_used": "none",
                    "execution_time": time.time() - start_time,
                    "error": "No suitable agent found"
                }
            
            # Process the query with the selected agent
            result = await selected_agent.process_query(query, context)
            
            # Add coordinator metadata
            result["agent_used"] = selected_agent.name
            result["coordinator_time"] = time.time() - start_time
            result["user_id"] = user_id
            
            # Store query in history
            self._store_query_history(query, result, user_id)
            
            logger.info(f"Query processed successfully by {selected_agent.name}")
            
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            error_msg = f"Error in coordinator: {str(e)}"
            logger.error(error_msg)
            
            return {
                "response": f"I encountered an error while processing your request: {str(e)}",
                "agent_used": "coordinator",
                "execution_time": execution_time,
                "error": str(e),
                "user_id": user_id
            }
    
    async def _select_agent(self, query: str) -> Optional[BaseAgent]:
        """
        Select the most appropriate agent for the query
        
        Args:
            query: The user query
            
        Returns:
            The selected agent or None if no suitable agent found
        """
        try:
            # Get confidence scores from all agents
            agent_scores = {}
            
            for agent_name, agent in self.agents.items():
                try:
                    score = agent.can_handle_query(query)
                    agent_scores[agent_name] = score
                    logger.debug(f"Agent {agent_name} confidence: {score}")
                except Exception as e:
                    logger.warning(f"Error getting confidence from {agent_name}: {str(e)}")
                    agent_scores[agent_name] = 0.0
            
            # Select agent with highest confidence
            if not agent_scores:
                return None
            
            best_agent_name = max(agent_scores, key=agent_scores.get)
            best_score = agent_scores[best_agent_name]
            
            # Only use agent if confidence is above threshold
            if best_score < 0.3:
                logger.info(f"No agent has sufficient confidence (best: {best_score})")
                return self.agents.get("GeneralAgent")  # Fallback to general agent
            
            logger.info(f"Selected agent: {best_agent_name} (confidence: {best_score})")
            return self.agents[best_agent_name]
            
        except Exception as e:
            logger.error(f"Error selecting agent: {str(e)}")
            return self.agents.get("GeneralAgent")  # Fallback to general agent
    
    def _store_query_history(
        self,
        query: str,
        result: Dict[str, Any],
        user_id: str
    ):
        """Store query and result in history"""
        history_entry = {
            "timestamp": time.time(),
            "user_id": user_id,
            "query": query,
            "agent_used": result.get("agent_used"),
            "execution_time": result.get("execution_time"),
            "success": "error" not in result
        }
        
        self.query_history.append(history_entry)
        
        # Keep only last 100 queries
        if len(self.query_history) > 100:
            self.query_history = self.query_history[-100:]
    
    async def get_agent_status(self) -> Dict[str, Any]:
        """Get status of all agents"""
        status = {
            "coordinator_initialized": self.initialized,
            "total_agents": len(self.agents),
            "total_queries": len(self.query_history),
            "agents": {}
        }
        
        for agent_name, agent in self.agents.items():
            status["agents"][agent_name] = agent.get_status()
        
        return status
    
    def get_query_history(self, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get query history, optionally filtered by user"""
        if user_id:
            return [entry for entry in self.query_history if entry["user_id"] == user_id]
        return self.query_history.copy()
    
    async def add_agent(self, agent: BaseAgent):
        """Add a new agent to the coordinator"""
        try:
            await agent.initialize()
            self.agents[agent.name] = agent
            logger.info(f"Added new agent: {agent.name}")
        except Exception as e:
            logger.error(f"Failed to add agent {agent.name}: {str(e)}")
            raise
    
    def remove_agent(self, agent_name: str) -> bool:
        """Remove an agent from the coordinator"""
        if agent_name in self.agents:
            del self.agents[agent_name]
            logger.info(f"Removed agent: {agent_name}")
            return True
        return False
