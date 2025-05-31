Barcelona Data Trivia
=========

Welcome! We post a daily factoid on BlueSky about the city of Barcelona, derived from data from the Barcelona Open Data portal.

https://bsky.app/profile/bcndatatrivia.bsky.social

The goal is for this project is to be fully automated, relying heavily on LLM services integrated smartly.


Current strategy
-------
1. Choose an interesting dataset manually.

2. Download the dataset manually into the `raw_data` folder.

3. Create a new DuckDB persistent DB in the `working_data` folder.
    - `$ duckdb [dataset].db`
    - `D CREATE TABLE '[table name]' AS SELECT FROM read_csv_auto('../raw_data/[dataset].csv');`
    - `D .tables`

4. Run `main.py` in the VS Code interactive window. Step through the cells one-by-one.
    - Set the motivating question manually.
    - Get the dataset metadata from the OpenData BCN portal (this is currently the only call to the data portal).
    - Ask the LLM which fields it needs more info about (i.e. for filtering on certain values).
    - Query the DB for more info on those fields.
    - Generate the final SQL query with an LLM.
    - Clean and validate the final SQL query with `sqlglot` and an LLM.
    - Execute the final SQL query.
    - Use an LLM to write a factoid based on the results.
    - Post the factoid as a BlueSky tweet.


V1 To Do's
----------
When these items are done, it's time to show it off to the world.

* Start adding the #Barcelona tag so the tweets get picked up in lists.

* Check out the catalog dataset - can I use this to auto-generate interesting questions?

* Download a bunch of datasets, names, example rows of data, etc.

* LLM to generate the motivating question.

* Run on a remote machine.

* Run with a cron scheduler.

* Evaluations

    
Future To Do's
--------------
* Generalize the LLM call that strips formatting from the SQL output.
    - It should get all of the information from the SQL validator, i.e. bogus table name, etc.
    - It's task should be to fix whatever the bug is.

* Automate dataset management
    * Check for more recent resources or revisions and download, create the DuckDB table if necessary.

* Explore agent frameworks to see if they make it easier
    - This *is* an agentic flow, after all.
    - LangGraph, PydanticAI, etc.
    - Maybe better branded as "build an agent from scratch"?

* Make a CLI for faster human-in-the-loop go/no-go decisions at the key points.
