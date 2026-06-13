from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
import time
import os

from app.api.deps import get_db
from app.schemas.system import SystemStatusResponse, HelpCenterResponse

router = APIRouter()


@router.get("/status", response_model=SystemStatusResponse)
def get_system_status(db: Session = Depends(get_db)):
    """Check backend, database connectivity, and Gemini AI status."""
    start_time = time.time()
    
    # 1. Database Check
    try:
        db.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception:
        db_status = "disconnected"
        
    # 2. Gemini AI Check
    key = os.environ.get("GEMINI_API_KEY")
    if key and len(key) > 10:
        gemini_status = "online"
    else:
        gemini_status = "unconfigured"
        
    elapsed = time.time() - start_time
    
    return {
        "backend_status": "healthy",
        "database_status": db_status,
        "gemini_status": gemini_status,
        "last_api_response_time": round(elapsed * 1000, 2)  # returns in milliseconds
    }


@router.get("/help", response_model=HelpCenterResponse)
def get_help_center():
    """Retrieve guides, FAQs, and troubleshooting articles."""
    return {
        "guides": {
            "soil_analysis": (
                "To run a Soil Health Analysis, navigate to the Soil Analyzer tab. Enter the measured "
                "values for Soil pH, Nitrogen (N), Phosphorus (P), and Potassium (K) in mg/kg. "
                "The analyzer will calculate NPK ratios and supply tailored organic/inorganic fertilizer "
                "recommendation instructions based on your target crop."
            ),
            "crop_recommendation": (
                "Smart Crop Recommendations use local soil report parameters, temperature forecasts, and "
                "climatic metrics to check compatibility against a catalog of 20+ crops. Click 'Generate "
                "Recommendations' to view compatibility match percentages."
            ),
            "disease_detection": (
                "The Plant Disease Diagnostic module accepts uploaded crop leaf images. It runs image-based "
                "classification (simulated disease scan or live vision check) to identify potential pests, "
                "leaf spots, or nutrient deficiencies, detailing treatment steps and precautions."
            )
        },
        "faqs": [
            {
                "question": "How do Sowing Planner calendars adapt to weather changes?",
                "answer": (
                    "The Farm Planner retrieves local 7-day weather predictions. If rainfall is expected, "
                    "it reschedules water-intensive tasks. If high temperatures are forecasted, it adds protective "
                    "mulching tasks to protect young saplings."
                )
            },
            {
                "question": "Can I switch back to a farm context after switching away?",
                "answer": (
                    "Yes. Use the Active Farm dropdown in the top header, or click 'Activate' on any farm card in "
                    "the Farm Portfolio panel. The entire application context will switch immediately."
                )
            }
        ],
        "troubleshooting": [
            "If the page shows a connection failure warning, verify your network connection and reload.",
            "If Gemini reports rate limits, wait 30 seconds to allow the quota threshold to reset.",
            "Make sure your soil pH is entered between 3.5 and 9.5 for correct diagnosis."
        ]
    }
