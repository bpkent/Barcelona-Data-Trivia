"""
Utils.
"""

# %%
import os
from dotenv import load_dotenv
from atproto import Client, client_utils, models


load_dotenv()


def publish_bsky_post(text: str, link_url: str, link_title: str = "", language="ca"):
    """Push a new post to the BlueSky account specified in the env vars.

    NOTE: assumes the post is in Catalan!
    """

    bsky_handle = os.environ.get("BLUESKY_HANDLE")
    bsky_passwd = os.environ.get("BLUESKY_APP_PASSWORD")

    client = Client()
    client.login(login=bsky_handle, password=bsky_passwd)

    full_text = client_utils.TextBuilder().text(text).link(link_url, link_url)

    external_embed = models.AppBskyEmbedExternal.Main(
        external=models.AppBskyEmbedExternal.External(
            uri=link_url,
            title=link_title,
            description="",
        )
    )

    response = client.send_post(text=full_text, embed=external_embed, langs=[language])
    return response
