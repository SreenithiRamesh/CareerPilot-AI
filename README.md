<div align="center">

🚀 CareerPilot AI

Resume-Grounded Career Intelligence for Software Engineering Aspirants

From resume evidence to job-fit analysis, skill-gap discovery, project proof, career planning, AI guidance, mock interviews, and exportable career-readiness reports — in one persistent workspace.

<br>

React 19 · FastAPI · LangChain · LangGraph · Google Gemini · MySQL · ChromaDB · JWT · RAG

<br>

<img src="./docs/screenshots/home-hero.png" alt="CareerPilot AI Home" width="100%">

<br>

Built as a full-stack Applied AI portfolio project with authenticated workflows, persistent analysis history, resume-grounded retrieval, structured AI outputs, and interview preparation.

</div>

📖 Table of Contents

Why CareerPilot AI

What the Platform Does

End-to-End Product Flow

System Architecture

AI Orchestration

Resume RAG Architecture

Data & Persistence Architecture

Technology Stack

Product Walkthrough

Project Structure

API Overview

Security & User Isolation

Local Development

Testing & Quality Gates

Engineering Highlights

Roadmap

Author

🎯 Why CareerPilot AI

A resume contains useful evidence about a candidate, but turning that evidence into a practical career strategy usually requires several disconnected activities: comparing a profile with job descriptions, identifying missing skills, deciding what to learn, building proof of those skills, preparing for interviews, and tracking previous analyses.

CareerPilot AI brings that workflow into one system.

Instead of behaving like a generic chatbot, CareerPilot uses the user's selected resume as persistent career context. It combines structured application data with Retrieval-Augmented Generation (RAG) and specialized LangGraph workflows so recommendations can be grounded in the user's actual skills, projects, experience, and target role.

The core idea

Resume evidence → Role requirements → Skill gaps → Proof of skill → Career plan → Interview readiness

The platform is designed especially for students and fresh graduates who need actionable guidance without repeatedly explaining their background in every AI conversation.

✨ What the Platform Does

Capability

What CareerPilot Provides

📄 Resume Intelligence

PDF processing, semantic indexing, active-resume context, and resume-grounded retrieval

🎯 Job Match

Match score, strong matches, partial matches, missing skills, resume improvements, and priority actions

📊 Skill Gap

Existing skills, missing skills, priority gaps, learning order, practice tasks, and proof-of-skill actions

🧱 Build Evidence

Portfolio project prompts that turn missing skills into demonstrable engineering work

🗺️ Career Plan

Readiness summary, priorities, practical tasks, portfolio evidence, interview focus, and a 30-day roadmap

🤖 Career AI

Resume-aware conversational guidance with persisted context and specialized intent routing

🧑‍💻 Project Coach

Step-by-step project execution, README guidance, resume bullets, and project interview preparation

🎤 Mock Interview

Contextual questions, answer evaluation, feedback, and session summaries

🕘 Analysis History

Persistent Job Match, Skill Gap, and Career Plan results scoped to the authenticated user

📥 PDF Export

Downloadable saved-analysis reports for offline review

🔄 End-to-End Product Flow

flowchart LR
    A[Create Account] --> B[Upload Resume]
    B --> C[Resume Indexed]
    C --> D[Add Job Description]
    D --> E[Job Match]
    E --> F[Skill Gap]
    F --> G[Build Evidence]
    G --> H[Career Plan]
    H --> I[Career AI]
    I --> J[Project Coach]
    J --> K[Mock Interview]
    K --> L[History]
    L --> M[PDF Export]

CareerPilot is intentionally designed as a connected workflow. Resume context is reused across features, analyses are persisted, and Career AI can continue from existing career intelligence instead of treating each page as an isolated prompt.

🏗️ System Architecture

