import logging
import time
import os
from typing import List, Optional
from fastapi import HTTPException, status
from google import genai
from google.genai import types
from app.core.config import settings
from app.core.context import request_language
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
        # Mark as enabled only if key is set and is not a placeholder
        self.enabled = bool(api_key) and api_key != "your_gemini_api_key_here"
        self.client = None
        
        if self.enabled:
            try:
                self.client = genai.Client(api_key=self.api_key)
                logger.info("Gemini API Client initialized successfully.")
            except Exception as e:
                logger.error(f"Failed to initialize Gemini API Client: {e}")
                self.enabled = False
        else:
            logger.warning("No valid GEMINI_API_KEY provided. AI service runs in unconfigured fallback mode.")

    def _get_lang_instruction(self) -> str:
        lang = request_language.get()
        if lang == "te":
            return "IMPORTANT: You must translate and respond entirely in Telugu (తెలుగు) script."
        if lang == "hi":
            return "IMPORTANT: You must translate and respond entirely in Hindi (हिन्दी) script."
        return "Respond in English."

    def _raise_service_unavailable(self, feature_name: str, err: Optional[Exception] = None):
        msg = f"AI recommendations are temporarily unavailable for {feature_name}."
        if err:
            logger.error(f"{feature_name} failed: {err}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=msg
        )

    def generate_chat_response(self, prompt: str, history: List[ChatMessage]) -> str:
        """
        Send conversational history and the current user prompt to Gemini,
        returning the generated text response in the selected language.
        """
        if not self.enabled or not self.client:
            self._raise_service_unavailable("chat")

        lang_instruction = self._get_lang_instruction()

        try:
            contents = []
            for msg in history:
                role = "user" if msg.sender == SenderRole.FARMER else "model"
                contents.append(
                    types.Content(
                        role=role,
                        parts=[types.Part.from_text(text=msg.message_text)]
                    )
                )
            
            contents.append(
                types.Content(
                    role="user",
                    parts=[types.Part.from_text(text=f"{prompt}\n\n{lang_instruction}")]
                )
            )

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
            self._raise_service_unavailable("chat", e)

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
        recommendation in the selected language.
        """
        if not self.enabled or not self.client:
            self._raise_service_unavailable("soil analysis")

        lang_instruction = self._get_lang_instruction()

        try:
            from pydantic import BaseModel
            
            class SoilRecommendationSchema(BaseModel):
                nitrogen_recommendation: str
                phosphorus_recommendation: str
                potassium_recommendation: str
                fertilizer_schedule: str
                ai_raw_analysis: str
                organic_matter_recommendation: str

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
                f"Instructions:\n"
                f"1. Generate nitrogen, phosphorus, and potassium recommendations based on measured values.\n"
                f"2. Generate specific organic matter advice/improvement recommendations. IMPORTANT: If Organic Matter is 'Not tested' (or None), do NOT hallucinate a value or percentage. Instead, clearly explain in the target translation language that Organic Matter measurements were not provided, and explain that recommendations are based on the remaining available soil parameters (pH, Nitrogen, Phosphorus, Potassium).\n"
                f"3. Provide a clear, chronological fertilizer application schedule.\n"
                f"4. Provide a general diagnostics summary of the soil parameters under 'ai_raw_analysis'.\n"
                f"5. {lang_instruction}"
            )

            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=SoilRecommendationSchema,
                    system_instruction=(
                        "You are AgriAssist AI, a professional agricultural scientist and agronomist. "
                        "Provide accurate, specific, and actionable fertilizer and soil health recommendations."
                    )
                )
            )

            if response.text:
                import json
                parsed = json.loads(response.text)
                org_advice = parsed.get("organic_matter_recommendation", "")
                raw_analysis = parsed.get("ai_raw_analysis", "")
                parsed["ai_raw_analysis"] = f"{raw_analysis}\n\n[ORGANIC_MATTER_ADVICE]\n{org_advice}"
                return parsed
            else:
                raise ValueError("Empty response received from Gemini model.")
        except Exception as e:
            self._raise_service_unavailable("soil analysis", e)

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
        returning structured advisories in the selected language.
        """
        if not self.enabled or not self.client:
            self._raise_service_unavailable("weather advisory")

        lang_instruction = self._get_lang_instruction()

        try:
            from pydantic import BaseModel
            
            class AIAdvisorySchema(BaseModel):
                advisory_points: List[str]
                severity: str

            prompt = (
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
                f"1. Evaluate if upcoming weather impacts irrigation.\n"
                f"2. Evaluate if upcoming weather impacts fertilizer application.\n"
                f"3. Provide 3 to 5 clear, concise, actionable advice bullet points in 'advisory_points'.\n"
                f"4. Categorize the advisory 'severity' as 'info', 'warning', or 'critical'.\n"
                f"5. {lang_instruction}"
            )

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
            self._raise_service_unavailable("weather advisory", e)

    def analyze_crop_image(self, img_bytes: bytes, mime_type: str) -> dict:
        """
        Analyze a crop leaf image using Gemini Vision (multimodal) capabilities.
        Detects disease or deficiency and returns structured information in the selected language.
        """
        if not self.enabled or not self.client:
            self._raise_service_unavailable("disease detection")

        lang_instruction = self._get_lang_instruction()

        try:
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
                "1. Evaluate if the image is a plant or crop leaf. If the image is unrelated, set 'diagnosis_type' to 'invalid'.\n"
                "2. Classify it into one of the categories: 'disease', 'deficiency', 'healthy', or 'invalid'.\n"
                "3. Fill in the 'disease_name' and severity.\n"
                "4. Provide symptoms observed as a list of strings in 'symptoms'.\n"
                "5. Provide treatments in 'treatment'. You MUST include both standard chemical/core treatments AND organic treatments.\n"
                "   - For organic treatments, prefix the item string with '[ORGANIC] '.\n"
                "   - For standard chemical treatments, do not prefix them.\n"
                "6. Provide preventive measures and recovery steps in 'preventive_measures'. You MUST include both prevention actions and recovery steps.\n"
                "   - For recovery steps, prefix the item string with '[RECOVERY] '.\n"
                "   - For preventive measures, do not prefix them.\n"
                f"7. {lang_instruction}"
            )

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
                        "Analyze leaf/plant images to detect diseases or nutrient deficiencies."
                    )
                )
            )

            if response.text:
                import json
                return json.loads(response.text)
            else:
                raise ValueError("Empty response received from Gemini Vision model.")
        except Exception as e:
            self._raise_service_unavailable("disease detection", e)

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
            self._raise_service_unavailable("crop recommendations")

        lang_instruction = self._get_lang_instruction()

        try:
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
                f"Generate exactly the Top 5 most suitable crops to plant based on environmental context:\n\n"
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
                f"1. Analyze soil properties and weather parameters. Identify 5 crops that will grow best.\n"
                f"2. Assign each crop a suitability score (integer from 0 to 100).\n"
                f"3. Provide recommendation_reason, risk_factors, and farming_tips.\n"
                f"4. {lang_instruction}"
            )

            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=AICropRecommendationsListSchema,
                    system_instruction=(
                        "You are AgriAssist AI, a professional agricultural scientist and agronomist. "
                        "Evaluate the soil profile and weather conditions to recommend crops."
                    )
                )
            )

            if response.text:
                import json
                return json.loads(response.text)
            else:
                raise ValueError("Empty response received from Gemini.")
        except Exception as e:
            self._raise_service_unavailable("crop recommendations", e)

    def explain_price_trends(self, crop_name: str, trends: List[dict]) -> str:
        """
        Query Gemini to summarize the historical price trends for a crop in plain language.
        """
        if not self.enabled or not self.client:
            self._raise_service_unavailable("market intelligence")

        lang_instruction = self._get_lang_instruction()

        try:
            trend_str = "\n".join([f"- Date: {t['recorded_date']}, Price: Rs. {t['price_per_kg']}/kg" for t in trends])
            
            prompt = (
                f"Explain the following price trend data for the crop '{crop_name}' to a farmer.\n\n"
                f"Historical Price Trend:\n{trend_str}\n\n"
                f"Provide a concise summary. {lang_instruction}"
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
                return f"Price for {crop_name} is stable."
        except Exception as e:
            self._raise_service_unavailable("market intelligence", e)

    def generate_yield_prediction(
        self,
        soil_metrics: dict,
        weather_metrics: dict,
        crop_name: str,
        location: str
    ) -> dict:
        """
        Invoke Gemini to predict crop yield per acre and return a structured response in the selected language.
        """
        if not self.enabled or not self.client:
            self._raise_service_unavailable("yield prediction")

        lang_instruction = self._get_lang_instruction()

        try:
            from pydantic import BaseModel

            class AIYieldPredictionSchema(BaseModel):
                predicted_yield: float
                confidence_score: int
                yield_category: str  # "Low", "Medium", or "High"
                prediction_factors: List[str]
                recommendations: List[str]

            prompt = (
                f"Predict the expected yield (in kg per acre) for the crop '{crop_name}' in '{location}'.\n\n"
                f"Soil Metrics:\n"
                f"- pH: {soil_metrics.get('ph')}\n"
                f"- Nitrogen: {soil_metrics.get('nitrogen')} mg/kg\n"
                f"- Phosphorus: {soil_metrics.get('phosphorus')} mg/kg\n"
                f"- Potassium: {soil_metrics.get('potassium')} mg/kg\n"
                f"Weather Metrics:\n"
                f"- Current: {weather_metrics.get('temp')}°C, {weather_metrics.get('condition')}\n"
                f"- Forecast Summary: {weather_metrics.get('forecast_summary')}\n\n"
                f"Instructions:\n"
                f"1. Estimate yield in kg/acre and confidence score (0 to 100).\n"
                f"2. Provide 3-4 limiting factors and 3-4 recommendations.\n"
                f"3. {lang_instruction}"
            )

            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=AIYieldPredictionSchema,
                    system_instruction=(
                        "You are AgriAssist AI, a professional agronomist and yield forecaster. "
                        "Assess soil, weather, and crop variables to estimate expected yield."
                    )
                )
            )

            if response.text:
                import json
                return json.loads(response.text)
            else:
                raise ValueError("Empty response received from Gemini.")
        except Exception as e:
            self._raise_service_unavailable("yield prediction", e)

    def generate_farm_plan(
        self,
        soil_metrics: dict,
        weather_metrics: dict,
        crop_name: str,
        location: str
    ) -> dict:
        """
        Invoke Gemini to generate a complete farm plan containing chronological
        tasks and offsets relative to start date in the selected language.
        """
        if not self.enabled or not self.client:
            self._raise_service_unavailable("planner")

        lang_instruction = self._get_lang_instruction()

        try:
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
                f"Generate a chronological farming activity schedule for growing '{crop_name}' in '{location}'.\n\n"
                f"Soil Metrics:\n"
                f"- pH: {soil_metrics.get('ph')}\n"
                f"- Nitrogen: {soil_metrics.get('nitrogen')} mg/kg\n"
                f"- Phosphorus: {soil_metrics.get('phosphorus')} mg/kg\n"
                f"- Potassium: {soil_metrics.get('potassium')} mg/kg\n"
                f"Weather Context:\n"
                f"- Current Weather: {weather_metrics.get('temp')}°C, {weather_metrics.get('condition')}\n"
                f"- 7-Day Forecast: {weather_metrics.get('forecast_summary')}\n\n"
                f"Instructions:\n"
                f"1. Generate a schedule of activities from land preparation up to post-harvest.\n"
                f"2. Each activity offset should represent the number of days after sowing.\n"
                f"3. {lang_instruction}"
            )

            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=AIFarmPlanSchema,
                    system_instruction=(
                        "You are AgriAssist AI, a professional agronomist and crop planner. "
                        "Build crop operation schedules."
                    )
                )
            )

            if response.text:
                import json
                return json.loads(response.text)
            else:
                raise ValueError("Empty response received from Gemini.")
        except Exception as e:
            self._raise_service_unavailable("planner", e)

    def generate_risk_analysis(
        self,
        soil_metrics: dict,
        weather_metrics: dict,
        crop_names: List[str],
        location: str
    ) -> dict:
        """
        Invoke Gemini to analyze early pest & disease risks for active crops
        based on forecast weather models and soil metrics in the selected language.
        """
        if not self.enabled or not self.client:
            self._raise_service_unavailable("risk warning")

        lang_instruction = self._get_lang_instruction()

        try:
            from pydantic import BaseModel, Field
            from typing import Literal

            class AIRiskAlertSchema(BaseModel):
                title: str
                crop_name: str
                category: Literal["disease", "pest", "weather"]
                risk_level: Literal["low", "medium", "high", "critical"]
                probability: int = Field(..., ge=0, le=100)
                description: str
                prevention_steps: List[str]
                monitoring_advice: List[str]

            class AIRiskAnalysisListSchema(BaseModel):
                alerts: List[AIRiskAlertSchema]

            crops_str = ", ".join(crop_names)

            prompt = (
                f"Perform a risk warning analysis for crops: '{crops_str}' at location '{location}'.\n\n"
                f"Soil Metrics:\n"
                f"- pH: {soil_metrics.get('ph')}\n"
                f"- Nitrogen: {soil_metrics.get('nitrogen')} mg/kg\n"
                f"- Phosphorus: {soil_metrics.get('phosphorus')} mg/kg\n"
                f"- Potassium: {soil_metrics.get('potassium')} mg/kg\n"
                f"Weather Context:\n"
                f"- Current: {weather_metrics.get('temp')}°C, {weather_metrics.get('condition')}\n"
                f"- 7-Day Forecast: {weather_metrics.get('forecast_summary')}\n\n"
                f"Instructions:\n"
                f"1. Generate 2-4 risk warnings categorized into pest, disease, or weather.\n"
                f"2. {lang_instruction}"
            )

            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=AIRiskAnalysisListSchema,
                    system_instruction=(
                        "You are AgriAssist AI, a professional agricultural risk assessment expert. "
                        "Forecast pests, diseases, and crop hazards using soil and weather details."
                    )
                )
            )

            if response.text:
                import json
                return json.loads(response.text)
            else:
                raise ValueError("Empty response received from Gemini.")
        except Exception as e:
            self._raise_service_unavailable("risk warning", e)

    def generate_farm_consultation(
        self,
        soil_report: Optional[dict],
        weather_data: Optional[dict],
        crop_recommendations: List[dict],
        yield_predictions: List[dict],
        market_intelligence: List[dict],
        active_farm_plans: List[dict],
        active_risk_warnings: List[dict],
        question: str,
        location: str
    ) -> dict:
        """
        Reason across all agricultural context inputs to provide an expert farm consultation
        replying to the farmer's question in the selected language.
        """
        if not self.enabled or not self.client:
            self._raise_service_unavailable("virtual consultant")

        lang_instruction = self._get_lang_instruction()

        try:
            import json
            from pydantic import BaseModel, Field

            class AIConsultationResponseSchema(BaseModel):
                farm_health_score: int = Field(..., ge=0, le=100)
                health_summary: str
                key_findings: List[str]
                recommended_actions: List[str]
                risk_assessment: str
                answer: str
                confidence_score: int = Field(..., ge=0, le=100)

            prompt = (
                f"Reason across all parts of the farmer's details below to answer their question: '{question}'\n\n"
                f"--- FARM CONTEXT ---\n"
                f"Farmer Location: {location}\n\n"
                f"Soil Report:\n{json.dumps(soil_report, indent=2) if soil_report else 'No report available'}\n\n"
                f"Weather Data:\n{json.dumps(weather_data, indent=2) if weather_data else 'No weather data'}\n\n"
                f"Latest Crop Recommendations:\n{json.dumps(crop_recommendations, indent=2)}\n\n"
                f"Latest Yield Predictions:\n{json.dumps(yield_predictions, indent=2)}\n\n"
                f"Latest Market Intelligence:\n{json.dumps(market_intelligence, indent=2)}\n\n"
                f"Active Farm Sowing Plans:\n{json.dumps(active_farm_plans, indent=2)}\n\n"
                f"Active Risk Warnings:\n{json.dumps(active_risk_warnings, indent=2)}\n\n"
                f"Question:\n{question}\n\n"
                f"Instructions:\n"
                f"1. Answer the question incorporating all context.\n"
                f"2. Provide key findings, recommended actions, and confidence score.\n"
                f"3. {lang_instruction}"
            )

            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=AIConsultationResponseSchema,
                    system_instruction=(
                        "You are AgriAssist AI, a professional virtual agronomist and farm management advisor. "
                        "Provide high-quality recommendations in the requested language."
                    )
                )
            )

            if response.text:
                return json.loads(response.text)
            else:
                raise ValueError("Empty response received from Gemini.")
        except Exception as e:
            self._raise_service_unavailable("virtual consultant", e)


ai_service = AIService()
