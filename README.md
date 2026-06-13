# 🌿 AgriAssist AI — Virtual Agronomist & Enterprise Multi-Farm Intelligence Platform

[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)](https://react.dev/)
[![MySQL](https://img.shields.io/badge/MySQL-00758F?style=for-the-badge&logo=mysql&logoColor=white)](https://www.mysql.com/)
[![Gemini](https://img.shields.io/badge/Gemini_API-8E75C2?style=for-the-badge&logo=google&logoColor=white)](https://ai.google.dev/)
[![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)
[![Nginx](https://img.shields.io/badge/Nginx-009639?style=for-the-badge&logo=nginx&logoColor=white)](https://nginx.org/)

AgriAssist AI is a production-grade, full-stack agricultural decision-support platform built using FastAPI, React, MySQL, and Google Gemini AI. It enables multi-farm managers to aggregate NPK soil diagnostics, weather forecast telemetry, pest/disease risk warning forecasts, and live crop market prices into a unified dashboard workspace.

---

## 📖 Table of Contents
1. [Project Overview](#-project-overview)
2. [Problem Statement & Solution](#-problem-statement--solution)
3. [Core Capabilities (15 Sprints)](#-core-capabilities-15-sprints)
4. [Tech Stack](#-tech-stack)
5. [System Architecture](#-system-architecture)
6. [Database Schema & Migrations](#-database-schema--migrations)
7. [Installation & Setup](#-installation--setup)
   - [A. Docker Compose Orchestration (Recommended)](#a-docker-compose-orchestration-recommended)
   - [B. Direct Local Setup](#b-direct-local-setup)
8. [API Overview](#-api-overview)
9. [Automated Testing & Live Checks](#-automated-testing--live-checks)
10. [Folder Structure](#-folder-structure)
11. [Author & Contributions](#-author--contributions)

---

## 🌟 Project Overview
AgriAssist AI bridges the gap between raw scientific agronomy data (chemical soil reports, meteorological models) and daily farm operations. Using Google Gemini AI, the platform acts as a personalized virtual consultant, outputting structured crop suitability scores, organic pest mitigation steps, and adaptive sowing calendars.

---

## 💡 Problem Statement & Solution
* **The Problem**: Modern farmers manage multiple disparate land holdings and struggle to synthesize soil data sheets, weather alerts, fluctuating market rates, and crop disease anomalies into cohesive schedules. Django/Flask monolithic apps are often slow and lack mobile responsiveness.
* **The Solution**: AgriAssist AI isolates multi-farm contexts, offering a single responsive workspace where farmers can log reports, run AI diagnostics, track calendar checklists, and download PDF analytics snapshots.

---

## 🌾 Core Capabilities (15 Sprints)
* **Authentication & Profiles**: Secure signup, login, and token session control with bcrypt hashing and JWT.
* **Soil Diagnostics & Analysis**: Input and track pH, Nitrogen, Phosphorus, Potassium (NPK) values over time.
* **AI Crop Recommendation**: Matches soil parameters with optimal crop types using structured Gemini AI JSON outputs.
* **Disease Leaf spot Scanning**: Upload crop leaf photos to identify infections (fungal, bacterial) and receive organic treatment steps.
* **Market Price Tracker**: Live price feeds, net revenue projection models, and ROI ratio calculations.
* **Yield Projections**: Expected yield estimations per acre with confidence intervals.
* **Farm Planner & Activity Planners**: Sequential crop timeline calendars with tasks prioritized, complete flags, and snooze capabilities.
* **Risk Early Warnings**: Regional warning center alerting farmers of storms, pest threats, and soil hazards.
* **Virtual AI Consultant**: Context-aware agronomist chatbot referencing active soil profiles, location constraints, and chat logs.
* **Alert Inbox Inbox**: Central inbox aggregating notifications from all modules with soft-delete controls.
* **Executive PDF Report Compiler**: Generates downloadable PDF performance charts and profit gauges using ReportLab.
* **Multi-Farm Context Switching**: Create, manage, and toggle between multiple land holdings. Features self-healing fallback logic if context is lost.
* **Placement-Ready UX Polish**: Dynamic HSL light/dark themes, full-page loading indicators, skeleton card shimmers, global toast notifications, error boundaries, and system health status widgets.

---

## 🛠️ Tech Stack
* **Frontend SPA**: React.js (Vite, JavaScript), Axios (with request/response interceptors), Context API, HSL CSS design variables.
* **Backend API**: FastAPI (Python), SQLAlchemy ORM (MySQL driver), Pydantic v2 schemas, PyJWT token security, ReportLab PDF generator.
* **Database**: MySQL RDBMS, database schemas managed using Alembic migrations.
* **Deployment Packaging**: Docker, Docker-Compose, Nginx (for static SPA hosting and clean routing).
* **AI Cognitive Engine**: Google Gemini AI (1.5 Flash) via `google-genai` SDK.

---

## 📊 System Architecture

```mermaid
graph TD
    subgraph Client [React Frontend SPA]
        ReactSPA["React SPA (Vite)"]
        Nginx["Nginx Reverse Proxy"]
        AxiosClient["Axios Interceptor"]
    end

    subgraph API [FastAPI Backend]
        Router["REST routers (/auth, /farmers, /farms, /system)"]
        AuthMiddleware["JWT Middleware"]
        Services["Services (Auth, Farm, Chat, PDF Compiler)"]
        Repos["Repositories (CRUD layers)"]
    end

    subgraph Storage [Storage & External AI]
        MySQL[("MySQL RDBMS")]
        Gemini["Google Gemini AI"]
    end

    ReactSPA --> AxiosClient
    AxiosClient -->|Port 8000 REST| Router
    Router --> AuthMiddleware
    AuthMiddleware --> Services
    Services --> Repos
    Repos -->|SQLAlchemy| MySQL
    Services -->|API Client| Gemini
```

---

## 🔌 API Overview
All REST routes are prefixed under `/api/v1/`:

* `POST /auth/register` - Create farmer profile.
* `POST /auth/login` - Authenticate and retrieve bearer token.
* `GET /farmers/settings` / `PUT /farmers/settings` - Read/Update settings.
* `POST /farmers/change-password` - Update password.
* `GET /farms/portfolio` - Fetch total holdings summary.
* `POST /soil/reports` - Log soil metrics.
* `POST /crop-recommendations/generate` - Run AI suitability engine.
* `POST /disease/scans` - Upload foliage image for scanning.
* `POST /farm-planner/plans/generate` - Generate AI activity calendar.
* `GET /system/status` - Live system diagnostics.
* `GET /system/help` - Help guides and FAQs.

---

## ⚙️ Installation & Setup

### A. Docker Compose Orchestration (Recommended)
This runs the entire stack (React UI, FastAPI backend, MySQL database) with a single command.

1.  **Prerequisites**: Install [Docker Desktop](https://www.docker.com/products/docker-desktop/).
2.  **Configuration**: Copy `.env.example` to `.env` in the root folder and add your Gemini API Key:
    ```bash
    cp .env.example .env
    ```
    *Ensure `GEMINI_API_KEY=your_key` is set.*
3.  **Start Services**: Build and launch all container services:
    ```bash
    docker compose up --build -d
    ```
4.  **Database Seeding (Optional)**: Populates the container database with a recruiter demo profile:
    ```bash
    docker exec -it agriassist-api python ../scripts/seed_demo_data.py
    ```
5.  **Access URL Routes**:
    * **Frontend React SPA**: [http://localhost:3000/](http://localhost:3000/)
    * **Backend REST API**: [http://localhost:8000/docs/](http://localhost:8000/docs/)

---

### B. Direct Local Setup

#### 1. Database Configuration
Create your MySQL application database:
```sql
CREATE DATABASE IF NOT EXISTS agriassist;
```

#### 2. Backend API Setup
1.  Navigate to the backend directory and activate the virtual environment:
    ```bash
    cd backend
    python3 -m venv venv
    source venv/bin/activate
    ```
2.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
3.  Configure your local variables inside `backend/.env`:
    ```env
    DATABASE_URL=mysql+pymysql://root:password@localhost:3306/agriassist
    GEMINI_API_KEY=your_gemini_api_key_here
    JWT_SECRET_KEY=supersecretkeychangeinproduction1234567890
    ```
4.  Run database migrations and seed demo data:
    ```bash
    alembic upgrade head
    python ../scripts/seed_demo_data.py
    ```
5.  Start the dev server:
    ```bash
    uvicorn app.main:app --reload
    ```

#### 3. Frontend UI Setup
1.  Navigate to the frontend directory and install NPM packages:
    ```bash
    cd ../frontend
    npm install
    ```
2.  Start the Vite React development server:
    ```bash
    npm run dev
    ```
    *The client application will open at: http://localhost:5173/*

---

## 🧪 Automated Testing & Live Checks

### 1. Run Backend Unit Tests Suite
Verify database models, authentication constraints, and session logic using pytest:
```bash
PYTHONPATH=backend backend/venv/bin/pytest backend/app/tests/test_sprint14_ui.py
```

### 2. Run E2E Production Verification
Pings the live server endpoints, authenticates the recruiter account, verifies portfolio summaries, and tracks response times:
```bash
backend/venv/bin/python verify_release.py
```

---

## 📂 Folder Structure
```
agriassist-ai/
├── backend/                  # FastAPI REST Backend Service
│   ├── alembic/              # Database schema versions (Migrations)
│   ├── app/                  # Main server application
│   │   ├── api/              # Routers and controllers
│   │   ├── core/             # Base configurations and security
│   │   ├── models/           # SQLAlchemy DB Models
│   │   ├── repositories/     # Database CRUD layer
│   │   ├── schemas/          # Pydantic validation schemas
│   │   └── services/         # Business services and Gemini clients
│   ├── Dockerfile            # Backend production container script
│   └── requirements.txt      # Python dependencies list
├── frontend/                 # React Frontend Client
│   ├── src/                  # React components and contexts
│   ├── Dockerfile            # Frontend production container script
│   ├── nginx.conf            # Custom Nginx SPA configuration
│   └── package.json          # Node dependencies list
├── docs/                     # Technical specifications & guides
│   ├── architecture.md       # Detailed system design
│   ├── api.md                # Complete API payload directory
│   ├── interview-guide.md    # Placement Q&As package
│   └── resume-project.md     # Resume bullet points template
├── scripts/                  # Management scripts
│   └── seed_demo_data.py     # MySQL database seeder script
├── docker-compose.yml        # Orchestration compose configurations
├── verify_release.py         # Release integration test suite
└── RELEASE_NOTES.md          # Sprint roadmap summaries
```
