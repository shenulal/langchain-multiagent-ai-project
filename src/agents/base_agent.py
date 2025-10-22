"""
Base agent class for the multi-agent system
"""

import time
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from langchain.schema import BaseMessage
from loguru import logger

class BaseAgent(ABC):
    """
    Abstract base class for all agents in the system
    """
    
    def __init__(
        self,
        name: str,
        description: str,
        tools: List[Any],
        model_name: str = "gpt-3.5-turbo",
        temperature: float = 0.7
    ):
        self.name = name
        self.description = description
        self.tools = tools
        self.model_name = model_name
        self.temperature = temperature
        self.llm = None
        self.agent_executor = None
        self.conversation_history: List[BaseMessage] = []
        
    async def initialize(self):
        """Initialize the agent with LLM and tools"""
        try:
            # Initialize the language model
            self.llm = ChatOpenAI(
                model=self.model_name,
                temperature=self.temperature
            )
            
            # Create the agent prompt
            prompt = self._create_prompt()
            
            # Create the agent
            agent = create_openai_functions_agent(
                llm=self.llm,
                tools=self.tools,
                prompt=prompt
            )
            
            # Create agent executor
            self.agent_executor = AgentExecutor(
                agent=agent,
                tools=self.tools,
                verbose=True,
                return_intermediate_steps=True,
                max_iterations=5
            )
            
            logger.info(f"Agent {self.name} initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize agent {self.name}: {str(e)}")
            raise
    
    def _create_prompt(self) -> ChatPromptTemplate:
        """Create the prompt template for the agent"""
        system_message = f"""
        You are {self.name}, a specialized AI agent.
        
        Description: {self.description}
        
        Your role is to help users by using the available tools effectively.
        Always be helpful, accurate, and provide clear explanations.
        
        Available tools: {[tool.name for tool in self.tools]}
        
        When using tools:
        1. Choose the most appropriate tool for the task
        2. Provide clear reasoning for your tool selection
        3. Handle errors gracefully and suggest alternatives
        4. Always verify the results before responding
        """
        
        return ChatPromptTemplate.from_messages([
            ("system", system_message),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad")
        ])
    
    async def process_query(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process a query using the agent
        
        Args:
            query: The user query
            context: Additional context for the query
            
        Returns:
            Dictionary containing response and metadata
        """
        start_time = time.time()
        
        try:
            logger.info(f"Agent {self.name} processing query: {query}")
            
            # Prepare input for the agent
            agent_input = {
                "input": query,
                "chat_history": self.conversation_history
            }
            
            # Add context if provided
            if context:
                agent_input["context"] = context
            
            # Execute the agent
            result = await self.agent_executor.ainvoke(agent_input)
            
            execution_time = time.time() - start_time
            
            # Extract response and intermediate steps
            response = result.get("output", "I couldn't process your request.")
            intermediate_steps = result.get("intermediate_steps", [])
            
            # Update conversation history
            self._update_conversation_history(query, response)
            
            logger.info(f"Agent {self.name} completed query in {execution_time:.2f}s")
            
            return {
                "response": response,
                "agent_name": self.name,
                "execution_time": execution_time,
                "intermediate_steps": intermediate_steps,
                "tools_used": [step[0].tool for step in intermediate_steps if hasattr(step[0], 'tool')]
            }
            
        except Exception as e:
            execution_time = time.time() - start_time
            error_msg = f"Error in agent {self.name}: {str(e)}"
            logger.error(error_msg)
            
            return {
                "response": f"I encountered an error while processing your request: {str(e)}",
                "agent_name": self.name,
                "execution_time": execution_time,
                "error": str(e)
            }
    
    def _update_conversation_history(self, query: str, response: str):
        """Update the conversation history"""
        from langchain.schema import HumanMessage, AIMessage
        
        self.conversation_history.append(HumanMessage(content=query))
        self.conversation_history.append(AIMessage(content=response))
        
        # Keep only last 10 messages to prevent context overflow
        if len(self.conversation_history) > 10:
            self.conversation_history = self.conversation_history[-10:]
    
    @abstractmethod
    def can_handle_query(self, query: str) -> float:
        """
        Determine if this agent can handle the given query
        
        Args:
            query: The user query
            
        Returns:
            Confidence score (0.0 to 1.0)
        """
        pass
    
    def get_status(self) -> Dict[str, Any]:
        """Get the current status of the agent"""
        return {
            "name": self.name,
            "description": self.description,
            "tools": [tool.name for tool in self.tools],
            "model": self.model_name,
            "initialized": self.agent_executor is not None,
            "conversation_length": len(self.conversation_history)
        }
