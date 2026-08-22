<div align="center">

# CareerPilot AI

### AI-Powered Career Intelligence Platform for Students & Fresh Graduates

**Transform your resume into actionable career intelligence — from job matching and skill-gap analysis to personalized career planning and AI-powered interview preparation.**

<br />

[![React](https://img.shields.io/badge/React-19-61DAFB?style=for-the-badge&logo=react&logoColor=white)](https://react.dev/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.141-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![MySQL](https://img.shields.io/badge/MySQL-8-4479A1?style=for-the-badge&logo=mysql&logoColor=white)](https://www.mysql.com/)
[![LangChain](https://img.shields.io/badge/LangChain-AI-1C3C3C?style=for-the-badge&logo=langchain&logoColor=white)](https://www.langchain.com/)
[![Google Gemini](https://img.shields.io/badge/Google_Gemini-AI-8E75B2?style=for-the-badge&logo=googlegemini&logoColor=white)](https://ai.google.dev/)

<br />

**React • FastAPI • LangChain • LangGraph • Google Gemini • MySQL • ChromaDB • JWT • RAG**

</div>

---

## 📌 Overview

**CareerPilot AI** is a full-stack AI-powered career intelligence platform designed for students, fresh graduates, and early-career software professionals.

Instead of providing generic career advice, CareerPilot uses the user's **actual resume as contextual evidence** to generate personalized career insights.

The platform combines **Retrieval-Augmented Generation (RAG)**, semantic resume retrieval, structured AI workflows, job-description analysis, persistent application data, and conversational AI to help users understand:

- how well their profile matches a target role,
- which skills they are currently missing,
- what they should learn next,
- how they can improve their career readiness,
- and how prepared they are for interviews.

---

## ✨ Core Features

### 📄 Resume Intelligence

Upload a PDF resume and transform it into structured career context.

- PDF text extraction
- Resume chunking
- Gemini embeddings
- Chroma vector storage
- Semantic resume retrieval
- Resume-grounded AI responses
- Active resume management

---

### 🎯 Job Match Analysis

Compare an uploaded resume against a target job description.

CareerPilot evaluates:

- overall job-match score,
- strong skill matches,
- partial matches,
- missing requirements,
- resume improvement opportunities,
- and priority actions.

The analysis is persisted so users can revisit previous results.

---

### 📊 Skill Gap Analysis

Convert job-match results into a prioritized learning strategy.

Skill gaps are classified based on importance and transformed into actionable recommendations, helping users understand **what to learn first instead of receiving an unstructured list of missing technologies**.

---

### 🗺️ Career Planning

Generate a structured career-development roadmap based on the user's profile and target role.

CareerPilot can provide:

- prioritized learning goals,
- practical development tasks,
- project recommendations,
- career-readiness guidance,
- immediate next actions,
- and structured progression plans.

---

### 🤖 Career AI

A resume-aware conversational career assistant powered by **LangChain, LangGraph, and Google Gemini**.

Career AI combines:

- resume context,
- semantic retrieval,
- conversation threads,
- routing workflows,
- career guidance,
- project guidance,
- interview preparation,
- and contextual AI responses.

The goal is to provide guidance grounded in what the user has actually built and learned.

---

### 🎤 Mock Interview

Practice interviews generated around the user's actual career profile.

Interview sessions can incorporate:

- resume context,
- target job information,
- identified skill gaps,
- interview type,
- adaptive questions,
- answer evaluation,
- feedback,
- and final readiness summaries.

Interview sessions are persisted for structured practice.

---

### 🕘 Analysis History

CareerPilot maintains previous career analyses so users do not lose earlier results.

Users can revisit historical:

- Job Match analyses
- Skill Gap reports
- Career Plans
- associated career insights

This turns CareerPilot from a one-time AI prompt into a persistent career-development workspace.

---

### 📥 Career Readiness Reports

CareerPilot supports PDF report generation for career-analysis results.

Reports can consolidate career intelligence such as:

- Job Match
- Skill Gap
- Career Plan
- learning priorities
- action plans
- interview preparation insights

This allows users to keep an offline snapshot of their career-readiness progress.

---

### 🔐 Authentication & User Isolation

CareerPilot includes JWT-based authentication and user-scoped application data.

Implemented capabilities include:

- user registration,
- secure login,
- password hashing,
- JWT access tokens,
- protected frontend routes,
- authenticated backend endpoints,
- user-owned resume access,
- and user-specific analysis persistence.

---

## 🧠 AI & RAG Workflow

CareerPilot does not rely only on a single prompt.

Resume information is processed through a retrieval pipeline so relevant evidence can be supplied to the AI when needed.

```mermaid
flowchart LR
    A[Resume PDF] --> B[PDF Text Extraction]
    B --> C[Text Chunking]
    C --> D[Gemini Embeddings]
    D --> E[(ChromaDB)]
    F[User Query] --> G[Semantic Search]
    E --> G
    G --> H[Relevant Resume Context]
    H --> I[LangChain / LangGraph]
    F --> I
    I --> J[Google Gemini]
    J --> K[Personalized Career Response]
```

This architecture enables CareerPilot to generate responses that are **grounded in resume evidence rather than relying entirely on generic model knowledge**.

---

## 🏗️ Application Architecture

```mermaid
flowchart TD
    USER[User] --> UI[React Frontend]

    UI --> AUTH[JWT Authentication]
    UI --> API[FastAPI REST API]

    API --> SQL[(MySQL)]
    API --> AI[AI Services]
    API --> VECTOR[(ChromaDB)]

    AI --> LC[LangChain]
    AI --> LG[LangGraph]

    LC --> GEMINI[Google Gemini]
    LG --> GEMINI

    VECTOR --> EMB[Gemini Embeddings]

    SQL --> USERS[Users]
    SQL --> RESUMES[Resume Metadata]
    SQL --> ANALYSIS[Career Analyses]
    SQL --> INTERVIEWS[Mock Interview Sessions]
```

### Storage Responsibilities

| Layer | Responsibility |
|---|---|
| **MySQL** | Users, resume metadata, analyses, workflow state and interview sessions |
| **ChromaDB** | Resume chunks, embeddings and semantic retrieval |
| **Gemini** | LLM reasoning, structured generation and embeddings |
| **Browser Storage** | Selected client-side UI/session state |

---

## 🛠️ Technology Stack

<div align="center">

### Frontend

<img src="https://skillicons.dev/icons?i=react,vite,tailwind,js" alt="Frontend technologies" />

**React 19 • Vite • Tailwind CSS • JavaScript • Axios • React Router**

<br />

### Backend

<img src="https://skillicons.dev/icons?i=python,fastapi" alt="Backend technologies" />

**Python 3.12 • FastAPI • SQLAlchemy • Pydantic • Alembic**

<br />

### AI & Retrieval

**LangChain • LangGraph • Google Gemini • Gemini Embeddings • ChromaDB • RAG**

<br />

### Database

<img src="https://skillicons.dev/icons?i=mysql" alt="Database technologies" />

**MySQL • SQLAlchemy ORM • Alembic Migrations**

<br />

### Development

<img src="https://skillicons.dev/icons?i=git,github,vscode" alt="Development tools" />

**Git • GitHub • VS Code • Pytest • ESLint**

</div>

---

## 📂 Project Structure

```text
CareerPilot-AI/
│
├── backend/
│   ├── alembic/
│   │   └── versions/
│   │
│   ├── app/
│   │   ├── auth/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   │
│   │   ├── agent_tools.py
│   │   ├── analysis_history_routes.py
│   │   ├── auth_routes.py
│   │   ├── database.py
│   │   ├── graph.py
│   │   ├── main.py
│   │   ├── mock_interview_routes.py
│   │   ├── resume_rag.py
│   │   ├── resume_routes.py
│   │   ├── router_graph.py
│   │   └── tool_agent_graph.py
│   │
│   ├── tests/
│   │   ├── manual_gemini_check.py
│   │   ├── manual_langchain_gemini_check.py
│   │   ├── test_analysis_service.py
│   │   ├── test_database.py
│   │   ├── test_graph.py
│   │   ├── test_mysql_checkpointer.py
│   │   ├── test_resume_rag.py
│   │   ├── test_router_graph.py
│   │   └── test_tool_agent.py
│   │
│   ├── .env.example
│   ├── alembic.ini
│   └── requirements.txt
│
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   ├── utils/
│   │   ├── App.jsx
│   │   ├── index.css
│   │   └── main.jsx
│   │
│   ├── .env.example
│   ├── package.json
│   └── vite.config.js
│
├── docs/
├── .gitignore
├── pyrefly.toml
└── README.md
```

---

## ⚙️ Local Development Setup

### Prerequisites

Make sure the following are installed:

- Python 3.12+
- Node.js and npm
- MySQL
- Git
- Google Gemini API key

---

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/SreenithiRamesh/CareerPilot-AI.git
cd CareerPilot-AI
```

---

### 2️⃣ Backend Setup

```bash
cd backend
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it.

#### Linux / WSL

```bash
source .venv/bin/activate
```

#### Windows PowerShell

```powershell
.venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

### 3️⃣ Configure Backend Environment

Copy the environment template:

```bash
cp .env.example .env
```

Configure the required values in `.env`.

Example:

```env
GEMINI_API_KEY=your_gemini_api_key_here

DATABASE_URL=mysql+pymysql://careerpilot:your_password@127.0.0.1:3306/careerpilot_ai

JWT_SECRET_KEY=replace_with_a_long_random_secret
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

LANGGRAPH_DATABASE_URL=mysql://careerpilot:your_password@127.0.0.1:3306/careerpilot_ai
```

> Never commit the real `.env` file or production credentials to source control.

---

### 4️⃣ Run Database Migrations

From the `backend` directory:

```bash
alembic upgrade head
```

Verify the current migration:

```bash
alembic current
```

---

### 5️⃣ Start the FastAPI Backend

```bash
uvicorn app.main:app --reload
```

Backend:

```text
http://127.0.0.1:8000
```

FastAPI API documentation:

```text
http://127.0.0.1:8000/docs
```

Health endpoint:

```text
http://127.0.0.1:8000/health
```

Expected response:

```json
{
  "status": "ok",
  "message": "CareerPilot AI backend is running"
}
```

---

### 6️⃣ Frontend Setup

Open another terminal:

```bash
cd frontend
npm install
```

Create the frontend environment file:

```bash
cp .env.example .env
```

Development configuration:

```env
VITE_API_BASE_URL=http://127.0.0.1:8000
```

Start Vite:

```bash
npm run dev
```

Open the local URL displayed by Vite in your browser.

---

## 🧪 Testing & Quality Checks

### Backend Tests

From `backend/`:

```bash
python -m pytest -q
```

Current validated test suite:

```text
10 passed
```

### Frontend Lint

From `frontend/`:

```bash
npm run lint
```

### Production Build

```bash
npm run build
```

The current frontend passes ESLint and generates a successful Vite production build.

---

## 🔒 Security Practices

CareerPilot currently applies several application-security practices:

- JWT-based authentication
- password hashing
- protected frontend routes
- authenticated backend endpoints
- user-scoped database queries
- environment-based secret configuration
- `.env` exclusion from Git
- tracked `.env.example` templates
- separation of user data and vector metadata
- server-side ownership validation

Sensitive credentials must never be stored directly in source code.

---

## 📸 Product Preview

### 🏠 CareerPilot AI — Home

CareerPilot introduces the complete career-readiness workflow through a clean, focused interface designed for students and fresh graduates.

<div align="center">
  <img
    src="docs/screenshots/home-hero.png"
    alt="CareerPilot AI Home Page"
    width="100%"
  />
</div>

<br />

### 🔄 From Resume to Career Roadmap

CareerPilot transforms one resume through four focused stages — **Parse, Match, Diagnose, and Plan** — turning raw profile information into actionable career guidance.

<div align="center">
  <img
    src="docs/screenshots/home-workflow.png"
    alt="CareerPilot AI Four Stage Career Analysis Workflow"
    width="100%"
  />
</div>

<br />

### 🎯 Explainable Career Insights

Instead of returning only a match score, CareerPilot separates **strong matches, partial matches, and priority skill gaps** so users can understand why they received a particular result.

<div align="center">
  <img
    src="docs/screenshots/home-career-insights.png"
    alt="CareerPilot AI Explainable Career Insights"
    width="100%"
  />
</div>

<br />

### 💡 Product Guidance

Built-in guidance explains how Career AI, Job Match, Skill Gap Analysis, Career Readiness Reports, and Mock Interviews work together.

<div align="center">
  <img
    src="docs/screenshots/home-faq.png"
    alt="CareerPilot AI Product FAQ"
    width="100%"
  />
</div>

<br />

### 🚀 Start Your Career Analysis

CareerPilot provides a clear path from resume upload to personalized career preparation.

<div align="center">
  <img
    src="docs/screenshots/home-cta.png"
    alt="CareerPilot AI Career Analysis Call to Action"
    width="100%"
  />
</div>

Once screenshots are added, this section can become a visual product walkthrough.

## 🔐 Authentication

CareerPilot includes secure user authentication with protected application routes and session-based access to career features.

### 📝 User Registration

New users can create an account through the registration flow before accessing the CareerPilot workspace.

<div align="center">
  <img
    src="docs/screenshots/register.png"
    alt="CareerPilot AI Registration Page"
    width="100%"
  />
</div>

<br />

### 🔑 User Login

Registered users can securely sign in and access protected pages such as Dashboard, Resume, Career AI, Job Match, Skill Gap, Career Plan, History, and Mock Interview.

<div align="center">
  <img
    src="docs/screenshots/login.png"
    alt="CareerPilot AI Login Page"
    width="100%"
  />
</div>

### ✅ Authentication Flow Validated

- User registration
- Form validation
- Secure password handling
- Login authentication
- JWT-based access
- Protected route access
- Session persistence
- Logout flow
## 📊 Career Dashboard

CareerPilot provides a centralized career workspace where users can track their progress across the complete career-preparation workflow.

The dashboard connects Resume Analysis, Job Match, Skill Gap Analysis, Career Planning, Mock Interviews, Career AI, and historical reports through a unified interface.

### Career Preparation Workflow

<div align="center">
  <img
    src="docs/screenshots/dashboard1.png"
    alt="CareerPilot AI Career Dashboard and Workflow"
    width="100%"
  />
</div>

<br />

### Career Readiness & Analysis Tracking

<div align="center">
  <img
    src="docs/screenshots/dashboard2.png"
    alt="CareerPilot AI Career Readiness Dashboard"
    width="100%"
  />
</div>

### Dashboard Capabilities

- Resume-driven career preparation workflow
- Career readiness progress tracking
- Job Match, Skill Gap, and Career Plan status
- Context-aware next-best-step recommendations
- Latest career analysis overview
- Direct access to Career AI
- Integrated Mock Interview and History modules
- Authenticated user workspace

  ## 📄 Resume Workspace

CareerPilot uses the user's selected resume as the evidence base for personalized career analysis.

Users can upload a PDF resume, which is prepared for downstream workflows including Job Match, Skill Gap Analysis, Career Planning, Career AI, and interview preparation.

### Resume Upload

<div align="center">
  <img
    src="docs/screenshots/before_resume_upload.png"
    alt="CareerPilot AI Resume Upload Workspace"
    width="100%"
  />
</div>

<br />

### Resume Successfully Prepared

<div align="center">
  <img
    src="docs/screenshots/after_resume_upload.png"
    alt="CareerPilot AI Successful Resume Upload"
    width="100%"
  />
</div>

### Resume Pipeline

- PDF resume selection and upload
- File type and size handling
- Resume text extraction
- Resume chunking for semantic retrieval
- Gemini embedding generation
- Chroma vector indexing
- Resume-grounded career analysis
- Active resume available across CareerPilot workflows
---

## 🚧 Engineering Roadmap

CareerPilot's application-level MVP is implemented. The next milestones focus on infrastructure and production deployment.

### 🐳 Containerization

- [ ] Backend Dockerfile
- [ ] MySQL container
- [ ] Docker Compose
- [ ] Environment-based container configuration
- [ ] Persistent Chroma volume
- [ ] Container networking
- [ ] Database migrations during deployment

### ☁️ AWS Deployment

- [ ] React production build on Amazon S3
- [ ] CloudFront distribution
- [ ] FastAPI deployment on Amazon EC2
- [ ] Nginx reverse proxy
- [ ] HTTPS configuration
- [ ] Private S3 resume storage
- [ ] IAM configuration
- [ ] CloudWatch logging and monitoring

### 🔄 CI/CD

- [ ] GitHub Actions
- [ ] Automated backend validation
- [ ] Automated frontend lint/build
- [ ] Deployment workflow
- [ ] Production secrets management

---

## 🎯 Project Goals

CareerPilot AI is being developed around four engineering objectives:

1. **Personalization** — career guidance should be grounded in the user's actual profile.
2. **Actionability** — AI output should translate into concrete next steps.
3. **Persistence** — analyses, interview sessions, and career progress should survive beyond a single prompt.
4. **Production readiness** — the application should evolve from a local AI prototype into a deployable full-stack system.

---

## 👩‍💻 Author

### Sreenithi Ramesh

Computer Science & Engineering Graduate | Software Development • Cloud • AI

[![GitHub](https://img.shields.io/badge/GitHub-SreenithiRamesh-181717?style=for-the-badge&logo=github)](https://github.com/SreenithiRamesh)

---

<div align="center">

### ⭐ CareerPilot AI

**From resume to roadmap — one career intelligence platform.**

Built with React, FastAPI, LangChain, LangGraph and Google Gemini.

</div>
