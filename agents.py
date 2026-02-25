# agents.py

from crewai import Agent, LLM
from tools import FinancialDocumentTool

llm = LLM(
    model="ollama/mistral",
    base_url="http://localhost:11434",
    temperature=0.2
)

verifier = Agent(
    role="Financial Document Verifier",
    goal="Verify whether the uploaded document at {path} is a valid financial report.",
    backstory="You are a compliance specialist trained to verify financial documents before analysis.",
    verbose=True,
    memory=False,
    llm=llm,
    max_iter=1,
    allow_delegation=False
)

financial_analyst = Agent(
    role="Senior Financial Analyst",
    goal=(
        "Use the financial_document_reader tool to extract structured financial metrics "
        "from the document at {path}. Return the JSON exactly as extracted. "
        "Do NOT compute additional values manually."
    ),
    backstory="You are a CFA-certified financial analyst specializing in structured financial extraction.",
    verbose=True,
    memory=False,
    tools=[FinancialDocumentTool()],
    llm=llm,
    max_iter=1,
    allow_delegation=False
)

risk_assessor = Agent(
    role="Financial Risk Analyst",
    goal="Based strictly on the extracted financial metrics, identify key financial risks.",
    backstory="You specialize in identifying operational and financial risks from structured financial data.",
    verbose=True,
    memory=False,
    llm=llm,
    max_iter=1,
    allow_delegation=False
)

investment_advisor = Agent(
    role="Investment Strategist",
    goal=(
        "Provide a general investment outlook strictly based on the "
        "financial analysis and identified risks. Do NOT fabricate data."
    ),
    backstory="You provide objective investment perspectives grounded strictly in financial analysis.",
    verbose=True,
    memory=False,
    llm=llm,
    max_iter=1,
    allow_delegation=False
)