flowchart TB
    U[User / Browser]

    subgraph FE[Frontend - React + Vite]
        UI[CareerPilot UI]
        ROUTES[Protected Routes]
        AXIOS[Axios API Client]
    end

    subgraph BE[Backend - FastAPI]
        API[REST API]
        AUTH[JWT Authentication]
        GRAPH[LangGraph Router]
        SERVICES[Analysis Services]
        RAG[Resume RAG Service]
    end

    subgraph AI[AI Layer]
        LC[LangChain]
        GEMINI[Google Gemini]
        EMB[Gemini Embeddings]
    end

    subgraph DATA[Persistence Layer]
        MYSQL[(MySQL)]
        CHROMA[(ChromaDB)]
    end

    U --> UI
    UI --> ROUTES
    ROUTES --> AXIOS
    AXIOS --> API

    API --> AUTH
    API --> GRAPH
    API --> SERVICES
    GRAPH --> LC
    SERVICES --> LC
    LC --> GEMINI

    API --> RAG
    RAG --> EMB
    EMB --> CHROMA
    RAG --> CHROMA

    AUTH --> MYSQL
    SERVICES --> MYSQL
    API --> MYSQL

Architecture responsibilities

Layer

Responsibility

React frontend

Product UI, protected navigation, analysis workspaces, conversation UI, report actions

FastAPI backend

Authentication, request validation, orchestration, persistence, resume processing, API contracts

LangGraph

Intent routing and specialized career-analysis workflow orchestration

LangChain

Model integration, prompts, structured outputs, retrieval-aware AI operations

Google Gemini

Career reasoning, analysis generation, interview evaluation, and embedding generation

MySQL

Users, resume metadata, conversations, job descriptions, analyses, plans, and interview sessions

ChromaDB

Persistent vector collections containing resume chunks and metadata

JWT

Authenticated API access and user-scoped workflows

🧠 AI Orchestration

CareerPilot does not send every request through one generic prompt. The backend routes user intent to the appropriate workflow.

flowchart TD
    Q[User Request] --> R[LangGraph Intent Router]

    R -->|General career guidance| CA[Career Advisor]
    R -->|Resume question| RA[Resume Analysis]
    R -->|Role comparison| JM[Job Match]
    R -->|Missing skills| SG[Skill Gap]
    R -->|Preparation roadmap| CP[Career Plan]
    R -->|Build a project| PC[Project Coach]

    RES[Selected Resume Context] --> CA
    RES --> RA
    RES --> JM
    RES --> SG
    RES --> CP
    RES --> PC

    SAVED[Persisted Skill Gap Context] --> CA

    JM --> DB[(Persist Analysis)]
    SG --> DB
    CP --> DB

This separation keeps outputs purpose-specific while still allowing Career AI to reuse resume evidence and previously generated career context.

🔎 Resume RAG Architecture

The resume pipeline is the grounding layer behind CareerPilot.

flowchart LR
    PDF[Resume PDF] --> EXTRACT[Extract Text]
    EXTRACT --> SPLIT[Recursive Text Chunking]
    SPLIT --> EMBED[Gemini Embeddings]
    EMBED --> VECTOR[(ChromaDB)]

    QUERY[Career Query] --> SEARCH[Semantic Search]
    VECTOR --> SEARCH
    SEARCH --> CONTEXT[Relevant Resume Chunks]
    CONTEXT --> PROMPT[Grounded Prompt]
    QUERY --> PROMPT
    PROMPT --> LLM[Gemini]
    LLM --> ANSWER[Personalized Response]

Resume-level vector identity

Resume vector collections are associated with the resume ID, not a single conversation thread. This lets one selected resume support multiple Career AI conversations and downstream analysis workflows while keeping resume ownership tied to the authenticated user.

🗃 Data & Persistence Architecture

CareerPilot uses two storage systems because structured application state and semantic retrieval solve different problems.

flowchart TD
    USER[Authenticated User] --> RESUME[Resume Metadata]
    USER --> CONV[Conversations]
    USER --> JD[Job Descriptions]

    RESUME --> MATCH[Job Match Results]
    JD --> MATCH

    RESUME --> GAP[Skill Gap Reports]
    JD --> GAP

    RESUME --> PLAN[Career Plans]
    JD --> PLAN

    USER --> INTERVIEW[Mock Interview Sessions]

    RESUME --> VECTORS[(Chroma Resume Collection)]

MySQL stores

user accounts and authentication-related application data,

resume metadata and processing status,

conversation/thread metadata,

job descriptions,

Job Match results,

Skill Gap reports,

Career Plans,

Mock Interview sessions and related state.

ChromaDB stores

resume text chunks,

Gemini embeddings,

resume/user metadata used for semantic retrieval.

