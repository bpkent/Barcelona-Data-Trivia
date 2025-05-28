"""
Main script.
"""

# %%
from utils import (
    dataset_title,
    get_dataset_metadata,
    publish_bsky_post,
    query_csv_resource,
    write_factoid,
)

## 1. Choose a dataset.
# %%
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
question = "Which neighborhoods of Barcelona have the most pharmacies?"


## 3. Translate to SQL
# %%
sql = (
    f"""SELECT "Nom_Barri", COUNT(*) FROM "{table_id}" WHERE "Nom_Principal_Activitat" = 'Actiu' """
    "GROUP BY 1 "
    "ORDER BY 2 DESC "
    "LIMIT 3"
)


## 4. Execute the SQL against the API.
# %%
raw_result = query_csv_resource(sql)
result = raw_result["result"]["records"]


# %%
## 5. Write the factoid based on the results.
factoid, llm_usage = write_factoid(question, result)
print(factoid)


## 6. Post the result to BlueSky.
# %%
tweet_text = f"Saps que...?\n\n{factoid}\n\n"

response = publish_bsky_post(tweet_text, link_url=table_url, link_title=table_title)

print(response)

# %%
