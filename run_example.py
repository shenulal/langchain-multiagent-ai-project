#!/usr/bin/env python3
"""
Quick start script for LangChain Multi-Agent AI System
"""

import os
import sys
import asyncio
import subprocess
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version.split()[0]}")
    return True

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import fastapi
        import langchain
        import openai
        print("✅ Core dependencies found")
        return True
    except ImportError as e:
        print(f"❌ Missing dependencies: {e}")
        print("Run: pip install -r requirements.txt")
        return False

def check_env_file():
    """Check if .env file exists and has required keys"""
    env_path = Path(".env")
    if not env_path.exists():
        print("⚠️  .env file not found")
        print("Creating .env from template...")
        
        # Copy .env.example to .env
        example_path = Path(".env.example")
        if example_path.exists():
            with open(example_path, 'r') as src, open(env_path, 'w') as dst:
                dst.write(src.read())
            print("✅ Created .env file from template")
            print("📝 Please edit .env file with your API keys")
        else:
            print("❌ .env.example not found")
            return False
    
    # Check for OpenAI API key
    with open(env_path, 'r') as f:
        content = f.read()
        if "your_openai_api_key_here" in content:
            print("⚠️  Please set your OPENAI_API_KEY in .env file")
            return False
    
    print("✅ .env file configured")
    return True

def create_directories():
    """Create necessary directories"""
    dirs = ["logs", "static", "templates"]
    for dir_name in dirs:
        Path(dir_name).mkdir(exist_ok=True)
    print("✅ Directories created")

async def test_system():
    """Test the system with a simple query"""
    print("\n🧪 Testing system...")
    
    try:
        # Import after ensuring dependencies
        sys.path.insert(0, 'src')
        from agents.coordinator import AgentCoordinator
        
        coordinator = AgentCoordinator()
        await coordinator.initialize()
        
        # Test with a simple query
        result = await coordinator.process_query("Hello, how are you?")
        
        if result and 'response' in result:
            print("✅ System test passed")
            print(f"Response: {result['response'][:100]}...")
            return True
        else:
            print("❌ System test failed - no response")
            return False
            
    except Exception as e:
        print(f"❌ System test failed: {e}")
        return False

def start_server():
    """Start the FastAPI server"""
    print("\n🚀 Starting server...")
    print("Server will be available at: http://localhost:8000")
    print("Press Ctrl+C to stop the server")
    
    try:
        subprocess.run([sys.executable, "main.py"], check=True)
    except KeyboardInterrupt:
        print("\n👋 Server stopped")
    except subprocess.CalledProcessError as e:
        print(f"❌ Server failed to start: {e}")

def main():
    """Main function"""
    print("🤖 LangChain Multi-Agent AI System - Quick Start")
    print("=" * 60)
    
    # Check prerequisites
    if not check_python_version():
        return
    
    if not check_dependencies():
        print("\n📦 Installing dependencies...")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                         check=True)
            print("✅ Dependencies installed")
        except subprocess.CalledProcessError:
            print("❌ Failed to install dependencies")
            return
    
    if not check_env_file():
        print("\n⚠️  Please configure your .env file with API keys and run again")
        return
    
    create_directories()
    
    # Ask user what they want to do
    print("\n🎯 What would you like to do?")
    print("1. Test the system (quick test)")
    print("2. Start the web server")
    print("3. Run example queries")
    print("4. Run unit tests")
    
    choice = input("\nEnter your choice (1-4): ").strip()
    
    if choice == "1":
        print("\n🧪 Running system test...")
        asyncio.run(test_system())
        
    elif choice == "2":
        start_server()
        
    elif choice == "3":
        print("\n📝 Running example queries...")
        try:
            subprocess.run([sys.executable, "examples/example_queries.py"], check=True)
        except subprocess.CalledProcessError:
            print("❌ Failed to run examples")
            
    elif choice == "4":
        print("\n🧪 Running unit tests...")
        try:
            subprocess.run([sys.executable, "-m", "pytest", "tests/", "-v"], check=True)
        except subprocess.CalledProcessError:
            print("❌ Tests failed")
            
    else:
        print("❌ Invalid choice")

if __name__ == "__main__":
    main()
