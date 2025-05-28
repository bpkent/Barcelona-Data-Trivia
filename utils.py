"""
Utils.
"""

import os

import requests
import sqlglot
from atproto import Client, client_utils, models
from dotenv import load_dotenv
from sqlglot.errors import ParseError

load_dotenv()

data_api = "https://opendata-ajuntament.barcelona.cat/data/api/action"


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


def validate_sql(sql: str) -> str:
    """Validate that a SQL query string parses as proper (DuckDB) SQL."""

    try:
        parsed_sql = sqlglot.parse_one(sql, dialect="duckdb")
    except ParseError as e:
        print(f"Invalid SQL: {e}")
    except Exception as e:
        print(f"Error during validation: {e}")

    return parsed_sql.sql()


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
    return response


def get_table_schema(resource_id):
    """Get schema by requesting 0 records."""

    url = f"{data_api}/datastore_search"
    params = {
        "resource_id": resource_id,
        "limit": 0,  # Get structure without data
    }

    response = requests.get(url, params=params)
    return response.json()
