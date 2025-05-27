"""
Utils.
"""

import os
from dotenv import load_dotenv
from atproto import Client

load_dotenv()


def publish_bsky_post(text: str, language="ca"):
    """Push a new post to the BlueSky account specified in the env vars.

    NOTE: assumes the post is in Catalan!
    """

    bsky_handle = os.environ.get("BLUESKY_HANDLE")
    bsky_passwd = os.environ.get("BLUESKY_APP_PASSWORD")

    client = Client()
    client.login(login=bsky_handle, password=bsky_passwd)

    response = client.send_post(text=text, langs=[language])
    return response
