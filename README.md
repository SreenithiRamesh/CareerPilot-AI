# CareerPilot AI

CareerPilot AI is an AI-powered career guidance platform designed for students and fresh graduates preparing for software engineering careers.

The platform combines FastAPI, LangChain, LangGraph, Google Gemini, resume RAG, semantic retrieval, and multi-agent workflows to provide personalized career guidance.

## Current Features

- Career guidance specialist agent
- Resume analysis agent
- Interview preparation agent
- Resume-to-job-description matching
- Skill-gap analysis
- Multi-step career planning workflow
- LangGraph conversation memory using thread IDs
- Resume PDF upload and text extraction
- Resume chunking and Gemini embeddings
- Semantic resume retrieval
- Resume RAG
- Autonomous tool-calling prototype
- FastAPI Swagger documentation

## Current Technology Stack

### Backend

- Python
- FastAPI
- Pydantic

### AI

- LangChain
- LangGraph
- Google Gemini
- Gemini Embeddings

### Resume Processing

- PyPDF
- LangChain Text Splitters

### Planned Infrastructure

- MySQL
- Persistent Chroma
- JWT Authentication
- React.js
- Amazon S3
- Amazon EC2
- Amazon CloudFront
- Docker
- Nginx
- Amazon CloudWatch
- GitHub Actions

## Project Structure

```text
CareerPilot-AI/
│
├── backend/
│   ├── app/
│   │   ├── agent_tools.py
│   │   ├── graph.py
│   │   ├── main.py
│   │   ├── resume_rag.py
│   │   ├── resume_routes.py
│   │   ├── router_graph.py
│   │   └── tool_agent_graph.py
│   │
│   ├── tests/
│   │   ├── direct_gemini_test.py
│   │   ├── test_gemini.py
│   │   ├── test_graph.py
│   │   ├── test_resume_rag.py
│   │   ├── test_router_graph.py
│   │   └── test_tool_agent.py
│   │
│   ├── .env.example
│   ├── .gitignore
│   └── requirements.txt
│
├── pyrefly.toml
└── README.md
```
