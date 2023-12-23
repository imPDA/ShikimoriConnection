import os

from discord_connections import Client as ConnectionsClient


connections_client = ConnectionsClient(
    discord_token=os.environ['DISCORD_TOKEN'],
    client_id=os.environ['DISCORD_CLIENT_ID'],
    client_secret=os.environ['DISCORD_CLIENT_SECRET'],
    redirect_uri=os.environ['DISCORD_REDIRECT_URI']
)


class ShikimoriClient:
    pass


shikimori_client = ShikimoriClient()

# shiki_client = ShikiClient(  TODO
#     application_name=os.environ['SHIKI_APPLICATION_NAME'],
#     client_id=os.environ['SHIKI_CLIENT_ID'],
#     client_secret=os.environ['SHIKI_CLIENT_SECRET'],
#     redirect_uri='https://impda.duckdns.org:500/shikimori-oauth-callback'
# )
