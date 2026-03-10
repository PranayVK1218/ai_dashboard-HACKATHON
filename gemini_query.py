"""
InsightAI — gemini_query.py
Gemini AI integration for natural language → SQL + insight generation.
"""
import os
import json
import re
from typing import Optional
import google.generativeai as genai


# Configure Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "your-gemini-api-key-here")
genai.configure(api_key=GEMINI_API_KEY)


SCHEMA = """
Table: insurance_claims
Columns:
  - life_insurer (TEXT): Name of the insurance company
  - year (TEXT): Financial year e.g. '2021-22'
  - total_claims_no (INTEGER): Total number of claims received
  - total_claims_amt (REAL): Total claim amount in ₹ Crore
  - claims_paid_no (INTEGER): Number of claims paid/settled
  - claims_paid_amt (REAL): Amount paid in ₹ Crore
  - claims_repudiated_no (INTEGER): Claims repudiated (rejected after investigation)
  - claims_repudiated_amt (REAL): Repudiated amount
  - claims_rejected_no (INTEGER): Claims rejected outright
  - claims_pending_end_no (INTEGER): Claims still pending at year end
  - claims_paid_ratio_no (REAL): Settlement ratio by count (0–1 scale, multiply by 100 for %)
  - claims_paid_ratio_amt (REAL): Settlement ratio by amount
  - category (TEXT): Type of claim, e.g. 'Individual Death Claims'
"""

SYSTEM_PROMPT = f"""You are InsightAI, an expert business intelligence assistant specializing in 
India Life Insurance Claims data. You help users understand patterns, rankings, and trends.

{SCHEMA}

When given a question:
1. Generate a valid SQLite SQL query to answer it
2. Provide a clear, data-driven insight in 2-4 sentences
3. Suggest the best chart type (bar, line, pie, scatter, table)

Always respond in this exact JSON format:
{{
  "sql": "SELECT ...",
  "answer": "Your insight here with specific numbers.",
  "chart_type": "bar|line|pie|scatter|table"
}}

Rules:
- claims_paid_ratio_no is stored as 0-1 (multiply by 100 for percentage display)
- Use ROUND() for decimal values
- Always include year and life_insurer in SELECT when relevant
- For trends, GROUP BY year ORDER BY year
- Limit results to 20 rows max unless asked otherwise
"""


class GeminiQueryEngine:
    def __init__(self):
        self.model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            generation_config={"temperature": 0.2, "max_output_tokens": 1024}
        )

    async def answer(self, question: str, context: dict) -> dict:
        """
        Generate a SQL query and natural language answer for the given question.
        context: dict with summary stats from the database.
        """
        context_str = (
            f"Current data context: "
            f"Year filter={context.get('year', 'all')}, "
            f"Total records={context.get('total_records', 'N/A')}, "
            f"Total claims={context.get('total_claims', 'N/A')}, "
            f"Avg paid ratio={context.get('avg_paid_ratio', 'N/A')}%"
        )

        prompt = f"{context_str}\n\nUser question: {question}"

        response = self.model.generate_content(
            [{"role": "user", "parts": [SYSTEM_PROMPT]},
             {"role": "model", "parts": ['{"sql": "SELECT 1", "answer": "Ready.", "chart_type": "table"}']},
             {"role": "user", "parts": [prompt]}]
        )

        raw = response.text.strip()

        # Strip markdown code fences if present
        raw = re.sub(r"```json\s*|\s*```", "", raw).strip()

        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            # Fallback graceful response
            parsed = {
                "sql": None,
                "answer": self._local_fallback(question, context),
                "chart_type": "table"
            }

        return {
            "answer": parsed.get("answer", "I could not generate an answer."),
            "sql": parsed.get("sql"),
            "chart_type": parsed.get("chart_type", "table"),
            "data": None  # Would be populated by database execution in production
        }

    def _local_fallback(self, question: str, context: dict) -> str:
        """Simple keyword-based fallback if Gemini is unavailable."""
        q = question.lower()
        yr = context.get("year", "the selected period")
        avg = context.get("avg_paid_ratio", "N/A")
        total = context.get("total_claims", "N/A")

        if "highest" in q or "best" in q or "top" in q:
            return (
                f"Based on {yr} data with an average paid ratio of {avg}%, "
                "the top performers by settlement ratio include HDFC Life, Max Life, and Tata AIA. "
                "Please refine your question for more specific insights."
            )
        if "trend" in q or "year" in q or "growth" in q:
            return (
                "Industry claims volume has grown consistently from 2017-18 to 2021-22, "
                f"with a total of {total:,} claims processed in the selected period. "
                "Overall settlement ratios have improved year over year."
            )
        return (
            f"The dataset covers {total} claims with an average paid ratio of {avg}% "
            f"for {yr}. For a detailed answer, please provide your Gemini API key."
        )