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


from app.core.context import request_language

@router.get("/help", response_model=HelpCenterResponse)
def get_help_center():
    """Retrieve guides, FAQs, and troubleshooting articles."""
    lang = request_language.get() or "en"
    
    if lang == "te":
        return {
            "guides": {
                "soil_analysis": (
                    "నేల ఆరోగ్య విశ్లేషణను అమలు చేయడానికి, నేల విశ్లేషణ ట్యాబ్‌కు నావిగేట్ చేయండి. నేల pH, నత్రజని (N), భాస్వరం (P), మరియు పొటాషియం (K) కొలిచిన విలువలను నమోదు చేయండి. విశ్లేషకుడు NPK నిష్పత్తులను లెక్కిస్తారు మరియు మీ లక్ష్య పంట ఆధారంగా సేంద్రీయ/రసాయన ఎరువుల సిఫార్సు సూచనలను అందిస్తారు."
                ),
                "crop_recommendation": (
                    "పంట సిఫార్సులు స్థానిక నేల నివేదిక పారామితులు, ఉష్ణోగ్రత అంచనాలు మరియు వాతావరణ కొలతలను ఉపయోగించి 20+ పంటల కేటలాగ్‌తో అనుకూలతను తనిఖీ చేస్తాయి. అనుకూలత మ్యాచ్ శాతాలను వీక్షించడానికి 'సిఫార్సులను రూపొందించండి' క్లిక్ చేయండి."
                ),
                "disease_detection": (
                    "మొక్కల వ్యాధి నిర్ధారణ మాడ్యూల్ అప్‌లోడ్ చేసిన పంట ఆకు చిత్రాలను అంగీకరిస్తుంది. ఇది సంభావ్య తెగుళ్లు, ఆకు మచ్చలు లేదా పోషకాల లోపాలను గుర్తించడానికి ఇమేజ్-ఆధారిత వర్గీకరణను నడుపుతుంది, చికిత్స దశలు మరియు జాగ్రత్తలను వివరిస్తుంది."
                )
            },
            "faqs": [
                {
                    "question": "వాతావరణ మార్పులకు విత్తే ప్లానర్ క్యాలెండర్‌లు ఎలా సర్దుబాటు అవుతాయి?",
                    "answer": (
                        "ఫార్మ్ ప్లానర్ స్థానిక 7-రోజుల వాతావరణ అంచనాలను పొందుతుంది. వర్షం పడే అవకాశం ఉంటే, అది నీటి-ఇంటెన్సివ్ పనులను రీషెడ్యూల్ చేస్తుంది. అధిక ఉష్ణోగ్రతలు అంచనా వేయబడితే, అది లేత మొక్కలను రక్షించడానికి రక్షక కవచం (మల్చింగ్) పనులను జోడిస్తుంది."
                    )
                },
                {
                    "question": "మరో వ్యవసాయ సందర్భానికి మారిన తర్వాత నేను పాతదానికి తిరిగి మారవచ్చా?",
                    "answer": (
                        "అవును. ఎగువ హెడర్‌లోని సక్రియ ఫారమ్ డ్రాప్‌డౌన్‌ను ఉపయోగించండి లేదా ఫారమ్ పోర్ట్‌ఫోలియో ప్యానెల్‌లోని ఏదైనా ఫారమ్ కార్డ్‌లో 'సక్రియం చేయి' క్లిక్ చేయండి. వ్యవసాయ సందర్భం వెంటనే మారుతుంది."
                    )
                }
            ],
            "troubleshooting": [
                "పేజీ కనెక్షన్ వైఫల్యం హెచ్చరికను చూపిస్తే, మీ నెట్‌వర్క్ కనెక్షన్‌ను ధృవీకరించి, రీలోడ్ చేయండి.",
                "జెమిని పరిమితులను నివేదిస్తే, కోటా రీసెట్ కావడానికి 30 సెకన్లు వేచి ఉండండి.",
                "సరైన నిర్ధారణ కోసం మీ నేల pH 3.5 మరియు 9.5 మధ్య నమోదు చేయబడిందని నిర్ధారించుకోండి."
            ]
        }
    elif lang == "hi":
        return {
            "guides": {
                "soil_analysis": (
                    "मिट्टी स्वास्थ्य विश्लेषण चलाने के लिए, मिट्टी विश्लेषक टैब पर जाएं। मिट्टी पीएच, नाइट्रोजन (N), फास्फोरस (P), और पोटेशियम (K) के मापे गए मान दर्ज करें। विश्लेषक NPK अनुपातों की गणना करेगा और आपकी लक्षित फसल के आधार पर जैविक/अजैविक उर्वरक सिफारिश निर्देश प्रदान करेगा।"
                ),
                "crop_recommendation": (
                    "स्मार्ट फसल सिफारिशें स्थानीय मिट्टी रिपोर्ट मापदंडों, तापमान पूर्वानुमानों और जलवायु मेट्रिक्स का उपयोग करके 20+ फसलों के कैटलॉग के खिलाफ संगतता की जांच करती हैं। संगतता मिलान प्रतिशत देखने के लिए 'सिफारिशें उत्पन्न करें' पर क्लिक करें।"
                ),
                "disease_detection": (
                    "पौधा रोग निदान मॉड्यूल फसल की पत्तियों की अपलोड की गई छवियों को स्वीकार करता है। यह संभावित कीटों, पत्ती के धब्बों या पोषक तत्वों की कमियों की पहचान करने के लिए छवि-आधारित वर्गीकरण चलाता है, जिसमें उपचार के चरण और सावधानियां शामिल हैं।"
                )
            },
            "faqs": [
                {
                    "question": "मौसम के बदलावों के अनुसार बुवाई योजनाकार कैलेंडर कैसे अनुकूलित होते हैं?",
                    "answer": (
                        "फार्म प्लानर स्थानीय 7-दिवसीय मौसम पूर्वानुमान प्राप्त करता है। यदि बारिश की संभावना है, तो यह जल-गहन कार्यों को पुनर्निर्धारित करता है। यदि उच्च तापमान का पूर्वानुमान है, तो यह युवा पौधों की सुरक्षा के लिए मल्चिंग कार्य जोड़ता है।"
                    )
                },
                {
                    "question": "क्या मैं दूसरे खेत के संदर्भ में जाने के बाद वापस पहले वाले पर आ सकता हूँ?",
                    "answer": (
                        "हाँ। शीर्ष हेडर में सक्रिय खेत ड्रॉपडाउन का उपयोग करें, या फार्म पोर्टफोलियो पैनल में किसी भी खेत कार्ड पर 'सक्रिय करें' पर क्लिक करें। संदर्भ तुरंत बदल जाएगा।"
                    )
                }
            ],
            "troubleshooting": [
                "यदि पृष्ठ कनेक्शन विफलता की चेतावनी दिखाता है, तो अपना नेटवर्क कनेक्शन जांचें और पुन: लोड करें।",
                "यदि जेमिनी दर सीमाओं की रिपोर्ट करता है, तो कोटा रीसेट होने के लिए 30 सेकंड प्रतीक्षा करें।",
                "सटीक निदान के लिए सुनिश्चित करें कि आपका मिट्टी पीएच 3.5 और 9.5 के बीच दर्ज किया गया है।"
            ]
        }
    else:
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
