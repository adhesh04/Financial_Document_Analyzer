from celery_app import celery_app
from db import save_analysis
from crew_runner import run_crew  # move run_crew to separate file
import os 

@celery_app.task
def process_analysis(file_path: str, filename: str, query: str):
    result = run_crew(query=query, file_path=file_path)

    save_analysis(
        filename=filename,
        query=query,
        analysis=str(result)
    )
    
    if os.path.exists(file_path):
        os.remove(file_path)

    return str(result)