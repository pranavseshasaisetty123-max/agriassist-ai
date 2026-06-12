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

    def generate_soil_recommendation(
        self,
        ph: float,
        nitrogen: float,
        phosphorus: float,
        potassium: float,
        organic_matter: float | None,
        crop_planned: str,
        location: str | None
    ) -> dict:
        """
        Invoke Gemini to analyze soil health parameters and return a structured
        recommendation conforming to SoilRecommendationSchema.
        """
        if not self.enabled or not self.client:
            # Return demo mock response
            return {
                "nitrogen_recommendation": f"[DEMO] Suggest Nitrogen treatment for planned crop {crop_planned}.",
                "phosphorus_recommendation": f"[DEMO] Suggest Phosphorus treatment for planned crop {crop_planned}.",
                "potassium_recommendation": f"[DEMO] Suggest Potassium treatment for planned crop {crop_planned}.",
                "fertilizer_schedule": f"[DEMO] Week 1: Basal dressing.\nWeek 4: Top dressing.",
                "ai_raw_analysis": f"[DEMO MODE] Analyzed report with pH {ph}, N {nitrogen}, P {phosphorus}, K {potassium}."
            }

        try:
            from pydantic import BaseModel
            
            class SoilRecommendationSchema(BaseModel):
                nitrogen_recommendation: str
                phosphorus_recommendation: str
                potassium_recommendation: str
                fertilizer_schedule: str
                ai_raw_analysis: str

            prompt = (
                f"Analyze the following soil test report details and provide structured agronomist recommendations.\n"
                f"Soil Metrics:\n"
                f"- pH: {ph}\n"
                f"- Nitrogen: {nitrogen} mg/kg\n"
                f"- Phosphorus: {phosphorus} mg/kg\n"
                f"- Potassium: {potassium} mg/kg\n"
                f"- Organic Matter: {f'{organic_matter}%' if organic_matter is not None else 'Not tested'}\n"
                f"Planned Crop: {crop_planned}\n"
                f"Location: {location or 'Unknown'}\n\n"
                f"Provide fertilizer recommendations for each nutrient (nitrogen, phosphorus, potassium) and a clear, chronological fertilizer application schedule."
            )

            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=SoilRecommendationSchema,
                    system_instruction=(
                        "You are AgriAssist AI, a professional agricultural scientist and agronomist. "
                        "Your goal is to provide accurate, specific, and actionable fertilizer and soil "
                        "health recommendations to farmers based on their soil test metrics."
                    )
                )
            )

            if response.text:
                import json
                return json.loads(response.text)
            else:
                raise ValueError("Empty response received from Gemini model.")
        except Exception as e:
            logger.error(f"Gemini structured generation failed: {e}")
            raise e

    def generate_weather_advisory(
        self,
        crop_planned: str,
        ph: float,
        nitrogen: float,
        phosphorus: float,
        potassium: float,
        organic_matter: float | None,
        location: str,
        current_temp: float,
        current_condition: str,
        forecast_summary: str
    ) -> dict:
        """
        Query Gemini to analyze soil reports and the 7-day weather forecast,
        returning structured advisories.
        """
        if not self.enabled or not self.client:
            # Return demo mock response
            return {
                "advisory_points": [
                    f"[DEMO] Upcoming forecast is {current_condition} ({current_temp}°C). Perfect for planned crop {crop_planned}.",
                    f"[DEMO] Soil pH {ph} is optimal. Keep watering regularly."
                ],
                "severity": "info"
            }

        import time
        from pydantic import BaseModel
        
        class AIAdvisorySchema(BaseModel):
            advisory_points: List[str]
            severity: str

        prompt = (
            f"You are a professional agricultural scientist and agronomist.\n"
            f"Analyze the soil report and weather forecast to provide immediate, actionable farming advisories.\n\n"
            f"Farmer Context:\n"
            f"- Location: {location}\n"
            f"- Planned Crop: {crop_planned}\n"
            f"Soil Metrics:\n"
            f"- pH: {ph}\n"
            f"- Nitrogen: {nitrogen} mg/kg\n"
            f"- Phosphorus: {phosphorus} mg/kg\n"
            f"- Potassium: {potassium} mg/kg\n"
            f"- Organic Matter: {f'{organic_matter}%' if organic_matter is not None else 'Not tested'}\n\n"
            f"Weather Context:\n"
            f"- Current: {current_temp}°C, {current_condition}\n"
            f"- 7-Day Forecast: {forecast_summary}\n\n"
            f"Instructions:\n"
            f"1. Evaluate if upcoming weather impacts irrigation (e.g., reduce watering before heavy rain, increase before hot dry spells).\n"
            f"2. Evaluate if upcoming weather impacts fertilizer application (e.g., do not apply nitrogen right before intense rain to prevent leaching).\n"
            f"3. Evaluate any extreme conditions (e.g. frost, storm) and recommend protective actions.\n"
            f"4. Provide 3 to 5 clear, concise, actionable advice bullet points in 'advisory_points'.\n"
            f"5. Categorize the advisory 'severity' as 'info', 'warning', or 'critical'."
        )

        max_retries = 2
        delay = 1.0
        for attempt in range(max_retries + 1):
            try:
                response = self.client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        response_schema=AIAdvisorySchema,
                        system_instruction=(
                            "You are AgriAssist AI, a professional agricultural scientist and agronomist. "
                            "Evaluate weather and soil variables to suggest immediate crop protection actions."
                        )
                    )
                )

                if response.text:
                    import json
                    return json.loads(response.text)
                else:
                    raise ValueError("Empty response received from Gemini.")
            except Exception as e:
                if attempt == max_retries:
                    logger.error(f"Gemini advisory generation failed after {max_retries} retries: {e}", exc_info=True)
                    raise e
                logger.warning(f"Gemini API request failed on attempt {attempt+1}. Retrying in {delay}s... Error: {e}")
                time.sleep(delay)
                delay *= 2

    def analyze_crop_image(self, img_bytes: bytes, mime_type: str) -> dict:
        """
        Analyze a crop leaf image using Gemini Vision (multimodal) capabilities.
        Detects disease or deficiency and returns structured information.
        """
        if not self.enabled or not self.client:
            # Return demo mock response
            return {
                "disease_name": "[DEMO] Tomato Late Blight",
                "diagnosis_type": "disease",
                "confidence": 0.88,
                "severity": "High",
                "symptoms": [
                    "[DEMO] Dark water-soaked spots on leaves",
                    "[DEMO] White fungal growth on underside of leaves in humid conditions"
                ],
                "treatment": [
                    "[DEMO] Apply copper-based fungicides immediately",
                    "[DEMO] Remove and destroy infected plant debris"
                ],
                "preventive_measures": [
                    "[DEMO] Use certified disease-free seeds",
                    "[DEMO] Ensure adequate plant spacing for airflow",
                    "[DEMO] Avoid overhead watering"
                ]
            }

        import time
        from pydantic import BaseModel
        
        class AIDiseaseAnalysisSchema(BaseModel):
            diagnosis_type: str  # "disease", "deficiency", "healthy", or "invalid"
            disease_name: str
            confidence: float
            severity: str  # "Low", "Medium", or "High"
            symptoms: List[str]
            treatment: List[str]
            preventive_measures: List[str]

        prompt = (
            "Analyze the uploaded image of a crop leaf or plant.\n"
            "1. Evaluate if the image is a plant or crop leaf. If the image is unrelated to plants/agriculture, is a non-plant object, "
            "or is a user interface screenshot, set 'diagnosis_type' to 'invalid' and 'disease_name' to 'Invalid Image'.\n"
            "2. If it is a plant, classify it into one of the following 'diagnosis_type' categories:\n"
            "   - 'disease': Plant shows symptoms of pathogens, fungi, mold, bacteria, or virus infection.\n"
            "   - 'deficiency': Plant shows signs of nutrient deficiency (e.g. chlorosis, purple tint, stunted growth).\n"
            "   - 'healthy': Plant appears healthy with no visual symptoms of disease or deficiency.\n"
            "3. Fill in the 'disease_name' (e.g., 'Tomato Late Blight', 'Iron Deficiency', or 'Healthy Wheat Leaf').\n"
            "4. Provide confidence (float between 0.0 and 1.0) and severity ('Low', 'Medium', or 'High' - use 'Low' for healthy or invalid images).\n"
            "5. Provide symptoms observed, recommended treatment points, and preventive measures as lists of strings."
        )

        max_retries = 2
        delay = 1.0
        for attempt in range(max_retries + 1):
            try:
                response = self.client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=[
                        types.Part.from_bytes(
                            data=img_bytes,
                            mime_type=mime_type
                        ),
                        prompt
                    ],
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        response_schema=AIDiseaseAnalysisSchema,
                        system_instruction=(
                            "You are AgriAssist AI, a professional agricultural scientist, botanist, and plant pathologist. "
                            "Analyze leaf/plant images to detect diseases, nutrient deficiencies, or confirm health. "
                            "Accurately flag non-plant or unrelated inputs as 'invalid'."
                        )
                    )
                )

                if response.text:
                    import json
                    return json.loads(response.text)
                else:
                    raise ValueError("Empty response received from Gemini Vision model.")
            except Exception as e:
                if attempt == max_retries:
                    logger.error(f"Gemini crop image analysis failed after {max_retries} retries: {e}", exc_info=True)
                    raise e
                logger.warning(f"Gemini API request failed on attempt {attempt+1}. Retrying in {delay}s... Error: {e}")
                time.sleep(delay)
                delay *= 2

    def generate_crop_recommendations(
        self,
        soil_metrics: dict,
        current_weather: dict,
        forecast_summary: str,
        location: str
    ) -> dict:
        """
        Query Gemini to generate structured top 5 crop recommendations based on
        soil metrics, location, current weather, and 7-day forecast.
        """
        if not self.enabled or not self.client:
            # Return demo mock response
            return {
                "recommendations": [
                    {
                        "crop_name": "[DEMO] Wheat",
                        "suitability_score": 90,
                        "season": "Rabi",
                        "recommendation_reason": "Soil pH and winter forecast are optimal for Wheat growing.",
                        "risk_factors": ["Frost during early stages", "Late rust disease risk"],
                        "farming_tips": ["Sow in November", "Ensure 4-6 irrigations"]
                    },
                    {
                        "crop_name": "[DEMO] Mustard",
                        "suitability_score": 85,
                        "season": "Rabi",
                        "recommendation_reason": "Low organic matter and cool temperature are perfect.",
                        "risk_factors": ["Aphid infestation", "White rust disease"],
                        "farming_tips": ["Maintain plant spacing", "Monitor for pests regularly"]
                    },
                    {
                        "crop_name": "[DEMO] Barley",
                        "suitability_score": 80,
                        "season": "Rabi",
                        "recommendation_reason": "Barley performs well in slightly acidic soils with low water requirements.",
                        "risk_factors": ["Lodging under high winds", "Stripe rust"],
                        "farming_tips": ["Use certified seeds", "Avoid excessive nitrogen application"]
                    },
                    {
                        "crop_name": "[DEMO] Chickpeas",
                        "suitability_score": 78,
                        "season": "Rabi",
                        "recommendation_reason": "Enriches soil nitrogen while thriving on residual moisture.",
                        "risk_factors": ["Pod borer damage", "Wilt disease"],
                        "farming_tips": ["Treat seeds with Rhizobium", "Ensure good drainage"]
                    },
                    {
                        "crop_name": "[DEMO] Peas",
                        "suitability_score": 75,
                        "season": "Rabi",
                        "recommendation_reason": "Cool climate and pH support excellent leguminous growth.",
                        "risk_factors": ["Powdery mildew", "Frost damage during flowering"],
                        "farming_tips": ["Provide staking for support", "Keep soil moist but not waterlogged"]
                    }
                ]
            }

        import time
        from pydantic import BaseModel

        class AICropRecommendationItemSchema(BaseModel):
            crop_name: str
            suitability_score: int
            season: str
            recommendation_reason: str
            risk_factors: List[str]
            farming_tips: List[str]

        class AICropRecommendationsListSchema(BaseModel):
            recommendations: List[AICropRecommendationItemSchema]

        prompt = (
            f"You are a professional agricultural scientist and agronomist.\n"
            f"Generate exactly the Top 5 most suitable crops to plant based on the following farmer's environmental context:\n\n"
            f"Farmer Context:\n"
            f"- Location: {location}\n"
            f"Soil Metrics:\n"
            f"- pH: {soil_metrics.get('ph')}\n"
            f"- Nitrogen: {soil_metrics.get('nitrogen')} mg/kg\n"
            f"- Phosphorus: {soil_metrics.get('phosphorus')} mg/kg\n"
            f"- Potassium: {soil_metrics.get('potassium')} mg/kg\n"
            f"- Organic Matter: {soil_metrics.get('organic_matter')}% (if available)\n\n"
            f"Weather Context:\n"
            f"- Current Weather: {current_weather.get('temp')}°C, {current_weather.get('condition')}\n"
            f"- 7-Day Forecast: {forecast_summary}\n\n"
            f"Instructions:\n"
            f"1. Analyze soil properties and weather parameters. Identify 5 crops that will grow best under these specific parameters.\n"
            f"2. Assign each recommended crop a suitability score (integer from 0 to 100).\n"
            f"3. Specify the appropriate growing season (e.g. Rabi, Kharif, Zaid).\n"
            f"4. Provide a clear recommendation_reason, potential risk_factors (list of strings), and helpful farming_tips (list of strings) for each crop."
        )

        max_retries = 2
        delay = 1.0
        for attempt in range(max_retries + 1):
            try:
                response = self.client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        response_schema=AICropRecommendationsListSchema,
                        system_instruction=(
                            "You are AgriAssist AI, a professional agricultural scientist and agronomist. "
                            "Evaluate the farmer's soil profile and local weather conditions to recommend "
                            "exactly 5 most suitable crops, providing clear recommendations, risks, and tips."
                        )
                    )
                )

                if response.text:
                    import json
                    return json.loads(response.text)
                else:
                    raise ValueError("Empty response received from Gemini.")
            except Exception as e:
                if attempt == max_retries:
                    logger.error(f"Gemini crop recommendation generation failed after {max_retries} retries: {e}", exc_info=True)
                    raise e
                logger.warning(f"Gemini API request failed on attempt {attempt+1}. Retrying in {delay}s... Error: {e}")
                time.sleep(delay)
                delay *= 2

    def explain_price_trends(self, crop_name: str, trends: List[dict]) -> str:
        """
        Query Gemini to summarize the historical price trends for a crop in plain language.
        """
        if not self.enabled or not self.client:
            # Return demo mock response
            return (
                f"[DEMO] Over the past 30 days, the price of {crop_name} has shown steady growth "
                "with moderate fluctuations. A minor dip occurred in mid-month due to increased market arrivals, "
                "followed by a quick recovery. Overall market conditions remain favorable."
            )

        try:
            # Format trend data for prompt
            trend_str = "\n".join([f"- Date: {t['recorded_date']}, Price: Rs. {t['price_per_kg']}/kg" for t in trends])
            
            prompt = (
                f"You are a professional agricultural market analyst and agronomist.\n"
                f"Explain the following price trend data for the crop '{crop_name}' to a farmer in plain, encouraging language.\n"
                f"Focus on key insights like price direction, spikes/drops, stability, and whether they should consider selling now or wait.\n\n"
                f"Historical Price Trend:\n{trend_str}\n\n"
                f"Provide a concise summary (around 3 to 4 sentences max). Keep the tone helpful and easy to understand for a farmer."
            )

            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=(
                        "You are AgriAssist AI, a professional agricultural economist. "
                        "Translate market price graphs into simple, actionable insights and advice for farmers."
                    )
                )
            )

            if response.text:
                return response.text.strip()
            else:
                return f"Price for {crop_name} is stable. Market indicators are positive."
        except Exception as e:
            logger.error(f"Gemini trend explanation failed: {e}")
            return f"Unable to generate AI market analysis for {crop_name} at this time. Standard market indicators are positive."

    def generate_yield_prediction(
        self,
        soil_metrics: dict,
        weather_metrics: dict,
        crop_name: str,
        location: str
    ) -> dict:
        """
        Invoke Gemini to predict crop yield per acre and return a structured response.
        """
        if not self.enabled or not self.client:
            # Return demo mock response
            return {
                "predicted_yield": 850.5,
                "confidence_score": 90,
                "yield_category": "High",
                "prediction_factors": [
                    f"[DEMO] Optimal soil pH of {soil_metrics.get('ph')} supports strong root nutrient intake.",
                    f"[DEMO] Adequate seasonal weather conditions in {location}.",
                    "[DEMO] Mild temperatures forecasted for early stages of crop lifecycle."
                ],
                "recommendations": [
                    "[DEMO] Add a nitrogen top dressing in Week 3 to maintain vegetative growth.",
                    "[DEMO] Time your seeding schedule right before mild showers for higher seed establishment.",
                    "[DEMO] Ensure drainage trenches are clear to prevent monsoon waterlogging."
                ]
            }

        import time
        from pydantic import BaseModel

        class AIYieldPredictionSchema(BaseModel):
            predicted_yield: float
            confidence_score: int
            yield_category: str  # "Low", "Medium", or "High"
            prediction_factors: List[str]
            recommendations: List[str]

        prompt = (
            f"You are a professional agricultural scientist, agronomist, and crop modeler.\n"
            f"Predict the expected yield (in kg per acre) for the crop '{crop_name}' in the location '{location}'.\n\n"
            f"Farmer Context:\n"
            f"- Location: {location}\n"
            f"- Crop to Plant: {crop_name}\n\n"
            f"Soil Metrics:\n"
            f"- pH: {soil_metrics.get('ph')}\n"
            f"- Nitrogen: {soil_metrics.get('nitrogen')} mg/kg\n"
            f"- Phosphorus: {soil_metrics.get('phosphorus')} mg/kg\n"
            f"- Potassium: {soil_metrics.get('potassium')} mg/kg\n"
            f"- Organic Matter: {soil_metrics.get('organic_matter')}% (if available)\n\n"
            f"Weather Metrics:\n"
            f"- Current: {weather_metrics.get('temp')}°C, {weather_metrics.get('condition')}\n"
            f"- Forecast Summary: {weather_metrics.get('forecast_summary')}\n\n"
            f"Instructions:\n"
            f"1. Evaluate how the soil nutrients and upcoming weather variables affect the growth of '{crop_name}'.\n"
            f"2. Estimate the expected yield in kg/acre (float) and confidence score (integer 0 to 100).\n"
            f"3. Classify the yield category as 'Low', 'Medium', or 'High'.\n"
            f"4. Provide 3-4 limiting or enabling prediction factors (list of strings).\n"
            f"5. Suggest 3-4 actionable recommendations to improve the yield (list of strings)."
        )

        max_retries = 2
        delay = 1.0
        for attempt in range(max_retries + 1):
            try:
                response = self.client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        response_schema=AIYieldPredictionSchema,
                        system_instruction=(
                            "You are AgriAssist AI, a professional agronomist and yield forecaster. "
                            "Assess soil, location, weather, and crop variables to estimate expected yield, "
                            "confidence level, category, contributing factors, and advice."
                        )
                    )
                )

                if response.text:
                    import json
                    return json.loads(response.text)
                else:
                    raise ValueError("Empty response received from Gemini.")
            except Exception as e:
                if attempt == max_retries:
                    logger.error(f"Gemini yield prediction failed after {max_retries} retries: {e}", exc_info=True)
                    raise e
                logger.warning(f"Gemini API request failed on attempt {attempt+1}. Retrying in {delay}s... Error: {e}")
                time.sleep(delay)
                delay *= 2

    def generate_farm_plan(
        self,
        soil_metrics: dict,
        weather_metrics: dict,
        crop_name: str,
        location: str
    ) -> dict:
        """
        Invoke Gemini to generate a complete farm plan containing chronological
        tasks and offsets relative to start date.
        """
        if not self.enabled or not self.client:
            # Return demo mock response
            return {
                "expected_harvest_days": 90,
                "tasks": [
                    {
                        "title": "[DEMO] Land Soil Tilling",
                        "description": f"[DEMO] Deep plow the soil and add organic compost to prepare the field for sowing {crop_name}.",
                        "planned_date_offset_days": 0,
                        "priority": "medium",
                        "category": "land_preparation"
                    },
                    {
                        "title": f"[DEMO] {crop_name} Seed Sowing",
                        "description": f"[DEMO] Sow high-quality certified {crop_name} seeds at recommended depth and spacing.",
                        "planned_date_offset_days": 3,
                        "priority": "high",
                        "category": "sowing"
                    },
                    {
                        "title": "[DEMO] First Irrigation",
                        "description": "[DEMO] Irrigate lightly to ensure seed bed moisture is optimal for germination.",
                        "planned_date_offset_days": 4,
                        "priority": "high",
                        "category": "irrigation"
                    },
                    {
                        "title": "[DEMO] Weed Monitoring",
                        "description": "[DEMO] Inspect rows for weed growth and perform manual removal if necessary.",
                        "planned_date_offset_days": 10,
                        "priority": "low",
                        "category": "monitoring"
                    },
                    {
                        "title": "[DEMO] Fertilizer Application",
                        "description": f"[DEMO] Apply balanced fertilizer based on soil pH {soil_metrics.get('ph', 6.5)} and NPK values.",
                        "planned_date_offset_days": 15,
                        "priority": "medium",
                        "category": "fertilizer"
                    },
                    {
                        "title": "[DEMO] Disease Inspection",
                        "description": f"[DEMO] Monitor foliage for common {crop_name} diseases or pest symptoms.",
                        "planned_date_offset_days": 25,
                        "priority": "medium",
                        "category": "disease_control"
                    },
                    {
                        "title": f"[DEMO] {crop_name} Harvest Preparation",
                        "description": f"[DEMO] Prepare clean storage, packing crates, and harvesting tools for {crop_name}.",
                        "planned_date_offset_days": 85,
                        "priority": "medium",
                        "category": "harvest"
                    },
                    {
                        "title": f"[DEMO] Harvest {crop_name}",
                        "description": f"[DEMO] Harvest the crop at peak maturity under favorable weather conditions.",
                        "planned_date_offset_days": 90,
                        "priority": "high",
                        "category": "harvest"
                    },
                    {
                        "title": "[DEMO] Post-Harvest Storage",
                        "description": "[DEMO] Sort harvested yield by grade, place in cool dry storage, and transport to market.",
                        "planned_date_offset_days": 91,
                        "priority": "low",
                        "category": "post_harvest"
                    }
                ]
            }

        import time
        from pydantic import BaseModel
        from typing import Literal

        class AITaskSchema(BaseModel):
            title: str
            description: str
            planned_date_offset_days: int
            priority: Literal["low", "medium", "high"]
            category: Literal[
                "land_preparation",
                "sowing",
                "irrigation",
                "fertilizer",
                "monitoring",
                "disease_control",
                "harvest",
                "post_harvest",
            ]

        class AIFarmPlanSchema(BaseModel):
            expected_harvest_days: int
            tasks: List[AITaskSchema]

        prompt = (
            f"You are a professional agricultural scientist, agronomist, and farm planner.\n"
            f"Generate a complete chronological farming activity schedule (lifecycle) for growing '{crop_name}' in the location '{location}'.\n\n"
            f"Farmer Context:\n"
            f"- Location: {location}\n"
            f"- Crop to Grow: {crop_name}\n\n"
            f"Soil Metrics:\n"
            f"- pH: {soil_metrics.get('ph')}\n"
            f"- Nitrogen: {soil_metrics.get('nitrogen')} mg/kg\n"
            f"- Phosphorus: {soil_metrics.get('phosphorus')} mg/kg\n"
            f"- Potassium: {soil_metrics.get('potassium')} mg/kg\n"
            f"- Organic Matter: {soil_metrics.get('organic_matter')}% (if available)\n\n"
            f"Weather Context:\n"
            f"- Current Weather: {weather_metrics.get('temp')}°C, {weather_metrics.get('condition')}\n"
            f"- 7-Day Forecast Summary: {weather_metrics.get('forecast_summary')}\n\n"
            f"Instructions:\n"
            f"1. Generate a complete schedule of activities from land preparation up to post-harvest.\n"
            f"2. Each activity must have a positive or zero 'planned_date_offset_days' (the number of days after the plan's start date that the activity should occur).\n"
            f"3. Create tasks across these specific categories:\n"
            f"   - 'land_preparation' (soil prep, plowing, composting before sowing)\n"
            f"   - 'sowing' (sowing seeds)\n"
            f"   - 'irrigation' (weather-aware watering intervals)\n"
            f"   - 'fertilizer' (NPK/organic fertilization timings tailored to soil metrics)\n"
            f"   - 'monitoring' (regular checks, weeding, growth checks)\n"
            f"   - 'disease_control' (disease and pest scouting or preventative treatments)\n"
            f"   - 'harvest' (harvesting preparations and execution)\n"
            f"   - 'post_harvest' (sorting, packaging, storing, transport)\n"
            f"4. Expected harvest date offset (in days) should be specified in 'expected_harvest_days'.\n"
            f"5. Ensure tasks are tailored to the local weather context (e.g., suggest irrigation checks if forecast is hot/dry, adjust fertilizer schedules, etc.)."
        )

        max_retries = 2
        delay = 1.0
        for attempt in range(max_retries + 1):
            try:
                response = self.client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        response_schema=AIFarmPlanSchema,
                        system_instruction=(
                            "You are AgriAssist AI, a professional agronomist and crop planner. "
                            "Build logical, detailed, weather-aware, and soil-adapted crop operation schedules."
                        )
                    )
                )

                if response.text:
                    import json
                    return json.loads(response.text)
                else:
                    raise ValueError("Empty response received from Gemini.")
            except Exception as e:
                if attempt == max_retries:
                    logger.error(f"Gemini farm plan generation failed after {max_retries} retries: {e}", exc_info=True)
                    raise e
                logger.warning(f"Gemini API request failed on attempt {attempt+1}. Retrying in {delay}s... Error: {e}")
                time.sleep(delay)
                delay *= 2


ai_service = AIService()