This separation allows CareerPilot to preserve transactional career history in MySQL while using vector search only where semantic retrieval adds value.

🛠️ Technology Stack

Frontend

React 19

Vite

React Router

Axios

Tailwind CSS

Lucide React

Backend

Python 3.12

FastAPI

SQLAlchemy

Pydantic

Uvicorn

PyPDF

Applied AI

LangChain

LangGraph

Google Gemini

Gemini Embeddings

Retrieval-Augmented Generation (RAG)

Structured AI outputs

Data

MySQL

ChromaDB

Authentication & Security

JWT

bcrypt password hashing

protected frontend routes

authenticated backend dependencies

user-owned resource checks

Engineering Tooling

Git

GitHub

ESLint

Pytest

VS Code

WSL2 / Linux development environment

🖥️ Product Walkthrough

The following screenshots show the actual CareerPilot workflow from discovery and authentication through career analysis, AI guidance, interview preparation, history, and report export.

🏠 1. Product Landing Experience

The landing experience introduces CareerPilot as a career-intelligence workflow rather than a standalone chatbot.

Hero

<img src="./docs/screenshots/home-hero.png" alt="CareerPilot AI Hero" width="100%">

Career Intelligence Overview

The product explains how resume evidence is transformed into personalized career insights.

<img src="./docs/screenshots/home-career-insights.png" alt="CareerPilot Career Insights" width="100%">

Product Workflow

The homepage communicates the connected journey from resume analysis to career preparation.

<img src="./docs/screenshots/home-workflow.png" alt="CareerPilot Product Workflow" width="100%">

Frequently Asked Questions

<img src="./docs/screenshots/home-faq.png" alt="CareerPilot FAQ" width="100%">

Call to Action

<img src="./docs/screenshots/home-cta.png" alt="CareerPilot CTA" width="100%">

🔐 2. Authentication

CareerPilot protects personalized career data behind authenticated user accounts.

Registration

<img src="./docs/screenshots/register.png" alt="CareerPilot Registration" width="100%">

Login

<img src="./docs/screenshots/login.png" alt="CareerPilot Login" width="100%">

JWT-backed authentication protects API requests while frontend protected routes keep workspace pages unavailable to unauthenticated users.

📊 3. Career Dashboard

The dashboard acts as the authenticated workspace entry point and provides access to the major CareerPilot workflows.

<img src="./docs/screenshots/dashboard1.png" alt="CareerPilot Dashboard" width="100%">

<img src="./docs/screenshots/dashboard2.png" alt="CareerPilot Dashboard Extended View" width="100%">

📄 4. Resume Intelligence

The Resume workspace establishes the grounding context used by the rest of the platform.

Before Upload

Users select a PDF resume for processing and indexing.

<img src="./docs/screenshots/before_resume_upload.png" alt="CareerPilot Resume Before Upload" width="100%">

After Upload

After processing, CareerPilot stores resume metadata and indexes semantic chunks for later retrieval.

<img src="./docs/screenshots/after_resume_upload.png" alt="CareerPilot Resume After Upload" width="100%">

Pipeline: PDF → text extraction → chunking → Gemini embeddings → ChromaDB → resume-grounded retrieval.

🎯 5. Job Match Workspace

Job Match compares the selected resume with a target role and returns an explainable fit assessment.

Target Job Description

The user provides the target role requirements that become the comparison baseline.

<img src="./docs/screenshots/job%20description.png" alt="CareerPilot Job Description Input" width="100%">

Match Score & Evidence

CareerPilot evaluates the profile across strong matches, partial matches, missing skills, resume improvements, and priority actions instead of returning only a similarity percentage.

<img src="./docs/screenshots/match_score.png" alt="CareerPilot Job Match Score" width="100%">

The completed analysis is persisted so it can be reopened later through Analysis History.

📊 6. Skill Gap Workspace

Skill Gap turns role mismatch into a prioritized development strategy.

Skill Gap Entry Point

The workflow reuses the selected resume and role context instead of requiring the user to rebuild their profile manually.

<img src="./docs/screenshots/skill-gap-initial.png" alt="CareerPilot Skill Gap Initial View" width="100%">

Skill Gap Analysis

CareerPilot separates:

existing skills,

partially demonstrated skills,

