"""
Utils.
"""

import os

import anthropic
import requests
from atproto import Client, client_utils, models
from dotenv import load_dotenv

load_dotenv()

data_api = "https://opendata-ajuntament.barcelona.cat/data/api/action"

llm_api_key = os.environ.get("ANTHROPIC_API_KEY")
llm_client = anthropic.Anthropic(api_key=llm_api_key)


def publish_bsky_post(text: str, link_url: str, link_title: str = "", language="ca"):
    """Push a new post to the BlueSky account specified in the env vars.

    NOTE: assumes the post is in Catalan!
    """

    bsky_handle = os.environ.get("BLUESKY_HANDLE")
    bsky_passwd = os.environ.get("BLUESKY_APP_PASSWORD")

    client = Client()
    client.login(login=bsky_handle, password=bsky_passwd)

    full_text = client_utils.TextBuilder().text(text).link(link_url, link_url)

    external_embed = models.AppBskyEmbedExternal.Main(
        external=models.AppBskyEmbedExternal.External(
            uri=link_url,
            title=link_title,
            description="",
        )
    )

    response = client.send_post(text=full_text, embed=external_embed, langs=[language])
    return response


def get_dataset_metadata(dataset: str) -> list:
    """Get all metadata for a dataset, including the resources."""

    url = f"{data_api}/package_show"
    params = {"id": dataset}
    response = requests.get(url, params=params)

    if response.json()["success"]:
        return response.json()["result"]

    return []


def dataset_title(dataset_meta: dict) -> str:
    """From dataset metadata, extract the website title."""
    return dataset_meta["title_translated"]["ca"]


def query_csv_resource(sql_query: str):
    """Query a CSV resource with SQL"""

    url = f"{data_api}/datastore_search_sql"
    params = {"sql": sql_query}
    response = requests.get(url, params=params)
    return response.json()


def write_factoid(question: str, results: list):
    """Write a factoid based on an input question and SQL query results."""

    response = llm_client.messages.create(
        model="claude-3-7-sonnet-20250219",
        max_tokens=1000,
        temperature=0,
        system=[
            {
                "type": "text",
                "text": (
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
        ],
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"The motivating question is:\n'{question}'",
                    },
                    {"type": "text", "text": f"The query results are:\n{results}"},
                ],
            },
        ],
    )

    return response.content[0].text, response.usage
