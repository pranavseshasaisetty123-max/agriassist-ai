# AgriAssist AI: Architecture & System Design Document

This document provides a comprehensive technical overview of the AgriAssist AI software architecture, database relations, AI workflows, and request processing pipelines.

---

## 1. System Overview

AgriAssist AI is structured as a decoupled, multi-tier Web Platform designed using the client-server architectural model.

```
┌────────────────────────────────────────────────────────┐
│                      Client Layer                      │
│             React Single Page Application              │
└──────────────────────────┬─────────────────────────────┘
                           │ HTTP REST / JSON
                           ▼
┌────────────────────────────────────────────────────────┐
│                   Application Layer                    │
│             FastAPI Backend Server Engine              │
└──────────────┬───────────────────────────┬─────────────┘
               │ SQLAlchemy ORM            │ HTTP API
               ▼                           ▼
┌──────────────────────────┐   ┌─────────────────────────┐
│     Database Layer       │   │     Cognitive Layer     │
│    MySQL RDBMS Server    │   │  Gemini AI (Flash 1.5)  │
└──────────────────────────┘   └─────────────────────────┘
```

* **Client Layer**: A responsive React SPA styled with earthen-emerald HSL CSS design tokens.
* **Application Layer**: A high-performance FastAPI server engine organizing API endpoints into routers.
* **Database Layer**: A relational MySQL database storing structured profiles, soil charts, analytics, and plans.
* **Cognitive Layer**: Google Gemini AI model integrated to perform structured diagnosis and reasoning.

---

## 2. Dynamic Workflow Diagrams

### 2.1 Request Processing Pipeline
Describes the lifecycle of a frontend UI event query requesting data.

```mermaid
sequenceDiagram
    autonumber
    actor Farmer as 👨‍🌾 Farmer UI Client
    participant API as 🚀 FastAPI Router
    participant Serv as ⚙️ Business Service
    participant Repo as 📁 Repository CRUD
    participant DB as 🗄️ MySQL Database

    Farmer->>API: GET /api/v1/soil/reports (with Auth Header)
    API->>API: Verify JWT & extract farmer_id
    API->>Serv: SoilService.list_reports(farmer_id, active_farm_id)
    Serv->>Repo: soil_report_repo.list_by_farm(db, farm_id)
    Repo->>DB: SQL Query (SELECT * FROM soil_reports WHERE...)
    DB-->>Repo: Row data
    Repo-->>Serv: SQLAlchemy Model instance list
    Serv-->>API: Processed list payload
    API-->>Farmer: HTTP 200 JSON Response (Validated by Pydantic)
```

---

### 2.2 JWT Authentication & Session Security Flow
Details client registration, login validation, token issuance, and subsequent authenticated requests.

```mermaid
sequenceDiagram
    autonumber
    actor Farmer as 👨‍🌾 Farmer UI Client
    participant Auth as 🔒 Auth Controller
    participant Security as 🔑 Security Service
    participant DB as 🗄️ MySQL Database

    Farmer->>Auth: POST /auth/login {username, password}
    Auth->>DB: Query Farmer by Email
    DB-->>Auth: Farmer record (with Password Hash)
    Auth->>Security: verify_password(raw_pwd, hashed_pwd)
    alt Password Invalid
        Security-->>Auth: False
        Auth-->>Farmer: HTTP 401 (Unauthorized)
    else Password Valid
        Security-->>Auth: True
        Auth->>Security: create_access_token(farmer_id)
        Note over Security: Sign JWT with SECRET_KEY<br/>using HMAC-SHA256
        Security-->>Auth: JWT Access Token String
        Auth-->>Farmer: HTTP 200 {access_token, token_type: "bearer"}
    end
```

---

### 2.3 AI Crop Recommendation Flow
Illustrates how NPK soil parameters and regional parameters map to recommendations.

```mermaid
sequenceDiagram
    autonumber
    actor Farmer as 👨‍🌾 Farmer UI Client
    participant API as 🚀 Recommendations API
    participant DB as 🗄️ MySQL Database
    participant Gemini as 🤖 Google Gemini AI

    Farmer->>API: POST /crop-recommendations/generate {soil_report_id}
    API->>DB: Fetch Soil Report parameters
    DB-->>API: {pH: 6.2, N: 45, P: 32, K: 180, location: "Punjab"}
    API->>API: Compile structured LLM Prompt
    API->>Gemini: Request Structured recommendations (Gemini 1.5 Flash)
    Note over Gemini: Evaluate soil parameters,<br/>optimal crop profiles,<br/>and crop suitability indices.
    Gemini-->>API: JSON Object response matching Pydantic schema
    API->>DB: Save generated Recommendation in database
    DB-->>API: Confirmed
    API-->>Farmer: HTTP 201 Created {crop, description, matching_score, guidelines}
```

---

### 2.4 Virtual Agronomist Consultation Chat Flow
Maps user dialog to conversation sessions, context building, database audits, and response caches.

```mermaid
sequenceDiagram
    autonumber
    actor Farmer as 👨‍🌾 Farmer UI Client
    participant API as 🚀 Chat API
    participant DB as 🗄️ MySQL Database
    participant Gemini as 🤖 Google Gemini AI

    Farmer->>API: POST /chat/sessions/{session_id}/messages {message_text}
    API->>DB: Fetch active session context & chat history (last 10 messages)
    DB-->>API: Session context + Message history
    API->>DB: Fetch current Farmer profile & active Farm details (soil, weather cache)
    DB-->>API: Farm location (e.g. Haryana), Soil values, weather status
    API->>API: Assemble system instructions injecting location, soil, weather & history
    API->>Gemini: Send prompt query (Gemini 1.5 Flash)
    Gemini-->>API: Natural language response string
    API->>DB: Save User message & AI response to database
    DB-->>API: Saved
    API-->>Farmer: HTTP 200 {user_message, ai_response}
```

---

## 3. Database Architecture & Relationships

AgriAssist AI operates on a relational schema designed to guarantee clean referential integrity:

* **Farmers**: Central account table. Holds JWT hashes, profile parameters, default configurations, and active farm context pointers.
* **Farms**: Multi-farm portfolio container. Connects soil reports, crop plans, predicted yields, analytics snapshots, and alerts under a specific farm context.
* **Soil Reports**: Captures chemical soil tests (NPK, pH, tested date) linked directly to a farm.
* **Disease Scans**: Holds photo uploads, diagnostic analysis, leaf type, confidence scoring, and treatment options.
* **Farm Plans**: Sowing calendars holding a list of sequential tasks (`FarmTasks`) with completion markers and snoozing support.
* **Notifications**: Central alert logging table supporting soft-deletions for idempotency.
