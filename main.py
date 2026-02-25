from fastapi import FastAPI, File, UploadFile, Form, HTTPException
import os
import uuid
from crewai import Crew, Process
from agents import verifier, financial_analyst, risk_assessor, investment_advisor
from task import verification, extraction, risk_analysis, investment_analysis

app = FastAPI(title="Financial Document Analyzer")


def run_crew(query: str, file_path: str):

    financial_crew = Crew(
        agents=[verifier, financial_analyst, risk_assessor, investment_advisor],
        tasks=[verification, extraction, risk_analysis, investment_analysis],
        process=Process.sequential,
        planning=False
    )

    result = financial_crew.kickoff({
        "query": query,
        "path": file_path
    })

    return result


@app.post("/analyze")
async def analyze_financial_document(
    file: UploadFile = File(...),
    query: str = Form(default="Analyze this financial document")
):

    file_id = str(uuid.uuid4())
    file_path = f"data/{file_id}.pdf"

    try:
        os.makedirs("data", exist_ok=True)

        with open(file_path, "wb") as f:
            f.write(await file.read())

        response = run_crew(query=query, file_path=file_path)

        return {
            "status": "success",
            "analysis": str(response),
            "file_processed": file.filename
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        if os.path.exists(file_path):
            os.remove(file_path)