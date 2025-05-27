"""
Main script.
"""

# %%
from utils import (
    get_dataset_metadata,
    dataset_title,
    query_csv_resource,
    publish_bsky_post,
)

## 1. Choose a dataset.
# %%
dataset = "pad_m_nom_sexe"

meta = get_dataset_metadata(dataset)

table_title = dataset_title(meta)
table_url = f"https://opendata-ajuntament.barcelona.cat/data/ca/dataset/{dataset}"


## 1B. Identify the right resource
# %%
resources = [x for x in meta["resources"] if x["datastore_active"]]
table_id = resources[0]["id"]


## 2. Come up with an interesting question.
# %%
question = "What are the top 3 most common men's names in Barcelona?"


## 3. Translate to SQL
# %%
sql = f'SELECT "NOM" FROM "{table_id}" WHERE "SEXE" = 2 ORDER BY "Valor_Freq" DESC LIMIT 3'


## 4. Execute the SQL against the API.
# %%
raw_result = query_csv_resource(sql)

result = raw_result["result"]["records"]


## 5. Write the factoid based on the results.
# %%
factoid = "📍 Els noms masculins més comuns a Barcelona son Antonio, Jordi i José."


## 6. Post the result to BlueSky.
# %%
tweet_text = f"Saps que...?\n\n{factoid}\n\n"

response = publish_bsky_post(tweet_text, link_url=table_url, link_title=table_title)

print(response)

# %%
