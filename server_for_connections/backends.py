from typing import Generic, get_args

from fastapi_sessions.backends.session_backend import (
    BackendError,
    SessionBackend,
    SessionModel,
)
from fastapi_sessions.frontends.session_frontend import ID
from motor.motor_asyncio import AsyncIOMotorClient


class MongoDBBackend(Generic[ID, SessionModel], SessionBackend[ID, SessionModel]):
    def __init__(self, mongodb_url: str) -> None:
        self.db = AsyncIOMotorClient(mongodb_url, uuidRepresentation='standard').get_default_database()

    async def create(self, identifier: ID, data: SessionModel) -> None:
        try:
            await self.db.sessions.insert_one(data.model_dump(by_alias=True, exclude_none=True))
        except Exception as e:
            print(e)
            raise BackendError("`create` can't overwrite an existing session")

    async def read(self, identifier: ID) -> SessionModel:
        document = await self.db.sessions.find_one({'identifier': identifier})
        # https://stackoverflow.com/questions/57706180/generict-base-class-how-to-get-type-of-t-from-within-instance
        return document and get_args(self.__orig_class__)[1](**document)

    async def update(self, identifier: ID, data: SessionModel) -> None:
        result = await self.db.sessions.update_one(  # TODO replace?
            {'identifier': identifier},
            {'$set': data.model_dump()}
        )

        if not result.matched_count:
            raise BackendError("Session does not exist, cannot update")

    async def delete(self, identifier: ID) -> None:
        await self.db.sessions.delete_one({'identifier': identifier})
