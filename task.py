# task.py

from crewai import Task
from agents import verifier, financial_analyst, risk_assessor, investment_advisor


verification = Task(
    name="verification_task",
    description="""
    Verify whether the document located at {path}
    appears to be a legitimate financial report.
    """,
    expected_output="Validation result stating whether document is financial.",
    agent=verifier,
)

extraction = Task(
    name="extraction_task",
    description="""
    Use the financial_document_reader tool to extract
    structured financial metrics from {path}.
    Return only valid JSON output from the tool.
    """,
    expected_output="JSON of extracted financial metrics.",
    agent=financial_analyst,
)

risk_analysis = Task(
    name="risk_task",
    description="""
    Based strictly on the previously extracted financial metrics,
    identify key financial and operational risks.
    Do NOT invent numbers.
    """,
    expected_output="Structured risk assessment based only on extracted metrics.",
    agent=risk_assessor,
    context=[extraction],
)

investment_analysis = Task(
    name="investment_task",
    description="""
    Based strictly on the extracted financial metrics
    and the identified risks,
    provide a general investment outlook.
    Do NOT fabricate data.
    """,
    expected_output="General investment outlook grounded in metrics and risks.",
    agent=investment_advisor,
    context=[extraction, risk_analysis],
)