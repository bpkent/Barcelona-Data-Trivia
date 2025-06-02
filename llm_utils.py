from litellm import Router
from dotenv import load_dotenv

load_dotenv()

router = Router(
    model_list=[
        {
            "model_name": "claude",
            "litellm_params": {"model": "anthropic/claude-sonnet-4-20250514"},
        },
        {"model_name": "gpt4", "litellm_params": {"model": "openai/gpt-4.1"}},
    ],
    fallbacks=[{"claude": ["gpt4"]}],
    set_verbose=True,
    debug_level="INFO",
)


def plan_schema_queries(question: str, table_info: str):
    """Ask an LLM which fields it needs more information about to construct a correct
    SQL query."""

    response = router.completion(
        model="claude",
        messages=[
            {
                "role": "developer",
                "content": (
                    "You are an AI assistant ultimately tasked with generating a SQL "
                    "query to answer questions about a PostgreSQL table, given table "
                    "metadata, an example row of data, and descriptions of the fields. "
                    "Your immediate task is to identify which fields, if any, you "
                    "need more information about, to construct a correct, executable "
                    "SQL query. "
                    "Do not return any commentary in your response; only a JSON array of strings."
                ),
            },
            {"role": "user", "content": f"Question: {question}"},
            {"role": "user", "content": table_info},
        ],
    )

    return response.choices[0]["message"]["content"]


def generate_sql_query(question: str, table_info: str, hints: str) -> str:
    """Translate a natural langauge question to a SQL query."""

    response = router.completion(
        model="claude",
        messages=[
            {
                "role": "developer",
                "content": (
                    "You are an AI assistant tasked with generating SQL queries "
                    "to answer questions about a DuckDB table, given metadata "
                    "about the table, an example row of data, descriptions of the fields, "
                    "and optional hints from the user about the table schema. "
                    "Return only clean SQL code; do not use any reasoning or markdown formatting. "
                    "Remember to put quotes around table and field names."
                ),
            },
            {"role": "user", "content": f"Question: {question}"},
            {"role": "user", "content": table_info},
            {"role": "user", "content": f"Schema hints: {hints}"},
        ],
    )

    return response.choices[0]["message"]["content"]


def strip_formatting(llm_sql: str) -> str:
    """Use an LLM to strip everything except clean SQL code from another LLM's
    response."""

    response = router.completion(
        model="gpt4",
        messages=[
            {
                "role": "developer",
                "content": (
                    "You are an AI assistant tasked with extracting completely "
                    "clean SQL code from input text. "
                    "Your response should be pure, executable SQL code, free of any "
                    "commentary or markdown formatting.\n\n"
                    "Input: ```sql\nSELECT * FROM vehicles LIMIT 10```"
                    "Output: SELECT * FROM vehicles LIMIT 10"
                ),
            },
            {"role": "user", "content": f"Input:\n{llm_sql}"},
        ],
    )

    return response.choices[0]["message"]["content"]


def write_factoid(question: str, results: list):
    """Write a factoid based on an input question and SQL query results."""

    response = router.completion(
        model="claude",
        messages=[
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
                    "The factoid must be fewer than 275 characters in length. "
                    "Do not include any additional commentary. "
                    "Structure the sentence to build suspense.\n\n"
                    """Example: 🌳 L'arbre més comú de Barcelona és el plàtan (Platanus × acerifolia). Hi ha 40.553 arbres d'aquest tipus als carrers de la ciutat.\n"""
                    """Example: 📍 Els noms més comuns a Barcelona són Maria per a les dones i Antonio per als homes."""
                ),
            },
            {"role": "user", "content": f"Question: {question}"},
            {"role": "user", "content": f"Query results:\n{results}"},
        ],
    )

    return response.choices[0]["message"]["content"]