missing skills,

high-priority gaps,

medium-priority gaps,

low-priority gaps.

<img src="./docs/screenshots/skill-gap-analysis.png" alt="CareerPilot Skill Gap Analysis" width="100%">

Build Evidence

CareerPilot goes beyond “learn this technology.” Missing capabilities can be converted into portfolio project prompts and proof-of-skill actions that produce evidence a candidate can actually show.

<img src="./docs/screenshots/skill-gap-build-evidence.png" alt="CareerPilot Skill Gap Build Evidence" width="100%">

Action Plan

The final analysis organizes recommended learning order, practice tasks, and concrete next steps.

<img src="./docs/screenshots/skill-gap-action-plan.png" alt="CareerPilot Skill Gap Action Plan" width="100%">

🗺️ 7. Career Plan Workspace

Career Plan converts resume evidence and role-specific gaps into a realistic preparation roadmap.

Career Plan Entry Point

<img src="./docs/screenshots/career-plan-initial.png" alt="CareerPilot Career Plan Initial View" width="100%">

Readiness & Priority Analysis

The plan identifies what deserves attention first and connects learning with practical execution.

<img src="./docs/screenshots/career-plan-analysis-1.png" alt="CareerPilot Career Plan Analysis Part 1" width="100%">

<img src="./docs/screenshots/career-plan-analysis-2.png" alt="CareerPilot Career Plan Analysis Part 2" width="100%">

30-Day Roadmap

CareerPilot translates the analysis into a time-bounded roadmap designed to avoid wasting time on skills already demonstrated in the resume.

<img src="./docs/screenshots/career-plan-30-day-roadmap.png" alt="CareerPilot 30 Day Roadmap" width="100%">

🤖 8. Career AI Workspace

Career AI is the conversational layer of the platform, but it remains connected to CareerPilot's structured career context.

It can use:

the selected resume,

semantic resume retrieval,

persisted Skill Gap context,

conversation history,

intent routing,

and specialized project guidance.

Resume-Grounded Project Check

Career AI can evaluate a project in the context of what is already present in the user's resume.

<img src="./docs/screenshots/career-ai-project-check.png" alt="CareerPilot AI Project Check" width="100%">

Personalized Project Guidance

<img src="./docs/screenshots/careerpilot-ai-project-guidance.png" alt="CareerPilot AI Project Guidance" width="100%">

Project Coach

Project Coach turns a recommended skill into a structured implementation path.

<img src="./docs/screenshots/careerpilot-ai-project-coach.png" alt="CareerPilot AI Project Coach" width="100%">

Completion Guidance

The workflow continues beyond project ideation and helps the user close the implementation loop.

<img src="./docs/screenshots/careerpilot-project-coach-completion.png" alt="CareerPilot Project Coach Completion" width="100%">

README Guidance

Completed implementation can be translated into clear technical documentation.

<img src="./docs/screenshots/careerpilot-project-readme-guidance.png" alt="CareerPilot Project README Guidance" width="100%">

Resume Bullet Grounding

CareerPilot can turn completed project work into resume-ready bullets grounded in actual implementation evidence.

<img src="./docs/screenshots/careerpilot-resume-bullets-grounding.png" alt="CareerPilot Resume Bullet Grounding" width="100%">

Project Interview Preparation

The same project context can then be converted into interview preparation around architecture, implementation decisions, trade-offs, and outcomes.

<img src="./docs/screenshots/careerpilot-project-interview-preparation.png" alt="CareerPilot Project Interview Preparation" width="100%">

This creates a complete evidence loop:

Identify gap → Build project → Document project → Update resume → Prepare project explanation

🎤 9. Mock Interview Workspace

Mock Interview turns passive preparation into an interactive practice workflow.

Interview Setup

<img src="./docs/screenshots/mock-interview-initial.PNG" alt="CareerPilot Mock Interview Initial View" width="100%">

Interview Question

CareerPilot presents targeted questions one at a time.

<img src="./docs/screenshots/mock-interview-question.png" alt="CareerPilot Mock Interview Question" width="100%">

Answer Evaluation

<img src="./docs/screenshots/mock-interview-evaluating.png" alt="CareerPilot Mock Interview Evaluating" width="100%">

Actionable Feedback

