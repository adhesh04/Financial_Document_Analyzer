from fastapi import FastAPI, File, UploadFile, Form, HTTPException
import os
import uuid
from crewai import Crew, Process
from agents import verifier, financial_analyst, risk_assessor, investment_advisor
from task import verification, extraction, risk_analysis, investment_analysis
import sqlite3
from db import init_db, save_analysis
from worker import process_analysis
from celery.result import AsyncResult
from celery_app import celery_app


app = FastAPI(title="Financial Document Analyzer")
init_db()

@app.get("/status/{job_id}")
def check_status(job_id: str):
    result = AsyncResult(job_id, app=celery_app)

    if result.state == "PENDING":
        return {"status": "pending"}

    elif result.state == "SUCCESS":
        return {
            "status": "completed",
            "result": result.result
        }

    elif result.state == "FAILURE":
        return {
            "status": "failed",
            "error": str(result.info)
        }

    return {"status": result.state}

@app.get("/history")
def get_history():
    conn = sqlite3.connect("financial_analysis.db")
    cursor = conn.cursor()

    cursor.execute("SELECT id, filename, query, created_at FROM analyses ORDER BY id DESC")
    rows = cursor.fetchall()

    conn.close()

    return {"history": rows}

# def run_crew(query: str, file_path: str):

#     financial_crew = Crew(
#         agents=[verifier, financial_analyst, risk_assessor, investment_advisor],
#         tasks=[verification, extraction, risk_analysis, investment_analysis],
#         process=Process.sequential,
#         planning=False
#     )

#     result = financial_crew.kickoff({
#         "query": query,
#         "path": file_path
#     })

#     return result

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

        # response = run_crew(query=query, file_path=file_path)

        # save_analysis(
        #     filename=file.filename,
        #     query=query,
        #     analysis=str(response)
        # )

        task = process_analysis.delay(file_path, file.filename, query)
        
        return {
            # "status": "success",
            # "analysis": str(response),
            # "file_processed": file.filename,
            "status": "processing",
            "job_id": task.id
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    # finally:
    #     if os.path.exists(file_path):
    #         os.remove(file_path)