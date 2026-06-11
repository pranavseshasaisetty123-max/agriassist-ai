import logging
from typing import List
from google import genai
from google.genai import types
from app.core.config import settings
from app.models.chat import ChatMessage, SenderRole

logger = logging.getLogger("agriassist.ai_service")

SYSTEM_INSTRUCTION = (
    "You are AgriAssist AI, a professional virtual agronomist. Your goal is to support "
    "farmers by answering questions about crop management, soil health, pest control, "
    "weather preparation, and modern agricultural practices. Keep your tone encouraging, "
    "practical, and clear. If a query is unrelated to agriculture, farming, gardening, "
    "or weather, politely decline to answer, guiding the user back to agricultural topics."
)


class AIService:
    def __init__(self, api_key: str = settings.GEMINI_API_KEY):
        self.api_key = api_key
        self.enabled = bool(api_key)
        self.client = None
        
        if self.enabled:
            try:
                # Initialize Google GenAI Client
                self.client = genai.Client(api_key=self.api_key)
                logger.info("Gemini API Client initialized successfully.")
            except Exception as e:
                logger.error(f"Failed to initialize Gemini API Client: {e}")
                self.enabled = False
        else:
            logger.warning("No GEMINI_API_KEY provided. AI service will run in offline mock demo mode.")

    def generate_chat_response(self, prompt: str, history: List[ChatMessage]) -> str:
        """
        Send conversational history and the current user prompt to Gemini,
        returning the generated text response.
        """
        if not self.enabled or not self.client:
            # Fallback mock response when no API key is present
            return (
                f"[DEMO MODE] Received: '{prompt}'. (Note: Please set a valid GEMINI_API_KEY "
                "in your backend .env file to enable live responses from Google Gemini)."
            )

        try:
            # Build historical content objects
            contents = []
            for msg in history:
                role = "user" if msg.sender == SenderRole.FARMER else "model"
                contents.append(
                    types.Content(
                        role=role,
                        parts=[types.Part.from_text(text=msg.message_text)]
                    )
                )
            
            # Append current user prompt
            contents.append(
                types.Content(
                    role="user",
                    parts=[types.Part.from_text(text=prompt)]
                )
            )

            # Generate content from model
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=contents,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_INSTRUCTION
                )
            )
            
            if response.text:
                return response.text
            else:
                return "I'm sorry, I could not generate a response at this time."
                
        except Exception as e:
            logger.error(f"Gemini API request failed: {e}")
            return f"Error communicating with Gemini AI: {str(e)}"


ai_service = AIService()
