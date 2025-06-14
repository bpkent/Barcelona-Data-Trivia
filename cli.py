"""Command line tools for the Barcelona Data Trivia bot."""

from pathlib import Path

import duckdb
import json
import typer
import yaml
from rich import print
from typing_extensions import Annotated

from utils import get_dataset_metadata, create_db_from_csv

app = typer.Typer()


@app.callback()
def callback():
    pass


@app.command()
def createdb(
    db_slug: Annotated[str, typer.Argument(help="Path for the new DuckDB database")],
):
    """Create a DuckDB database from a CSV file and download the metadata.

    NOTE: run from the project root dir.
    """

    with open("datasets.yaml", "r") as f:
        datasets = yaml.safe_load(f)

    source_filename = f"{datasets[db_slug]['filename']}"
    csv_path = Path("raw_data") / source_filename
    db_path = Path("working_data") / f"{db_slug}.db"
    meta_path = Path("working_data") / f"{db_slug}.json"
    table_name = Path(source_filename).stem

    # Create the DB if it doesn't already exist.
    if db_path.exists():
        print(f"Database {db_path} already exists!")
        raise typer.Exit()

    try:
        row_count = create_db_from_csv(csv_path, db_path, table_name)
        print(
            f"✅ Created database '{db_path}' with table '{table_name}' ({row_count} rows)"
        )
    except Exception as e:
        typer.echo(f"Error creating database: {e}", err=True)
        typer.Exit()

    # Try to fetch metadata.
    meta = None

    try:
        meta = get_dataset_metadata(db_slug)
    except Exception as err:
        typer.echo(f"Failure fetching metadata from Open Data BCN: {err}", err=True)

    # Overwrite existing metadata, but only if the newly fetched meta is really there.
    if meta:
        with open(meta_path, "w") as f:
            json.dump(meta, f, indent=2)
        print(f"✅ Saved metadata at '{meta_path}'.")
    else:
        print("Failed to retrieve database metadata.")


if __name__ == "__main__":
    app()
