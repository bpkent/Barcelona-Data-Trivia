"""Command line tools for the Barcelona Data Trivia bot."""

from pathlib import Path

import duckdb
import typer
import yaml
from rich import print
from typing_extensions import Annotated

app = typer.Typer()


@app.callback()
def callback():
    pass


@app.command()
def createdb(
    db_slug: Annotated[str, typer.Argument(help="Path for the new DuckDB database")],
):
    """Create a DuckDB database from a CSV file. Run from the project root dir."""

    with open("datasets.yaml", "r") as f:
        datasets = yaml.safe_load(f)

    source_filename = f"{datasets[db_slug]['filename']}"
    csv_path = Path("raw_data") / source_filename
    db_path = Path("working_data") / f"{db_slug}.db"
    table_name = Path(source_filename).stem

    if db_path.exists():
        print(f"Database {db_path} already exists!")
        raise typer.Exit()

    try:
        conn = duckdb.connect(str(db_path))
        conn.execute(
            f"CREATE TABLE '{table_name}' AS SELECT * FROM read_csv_auto('{csv_path}')"
        )

        # Get row count for confirmation
        result = conn.execute(f"SELECT COUNT(*) FROM '{table_name}'").fetchone()
        row_count = result[0] if result else 0

        conn.close()

        print(
            f"✅ Created database {db_path} with table '{table_name}' ({row_count} rows)"
        )

    except Exception as e:
        typer.echo(f"Error creating database: {e}", err=True)
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
