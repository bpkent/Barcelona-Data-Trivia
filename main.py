"""
Main script.
"""

# %%
import json
from pathlib import Path
import random

# from pprint import pprint as pp
# import llmlite; llmlite._turn_on_debug()
import duckdb
import yaml

from llm_utils import (
    generate_sql_query,
    plan_schema_queries,
    strip_formatting,
    write_factoid,
)
from utils import (
    get_dataset_metadata,
    publish_bsky_post,
    query_field_details,
    validate_sql,
)

# %% 0. Read in dataset config.
with open("datasets.yaml", "r") as f:
    datasets = yaml.safe_load(f)


# %% 1. Choose a dataset.
# dataset = random.choice(list(datasets.keys()))
dataset = "est-vehicles-amb-distintiu"
print(f"Dataset: {dataset}")

table_name = Path(datasets[dataset]["filename"]).stem
resource_id = datasets[dataset]["resource_id"]


# %%
## Connect to the local DuckDB table.
db = duckdb.connect(f"working_data/{dataset}.db", read_only=True)


# %%
## 2. Get metadata about the chosen table.

meta = get_dataset_metadata(dataset)

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


### HAVE TO GO MANUAL HERE TO PICK THE QUESTION (FOR NOW) ###
### ----------------------------------------------------- ###

## 2. Come up with an interesting question.
# %%
question = "Which neighborhood has the highest ratio of working vehicles (trucks and vans) to personal vehicles (cars and motorcycles)?"


# %% 4. Which fields do we need more information about?
req_fields = json.loads(plan_schema_queries(question, table_info_str))
print(req_fields)


# %%
for field in req_fields:
    distinct_values = query_field_details(db, table_name, field)
    table_info.append(f"Distinct values for field '{field}': {distinct_values}")


# %%
hints = """"""

# %%
table_info_str = "\n\n".join(table_info)
print(table_info_str)


# %%
llm_sql = generate_sql_query(question, table_info_str, hints)
print(llm_sql)


# %% Validate the SQL
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
## 4. Execute the SQL against the API.
result = db.sql(sql)
result

# %% 5. Write the factoid based on the results.
data = result.df().to_dict(orient="records")

factoid = write_factoid(question, result)
print(factoid)

if len(factoid) > 273:
    raise ValueError("Factoid is too long!")


## 6. Post the result to BlueSky.
# %%
tweet_text = f"Sabies que...?\n\n{factoid}\n\n"
table_url = f"https://opendata-ajuntament.barcelona.cat/data/ca/dataset/{dataset}"

bsky_response = publish_bsky_post(
    tweet_text, link_url=table_url, link_title=dataset_title
)
print(bsky_response)

# %%
