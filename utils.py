"""
Utils.
"""

import os

import duckdb
import requests
import sqlglot
from atproto import Client, client_utils, models
from dotenv import load_dotenv
from pathlib import Path
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

    full_text = client_utils.TextBuilder().text(text).tag("#Barcelona\n", "Barcelona")

    external_embed = models.AppBskyEmbedExternal.Main(
        external=models.AppBskyEmbedExternal.External(
            uri=link_url,
            title=link_title,
            description="",
        )
    )

    response = client.send_post(text=full_text, embed=external_embed, langs=[language])
    return response


def validate_sql(sql: str) -> str | None:
    """Validate that a SQL query string parses as proper SQL."""

    try:
        parsed_sql = sqlglot.parse_one(sql, dialect="duckdb")
        return parsed_sql.sql()
    except ParseError as e:
        print(f"Invalid SQL: {e}")
    except Exception as e:
        print(f"Error during validation: {e}")

    return None


def get_dataset_metadata(dataset: str) -> dict:
    """Get all metadata for a dataset, including the resources."""

    url = f"{data_api}/package_show"
    params = {"id": dataset}
    response = requests.get(url, params=params)

    if response.json()["success"]:
        return response.json()["result"]

    return {}


def query_field_details(conn, table_name: str, field: str):
    """Get details about a specific field in a DuckDB table."""

    sql = f"""SELECT DISTINCT \"{field}\" FROM \"{table_name}\""""

    result = conn.sql(sql).fetchall()
    result = [x[0] for x in result]
    return result


def create_db_from_csv(csv_path: Path, db_path: Path, table_name: str) -> int:
    """"""

    conn = duckdb.connect(str(db_path))

    conn.execute(
        f"CREATE TABLE '{table_name}' AS SELECT * FROM read_csv_auto('{csv_path}')"
    )

    # Get row count for confirmation
    result = conn.execute(f"SELECT COUNT(*) FROM '{table_name}'").fetchone()
    row_count = result[0] if result else 0

    conn.close()
    return row_count
