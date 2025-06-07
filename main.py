import os
import logging
import tempfile
import asyncio
from fastapi import FastAPI, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, Optional
import whisper
from langchain_groq import ChatGroq
from langchain.agents import initialize_agent, Tool
from langchain.agents import AgentExecutor
from langchain_community.utilities import GoogleSerperAPIWrapper
from dotenv import load_dotenv

# Load the .env file
load_dotenv()

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Voice AI Assistant API",
    description="Voice-driven AI assistant with transcription and web search capabilities"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load environment variables
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
SERPER_API_KEY = os.getenv("SERPER_API_KEY")
WHISPER_MODEL_SIZE = os.getenv("WHISPER_MODEL")

# Initialize models and tools globally
whisper_model = None
groq_llm = None
search_tool = None
agent_executor = None

class VoiceResponse(BaseModel):
    transcript: str
    response: str
    search_triggered: bool

async def initialize_models():
    """Initialize ML models and tools in background"""
    global whisper_model, groq_llm, search_tool, agent_executor
    
    logger.info("Initializing Whisper model...")
    whisper_model = whisper.load_model(WHISPER_MODEL_SIZE)
    
    logger.info("Initializing Groq LLM...")
    groq_llm = ChatGroq(
        model="llama3-70b-8192",
        temperature=0.7,
        groq_api_key=GROQ_API_KEY
    )
    
    logger.info("Initializing search tool...")
    search_tool = GoogleSerperAPIWrapper(serper_api_key=SERPER_API_KEY)
    
    logger.info("Creating agent executor...")
    tools = [
        Tool(
            name="WebSearch",
            func=search_tool.run,
            description=(
                "Useful for answering questions about current events, products, "
                "or topics requiring up-to-date information. Use when user asks about "
                "things that might change frequently or when you need recent data."
            )
        )
    ]
    
    agent_executor = initialize_agent(
        tools,
        groq_llm,
        agent="zero-shot-react-description",
        verbose=True,
        return_intermediate_steps=True
    )
    logger.info("All models initialized successfully")

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(initialize_models())

def transcribe_audio(file_path: str) -> str:
    """Transcribe audio using Whisper"""
    if not whisper_model:
        raise HTTPException(status_code=503, detail="Models not initialized yet")
    
    try:
        result = whisper_model.transcribe(file_path, language="en")
        return result.get("text", "").strip()
    except Exception as e:
        logger.error(f"Transcription failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Audio processing failed")

def process_query(query: str) -> Dict[str, Any]:
    """Process user query with LLM agent"""
    if not agent_executor:
        raise HTTPException(status_code=503, detail="Models not initialized yet")
    
    try:
        if not query:
            return {
                "response": "I didn't catch that. Could you please repeat?",
                "search_triggered": False
            }
        
        result = agent_executor.invoke({"input": query})
        search_triggered = any(
            step[0].tool == "WebSearch" 
            for step in result.get("intermediate_steps", [])
        )
        
        return {
            "response": result.get("output", "I couldn't process that request."),
            "search_triggered": search_triggered
        }
    except Exception as e:
        logger.error(f"LLM processing failed: {str(e)}")
        return {
            "response": "I encountered an error processing your request.",
            "search_triggered": False
        }

@app.post("/chat/voice", response_model=VoiceResponse)
async def chat_voice(file: UploadFile):
    """Process voice input and return AI response"""
    # Validate file type
    if not file.filename.endswith((".wav", ".mp3", ".ogg", ".flac")):
        raise HTTPException(
            status_code=400,
            detail="Unsupported file format. Supported formats: WAV, MP3, OGG, FLAC"
        )
    
    # Save uploaded file to temp location
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name
    except Exception as e:
        logger.error(f"File handling error: {str(e)}")
        raise HTTPException(status_code=500, detail="File upload failed")
    
    try:
        # Transcribe audio
        transcript = transcribe_audio(tmp_path)
        os.unlink(tmp_path)  # Clean up temp file
        
        # Process transcript if not empty
        if not transcript:
            return VoiceResponse(
                transcript="",
                response="I didn't catch that. Could you please repeat?",
                search_triggered=False
            )
        
        # Get AI response
        result = process_query(transcript)
        
        return VoiceResponse(
            transcript=transcript,
            response=result["response"],
            search_triggered=result["search_triggered"]
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Processing failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

# For testing without audio upload
class TextRequest(BaseModel):
    text: str

@app.post("/chat/text", response_model=VoiceResponse)
async def chat_text(request: TextRequest):
    """Process text input and return AI response (for testing)"""
    result = process_query(request.text)
    return VoiceResponse(
        transcript=request.text,
        response=result["response"],
        search_triggered=result["search_triggered"]
    )