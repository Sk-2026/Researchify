# ZealWithin 🦅
### Keep the researcher in you alive.

**ZealWithin** is an AI-powered research discovery companion designed to help researchers discover relevant academic papers, stay updated with emerging research, and spend less time searching and more time innovating.

---

## 💡 The Idea

Research is driven by curiosity, passion, and the desire to discover something new. However, researchers often spend significant time searching across multiple academic platforms, filtering irrelevant publications, and manually tracking new developments.

ZealWithin aims to change this experience through personalized, AI-assisted paper discovery and continuous research monitoring.

**Our belief:** Even in a busy world, the researcher within us should never stop exploring.

## 🎯 The Problem

- **Information overload:** An enormous volume of academic publications makes relevant discoveries difficult.
- **Fragmented discovery:** Researchers must navigate multiple research platforms.
- **Limited personalization:** Traditional keyword searches often miss context and meaningful connections.
- **Missed opportunities:** Manual monitoring makes it difficult to stay current.

## 🚀 Our Solution

ZealWithin provides a personalized research discovery workflow:

1. Researchers create an account and define their research interests.
2. The platform discovers academic papers from integrated research sources.
3. An AI-powered recommendation engine evaluates and ranks papers.
4. Researchers receive relevant recommendations through their dashboard.
5. Background monitoring identifies newly available research.
6. Qualifying discoveries trigger in-app and email notifications.

## ✨ Key Features

| Feature | Description |
|---|---|
| Researcher profiles | Define research domains, descriptions, and interests. |
| Keyword personalization | Include relevant keywords and exclude unwanted topics. |
| Academic paper discovery | Discover publications using OpenAlex and Semantic Scholar. |
| AI-powered recommendations | Combine semantic similarity and keyword relevance. |
| Recency-aware ranking | Prioritize relevant and recent research. |
| Paper management | Save, dismiss, and mark papers as read. |
| Paper import | Import papers using a title or DOI and explore suggested keywords. |
| In-app notifications | Receive and manage research alerts from the dashboard. |
| Email notifications | Receive email alerts for qualifying discoveries. |
| Automated monitoring | A background worker checks for new research every 30 minutes. |

## 🧠 AI-Powered Recommendation Engine

ZealWithin uses a hybrid relevance-ranking approach.

**1. Semantic similarity — 55%**

Uses Sentence Transformers (`all-MiniLM-L6-v2`) to generate embeddings and evaluate contextual similarity between research interests and academic papers.

**2. Keyword relevance — 45%**

Evaluates keyword matches in paper titles and abstracts.

The relevance score combines these two signals.

The final ranking score incorporates:

- Relevance: 70%
- Recency: 25%
- Researcher feedback: 5%

These scores are ranking signals, not calibrated probabilities.

## 🏗️ System Architecture

```text
             RESEARCHER
                  |
                  v
          NEXT.JS FRONTEND
                  |
                  v
           FASTAPI BACKEND
                  |
        +---------+----------+
        |         |          |
        v         v          v
   DISCOVERY   AI ENGINE   USER APIs
        |         |          |
        v         v          v
   OpenAlex   Semantic    PostgreSQL
   Semantic   Ranking     + pgvector
   Scholar
        |
        v
  PAPER INGESTION
        |
        v
  RECOMMENDATIONS
        |
        v
 NOTIFICATION SYSTEM
        |
      +---+
      |   |
      v   v
   IN-APP EMAIL
   ALERTS  ALERTS

  BACKGROUND MONITORING WORKER
       (Every 30 Minutes)
```

## 🛠️ Technology Stack

| Layer | Technologies |
|---|---|
| Frontend | Next.js, React, TypeScript |
| Backend | Python, FastAPI |
| Database | PostgreSQL, pgvector |
| ORM | SQLAlchemy |
| Migrations | Alembic |
| AI / Embeddings | Sentence Transformers, NumPy |
| Authentication | JWT |
| Research APIs | OpenAlex, Semantic Scholar |
| Email | SMTP |
| Background processing | Python monitoring worker |
| Containerization | Docker |

## ⚙️ Running Locally

### Prerequisites

- Python 3.12
- Node.js and npm
- PostgreSQL with pgvector support
- Docker (for the configured database setup)

### 1. Clone the repository

```bash
git clone https://github.com/Sk-2026/Researchify.git
cd Researchify
```

### 2. Start the database

Start the PostgreSQL database using the project's Docker Compose configuration.

### 3. Configure the backend

Navigate to the backend:

```bash
cd backend
```

Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Configure your backend `.env` file with the required database, authentication, academic API, and SMTP settings.

Apply database migrations:

```bash
alembic upgrade head
```

Start the API:

```bash
uvicorn app.main:app --reload
```

API documentation:

http://127.0.0.1:8000/docs

### 4. Start the frontend

Open another terminal:

```bash
cd frontend
npm install
```

Configure `frontend/.env.local` with the backend API URL:

```env
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000/api/v1
```

Start the frontend:

```bash
npm run dev
```

Open:

http://localhost:3000

### 5. Start automated monitoring

Open another backend terminal, activate the virtual environment, and run:

```bash
python -m app.workers.monitoring_worker
```

The monitoring worker checks active researcher profiles every 30 minutes.

**Note:** In the local prototype, the database, internet connection, and worker process must remain available for continuous monitoring. Always-on cloud deployment is a future improvement.

## 👥 Who Can Use ZealWithin?

- Postgraduate students
- PhD scholars
- Research assistants
- Academic researchers and faculty
- University research laboratories
- Research and development teams

The platform is designed to support researchers across disciplines, with the initial prototype focused on Computer Vision research.

## 🔮 Future Scope

- Always-on cloud deployment
- Additional academic publication sources
- More advanced feedback-driven personalization
- Research group and laboratory workspaces
- Configurable notification preferences and richer digests
- Expanded notification channels
- Research analytics and productivity insights

## 🌟 Our Vision

We envision a research ecosystem where discovering knowledge becomes effortless, relevant research reaches the right people at the right time, and researchers can devote more energy to exploration, experimentation, and innovation.

**ZealWithin — Keep the researcher in you alive.**

---

*Built with curiosity, passion, and the belief that research should never stop.*
