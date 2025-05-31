"""
Main script.
"""

# %%
import json
from pprint import pprint as pp
# import llmlite; llmlite._turn_on_debug()

from utils import (
    get_dataset_metadata,
    dataset_title,
    query_csv_resource,
    validate_sql,
    publish_bsky_post,
    query_field_details,
)
from llm_utils import (
    generate_sql_query,
    write_factoid,
    strip_formatting,
    plan_schema_queries,
)


# %%

## 1. Choose a dataset.
dataset = "est-vehicles-amb-distintiu"
table_id = "0c93eb37-b145-4810-b8d9-17c72683eee4"


## 2. Come up with an interesting question.
# %%
question = "Which neighborhood of Barcelona had the highest ratio of vans and trucks to personal vehicles in 2023?"


# %%
## 3. Translate to SQL

meta = get_dataset_metadata(dataset)

table_title = dataset_title(meta)
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

table_info_str = "\n\n".join(table_info)
print(table_info_str)


# %% 4. Which fields do we need more information about?
req_fields = json.loads(plan_schema_queries(question, table_info_str))
print(req_fields)

for field in req_fields:
    distinct_values = query_field_details(table_id, field)
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

cleaning_attempts = 0
cleaned_sql = llm_sql

while not sql and cleaning_attempts <= 3:
    print("Stripping formatting....")
    cleaned_sql = strip_formatting(cleaned_sql)
    cleaning_attempts = 1
    print(f"\nCleaned SQL\n-----\n{cleaned_sql}")
    sql = validate_sql(cleaned_sql)
    print(f"\nValidated SQL\n-----\n{sql}")


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
tweet_text = f"Saps que...?\n\n{factoid}\n\n"
table_url = f"https://opendata-ajuntament.barcelona.cat/data/ca/dataset/{dataset}"

bsky_response = publish_bsky_post(
    tweet_text, link_url=table_url, link_title=table_title
)
print(bsky_response)

# %%
