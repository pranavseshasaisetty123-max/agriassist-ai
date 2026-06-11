from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import List, Dict, Any, Optional
from app.models.chat import ChatSession, ChatMessage, SenderRole
from app.repositories.chat import chat_repo
from app.services.ai import ai_service


class ChatService:
    def create_session(self, db: Session, farmer_id: int, title: Optional[str] = None) -> ChatSession:
        """Create a new chat session, defaulting title if empty."""
        session_title = title or "New Agricultural Query"
        return chat_repo.create_session(db, farmer_id=farmer_id, title=session_title)

    def get_farmer_sessions(
        self, db: Session, farmer_id: int, limit: int = 50, offset: int = 0
    ) -> List[ChatSession]:
        """Fetch all sessions belonging to the farmer."""
        return chat_repo.get_sessions_by_farmer(db, farmer_id=farmer_id, limit=limit, offset=offset)

    def _verify_session_ownership(self, db: Session, session_id: int, farmer_id: int) -> ChatSession:
        """Verify session exists and belongs to the requested farmer."""
        session = chat_repo.get_session_by_id(db, session_id=session_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat session not found."
            )
        if session.farmer_id != farmer_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have access to this chat session."
            )
        return session

    def get_messages(self, db: Session, session_id: int, farmer_id: int) -> List[ChatMessage]:
        """Fetch all messages inside a session after verifying access rights."""
        self._verify_session_ownership(db, session_id=session_id, farmer_id=farmer_id)
        return chat_repo.get_messages_by_session(db, session_id=session_id)

    def post_message(self, db: Session, session_id: int, farmer_id: int, prompt: str) -> Dict[str, Any]:
        """
        Post a prompt, generate the AI response, persist both, and return records.
        """
        # 1. Verify access
        self._verify_session_ownership(db, session_id=session_id, farmer_id=farmer_id)

        # 2. Persist the farmer's prompt message
        user_msg = chat_repo.create_message(
            db, session_id=session_id, sender=SenderRole.FARMER, message_text=prompt
        )

        # 3. Retrieve session message history for context
        # (Exclude the newly added prompt, or include it if the AI service expects it as a separate prompt parameter)
        history = chat_repo.get_messages_by_session(db, session_id=session_id)
        
        # We pass history[:-1] as context because we send the current prompt separately to generate_chat_response
        context_history = history[:-1]

        # 4. Generate response from Gemini API wrapper
        ai_text = ai_service.generate_chat_response(prompt, context_history)

        # 5. Persist the AI response message
        ai_msg = chat_repo.create_message(
            db, session_id=session_id, sender=SenderRole.AI, message_text=ai_text
        )

        return {
            "user_message": user_msg,
            "ai_response": ai_msg
        }


chat_service = ChatService()
