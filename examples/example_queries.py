"""
Example queries to test the multi-agent system
"""

import asyncio
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from agents.coordinator import AgentCoordinator

class ExampleQueries:
    """Example queries for testing the system"""
    
    def __init__(self):
        self.coordinator = AgentCoordinator()
    
    async def run_examples(self):
        """Run example queries"""
        print("🤖 Initializing LangChain Multi-Agent System...")
        
        try:
            await self.coordinator.initialize()
            print("✅ System initialized successfully!\n")
        except Exception as e:
            print(f"❌ Failed to initialize system: {e}")
            return
        
        # Example queries for different agents
        examples = [
            # Weather Agent Examples
            {
                "query": "What's the weather like in London today?",
                "expected_agent": "WeatherAgent",
                "description": "Current weather query"
            },
            {
                "query": "Will it rain tomorrow in New York?",
                "expected_agent": "WeatherAgent", 
                "description": "Weather forecast query"
            },
            
            # Research Agent Examples
            {
                "query": "What is artificial intelligence?",
                "expected_agent": "ResearchAgent",
                "description": "Information research query"
            },
            {
                "query": "Latest news about technology",
                "expected_agent": "ResearchAgent",
                "description": "News query"
            },
            {
                "query": "Tell me about quantum computing",
                "expected_agent": "ResearchAgent",
                "description": "Research query"
            },
            
            # General Agent Examples
            {
                "query": "Calculate 15% of 250",
                "expected_agent": "GeneralAgent",
                "description": "Mathematical calculation"
            },
            {
                "query": "What time is it?",
                "expected_agent": "GeneralAgent",
                "description": "Time query"
            },
            {
                "query": "Hello, how are you?",
                "expected_agent": "GeneralAgent",
                "description": "Greeting/conversation"
            }
        ]
        
        print("🧪 Running example queries...\n")
        
        for i, example in enumerate(examples, 1):
            print(f"{'='*60}")
            print(f"Example {i}: {example['description']}")
            print(f"Query: \"{example['query']}\"")
            print(f"Expected Agent: {example['expected_agent']}")
            print(f"{'='*60}")
            
            try:
                # Process the query
                result = await self.coordinator.process_query(example['query'])
                
                # Display results
                print(f"✅ Selected Agent: {result['agent_used']}")
                print(f"⏱️  Execution Time: {result['execution_time']:.2f}s")
                print(f"📝 Response: {result['response'][:200]}...")
                
                # Check if correct agent was selected
                if result['agent_used'] == example['expected_agent']:
                    print("✅ Correct agent selected!")
                else:
                    print(f"⚠️  Expected {example['expected_agent']}, got {result['agent_used']}")
                
            except Exception as e:
                print(f"❌ Error processing query: {e}")
            
            print("\n")
        
        # Display system status
        print("📊 System Status:")
        status = await self.coordinator.get_agent_status()
        print(f"Total Agents: {status['total_agents']}")
        print(f"Total Queries Processed: {status['total_queries']}")
        
        for agent_name, agent_status in status['agents'].items():
            print(f"  {agent_name}: {'✅' if agent_status['initialized'] else '❌'}")

async def main():
    """Main function to run examples"""
    examples = ExampleQueries()
    await examples.run_examples()

if __name__ == "__main__":
    # Set up environment variables for testing (optional)
    os.environ.setdefault("OPENAI_API_KEY", "your-api-key-here")
    os.environ.setdefault("WEATHER_API_KEY", "your-weather-api-key-here")
    os.environ.setdefault("NEWS_API_KEY", "your-news-api-key-here")
    
    print("🚀 LangChain Multi-Agent System - Example Queries")
    print("=" * 60)
    print("Note: Make sure to set your API keys in the .env file")
    print("=" * 60)
    
    asyncio.run(main())
