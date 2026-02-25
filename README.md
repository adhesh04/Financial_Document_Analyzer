# Financial_Document_Analyzer
Financial Document Analyzer – Debug Fix (CrewAI Assignment)
🚀 Project Overview

This project is a FastAPI-based Financial Document Analyzer built using CrewAI agents.
The system processes uploaded financial PDF documents and generates structured financial insights using an LLM.

The original repository contained multiple deterministic bugs and architectural issues.
This version reflects all debugging and fixes completed so far.

🛠 What Has Been Fixed
1️⃣ Tool System Fix (Major Issue)
❌ Original Problem

Tools were defined as plain async functions.

CrewAI requires tools to be instances of BaseTool.

This caused:

ValidationError: Input should be a valid dictionary or instance of BaseTool
✅ Fix Implemented

Converted raw async functions into a proper CrewAI BaseTool implementation.

Removed invalid class-based async tool definitions.

Ensured tools return serializable string output.

Final Tool Implementation
from crewai_tools import tool
from langchain_community.document_loaders import PyPDFLoader

@tool("read_financial_document")
def read_data_tool(path: str) -> str:
    loader = PyPDFLoader(path)
    documents = loader.load()

    full_text = ""
    for doc in documents:
        full_text += doc.page_content.strip() + "\n"

    return full_text
2️⃣ LLM Initialization Bug
❌ Original Problem
llm = llm

Undefined variable caused runtime crash.

✅ Fix Implemented

Integrated Ollama (local LLM) for free, offline usage.

from crewai import LLM

llm = LLM(
    model="ollama/llama3",
    base_url="http://localhost:11434"
)

This removes dependency on paid APIs and allows fully local execution.

3️⃣ Incorrect CrewAI Imports
❌ Original
from crewai.agents import Agent
✅ Corrected
from crewai import Agent

Fixed compatibility with current CrewAI version.

4️⃣ Invalid Tool Parameter
❌ Original
tool=[...]
✅ Fixed
tools=[...]

CrewAI expects tools (plural). This caused validation failure.

5️⃣ Removed Broken Search Tool Import
❌ Original
from crewai_tools.tools.serper_dev_tool import SerperDevTool

This import path was invalid in the installed version.

✅ Fix

Removed unused search tool to stabilize the system.

6️⃣ Dependency Conflicts Resolved

Encountered:

onnxruntime version conflict

pydantic version conflict

chroma-hnswlib requiring C++ build tools

outdated pip version

Actions Taken:

Recreated virtual environment

Updated pip

Adjusted dependency versions

Installed missing langchain-community and pypdf

📂 Current Architecture
FastAPI
   ↓
CrewAI Crew
   ↓
Financial Analyst Agent
   ↓
PDF Reading Tool
   ↓
Ollama LLM (Local)
   ↓
Structured Financial Analysis Output
⚙️ How the System Works

User uploads a financial PDF via /analyze

File is saved temporarily

CrewAI agent is initialized

Agent uses tool to read PDF contents

LLM analyzes extracted text

Structured analysis is returned

Uploaded file is deleted

▶️ How to Run the Project
1️⃣ Install Dependencies
pip install -r requirements.txt
pip install langchain-community pypdf
2️⃣ Run Ollama

Make sure Ollama is running locally:

ollama run llama3

Or ensure the Ollama server is active at:

http://localhost:11434
3️⃣ Start FastAPI Server
uvicorn main:app --reload

Server runs at:

http://127.0.0.1:8000
4️⃣ Test API

Use Swagger UI:

http://127.0.0.1:8000/docs

Upload a financial PDF and provide an optional query.


Prompt Engineering & Hallucination Fixes
7️⃣ Removal of Malicious / Hallucination-Heavy Prompts
❌ Original Problems

The original task.py intentionally encouraged:

Fabricating financial data

Generating fake URLs

Contradicting outputs

Providing speculative investment advice

Ignoring user query

Inventing financial risks

This made the system:

Unsafe

Non-deterministic

Legally risky

