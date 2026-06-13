# AgriAssist AI: API Reference Manual

This document details request and response payloads for all 12 modules of the AgriAssist AI platform.

---

## 1. Authentication APIs

### 1.1 Farmer Registration
* **Endpoint**: `POST /api/v1/auth/register`
* **Request Example**:
```json
{
  "email": "farmer@example.com",
  "password": "password123",
  "first_name": "Rajesh",
  "last_name": "Sharma",
  "location": "Punjab, India"
}
```
* **Response Example (201 Created)**:
```json
{
  "id": 1,
  "email": "farmer@example.com",
  "first_name": "Rajesh",
  "last_name": "Sharma",
  "location": "Punjab, India",
  "active_farm_id": null,
  "created_at": "2026-06-13T08:50:00Z",
  "updated_at": "2026-06-13T08:50:00Z"
}
```

### 1.2 Farmer Login (OAuth2 Password Flow)
* **Endpoint**: `POST /api/v1/auth/login`
* **Request Example (Form Urlencoded)**:
```
username=farmer@example.com&password=password123
```
* **Response Example (200 OK)**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

---

## 2. Soil Analyzer APIs

### 2.1 Log Soil Report
* **Endpoint**: `POST /api/v1/soil/reports`
* **Headers**: `Authorization: Bearer <token>`
* **Request Example**:
```json
{
  "ph": 6.5,
  "nitrogen": 45.0,
  "phosphorus": 30.0,
  "potassium": 180.0,
  "organic_matter": 2.5,
  "crop_planned": "Wheat",
  "tested_at": "2026-06-12"
}
```
* **Response Example (201 Created)**:
```json
{
  "id": 12,
  "farmer_id": 1,
  "farm_id": 3,
  "ph": 6.5,
  "nitrogen": 45.0,
  "phosphorus": 30.0,
  "potassium": 180.0,
  "organic_matter": 2.5,
  "crop_planned": "Wheat",
  "tested_at": "2026-06-12",
  "created_at": "2026-06-13T08:51:00Z"
}
```

---

## 3. Crop Recommendation APIs

### 3.1 Generate Crop Recommendation
* **Endpoint**: `POST /api/v1/crop-recommendations/generate`
* **Headers**: `Authorization: Bearer <token>`
* **Request Example**:
```json
{
  "soil_report_id": 12
}
```
* **Response Example (201 Created)**:
```json
{
  "id": 5,
  "soil_report_id": 12,
  "primary_recommendation": "Tomato",
  "suitability_score": 92.5,
  "rationale": "High Potassium and Nitrogen values are optimal for solanaceous crop vegetative expansion.",
  "sowing_instructions": "Sow seeds at a depth of 0.5 inches in well-draining soil beds.",
  "created_at": "2026-06-13T08:52:00Z"
}
```

---

## 4. Disease Detection APIs

### 4.1 Log Leaf Disease Scan
* **Endpoint**: `POST /api/v1/disease/scans`
* **Headers**: `Authorization: Bearer <token>`
* **Request Example (Multipart Form Data)**:
* `file`: (Image Binary Data)
* `diagnosis_type`: "ai_scanning"
* **Response Example (201 Created)**:
```json
{
  "id": 8,
  "image_path": "static/uploads/leaf_disease_8.jpg",
  "leaf_type": "Tomato",
  "disease_name": "Early Blight",
  "confidence": 0.89,
  "diagnosis_type": "ai_scanning",
  "organic_treatments": "Apply copper fungicides weekly and prune lower leaves to improve air circulation.",
  "created_at": "2026-06-13T08:53:00Z"
}
```

---

## 5. Market Intelligence APIs

### 5.1 Analyze Crop Profitability
* **Endpoint**: `POST /api/v1/market-intelligence/calculate`
* **Headers**: `Authorization: Bearer <token>`
* **Request Example**:
```json
{
  "crop_name": "Tomato",
  "area_acres": 2.5,
  "market_price_per_kg": 35.0,
  "estimated_yield_kg": 15000.0,
  "input_cost_rupees": 120000.0
}
```
* **Response Example (201 Created)**:
```json
{
  "id": 14,
  "crop_name": "Tomato",
  "area_acres": 2.5,
  "market_price_per_kg": 35.0,
  "estimated_yield_kg": 15000.0,
  "input_cost_rupees": 120000.0,
  "gross_revenue": 525000.0,
  "net_profit": 405000.0,
  "roi_ratio": 3.375,
  "created_at": "2026-06-13T08:54:00Z"
}
```

---

## 6. Yield Prediction APIs

