"""
Main script.
"""

from utils import publish_bsky_post

factoid = (
    "L'arbre més comú de Barcelona és el plàtan (Platanus × acerifolia). Hi ha 40.553 "
    "arbres d'aquest tipus als carrers de la ciutat."
)
table_url = "https://opendata-ajuntament.barcelona.cat/data/en/dataset/arbrat-viari"

table_title = "Arbrat viari de la ciutat de Barcelona"

tweet = f"Saps que...?\n\n{factoid}\n\n"

response = publish_bsky_post(tweet, link_url=table_url, link_title=table_title)
