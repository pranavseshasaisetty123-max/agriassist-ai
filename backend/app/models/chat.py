from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Enum, func
from sqlalchemy.orm import relationship
import enum
from app.core.database import Base


class SenderRole(str, enum.Enum):
    FARMER = "FARMER"
    AI = "AI"


class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(Integer, primary_key=True, index=True)
    farmer_id = Column(Integer, ForeignKey("farmers.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    farmer = relationship("Farmer", back_populates="sessions")
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("chat_sessions.id", ondelete="CASCADE"), nullable=False)
    sender = Column(Enum(SenderRole), nullable=False)
    message_text = Column(Text, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    # Relationships
    session = relationship("ChatSession", back_populates="messages")
