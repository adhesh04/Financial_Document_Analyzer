# tools.py

import re
import json
from typing import Type, Dict, List, ClassVar
from pydantic import BaseModel, Field
from crewai.tools import BaseTool
from langchain_community.document_loaders import PyPDFLoader


class FinancialDocumentInput(BaseModel):
    path: str = Field(..., description="Path to the financial PDF document")


class FinancialDocumentTool(BaseTool):
    name: str = "financial_document_reader"
    description: str = (
        "Extract structured financial metrics from the provided financial PDF document."
    )
    args_schema: Type[BaseModel] = FinancialDocumentInput

    TARGET_METRICS: ClassVar[Dict[str, List[str]]] = {
        "revenue": ["total revenue", "total revenues", "revenue"],
        "net_income": ["net income attributable", "net income", "net earnings"],
        "operating_income": ["income from operations", "operating income"],
        "gross_profit": ["gross profit"],
        "free_cash_flow": ["free cash flow"],
        "cash_position": [
            "cash and cash equivalents",
            "cash, cash equivalents and investments",
        ],
        "ebitda": ["adjusted ebitda", "ebitda"],
    }

    def _clean_line(self, line: str) -> str:
        line = re.sub(r"\(\d+\)", "", line)
        line = re.sub(r"\s+", " ", line)
        return line.strip()

    def _extract_numbers(self, line: str):
        matches = re.findall(
            r"(-?\d[\d,]*\.?\d*)\s*(B|M|billion|million)?",
            line,
            re.IGNORECASE,
        )

        values = []

        for number, unit in matches:
            try:
                value = float(number.replace(",", ""))

                if "%" in line:
                    continue

                if value < 10 and unit is None:
                    continue

                if unit:
                    unit = unit.lower()
                    if unit in ["b", "billion"]:
                        value *= 1000
                    elif unit in ["m", "million"]:
                        value *= 1

                values.append(value)

            except:
                continue

        return values

    def _run(self, path: str) -> str:
        loader = PyPDFLoader(path)
        docs = loader.load()

        extracted_metrics = {}

        for page in docs:
            lines = page.page_content.split("\n")

            for line in lines:
                clean_line = self._clean_line(line)
                lower_line = clean_line.lower()

                for metric_name, keywords in self.TARGET_METRICS.items():

                    if metric_name in extracted_metrics:
                        continue

                    if any(keyword in lower_line for keyword in keywords):
                        numbers = self._extract_numbers(clean_line)

                        if numbers:
                            extracted_metrics[metric_name] = round(numbers[-1], 2)

        if not extracted_metrics:
            return json.dumps({"error": "NO_RELEVANT_FINANCIAL_DATA_FOUND"})

        revenue = extracted_metrics.get("revenue")

        if revenue and revenue != 0:
            if "operating_income" in extracted_metrics:
                extracted_metrics["operating_margin_percent"] = round(
                    (extracted_metrics["operating_income"] / revenue) * 100, 2
                )

            if "net_income" in extracted_metrics:
                extracted_metrics["net_margin_percent"] = round(
                    (extracted_metrics["net_income"] / revenue) * 100, 2
                )

            if "ebitda" in extracted_metrics:
                extracted_metrics["ebitda_margin_percent"] = round(
                    (extracted_metrics["ebitda"] / revenue) * 100, 2
                )

        return json.dumps(extracted_metrics)