### 6.1 Generate Crop Yield Estimation
* **Endpoint**: `POST /api/v1/yield-predictions/generate`
* **Headers**: `Authorization: Bearer <token>`
* **Request Example**:
```json
{
  "crop_name": "Tomato",
  "area_acres": 2.5,
  "historical_avg_yield": 5500.0
}
```
* **Response Example (201 Created)**:
```json
{
  "id": 11,
  "crop_name": "Tomato",
  "area_acres": 2.5,
  "predicted_yield_kg": 14250.0,
  "confidence_lower": 13200.0,
  "confidence_upper": 15300.0,
  "reasoning_notes": "Predicted output based on pH levels (6.5) and regional weather forecast constants.",
  "created_at": "2026-06-13T08:55:00Z"
}
```

---

## 7. Farm Planner APIs

### 7.1 Generate AI Farm Operations Plan
* **Endpoint**: `POST /api/v1/farm-planner/plans/generate`
* **Headers**: `Authorization: Bearer <token>`
* **Request Example**:
```json
{
  "crop_name": "Tomato",
  "area_acres": 2.5,
  "planned_start_date": "2026-06-15"
}
```
* **Response Example (201 Created)**:
```json
{
  "id": 4,
  "crop_name": "Tomato",
  "area_acres": 2.5,
  "planned_start_date": "2026-06-15",
  "expected_harvest_date": "2026-10-15",
  "tasks": [
    {
      "id": 101,
      "title": "Soil Bed Preparation",
      "description": "Prepare soil beds with organic fertilizers.",
      "planned_date": "2026-06-15",
      "priority": "high",
      "category": "sowing",
      "status": "pending"
    }
  ]
}
```

### 7.2 Postpone Task (Snooze)
* **Endpoint**: `PATCH /api/v1/farm-planner/tasks/{task_id}/snooze?days=2`
* **Headers**: `Authorization: Bearer <token>`
* **Response Example (200 OK)**:
```json
{
  "id": 101,
  "planned_date": "2026-06-17",
  "snooze_count": 1
}
```

---

## 8. Risk Warning APIs

### 8.1 Fetch Regional Weather-Pest Risks
* **Endpoint**: `GET /api/v1/risk-intelligence/warnings`
* **Headers**: `Authorization: Bearer <token>`
* **Response Example (200 OK)**:
```json
[
  {
    "id": 3,
    "hazard_type": "pest_outbreak",
    "risk_level": "medium",
    "description": "Late blight warning on tomato crops due to moisture spikes.",
    "preventative_action": "Ensure dry foliage and spray neem oil.",
    "is_active": 1,
    "created_at": "2026-06-13T08:00:00Z"
  }
]
```

---

## 9. Virtual AI Agronomist Consultation APIs

### 9.1 Post Query in Consulting Session
* **Endpoint**: `POST /api/v1/chat/sessions/{session_id}/messages`
* **Headers**: `Authorization: Bearer <token>`
* **Request Example**:
```json
{
  "message_text": "What NPK fertilizer ratio fits sandy soils for growing potatoes?"
}
```
* **Response Example (200 OK)**:
```json
{
  "user_message": {
    "id": 201,
    "message_text": "What NPK fertilizer ratio fits sandy soils for growing potatoes?",
    "sender": "FARMER",
    "created_at": "2026-06-13T08:58:00Z"
  },
  "ai_response": {
    "id": 202,
    "message_text": "Sandy soils filter nutrients rapidly. Use a 10-20-20 slow-release NPK mix split in three doses.",
    "sender": "AGRONOMIST",
    "created_at": "2026-06-13T08:58:01Z"
  }
}
```

---

## 10. Smart Alert Center APIs

### 10.1 List Unread Warnings & Tasks
* **Endpoint**: `GET /api/v1/notifications/unread`
* **Headers**: `Authorization: Bearer <token>`
* **Response Example (200 OK)**:
```json
[
  {
    "id": 41,
    "notification_type": "risk_warning",
    "priority": "high",
    "title": "Severe Storm Advisory",
    "message": "Heavy rain forecast for your region within 24 hours. Verify farm drainages.",
    "read_status": false,
    "created_at": "2026-06-13T08:59:00Z"
  }
]
```

---

## 11. Farm Analytics APIs

### 11.1 Fetch Snapshot KPIs
* **Endpoint**: `GET /api/v1/analytics/kpis`
* **Headers**: `Authorization: Bearer <token>`
* **Response Example (200 OK)**:
```json
{
  "total_soil_tests": 12,
  "completed_sowing_tasks": 45,
  "active_warnings": 2,
  "latest_predicted_yield": 14250.0
}
```

---

## 12. Multi-Farm Portfolio APIs

### 12.1 Get Farmer Portfolio Summary
* **Endpoint**: `GET /api/v1/farms/portfolio`
* **Headers**: `Authorization: Bearer <token>`
* **Response Example (200 OK)**:
```json
{
  "total_farms": 3,
  "total_area_acres": 25.5,
  "expected_portfolio_profit": 540000.0,
  "expected_portfolio_yield": 24200.0,
  "portfolio_average_risk_index": 0.25,
  "active_plans_count": 2
}
```
