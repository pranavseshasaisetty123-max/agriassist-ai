# 🌿 AgriAssist AI — Virtual Agronomist & Farmer Assistant

[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)](https://react.dev/)
[![MySQL](https://img.shields.io/badge/MySQL-00758F?style=for-the-badge&logo=mysql&logoColor=white)](https://www.mysql.com/)
[![Gemini](https://img.shields.io/badge/Gemini_API-8E75C2?style=for-the-badge&logo=google&logoColor=white)](https://ai.google.dev/)
[![Tailwind](https://img.shields.io/badge/Vanilla_CSS-1572B6?style=for-the-badge&logo=css3&logoColor=white)](#design-aesthetics)

AgriAssist AI is a production-grade, full-stack virtual agronomist assistant built to support farmers. Powered by Google Gemini AI, it answers agricultural queries regarding soil testing, pest management, crop scheduling, and modern farming techniques. 

This repository houses the **Sprint 1** foundation, providing secure authentication, profile customization, and topic-based AI conversational workspaces. Designed with clean software architecture principles, it is ready to scale into a multimodal AI agent.

---

## 🚀 Features (Sprint 1)

*   **Farmer Authentication**: Secure signup and login using **Bcrypt** password hashing and **JWT** session authorization.
*   **Profile Settings**: Customized farmer profiles specifying location (state/district) and contact details to facilitate localized agricultural advice.
*   **Conversational Workspace**: Interactive chat interface with real-time prompt-response sequences, supported by custom loading indicators and micro-animations.
*   **Topic Sessions**: Session-based chat history tracking, allowing farmers to organize conversations by crop, season, or pest query.
*   **Gemini API Integration**: Directly integrated with the `google-genai` SDK using a tailored system instruction prompt instructing the model to act as a professional virtual agronomist.

---

## 🛠️ Tech Stack

*   **Frontend SPA**: [React](https://react.dev/) (Vite, JavaScript), [React Router v6](https://reactrouter.com/), [Axios](https://axios-http.com/) (with request/response JWT header interceptors), Context API.
*   **Backend API**: [FastAPI](https://fastapi.tiangolo.com/) (Python), [SQLAlchemy ORM](https://www.sqlalchemy.org/), [Alembic](https://alembic.sqlalchemy.org/) (database migrations), [Pydantic v2](https://docs.pydantic.dev/), [PyJWT](https://pyjwt.readthedocs.io/).
*   **Database**: [MySQL](https://www.mysql.com/) (Relational schema storing farmers, chat sessions, and message logs).
*   **AI Engine**: [Google Gemini API](https://ai.google.dev/) (`gemini-2.5-flash` model).

---

## 📊 System Architecture

The project is structured as a decoupled monorepo containing `frontend` and `backend` services communicating over a secure RESTful API.

```mermaid
graph TD
    %% Frontend Client
    subgraph Client [React Frontend]
        ReactSPA["React SPA (Vite)"]
        AuthCtx["Auth Context<br>(JWT Persistence)"]
        AxiosClient["Axios Interceptor<br>(Injects Bearer Token)"]
    end

    %% Backend Services
    subgraph API [FastAPI Backend]
        Router["Router / API Endpoints<br>(/auth, /farmers, /chat)"]
        AuthMiddleware["JWT Middleware<br>(Token validation)"]
        
        subgraph Services [Service Layer]
            AuthService["Auth Service<br>(Bcrypt verify)"]
            ChatService["Chat Service<br>(Message Flow Coordinator)"]
            AIService["AI Service<br>(Gemini SDK Client)"]
        end

        subgraph Repositories [Repository Layer]
            FarmerRepo["Farmer Repository<br>(CRUD on Farmers)"]
            ChatRepo["Chat Repository<br>(CRUD on Chat Logs)"]
        end
    end

    %% Data / AI Layer
    subgraph Storage [Storage & External AI]
        MySQL[("MySQL Database<br>(farmers, sessions, messages)")]
        Gemini["Google Gemini API<br>(gemini-2.5-flash)"]
    end

    %% Connect flows
    ReactSPA --> AuthCtx
    ReactSPA --> AxiosClient
    AxiosClient -->|HTTPS + JWT Header| Router
    Router --> AuthMiddleware
    AuthMiddleware --> AuthService
    AuthMiddleware --> ChatService
    
    AuthService --> FarmerRepo
    ChatService --> ChatRepo
    ChatService --> AIService
    
    FarmerRepo -->|SQLAlchemy| MySQL
    ChatRepo -->|SQLAlchemy| MySQL
    AIService -->|API Key Auth| Gemini
```

---

## ⚙️ Environment Variables

The backend application requires configuration values to be set in a `.env` file under the `/backend` directory:

| Variable | Description | Example |
| :--- | :--- | :--- |
| `DATABASE_URL` | MySQL Connection String | `mysql+pymysql://root:password@localhost:3306/agriassist` |
| `GEMINI_API_KEY` | Google Gemini API Key | `AIzaSyB...` (From Google AI Studio) |
| `JWT_SECRET_KEY` | Signing Secret Key for JWTs | `supersecretkeychangeinproduction12345` |
| `JWT_ALGORITHM` | Algorithm used to sign tokens | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Time limit before session expires | `30` |

---

## 🔌 API Routes

All endpoints reside under the `/api/v1` namespace. Operations labeled as **Authenticated** require a header: `Authorization: Bearer <JWT_TOKEN>`.

| Route | Method | Authenticated | Payload | Purpose |
| :--- | :--- | :--- | :--- | :--- |
| `/auth/register` | **POST** | No | `{ email, password, first_name, last_name, location, contact_number }` | Register a new farmer account |
| `/auth/login` | **POST** | No | Form-Data: `{ username, password }` | Authenticate and obtain JWT token |
| `/farmers/me` | **GET** | Yes | *None* | Retrieve logged-in profile data |
| `/farmers/me` | **PUT** | Yes | `{ first_name, last_name, location, contact_number }` | Update user location/contact info |
| `/chat/sessions` | **GET** | Yes | *None* | List chat history topics |
| `/chat/sessions` | **POST** | Yes | `{ title }` | Start a new chat topic session |
| `/chat/sessions/{id}/messages` | **GET** | Yes | *None* | Load messages inside a session |
| `/chat/sessions/{id}/messages` | **POST** | Yes | `{ message_text }` | Send user query and receive AI reply |

---

## 🛠️ Installation & Setup

### Prerequisites
*   Python 3.10+
*   Node.js 18+
*   MySQL Server running locally

### 1. Database Setup
Log into your MySQL terminal and create the application database:
```sql
CREATE DATABASE IF NOT EXISTS agriassist;
```

### 2. Backend Installation
1.  Navigate to the backend directory:
    ```bash
    cd backend
    ```
2.  Create and activate a virtual environment:
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```
3.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
4.  Configure your variables by creating a `.env` file under the `/backend` folder:
    ```env
    DATABASE_URL=mysql+pymysql://<user>:<password>@localhost:3306/agriassist
    GEMINI_API_KEY=your_gemini_api_key_here
    ```
5.  Run database migrations to generate schemas:
    ```bash
    alembic upgrade head
    ```
6.  Start the FastAPI development server:
    ```bash
    uvicorn app.main:app --reload
    ```
    *API documentation will be accessible at: http://127.0.0.1:8000/docs*

### 3. Frontend Installation
1.  Navigate to the frontend directory:
    ```bash
    cd ../frontend
    ```
2.  Install packages:
    ```bash
    npm install
    ```
3.  Start the Vite React development server:
    ```bash
    npm run dev
    ```
    *The client application will open at: http://localhost:5173/*

---

## 🧪 Testing

The backend includes a comprehensive test suite (10/10 test cases passing) built with `pytest` verifying auth validation and chat session constraints. Run tests with:
```bash
PYTHONPATH=backend venv/bin/pytest
```

---

## 🔮 Future Roadmap

*   **Weather Forecast Integration**: Implementing Gemini **Function Calling (Tools)** to query real-time external weather APIs and automatically advise on optimal harvest/watering dates.
*   **Multimodal Crop Diagnosis**: Allowing farmers to upload pictures of damaged leaves, sending image streams directly to Gemini Vision to diagnose pest issues.
*   **Knowledge Base (RAG)**: Integrating a Vector Database (Qdrant/Milvus) storing PDF farming guides to give localized, expert answers based on regional agricultural manuals.
*   **Asynchronous Background Queues**: Deploying Redis & Celery for automated soil health email reporting and scheduled alert configurations.
