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
dataset = "cens-locals-planta-baixa-act-economica"

meta = get_dataset_metadata(dataset)

table_title = dataset_title(meta)
table_url = f"https://opendata-ajuntament.barcelona.cat/data/ca/dataset/{dataset}"


## 1B. Identify the right resource
# %%
resources = [x for x in meta["resources"] if x["datastore_active"]]
table_id = resources[0]["id"]


## 2. Come up with an interesting question.
# %%
question = "Which three neighborhoods of Barcelona have the most pharmacies?"


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
hints = """Pharmacies are identified by 'Codi_Activitat_2022' = 2002000."""


# %%
response = generate_sql_query(question, table_info, hints)

llm_sql = response.output_text
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
factoid_response = write_factoid(question, result)
print(factoid_response.output_text)


## 6. Post the result to BlueSky.
# %%
tweet_text = f"Saps que...?\n\n{factoid_response.output_text}\n\n"

bsky_response = publish_bsky_post(
    tweet_text, link_url=table_url, link_title=table_title
)
print(bsky_response)

# %%
