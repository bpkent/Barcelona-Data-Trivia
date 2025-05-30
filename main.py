"""
Main script.
"""

# %%
from pprint import pprint as pp

from utils import (
    get_dataset_metadata,
    dataset_title,
    query_csv_resource,
    validate_sql,
    publish_bsky_post,
)
from llm_utils import generate_sql_query, write_factoid


# %%

## 1. Choose a dataset.
dataset = "precipitacio-hist-bcn"

meta = get_dataset_metadata(dataset)

table_title = dataset_title(meta)
table_url = f"https://opendata-ajuntament.barcelona.cat/data/ca/dataset/{dataset}"


## 1B. Identify the right resource
# %%
# resources = [x for x in meta["resources"] if x["datastore_active"]]
table_id = "5da03f48-020e-4f46-9199-a919feac2034"


## 2. Come up with an interesting question.
# %%
question = "In what year did Barcelona have the least accumulated rainfall?"


# %%
## 3. Translate to SQL

# Get table descriptions and notes
description = meta["notes_translated"]["ca"]
notes = meta["dataset_fields_description"]
data_source = meta["fuente"]
field_descriptions = meta["extras"]

# %% Get and example row of data and the official schema.
sql = f"""SELECT * FROM "{table_id}" LIMIT 1"""

response = query_csv_resource(sql)
example = response.json()["result"]["records"][0]

# %%
table_info = [
    f"Table ID: {table_id}",
    f"Table name: {table_title}",
    f"Table source: {data_source}",
    f"Table description: {description}",
    f"First row of data:\n{example}",
    f"Field descriptions:\n{field_descriptions}",
]

table_info = "\n\n".join(table_info)
print(table_info)


# %%
hints = """"""


# %%
llm_sql = generate_sql_query(question, table_info, hints)

print(llm_sql)


# %% Validate the SQL
sql = validate_sql(llm_sql)
print(sql)


# %%
## 4. Execute the SQL against the API.
db_response = query_csv_resource(sql)
result = db_response.json()["result"]["records"]
pp(result)

# %% 5. Write the factoid based on the results.
factoid = write_factoid(question, result)
print(factoid)


## 6. Post the result to BlueSky.
# %%
tweet_text = f"Saps que...?\n\n{factoid.output_text}\n\n"

bsky_response = publish_bsky_post(
    tweet_text, link_url=table_url, link_title=table_title
)
print(bsky_response)

# %%