Not production-ready

✅ Fix Implemented

Rewrote the task prompt to enforce:

Document-only reasoning

No fabrication

No fake URLs

No personalized investment advice

Structured output format

Explicit missing-data acknowledgment

Final Production-Safe Task Prompt
description="""
Read the provided financial document using the available tool.
Use the financial document located at: {path}

Carefully analyze the document content and answer the user's query:
{query}

STRICT RULES:
- Use only information present in the document.
- Do NOT fabricate data.
- Do NOT generate fake URLs.
- If information is missing, clearly state it.
- Do NOT provide personalized investment advice.
- Provide structured, factual analysis only.
"""

This significantly reduces hallucination risk and ensures deterministic financial analysis.

🧱 Tool Architecture Migration (Version Compatibility Fix)
8️⃣ Decorator-Based Tool Failure

The original fix used:

from crewai_tools import tool

However, the installed CrewAI ecosystem version did not support the @tool decorator.

This caused:

ImportError: cannot import name 'tool'

✅ Final Stable Implementation (BaseTool)

Migrated tool implementation to class-based BaseTool, which is version-safe.

from crewai.tools import BaseTool
from langchain_community.document_loaders import PyPDFLoader

class ReadFinancialDocumentTool(BaseTool):
    name: str = "read_financial_document"
    description: str = "Reads and extracts text from a financial PDF document."

    def _run(self, path: str) -> str:
        loader = PyPDFLoader(path)
        docs = loader.load()

        full_text = ""
        for doc in docs:
            content = doc.page_content.strip()
            while "\n\n" in content:
                content = content.replace("\n\n", "\n")
            full_text += content + "\n"

        return full_text
9️⃣ Pydantic v2 Compatibility Fix

CrewAI tools inherit from Pydantic models.

Pydantic v2 requires explicit type annotations for model fields.

❌ Invalid
name = "read_financial_document"
✅ Correct
name: str = "read_financial_document"

This resolved:

PydanticUserError: Field 'name' defined on a base class was overridden by a non-annotated attribute

🔄 Context Injection Bug (main.py)
🔟 Uploaded File Not Being Used

Original issue:

The uploaded PDF path was not passed into the Crew task context.

The system always defaulted to data/sample.pdf.

This made dynamic uploads ineffective.

✅ Fix Implemented

Updated run_crew():

result = financial_crew.kickoff({
    "query": query,
    "path": file_path
})

And injected {path} into the task prompt.

This ensures the agent analyzes the actual uploaded file.

📦 FastAPI Multipart Dependency Fix

While testing file uploads, encountered:

RuntimeError: Form data requires "python-multipart" to be installed.

✅ Fix

Added dependency:

pip install python-multipart

And included it in requirements.txt.

🧹 Removed Unnecessary / Risky Components

The following were intentionally removed to stabilize the system:

SerperDevTool (web search dependency)

Async placeholder investment tools

Fabricated risk tools

OpenAI dependency

Dead code not used by Crew

Why?

Reduced external API dependency

Removed hallucination vector (web search)

Simplified architecture

Improved determinism

Reduced attack surface

🏗 Final System Architecture (Stable Version)
User Upload (PDF)
        ↓
FastAPI Endpoint (/analyze)
        ↓
Temporary File Storage
        ↓
CrewAI Crew (Sequential Process)
        ↓
Financial Analyst Agent
        ↓
ReadFinancialDocumentTool (BaseTool)
        ↓
Ollama (llama3, local)
        ↓
Structured Financial Analysis
        ↓
File Cleanup
🛡 Production Safety Improvements

Removed hallucination-heavy prompts

Enforced document-only reasoning

Disabled delegation

Reduced max iterations

Set low temperature for stability

Removed fake URL generation

Avoided personalized financial advice

Cleaned and validated tool input

Deleted temporary files after processing

🚀 Multi-Agent Architecture Enhancement

After stabilizing the tool system and prompt logic, the system was upgraded into a fully functional sequential multi-agent pipeline instead of a single-agent execution model.