<img src="./docs/screenshots/mock-interview-feedback.png" alt="CareerPilot Mock Interview Feedback" width="100%">

The evaluation flow also supports technical-topic feedback.

<img src="./docs/screenshots/mock-interview-feedback-react.png" alt="CareerPilot React Interview Feedback" width="100%">

Interview Summary

At session completion, CareerPilot consolidates performance into a readiness-oriented summary.

<img src="./docs/screenshots/mock-interview-summary.png" alt="CareerPilot Mock Interview Summary" width="100%">

🕘 10. Analysis History

CareerPilot treats generated analysis as persistent career data rather than disposable chat output.

Saved Analysis Timeline

<img src="./docs/screenshots/history-saved-analysis.png" alt="CareerPilot Saved Analysis History" width="100%">

Job Match Detail

Users can reopen a previously generated Job Match result without rerunning it.

<img src="./docs/screenshots/history-job-match-detail.png" alt="CareerPilot Job Match History Detail" width="100%">

Skill Gap & Career Plan History

<img src="./docs/screenshots/history-skill-gap-career-plan.png" alt="CareerPilot Skill Gap and Career Plan History" width="100%">

Skill Gap Detail

<img src="./docs/screenshots/history-skill-gap-detail.png" alt="CareerPilot Skill Gap History Detail" width="100%">

Career Plan Detail

<img src="./docs/screenshots/history-career-plan.png" alt="CareerPilot Career Plan History Detail" width="100%">

All historical analyses remain scoped to the authenticated user.

📥 11. Saved Analysis PDF Export

CareerPilot can convert a saved analysis into a portable PDF for offline review and preparation tracking.

<img src="./docs/screenshots/saved-analysis-pdf-export.png" alt="CareerPilot Saved Analysis PDF Export" width="100%">

This closes the workflow by turning persistent career intelligence into a downloadable artifact.

📁 Project Structure

CareerPilot-AI/
├── backend/
│   ├── app/
│   │   ├── auth/
│   │   │   ├── dependencies.py
│   │   │   └── security.py
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── analysis_service.py
│   │   ├── career_graph.py
│   │   ├── database.py
│   │   ├── main.py
│   │   ├── resume_rag.py
│   │   ├── resume_routes.py
│   │   └── router_graph.py
│   ├── tests/
│   ├── chroma_db/
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   │   ├── CareerAI.jsx
│   │   │   ├── CareerPlan.jsx
│   │   │   ├── Dashboard.jsx
│   │   │   ├── History.jsx
│   │   │   ├── HistoryDetail.jsx
│   │   │   ├── JobMatch.jsx
│   │   │   ├── Login.jsx
│   │   │   ├── MockInterview.jsx
│   │   │   ├── Register.jsx
│   │   │   ├── Resume.jsx
│   │   │   └── SkillGap.jsx
│   │   ├── api.js
│   │   └── App.jsx
│   └── package.json
│
├── docs/
│   └── screenshots/
│
└── README.md

The tree above highlights the major application modules. Generated build artifacts, local virtual environments, caches, and secrets are intentionally omitted.

🔌 API Overview

CareerPilot exposes authenticated FastAPI endpoints for the major application workflows.

Area

Purpose

Authentication

Register, login, current-user identity

Resume

Upload, process, index, and manage resume context

Career Chat

LangGraph-routed conversational career guidance

Job Match

Resume-to-role analysis

Skill Gap

Priority gap and learning analysis

Career Plan

Structured preparation roadmap

Mock Interview

Session creation, questions, evaluation, summaries

History

Retrieve persisted career analyses

FastAPI also provides interactive API documentation during local development.

🔐 Security & User Isolation

CareerPilot's personalized data model requires user-level isolation across resumes, conversations, and analyses.

Implemented safeguards include:

password hashing,

JWT access tokens,

authenticated FastAPI dependencies,

protected React routes,

user ownership validation,

user-scoped resume access,

user-scoped conversation access,

user-scoped persisted analyses,

environment-based secret configuration.

Environment safety

Secrets such as the Gemini API key, database credentials, and JWT secret should remain in local environment files and must not be committed to Git.

⚙️ Local Development

Prerequisites

Install:

Python 3.12+

Node.js and npm

MySQL

Git

