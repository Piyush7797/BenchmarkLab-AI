import os
import re
import sqlite3
import time
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI


BASE_DIR = Path(__file__).resolve().parents[2]
DB_PATH = BASE_DIR / "benchmarklab.db"

load_dotenv(BASE_DIR / ".env")

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")


class OpenAIModel:

    def __init__(self):

        if not GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY not found in .env")

        self.client = OpenAI(
            api_key=GROQ_API_KEY,
            base_url="https://api.groq.com/openai/v1"
        )

        self.model_name = GROQ_MODEL

    def get_schema(self, dataset):

        table_mapping = {
            "customer_shopping": "customer_shopping",
            "online_retail": "online_retail"
        }

        table_name = table_mapping.get(dataset)

        if not table_name:
            raise ValueError(f"Unknown dataset: {dataset}")

        conn = sqlite3.connect(DB_PATH)

        try:
            cursor = conn.cursor()
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()

            schema = "\n".join(
                f"- {column[1]} ({column[2]})"
                for column in columns
            )

            return f"Table: {table_name}\nColumns:\n{schema}"

        finally:
            conn.close()

    def generate_sql(self, question, dataset):

        schema = self.get_schema(dataset)

        prompt = f"""
You are an expert Text-to-SQL engineer.

Generate a SQLite SQL query to answer the user's question.

DATABASE SCHEMA:
{schema}

QUESTION:
{question}

RULES:
1. Generate SQLite-compatible SQL.
2. Use only the provided table and columns.
3. Return only a single SQL query.
4. Do not include explanations.
5. Do not use Markdown code fences.
6. Only generate SELECT queries.
"""

        start_time = time.perf_counter()

        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {
                    "role": "system",
                    "content": "You generate accurate SQLite queries."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0
        )

        latency_ms = (time.perf_counter() - start_time) * 1000

        sql = response.choices[0].message.content.strip()

        sql = re.sub(
            r"^```(?:sql)?\s*|\s*```$",
            "",
            sql,
            flags=re.IGNORECASE
        ).strip()

        usage = response.usage

        prompt_tokens = usage.prompt_tokens if usage else 0
        completion_tokens = usage.completion_tokens if usage else 0
        total_tokens = usage.total_tokens if usage else 0

        return {
            "sql": sql,
            "latency_ms": round(latency_ms, 2),
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": total_tokens
        }