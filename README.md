<div align="center">
  <img src="./images/logo2.png" alt="Logo" width="30%"/>
</div>

Barcelona Data Trivia
=========

Welcome! We post a daily factoid on BlueSky about the city of Barcelona, derived from data from the Barcelona Open Data portal.

https://bsky.app/profile/bcndatatrivia.bsky.social

The goal is for this project is to be fully automated, relying heavily on LLM services integrated smartly.


Current strategy
-------
Ahead of time...

1. Download datasets manually into the `raw_data` folder from the Open Data BCN portal.

2. Add an entry to `datasets.yaml`.
    - Top level is the dataset slug.
    - Title is the title on the Open Data BCN portal.
    - Filename is whatever the CSV is called when its donwloaded.
    - resource_id can be found in the table's URL on the Open Data BCN website.

3. Run the CLI tool to do A. create a new DuckDB persistent DB and B. download and save the dataset metadata, both in the `working_data` folder. From project root, run:
    - `uv run cli.py createdb [DATASET SLUG]`

To generate a factoid and post it on BlueSky, run `main.py` in the VS Code interactive window. Step through the cells one-by-one.

1. Choose a dataset randomly from `datasets.yaml`.

2. Get the dataset metadata from the OpenData BCN portal (this is currently the only call to the data portal).

3. Come up with an interesting question about the data.
    - Currently manual. Should be automated soon.

4. Ask the LLM which fields it needs more info about to answer the question (i.e. for filtering on certain values).

5. Query the DB for more info on those fields.

6. Generate the final SQL query with an LLM.

7. Clean and validate the final SQL query with `sqlglot` and an LLM.

8. Execute the final SQL query.

9. Use an LLM to write a factoid based on the results.

10. Post the factoid as a BlueSky tweet.


V1 To Do's
----------
When these items are done, it's time to show it off to the world.

* Logging
    - Presumably via LiteLLM plus loguru (or similar)

* Prompt caching: cache the overall system instructions and the table info.

* Online validation and evaluations
    - `generate_sql_query` (done)
    - `write_factoid`

* Offline evaluation
    - `generate_question`: human, rubric scoring for AI as a judge
    - `plan_schema_queries`: human
    - `generate_sql_query`: functional correctness
    - `strip_formatting`: functional correctness
    - `write_factoid`: rubric

* The "get more info about a field" step could be smarter.
    - Currently just a simple SELECT DISTINCT.
    - Should be type, top 20 most common values, statistical summary, etc
    

Future To Do's
--------------
* Tune contextualization
    - Generated SQL should compute details that will add interesting detail to the question answer (e.g. "Which neighborhood consumes the most electricity?" should return both the neighbhorhood and the amount of electricity.)
    - Instruct the factoid writer explicitly to contextualize based on table metadata in addition to the question -- the question writer shouldn't have to be so precise about times and places.

* Run on a remote machine.

* Run with a cron scheduler.

* Keep expanding the set of downloaded datasets.

* Weight the dataset choice to prefer datasets that haven't been chosen in a while.
    - Include a field in the YAML with last chosen timestamp and write to it (when a tweet is actually posted at the end).
    - `random.choices` can take weights, or `numpy.choice`.

* Log the runs
    - Dataset
    - Question
    - SQL
    - Results
    - Factoid
    - Bsky URIs

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
