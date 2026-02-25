from crewai import Crew, Process
from agents import verifier, financial_analyst, risk_assessor, investment_advisor
from task import verification, extraction, risk_analysis, investment_analysis


def run_crew(query: str, file_path: str):
    financial_crew = Crew(
        agents=[verifier, financial_analyst, risk_assessor, investment_advisor],
        tasks=[verification, extraction, risk_analysis, investment_analysis],
        process=Process.sequential,
        planning=False
    )

    return financial_crew.kickoff({
        "query": query,
        "path": file_path
    })