Agents Integrated

1️⃣ Financial Document Verifier
Validates whether the uploaded file is a legitimate financial report.

2️⃣ Senior Financial Analyst
Uses the custom PDF extraction tool to return strictly structured financial metrics in JSON format.

3️⃣ Financial Risk Analyst
Identifies financial and operational risks based strictly on extracted metrics.

4️⃣ Investment Strategist
Generates an investment outlook grounded only in verified financial data.

Improvements Made

Enforced structured JSON output from the analyst agent

Prevented manual calculations outside the tool

Limited agent iteration cycles to avoid infinite reasoning loops

Disabled delegation to maintain deterministic execution

Reduced temperature for consistent financial reasoning

This transformed the system into a true multi-agent reasoning architecture.

⚡ Asynchronous Processing Upgrade (Celery + Redis)

The original architecture executed CrewAI inside the FastAPI request cycle.
This caused:

Long blocking API calls

Poor scalability

Timeout risk on large documents

To resolve this, the system was upgraded to a distributed async model.

🔴 Redis Integration (Dockerized)

Redis is used as:

Message broker

Result backend

When a document is uploaded:

FastAPI queues the task in Redis

Celery worker consumes the task

CrewAI multi-agent pipeline executes

Result is stored back in Redis

Redis Setup:

docker run -d -p 6379:6379 --name redis-server redis
🟢 Celery Worker Integration

Celery handles:

Heavy AI workload execution

Background processing

Task state management (PENDING → SUCCESS / FAILURE)

Worker Start Command (Windows Compatible):

python -m celery -A celery_app.celery_app worker --loglevel=info --pool=solo

--pool=solo ensures stable multiprocessing on Windows.

📡 Updated API Flow
1️⃣ Submit Analysis

POST /analyze

Instead of blocking until completion, the API now returns:

{
  "status": "processing",
  "job_id": "uuid"
}
2️⃣ Poll Task Status

GET /status/{job_id}

Possible responses:

While Processing

{
  "status": "pending"
}

On Completion

{
  "status": "completed",
  "result": "analysis output"
}

This ensures a non-blocking user experience.

🗄 Database Integration (Persistent Storage)

To satisfy bonus requirements and improve enterprise readiness, SQLite persistence was introduced.

Why Add Persistence?

Redis stores results temporarily.
A database enables:

Long-term storage of analysis history

Audit trail of uploaded documents

Query tracking

Historical retrieval

Stored Fields

Analysis ID

Filename

User query

AI result

Timestamp

Endpoint:

GET /history

This allows retrieval of past analyses.

🏗 Final System Architecture

The project evolved from a simple synchronous API into a distributed architecture:

User Upload (PDF)
↓
FastAPI Endpoint
↓
Redis Queue
↓
Celery Worker
↓
CrewAI Multi-Agent Pipeline
↓
Redis Result Backend
↓
SQLite Persistent Storage

⚙ Service Execution Model

The system now runs using three parallel services:

🟢 Redis (Docker Container)
🟢 Celery Worker
🟢 FastAPI Server

This architecture:

Prevents API blocking

Handles concurrent requests

Scales horizontally (multiple workers possible)

Supports long-running LLM tasks safely

📈 Architectural Evolution Summary
Feature	Before	After
API Blocking	Yes	No
Multi-Agent Execution	Partial	Full Sequential Pipeline
Task Queue	No	Redis
Background Processing	No	Celery
Persistent Storage	No	SQLite
Concurrency Support	No	Yes
Production Ready	Limited	Significantly Improved
🎯 Final Outcome

The system has evolved into:

✔ A deterministic multi-agent AI financial analysis system
✔ An asynchronous distributed backend architecture
✔ A Docker-integrated infrastructure
✔ A persistent, auditable analysis platform
✔ A scalable production-ready design

The project now demonstrates:

Debugging expertise

Prompt engineering refinement

Multi-agent orchestration

Distributed systems understanding

Background job processing

Infrastructure integration
