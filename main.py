"""
Main script.
"""

# %%
import json
import litellm
from pathlib import Path
import random

# from pprint import pprint as pp
# import llmlite; llmlite._turn_on_debug()
import duckdb
import yaml

from llm_utils import (
    UsageTracker,
    # write_haiku,
    generate_question,
    generate_sql_query,
    plan_schema_queries,
    strip_formatting,
    write_factoid,
)
from utils import (
    publish_bsky_post,
    query_field_details,
    validate_sql,
)


# %% Initialize trackers
usage = UsageTracker()
litellm.callbacks = [usage]

# %% 0. Read in dataset config.
with open("datasets.yaml", "r") as f:
    datasets = yaml.safe_load(f)


# %% 1. Choose a dataset.
# ------------
# dataset = random.choice(list(datasets.keys()))
dataset = "accidents-gu-bcn"
print(f"Dataset: {dataset}")

table_name = Path(datasets[dataset]["filename"]).stem
resource_id = datasets[dataset]["resource_id"]


# %% Test the usage tracker callbacks.
# haiku = write_haiku(table_name)


# %%
## Connect to the local DuckDB table.
db = duckdb.connect(f"working_data/{dataset}.db", read_only=True)


# %% 2. Get metadata about the chosen table.
# ------------------
with open(f"working_data/{dataset}.json", "r") as f:
    meta = json.load(f)

dataset_title = meta["title_translated"]["ca"]
description = meta["notes_translated"]["ca"]
notes = meta["dataset_fields_description"]
data_source = meta["fuente"]
field_descriptions = meta["extras"]


# %% Get and example row of data and the official schema.
sql = f"""SELECT * FROM "{table_name}" LIMIT 1"""

result = db.sql(sql)
field_names = [x[0] for x in result.description]
example = dict(zip(field_names, result.fetchone()))


# %%
table_info = [
    f"Table name: {table_name}",
    f"Dataset name: {dataset_title}",
    f"Dataset source: {data_source}",
    f"Dataset description: {description}",
    f"First row of data:\n{example}",
    f"Field descriptions:\n{field_descriptions}",
]

table_info_str = "\n\n".join(table_info)
print(table_info_str)


## 3. Come up with an interesting question.
## -------
## %%
# question = generate_question(table_info_str)
# print(question)
question = "What hour of the week had the most vehicular accidents in 2024?"


# %% 4. Which fields do we need more information about?
# ------------------
req_fields = json.loads(plan_schema_queries(question, table_info_str))
print(req_fields)


# %%
for field in req_fields:
    distinct_values = query_field_details(db, table_name, field)
    table_info.append(f"Distinct values for field '{field}': {distinct_values}")


# %% 5. Generate a SQL query to run agains the dataset.
# --------------
hints = """"""

# %%
table_info_str = "\n\n".join(table_info)
print(table_info_str)


# %%
llm_sql = generate_sql_query(question, table_info_str, hints)
print(llm_sql)


# %% 6. Validate and clean the SQL query
# --------------
sql = validate_sql(llm_sql)
print(sql)

# %%
cleaning_attempts = 0
cleaned_sql = llm_sql

while not sql and cleaning_attempts <= 3:
    print("Stripping formatting....")
    cleaned_sql = strip_formatting(cleaned_sql)
    cleaning_attempts += 1
    print(f"\nCleaned SQL\n-----\n{cleaned_sql}")
    sql = validate_sql(cleaned_sql)
    print(f"\nValidated SQL\n-----\n{sql}")


# %%
## 7. Execute the SQL against the database.
# ---------------
result = db.sql(sql)
result


# %% 8. Write the factoid based on the results.
# ----------------
data = result.df().to_dict(orient="records")

factoid = write_factoid(question, result, table_info_str)
print(factoid)

if len(factoid) > 273:
    raise ValueError("Factoid is too long!")


# %% 9. Post the factoid to BlueSky.
# --------------
tweet_text = f"Sabies que...?\n\n{factoid}\n\n"
table_url = f"https://opendata-ajuntament.barcelona.cat/data/ca/dataset/{dataset}"

bsky_response = publish_bsky_post(
    tweet_text, link_url=table_url, link_title=dataset_title
)
print(bsky_response)


# %% 10. Analyze LLM usage and cost
# ---------------
usage.to_df()

# %%
usage.summarize()

# %%
print(f"Total estimated cost: {usage.to_df()['cost_estimate'].sum()}")
