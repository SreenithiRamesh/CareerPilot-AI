<div align="center">

# CareerPilot AI

### AI-Powered Career Intelligence Platform for Students & Fresh Graduates

Turn one resume into a complete career-preparation workflow — job matching, skill-gap analysis, career planning, project guidance, mock interviews, history, and exportable reports.

<br/>

<img src="https://skillicons.dev/icons?i=react,vite,tailwind,js,python,fastapi,mysql,git,github,vscode" alt="CareerPilot AI Tech Stack" />

**LangChain · LangGraph · Google Gemini · ChromaDB · RAG · JWT · SQLAlchemy · Pytest**

<br/>

<img src="./docs/screenshots/home-hero.png" alt="CareerPilot AI Home" width="100%" />

<br/>

[![React](https://img.shields.io/badge/React-19-61DAFB?logo=react&logoColor=white)](https://react.dev)
[![FastAPI](https://img.shields.io/badge/FastAPI-Python%203.12-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![MySQL](https://img.shields.io/badge/MySQL-Database-4479A1?logo=mysql&logoColor=white)](https://www.mysql.com)
[![LangGraph](https://img.shields.io/badge/LangGraph-Orchestration-1C3C3C)](https://www.langchain.com/langgraph)
[![Gemini](https://img.shields.io/badge/Google-Gemini-8E75B2?logo=googlegemini&logoColor=white)](https://ai.google.dev)
[![Tests](https://img.shields.io/badge/Tests-10%20passing-brightgreen)](#testing--quality)

</div>

<br/>

## Table of Contents

- [About](#about-careerpilot-ai)
- [Key Capabilities](#key-capabilities)
- [End-to-End Workflow](#end-to-end-workflow)
- [System Architecture](#system-architecture)
- [Resume RAG Architecture](#resume-rag-architecture)
- [AI Orchestration with LangGraph](#ai-orchestration-with-langgraph)
- [Technology Stack](#technology-stack)
- [Product Showcase](#product-showcase)
- [Project Structure](#project-structure)
- [Local Development](#local-development)
- [Testing & Quality](#testing--quality)
- [Security](#security)
- [Engineering Highlights](#engineering-highlights)
- [Engineering Roadmap](#engineering-roadmap)
- [What This Project Demonstrates](#what-this-project-demonstrates)
- [Author](#author)

<br/>

## About CareerPilot AI

**CareerPilot AI** is a full-stack, resume-grounded career intelligence platform built for students and fresh graduates preparing for software engineering roles.

Instead of giving generic AI advice, CareerPilot uses the user's **actual resume as evidence** and combines it with a target job description, persisted analysis history, Retrieval-Augmented Generation (RAG), and structured AI workflows.

The platform helps answer practical questions such as:

> - How well does my resume match this role?
> - Which skills am I actually missing?
> - What should I learn first?
> - What should I build to prove those skills?
> - How should I plan the next 30 days?
> - How do I explain my projects in interviews?
> - Can I revisit previous analyses without starting over?

**Core workflow:**

```
Resume → Match → Diagnose → Build Evidence → Plan → Practice → Track
```

<br/>

## Key Capabilities

| Feature | What It Does |
|---|---|
| **Resume Intelligence** | Extracts PDF content, chunks it, generates embeddings, and indexes resume evidence in ChromaDB |
| **Job Match** | Compares the selected resume against a job description and produces an explainable match analysis |
| **Skill Gap** | Identifies existing, partial, and missing skills and prioritizes the most important gaps |
| **Build Evidence** | Converts missing skills into practical portfolio tasks and project recommendations |
| **Career Plan** | Generates a focused learning roadmap and 30-day preparation plan |
| **Career AI** | Provides resume-aware, contextual career guidance across fresh and existing conversations |
| **Project Coach** | Guides project execution, README documentation, resume bullets, and interview preparation |
| **Mock Interview** | Generates questions, evaluates answers, gives feedback, and produces readiness summaries |
| **Analysis History** | Persists Job Match, Skill Gap, and Career Plan results for later review |
| **PDF Export** | Exports saved analysis into a portable career-readiness report |
| **Authentication** | Uses JWT-based authentication with user-owned resumes, conversations, and analyses |

<br/>

## End-to-End Workflow

```mermaid
flowchart LR
    A[Register / Login] --> B[Upload Resume]
    B --> C[Resume RAG Index]
    C --> D[Add Job Description]
    D --> E[Job Match]
    E --> F[Skill Gap]
    F --> G[Build Evidence]
    G --> H[Career Plan]
    H --> I[Career AI]
    I --> J[Project Coach]
    J --> K[Mock Interview]
    K --> L[Analysis History]
    L --> M[PDF Export]
```

CareerPilot is designed as a **connected product**, not a collection of isolated AI pages. The selected resume becomes reusable context across workflows, while important analysis results are stored in MySQL for continuity.

<br/>

## System Architecture

```mermaid
flowchart TB
    U[User]

    subgraph FRONTEND[Frontend]
        R[React + Vite]
        ROUTER[React Router]
        API_CLIENT[Axios]
    end

    subgraph BACKEND[FastAPI Backend]
        API[REST API]
        AUTH[JWT Authentication]
        GRAPH[LangGraph Orchestration]
        SERVICES[Analysis Services]
        RAG[Resume RAG Service]
    end

    subgraph AI[AI Layer]
        LC[LangChain]
        GEMINI[Google Gemini]
        EMB[Gemini Embeddings]
    end

    subgraph DATA[Persistence]
        MYSQL[(MySQL)]
        CHROMA[(ChromaDB)]
    end

    U --> R
    R --> ROUTER
    ROUTER --> API_CLIENT
    API_CLIENT --> API

    API --> AUTH
    API --> GRAPH
    API --> SERVICES
    API --> RAG

    GRAPH --> LC
    SERVICES --> LC
    LC --> GEMINI

    RAG --> EMB
    EMB --> CHROMA

    AUTH --> MYSQL
    SERVICES --> MYSQL
    API --> MYSQL
```

**Storage responsibilities**

| Layer | Responsibility |
|---|---|
| **MySQL** | Users, resume metadata, conversations, job descriptions, Job Match results, Skill Gap reports, Career Plans, Mock Interview sessions |
| **ChromaDB** | Resume chunks, embeddings, resume/user metadata, semantic retrieval |
| **Gemini** | LLM reasoning, structured generation, interview evaluation, embeddings |
| **LangGraph** | Intent routing and specialized career workflow orchestration |
| **Browser Storage** | Lightweight selected UI/session state |

<br/>

## Resume RAG Architecture

```mermaid
flowchart LR
    A[Resume PDF] --> B[PDF Text Extraction]
    B --> C[Recursive Chunking]
    C --> D[Gemini Embeddings]
    D --> E[(ChromaDB)]

    F[User Query] --> G[Semantic Search]
    E --> G
    G --> H[Relevant Resume Evidence]
    H --> I[Grounded Prompt]
    F --> I
    I --> J[Google Gemini]
    J --> K[Personalized Response]
```

**Why this matters**

CareerPilot does not depend only on generic model knowledge. It retrieves relevant resume chunks and supplies them as context, allowing responses to remain connected to the candidate's actual projects, technologies, certifications, and experience.

Resume vector collections are associated with resume identity, so the same selected resume can support multiple Career AI conversations instead of being locked to a single chat thread.

<br/>

## AI Orchestration with LangGraph

```mermaid
flowchart TD
    Q[User Request] --> R[Intent Router]

    R -->|Career guidance| C[Career Advisor]
    R -->|Resume question| RES[Resume Advisor]
    R -->|Role comparison| JM[Job Match]
    R -->|Skill gaps| SG[Skill Gap]
    R -->|Preparation roadmap| CP[Career Plan]
    R -->|Project execution| PC[Project Coach]

    CTX[Resume Context] --> C
    CTX --> RES
    CTX --> JM
    CTX --> SG
    CTX --> CP
    CTX --> PC

    SAVED[Persisted Skill Gap Context] --> C
```

This makes CareerPilot more than a single-prompt chatbot. Different career requests are routed into specialized workflows while still sharing common authenticated context.

<br/>

## Technology Stack

<div align="center">

**Frontend**

<img src="https://skillicons.dev/icons?i=react,vite,tailwind,js" alt="Frontend Stack" />

React 19 · Vite · Tailwind CSS · JavaScript · Axios · React Router

<br/>

**Backend**

<img src="https://skillicons.dev/icons?i=python,fastapi" alt="Backend Stack" />

Python 3.12 · FastAPI · SQLAlchemy · Pydantic · Uvicorn · PyPDF

<br/>

**Database & Development**

<img src="https://skillicons.dev/icons?i=mysql,git,github,vscode" alt="Database and Tools" />

MySQL · ChromaDB · Git · GitHub · VS Code · Pytest · ESLint

<br/>

**Applied AI**

LangChain · LangGraph · Google Gemini · Gemini Embeddings · ChromaDB · Retrieval-Augmented Generation

</div>

<br/>

## Product Showcase

The screenshots below demonstrate the actual CareerPilot workflow from authentication and resume processing through career analysis, AI guidance, interview preparation, and history.

### 1 · Home Experience

CareerPilot introduces the full career-readiness workflow before the user enters the authenticated workspace.

**Home**
<img src="./docs/screenshots/home-hero.png" width="100%" />

**Resume-to-Roadmap Workflow**
<img src="./docs/screenshots/home-workflow.png" width="100%" />

**Explainable Career Insights**
<img src="./docs/screenshots/home-career-insights.png" width="100%" />

**Product Guidance (FAQ)**
<img src="./docs/screenshots/home-faq.png" width="100%" />

**Start Career Analysis**
<img src="./docs/screenshots/home-cta.png" width="100%" />

### 2 · Authentication

CareerPilot protects personalized career information with authenticated access.

**Registration**
<img src="./docs/screenshots/register.png" width="100%" />

**Login**
<img src="./docs/screenshots/login.png" width="100%" />

> **Authentication flow:** password hashing → JWT access token → protected frontend routes → authenticated backend endpoints → user-owned data access

### 3 · Career Dashboard

The dashboard provides a centralized workspace for the complete preparation flow.

**Dashboard — Overview**
<img src="./docs/screenshots/dashboard1.png" width="100%" />

**Dashboard — Readiness View**
<img src="./docs/screenshots/dashboard2.png" width="100%" />

### 4 · Resume Intelligence

The selected resume is the evidence base used by CareerPilot's downstream AI workflows.

**Before Upload**
<img src="./docs/screenshots/before_resume_upload.png" width="100%" />

**Resume Prepared Successfully**
<img src="./docs/screenshots/after_resume_upload.png" width="100%" />

> **Processing pipeline:** PDF validation → text extraction → text chunking → Gemini embeddings → ChromaDB indexing → reusable resume context

### 5 · Job Match Analysis

CareerPilot compares the selected resume against a target job description.

**Target Job Description**
<img src="./docs/screenshots/job%20description.png" width="100%" />

**Match Score & Explainable Results**
<img src="./docs/screenshots/match_score.png" width="100%" />

The analysis includes strong matches, partial matches, missing requirements, resume improvements, and priority actions, and is persisted for later review.

### 6 · Skill Gap Analysis

Skill Gap converts the Job Match result into a focused learning strategy.

**Skill Gap Workspace**
<img src="./docs/screenshots/skill-gap-initial.png" width="100%" />

**Existing, Partial & Missing Skills**
<img src="./docs/screenshots/skill-gap-analysis.png" width="100%" />

**Build Evidence** — instead of stopping with a list of missing technologies, CareerPilot recommends practical portfolio evidence that can demonstrate the skill.
<img src="./docs/screenshots/skill-gap-build-evidence.png" width="100%" />

**Learning & Action Plan**
<img src="./docs/screenshots/skill-gap-action-plan.png" width="100%" />

### 7 · Career Plan

Career Plan turns the analysis into a realistic preparation roadmap.

**Initial Career Plan Workspace**
<img src="./docs/screenshots/career-plan-initial.png" width="100%" />

**Priorities & Readiness**
<img src="./docs/screenshots/career-plan-analysis-1.png" width="100%" />
<img src="./docs/screenshots/career-plan-analysis-2.png" width="100%" />

**30-Day Roadmap**
<img src="./docs/screenshots/career-plan-30-day-roadmap.png" width="100%" />

> The plan prioritizes important gaps while avoiding unnecessary relearning of technologies already demonstrated by the candidate.

### 8 · Career AI & Project Coach

Career AI is resume-aware and uses conversation memory, semantic resume retrieval, and persisted career-analysis context.

**Resume-Grounded Project Check**
<img src="./docs/screenshots/career-ai-project-check.png" width="100%" />

**Personalized Project Guidance**
<img src="./docs/screenshots/careerpilot-ai-project-guidance.png" width="100%" />

**Project Coach**
<img src="./docs/screenshots/careerpilot-ai-project-coach.png" width="100%" />

**Project Completion Guidance**
<img src="./docs/screenshots/careerpilot-project-coach-completion.png" width="100%" />

**README Guidance**
<img src="./docs/screenshots/careerpilot-project-readme-guidance.png" width="100%" />

**Resume Bullet Grounding**
<img src="./docs/screenshots/careerpilot-resume-bullets-grounding.png" width="100%" />

**Project Interview Preparation**
<img src="./docs/screenshots/careerpilot-project-interview-preparation.png" width="100%" />

**CareerPilot Evidence Loop**

```
Identify Skill Gap
        ↓
   Build Project
        ↓
 Document Project
        ↓
Create Resume Evidence
        ↓
Prepare Interview Explanation
```

### 9 · Mock Interview

The Mock Interview workflow turns passive preparation into interactive practice.

**Interview Setup**
<img src="./docs/screenshots/mock-interview-initial.PNG" width="100%" />

**Interview Question**
<img src="./docs/screenshots/mock-interview-question.png" width="100%" />

**Answer Evaluation**
<img src="./docs/screenshots/mock-interview-evaluating.png" width="100%" />

**Feedback**
<img src="./docs/screenshots/mock-interview-feedback.png" width="100%" />

**Technical Feedback Example**
<img src="./docs/screenshots/mock-interview-feedback-react.png" width="100%" />

**Interview Summary**
<img src="./docs/screenshots/mock-interview-summary.png" width="100%" />

### 10 · Analysis History

CareerPilot stores generated analyses as persistent user-owned career data rather than disposable AI output.

**Saved Analysis Timeline**
<img src="./docs/screenshots/history-saved-analysis.png" width="100%" />

**Job Match Detail**
<img src="./docs/screenshots/history-job-match-detail.png" width="100%" />

**Skill Gap & Career Plan History**
<img src="./docs/screenshots/history-skill-gap-career-plan.png" width="100%" />

**Skill Gap Detail**
<img src="./docs/screenshots/history-skill-gap-detail.png" width="100%" />

**Career Plan Detail**
<img src="./docs/screenshots/history-career-plan.png" width="100%" />

### 11 · PDF Career Readiness Report

Saved analyses can be exported into a portable PDF report for offline preparation and review.

<img src="./docs/screenshots/saved-analysis-pdf-export.png" width="100%" />

<br/>

## Project Structure

```
CareerPilot-AI/
│
├── backend/
│   ├── alembic/
│   ├── app/
│   │   ├── auth/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   ├── analysis_history_routes.py
│   │   ├── auth_routes.py
│   │   ├── database.py
│   │   ├── main.py
│   │   ├── mock_interview_routes.py
│   │   ├── resume_rag.py
│   │   ├── resume_routes.py
│   │   └── router_graph.py
│   ├── tests/
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
│   ├── .env.example
│   ├── package.json
│   └── vite.config.js
│
├── docs/
│   └── screenshots/
│
├── .gitignore
└── README.md
```

<br/>

## Local Development

### Prerequisites

- Python 3.12+
- Node.js and npm
- MySQL
- Git
- Google Gemini API key

### Clone

```bash
git clone https://github.com/SreenithiRamesh/CareerPilot-AI.git
cd CareerPilot-AI
```

### Backend

```bash
cd backend
python -m venv .venv
```

**Linux / WSL:**
```bash
source .venv/bin/activate
```

**Windows PowerShell:**
```powershell
.venv\Scripts\Activate.ps1
```

**Install dependencies:**
```bash
pip install -r requirements.txt
```

**Create `.env`:**
```env
GEMINI_API_KEY=your_gemini_api_key

DATABASE_URL=mysql+pymysql://careerpilot:your_password@127.0.0.1:3306/careerpilot_ai

JWT_SECRET_KEY=replace_with_a_long_random_secret
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

LANGGRAPH_DATABASE_URL=mysql://careerpilot:your_password@127.0.0.1:3306/careerpilot_ai
```

**Run migrations:**
```bash
alembic upgrade head
```

**Start FastAPI:**
```bash
uvicorn app.main:app --reload
```

| Service | URL |
|---|---|
| API | `http://127.0.0.1:8000` |
| Swagger Docs | `http://127.0.0.1:8000/docs` |

### Frontend

```bash
cd frontend
npm install
```

**Create `.env`:**
```env
VITE_API_BASE_URL=http://127.0.0.1:8000
```

**Start:**
```bash
npm run dev
```

<br/>

## Testing & Quality

**Backend**

```bash
python -m pytest -q
```

Current validated test result: **10 passed** ✅

**Backend import validation**

```bash
python -c "from app.main import app; print('Backend import OK')"
```

**Frontend**

```bash
npm run lint
npm run build
```

The current local MVP has been validated with:

- ✅ Backend import success
- ✅ 10 passing Pytest tests
- ✅ Clean ESLint output
- ✅ Successful Vite production build

<br/>

## Security

CareerPilot implements:

- JWT authentication
- Password hashing
- Protected frontend routes
- Authenticated FastAPI endpoints
- User-owned resume validation
- User-scoped conversation access
- User-scoped analysis persistence
- Environment-based secrets
- `.env` exclusion from source control
- Server-side ownership checks

<br/>

## Engineering Highlights

| Highlight | Description |
|---|---|
| **Resume-grounded RAG** | Relevant resume evidence is retrieved before personalized guidance is generated |
| **Resume-level vector identity** | Resume collections are reusable across conversation threads while remaining associated with resume and user metadata |
| **Specialized AI workflows** | LangGraph routes requests into dedicated analysis and guidance paths instead of using one generic prompt |
| **Persistent career intelligence** | Job Match, Skill Gap, Career Plan, conversations, and interview sessions survive beyond a single model response |
| **Cross-session context reuse** | Career AI can reuse a selected resume and persisted Skill Gap context in a fresh conversation |
| **Evidence-first skill development** | Skill gaps are connected to practice tasks, proof-of-skill actions, and portfolio project prompts |
| **Full project evidence lifecycle** | Project Coach helps move from project implementation to README documentation, resume bullets, and interview preparation |
| **Explainable analysis** | The core workflows produce structured, inspectable fields rather than opaque free-form AI answers |

<br/>

## Engineering Roadmap

**Application MVP** ✅

- [x] Authentication
- [x] Resume PDF processing
- [x] Gemini embeddings
- [x] ChromaDB RAG
- [x] Job Match
- [x] Skill Gap
- [x] Build Evidence
- [x] Career Plan
- [x] Career AI
- [x] Project Coach
- [x] Mock Interview
- [x] Analysis History
- [x] PDF export
- [x] Backend tests
- [x] Frontend lint/build validation

**Next Phase** 🚧

- [ ] Dockerize the application
- [ ] Docker Compose local orchestration
- [ ] GitHub Actions CI/CD
- [ ] AWS EC2 backend deployment
- [ ] Amazon S3 + CloudFront frontend hosting
- [ ] Amazon RDS for production MySQL
- [ ] Private S3 resume storage
- [ ] CloudWatch monitoring
- [ ] Expanded integration tests

<br/>

## What This Project Demonstrates

CareerPilot AI demonstrates practical experience across:

**Full-Stack Development · REST APIs · Authentication · SQL Persistence · Vector Search · RAG · LLM Integration · LangGraph · Structured AI Workflows · State Management · Testing · Applied AI Product Engineering**

> The objective is not to build another chatbot interface, but to build a persistent, explainable, resume-grounded career intelligence system.

<br/>

## Author

<div align="center">

### Sreenithi Ramesh

**Computer Science & Engineering Graduate — 2026**

Software Engineering · Full-Stack Development · Cloud · Applied AI

<br/>

**CareerPilot AI**

*From resume to roadmap — one career intelligence platform.*

</div>
