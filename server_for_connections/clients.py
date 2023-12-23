import os

from discord_connections import Client as ConnectionsClient
from shikimori_extended_api import Client as ShikimoriClient


connections_client = ConnectionsClient(
    discord_token=os.environ['DISCORD_TOKEN'],
    client_id=os.environ['DISCORD_CLIENT_ID'],
    client_secret=os.environ['DISCORD_CLIENT_SECRET'],
    redirect_uri=os.environ['DISCORD_REDIRECT_URI']
)


shikimori_client = ShikimoriClient(
    application_name=os.environ['SHIKI_APPLICATION_NAME'],
    client_id=os.environ['SHIKI_CLIENT_ID'],
    client_secret=os.environ['SHIKI_CLIENT_SECRET'],
    redirect_uri=os.environ['SHIKI_REDIRECT_URL']
)
