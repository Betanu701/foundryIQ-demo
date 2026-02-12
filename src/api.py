"""FastAPI server for FoundryIQ chat interface."""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

from .chat_service import chat_with_documents

app = FastAPI(
    title="FoundryIQ API",
    description="Natural language querying for Vertex tax documents",
    version="1.0.0",
)

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    question: str
    chat_history: Optional[List[ChatMessage]] = None


class SourceDocument(BaseModel):
    file_name: str
    file_type: str
    score: float
    preview: str


class ChatResponse(BaseModel):
    answer: str
    sources: List[SourceDocument]


@app.get("/")
async def root():
    """Health check endpoint."""
    return {"status": "healthy", "service": "FoundryIQ API"}


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Chat with your documents using natural language.
    
    Send a question and optionally include chat history for context.
    Returns an AI-generated answer based on the indexed documents.
    """
    try:
        # Convert chat history to dict format
        history = None
        if request.chat_history:
            history = [{"role": msg.role, "content": msg.content} for msg in request.chat_history]
        
        result = chat_with_documents(
            user_question=request.question,
            chat_history=history,
            use_vector_search=True,
        )
        
        return ChatResponse(
            answer=result["answer"],
            sources=[SourceDocument(**src) for src in result["sources"]],
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok"}