1. Clone the repository

git clone <your-repository-url>
cd CareerPilot-AI

2. Backend setup

cd backend
python -m venv .venv-linux
source .venv-linux/bin/activate
pip install -r requirements.txt

Create backend/.env with the required local configuration:

GEMINI_API_KEY=your_gemini_api_key
DATABASE_URL=mysql+pymysql://username:password@localhost/careerpilot
JWT_SECRET_KEY=replace_with_a_strong_secret
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

Start the API:

uvicorn app.main:app --reload

Backend:

http://127.0.0.1:8000

3. Frontend setup

Open another terminal:

cd frontend
npm install
npm run dev

The Vite development server will print the local frontend URL.

4. Optional frontend environment variable

VITE_API_BASE_URL=http://127.0.0.1:8000

🧪 Testing & Quality Gates

Backend

Run:

cd backend
source .venv-linux/bin/activate
python -m pytest -q

Validated local test result:

10 passed

Backend import check

python -c "from app.main import app; print('Backend import OK')"

Frontend lint

cd frontend
npm run lint

Production build

npm run build

The project has been validated with:

successful FastAPI import,

passing backend tests,

clean frontend lint,

successful Vite production build.

🧩 Engineering Highlights

1. Resume-grounded RAG

CareerPilot retrieves relevant resume chunks before generating context-sensitive guidance instead of depending only on generic LLM knowledge.

2. Resume-level vector identity

Vector collections are tied to resume identity so a selected resume can support multiple Career AI threads and analysis workflows.

3. Specialized LangGraph routing

Different user intents are routed to dedicated workflows rather than forcing Job Match, Skill Gap, Career Plan, project coaching, and general guidance through one prompt.

4. Persistent career intelligence

Job descriptions, analyses, career plans, interview sessions, and conversation metadata are stored as application state instead of disappearing after one model response.

5. Cross-session context reuse

Career AI can reuse the selected resume and persisted Skill Gap context in a fresh conversation, reducing repetitive user input.

6. Evidence-oriented skill development

Skill Gap does not stop at identifying missing technologies. It recommends practice tasks, proof-of-skill actions, and portfolio projects that can create demonstrable evidence.

7. Full project evidence loop

Project Coach connects implementation guidance with completion, README documentation, resume bullets, and interview preparation.

8. Authenticated user isolation

Resume access, conversations, and historical analyses are associated with the authenticated user.

9. Structured, explainable outputs

Core analysis workflows return organized fields such as strong matches, missing skills, priority gaps, learning order, and action plans instead of opaque free-form responses.

10. Engineering quality gates

Backend tests, frontend linting, and production builds are used as regression checks before feature completion.

🛣️ Roadmap

Completed MVP

React frontend

FastAPI backend

JWT authentication

PDF resume processing

Gemini embeddings

ChromaDB resume RAG

Resume-grounded Career AI

Job Match analysis

Skill Gap analysis

Build Evidence recommendations

Career Plan generation

Project Coach workflow

Mock Interview workflow

Persistent analysis history

PDF export

Backend tests

Frontend lint and production build

Next Engineering Milestones

Dockerize frontend and backend

Add Docker Compose for local orchestration

Add CI/CD with GitHub Actions

Deploy backend to AWS EC2

Host frontend with Amazon S3 + CloudFront

Move production MySQL to Amazon RDS

Store original resume PDFs in Amazon S3

Add production monitoring and observability

Expand automated integration tests

💡 What This Project Demonstrates

CareerPilot AI brings together several software-engineering concerns in one application:

full-stack product development,

REST API design,

authentication and authorization,

relational persistence,

vector search,

RAG,

LLM integration,

LangGraph workflow orchestration,

structured AI outputs,

stateful user workflows,

AI-assisted career analysis,

automated testing,

and production-oriented architecture planning.

The project is intentionally built as an end-to-end applied AI system, not only as a chatbot interface.

👩‍💻 Author

Sreenithi Ramesh
Computer Science & Engineering Graduate — 2026
Software Engineering · Full-Stack Development · Cloud · Applied AI

<div align="center">

CareerPilot AI

Turn your resume into a practical career strategy.

Resume Intelligence · Job Match · Skill Gap · Career Plan · Career AI · Mock Interview

</div>
