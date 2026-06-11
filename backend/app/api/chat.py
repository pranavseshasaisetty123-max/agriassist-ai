from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from typing import List
from app.api.deps import get_current_farmer
from app.core.database import get_db
from app.models.farmer import Farmer
from app.schemas.chat import (
    ChatResponse,
    ChatMessageCreate,
    ChatMessageResponse,
    ChatSessionCreate,
    ChatSessionResponse,
)
from app.services.chat import chat_service

router = APIRouter()


@router.get("/sessions", response_model=List[ChatSessionResponse])
def read_sessions(
    db: Session = Depends(get_db),
    current_farmer: Farmer = Depends(get_current_farmer),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """Retrieve historical chat sessions for the authenticated farmer."""
    return chat_service.get_farmer_sessions(
        db, farmer_id=current_farmer.id, limit=limit, offset=offset
    )


@router.post("/sessions", response_model=ChatSessionResponse, status_code=status.HTTP_201_CREATED)
def create_session(
    *,
    db: Session = Depends(get_db),
    current_farmer: Farmer = Depends(get_current_farmer),
    session_in: ChatSessionCreate
):
    """Create a new chat session container."""
    return chat_service.create_session(
        db, farmer_id=current_farmer.id, title=session_in.title
    )


@router.get("/sessions/{session_id}/messages", response_model=List[ChatMessageResponse])
def read_messages(
    session_id: int,
    db: Session = Depends(get_db),
    current_farmer: Farmer = Depends(get_current_farmer)
):
    """Retrieve all messages in a specific chat session."""
    return chat_service.get_messages(
        db, session_id=session_id, farmer_id=current_farmer.id
    )


@router.post("/sessions/{session_id}/messages", response_model=ChatResponse)
def send_message(
    session_id: int,
    *,
    db: Session = Depends(get_db),
    current_farmer: Farmer = Depends(get_current_farmer),
    message_in: ChatMessageCreate
):
    """Send a prompt in a chat session and receive the AI agent's response."""
    return chat_service.post_message(
        db,
        session_id=session_id,
        farmer_id=current_farmer.id,
        prompt=message_in.message_text
    )
