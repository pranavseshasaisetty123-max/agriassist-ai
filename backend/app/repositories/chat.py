from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.chat import ChatSession, ChatMessage, SenderRole


class ChatRepository:
    def create_session(self, db: Session, farmer_id: int, title: str) -> ChatSession:
        """Create a new chat session for a farmer."""
        db_obj = ChatSession(farmer_id=farmer_id, title=title)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_session_by_id(self, db: Session, session_id: int) -> Optional[ChatSession]:
        """Retrieve a specific chat session."""
        return db.query(ChatSession).filter(ChatSession.id == session_id).first()

    def get_sessions_by_farmer(
        self, db: Session, farmer_id: int, limit: int = 50, offset: int = 0
    ) -> List[ChatSession]:
        """Fetch historical chat sessions for a farmer."""
        return (
            db.query(ChatSession)
            .filter(ChatSession.farmer_id == farmer_id)
            .order_by(ChatSession.updated_at.desc(), ChatSession.id.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )

    def create_message(
        self, db: Session, session_id: int, sender: SenderRole, message_text: str
    ) -> ChatMessage:
        """Append a message record to a session and update session's updated_at timestamp."""
        db_obj = ChatMessage(
            session_id=session_id, sender=sender, message_text=message_text
        )
        db.add(db_obj)
        
        # Touch session's updated_at
        session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
        if session:
            db.add(session)
            
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_messages_by_session(self, db: Session, session_id: int) -> List[ChatMessage]:
        """Fetch all messages within a specific session, sorted chronologically."""
        return (
            db.query(ChatMessage)
            .filter(ChatMessage.session_id == session_id)
            .order_by(ChatMessage.created_at.asc())
            .all()
        )


chat_repo = ChatRepository()
