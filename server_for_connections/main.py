import os
from typing import Literal, Any

from clients import connections_client, shikimori_client

from fastapi import FastAPI, Request, Response, Depends
from fastapi.responses import RedirectResponse
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.database import Database
from starlette.background import BackgroundTask

from session import cookie, verifier, session_backend
from models import Session, User, DiscordTokenInDB, ShikimoriTokenInDB

REDIRECT_URL = 'https://discord.com/app'


app = FastAPI()
app.state.connections_client = connections_client
app.state.shikimori_client = shikimori_client
app.state.database = AsyncIOMotorClient(os.environ['DB_URI']).get_default_database()


@app.get('/')
async def index():
    return "Hi 😊"


@app.get('/authorise-application')
async def authorise_application(request: Request):
    url, state = request.app.state.connections_client.oauth_url
    response = RedirectResponse(url)
    response.set_cookie(key='clientState', value=state, max_age=60 * 5)
    return response


@app.get('/discord-oauth-callback', dependencies=[Depends(cookie)])
async def discord_oauth_callback(
        request: Request,
        state: str,
        code: str,
        session: Session = Depends(verifier)
):
    connections_client = request.app.state.connections_client

    if state != request.cookies.get('clientState'):
        return Response("State verification failed.", status_code=403)

    token = await connections_client.get_oauth_token(code)
    user_data = await connections_client.get_user_data(token)
    user_id = int(user_data['user']['id'])

    database: Database = request.app.state.database
    await database.discord.tokens.update_one(
        {'id': user_id},
        {'$set': {'id': user_id, 'token': DiscordTokenInDB.from_token(token)}},
        upsert=True,
    )

    response = RedirectResponse(request.url_for('success'))

    await _handle_user_data({'discord_user_id': user_id}, session, request, response)

    return response


@app.get('/authorise-shikimori')
async def authorise_shikimori(request: Request):
    return RedirectResponse(request.app.state.shikimori_client.auth_url)


@app.get('/shikimori-oauth-callback', dependencies=[Depends(cookie)])
async def shikimori_oauth_callback(
        request: Request,
        code: str,
        session: Session = Depends(verifier)
):
    client = request.app.state.shikimori_client
    token = await client.get_access_token(code)
    user_info = await client.get_current_user_info(token)
    user_id = user_info['id']

    database: Database = request.app.state.database
    await database.shikimori.tokens.update_one(
        {'user_id': user_id},
        {'$set': {'id': user_id, 'token': ShikimoriTokenInDB.from_token(token)}},
        upsert=True
    )

    response = RedirectResponse(request.url_for('success'))

    await _handle_user_data({'shikimori_user_id': user_id}, session, request, response)

    return response


async def _handle_user_data(
        user_data: dict[Literal['shikimori_user_id', 'discord_user_id'], Any],
        session: Session,
        request: Request,
        response: Response
) -> None:
    database = request.app.state.database

    if session:
        db_user = await database.users.find_one({'_id': session.user_id})
    else:
        db_user = await database.users.find_one(user_data)

    if not db_user:
        user = User(**user_data)  # TODO auto id generation
        await database.users.insert_one(user.model_dump(by_alias=True, exclude_none=True))
        user = User(**await database.users.find_one(user_data))
    else:
        user = User(**db_user, **user_data)
        await database.users.update_one(
            {'_id': user.id},
            {'$set': user_data}
        )

    if not session:
        session = Session(user_id=user.id)
        await session_backend.create(session.identifier, session)
        cookie.attach_to_response(response, session.identifier)

    response.background = BackgroundTask(_update_metadata, user=user)


async def _update_metadata(*, user: User) -> None:
    if not (user.discord_user_id and user.shikimori_user_id):
        # we must have both user_id's
        return

    database = app.state.database

    discord_token = database.discord.tokens.find_one({'id': user.discord_user_id})  # TODO change to user_id
    shikimori_token = database.shikimori.tokens.find_one({'id': user.shikimori_user_id})

    shikimori_client = app.state.shikimori_client

    additional_data = await shikimori_client.get_current_user_info(shikimori_token)
    user_id = additional_data['id']
    # additional_data = await shikimori_client.go().users.id(user_id).get()

    # amount of completed anime
    anime_completed = 0
    rate_groups = additional_data['stats']['statuses']['anime']
    for rate_group in rate_groups:
        if rate_group['name'] == 'completed':
            anime_completed = rate_group['size']
            break

    metadata = {  # TODO ...
        # 'shikimori_user_id': user_info['id'],
        # 'shikimori_nickname': user_info['nickname'],
        # 'shikimori_token_id': shiki_token_data.pk,
        # 'anime_watched': anime_completed
    }

    await app.state.connections_client.push_metadata(discord_token, metadata)


@app.exception_handler(500)
async def handle_500(request: Request, __):
    # TODO logging
    return RedirectResponse(request.url_for('internal_server_error'))


@app.get('/internal_server_error')
async def internal_server_error(request: Request):
    return "Internal server error occurred :("


@app.get('/success')
async def success(request: Request):
    return "Success :)"
