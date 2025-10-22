"""
LangChain Multi-Agent AI Project
Main entry point for the application
"""

import os
import asyncio
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any
import uvicorn

from src.agents.coordinator import AgentCoordinator
from src.voice.speech_handler import SpeechHandler
from src.utils.logger import setup_logger

# Load environment variables
load_dotenv()

# Setup logging
logger = setup_logger()

# Initialize FastAPI app
app = FastAPI(
    title="LangChain Multi-Agent AI System",
    description="A multi-agent AI system with voice and text input capabilities",
    version="1.0.0"
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Request/Response models
class TextQuery(BaseModel):
    query: str
    user_id: Optional[str] = "default"

class QueryResponse(BaseModel):
    response: str
    agent_used: str
    execution_time: float
    metadata: Optional[Dict[str, Any]] = None

# Global instances
coordinator = None
speech_handler = None

@app.on_event("startup")
async def startup_event():
    """Initialize the application components"""
    global coordinator, speech_handler
    
    logger.info("Starting LangChain Multi-Agent AI System...")
    
    # Initialize agent coordinator
    coordinator = AgentCoordinator()
    await coordinator.initialize()
    
    # Initialize speech handler
    speech_handler = SpeechHandler()
    
    logger.info("Application startup complete!")

@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the main interface"""
    return FileResponse("templates/index.html")

@app.post("/query/text", response_model=QueryResponse)
async def process_text_query(query: TextQuery):
    """Process a text-based query"""
    try:
        logger.info(f"Processing text query: {query.query}")
        
        result = await coordinator.process_query(query.query, query.user_id)
        
        return QueryResponse(
            response=result["response"],
            agent_used=result["agent_used"],
            execution_time=result["execution_time"],
            metadata=result.get("metadata", {})
        )
    
    except Exception as e:
        logger.error(f"Error processing text query: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/query/voice")
async def process_voice_query(audio_file: UploadFile = File(...)):
    """Process a voice-based query"""
    try:
        logger.info("Processing voice query")
        
        # Convert audio to text
        audio_content = await audio_file.read()
        text_query = await speech_handler.speech_to_text(audio_content)
        
        # Process the query
        result = await coordinator.process_query(text_query, "voice_user")
        
        # Convert response to speech
        audio_response = await speech_handler.text_to_speech(result["response"])
        
        return JSONResponse({
            "text_query": text_query,
            "response": result["response"],
            "agent_used": result["agent_used"],
            "execution_time": result["execution_time"],
            "audio_response": audio_response  # Base64 encoded audio
        })
    
    except Exception as e:
        logger.error(f"Error processing voice query: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "agents": await coordinator.get_agent_status()}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=os.getenv("APP_HOST", "localhost"),
        port=int(os.getenv("APP_PORT", 8000)),
        reload=True
    )
