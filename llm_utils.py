from litellm import Router, completion_cost
from litellm.integrations.custom_logger import CustomLogger
from datetime import datetime, timezone
from dotenv import load_dotenv
import pandas as pd

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


class UsageTracker(CustomLogger):
    def __init__(self):
        self.data = []
        super().__init__()

    def to_df(self) -> pd.DataFrame:
        if self.data:
            out = pd.DataFrame(self.data)
        else:
            out = pd.DataFrame()

        return out

    def summarize(self) -> pd.DataFrame:
        df = self.to_df()
        grp = df.groupby("model")
        out = grp[["tokens_in", "tokens_out", "cost_estimate"]].sum()
        return out

    def log_success_event(self, kwargs, response_obj, start_time, end_time):
        usage = response_obj.usage
        cost = completion_cost(completion_response=response_obj)

        self.data.append(
            {
                "timestamp": datetime.now(timezone.utc),
                "model": response_obj.model,
                "tokens_in": usage.prompt_tokens,
                "tokens_out": usage.completion_tokens,
                "cost_estimate": cost,
                "duration": (end_time - start_time).total_seconds(),
            }
        )


def write_haiku(table_name: str) -> str:
    """Dev/testing function to ask an LLM to write a haiku."""

    response = router.completion(
        model="claude",
        messages=[
            {
                "role": "user",
                "content": f"Write a haiku about a database table named {table_name}.",
            }
        ],
    )

    return response.choices[0]["message"]["content"]


def generate_question(table_info: str) -> str:
    """Ask an LLM to generate an interesting question that can be answered with the
    given table."""

    response = router.completion(
        model="claude",
        messages=[
            {
                "role": "developer",
                "content": (
                    "You are an AI assistant tasked with coming up with an interesting "
                    "question that can be answered with a SQL table. The user will "
                    "provide information about the SQL table, including the name of "
                    "the table, the description, an example row of data, and field "
                    "descriptions. Your question must be answerable given only the "
                    "table described, so keep it on the simple side. "
                    "Try to be as precise as possible about the temporal and geographic context as possible. "
                    "Your response should include *only* the question, as a single sentence. "
                    "Do not include any additional reasoning in your output.\n\n"
                    "Example: Which neighborhood has the highest ratio of working vehicles (trucks and vans) to personal vehicles (cars and motorcycles)?\n"
                    "Example: What was the 5-year rolling average June temperature in 2024 vs. 1785?\n"
                    "Example: What is the most common stree tree in Barcelona?"
                ),
            },
            {"role": "user", "content": table_info},
        ],
    )

    return response.choices[0]["message"]["content"]


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
                    "query to answer questions about a DuckDB table, given table "
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


def write_factoid(question: str, results: list, table_info: str):
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
                    "question, query results, and metadata about the source data, "
                    "write a tweetable factoid, in Catalan. "
                    "Each factoid should be a single factual sentence without "
                    "excessive stylistic frills. Use at most one "
                    "thematically-appropriate emoji at the start of the sentence. "
                    "The factoid must be fewer than 275 characters in length. "
                    "Do not include any additional commentary. "
                    "Make sure the factoid is properly contextualized, for example, to "
                    "the specific period of time or area described in the question "
                    "or in the table metadata. "
                    "Structure the sentence to build suspense.\n\n"
                    """Example: 🌳 L'arbre més comú de Barcelona és el plàtan (Platanus × acerifolia). Hi ha 40.553 arbres d'aquest tipus als carrers de la ciutat.\n"""
                    """Example: 📍 Els noms més comuns a Barcelona són Maria per a les dones i Antonio per als homes."""
                ),
            },
            {"role": "user", "content": f"Question: {question}"},
            {"role": "user", "content": f"Query results:\n{results}"},
            {"role": "user", "content": f"Table info:\n{table_info}"},
        ],
    )

    return response.choices[0]["message"]["content"]
