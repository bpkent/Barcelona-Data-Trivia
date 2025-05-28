import os

import anthropic
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


api_key = os.environ.get("OPENAI_API_KEY")
client = client = OpenAI(api_key=api_key)


def generate_sql_query(question: str, table_info: str, hints: str) -> str:
    """Translate a natural langauge question to a SQL query."""

    response = client.responses.create(
        model="gpt-4.1",
        input=[
            {
                "role": "developer",
                "content": (
                    "You are an AI assistant tasked with generating SQL queries "
                    "to answer questions about a PostgreSQL table, given only metadata "
                    "about the table, an example row of data, descriptions of the fields, "
                    "and potentially hints from the user about the table schema. "
                    "Return only clean SQL code; do not include additional "
                    "commentary or even markdown formatting. "
                    "To identify the table in the query, use the table ID string provided."
                ),
            },
            {"role": "user", "content": f"Question: {question}"},
            {"role": "user", "content": table_info},
            {"role": "user", "content": f"Schema hints: {hints}"},
        ],
    )

    return response


def write_factoid(question: str, results: list):
    """Write a factoid based on an input question and SQL query results."""

    response = client.responses.create(
        model="gpt-4.1",
        input=[
            {
                "role": "developer",
                "content": (
                    "You are an AI assistant tasked with writing interesting daily "
                    "factoids about the city of Barcelona, based on the results of data "
                    "queries from the city's open data portal. Given a motivating "
                    "question and query results, write a tweetable factoid, in "
                    "Catalan. Each factoid should be a single factual sentence without "
                    "excessive stylistic frills. Use at most one "
                    "thematically-appropriate emoji at the start of the sentence. "
                    "Do not include any additional commentary. "
                    "Structure the sentence to build suspense.\n\n"
                    """Example: \"🌳 L'arbre més comú de Barcelona és el plàtan (Platanus × acerifolia). Hi ha 40.553 arbres d'aquest tipus als carrers de la ciutat.\"\n"""
                    """Example: \"📍 Els noms més comuns a Barcelona són Maria per a les dones i Antonio per als homes.\""""
                ),
            },
            {"role": "user", "content": f"Question: {question}"},
            {"role": "user", "content": f"Query results:\n{results}"},
        ],
    )

    return response
