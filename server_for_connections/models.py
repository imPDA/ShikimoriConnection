import os
from datetime import datetime, timedelta
from functools import partial
from typing import Optional
from uuid import UUID, uuid4

import pendulum
from bson import ObjectId
from discord_connections import DiscordToken
from pydantic import BaseModel, ConfigDict, Field, field_serializer, field_validator

TZ = os.environ.get('TZ')


class User(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    id: Optional[ObjectId] = Field(alias='_id', default=None)
    discord_user_id: Optional[int] = None
    shikimori_user_id: Optional[str] = None


class Session(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    id: Optional[ObjectId] = Field(alias='_id', default=None)
    identifier: UUID = Field(default_factory=uuid4)
    createdAt: datetime = Field(default_factory=partial(pendulum.now, tz=TZ))

    user_id: ObjectId
    # discord_user_id: Optional[int] = None
    # shikimori_user_id: Optional[Any] = None
    # action: Optional[Any] = None


class DiscordTokenInDB(DiscordToken):
    @field_serializer('expires_in')
    def serialize_timedelta(self, td: timedelta):
        return td.total_seconds()

    @field_validator('expires_in', mode='before')  # noqa
    @classmethod
    def deserialize_expires_in(cls, v) -> timedelta:
        if isinstance(v, timedelta):
            return v
        elif isinstance(v, (int, float)):
            return timedelta(seconds=v)
        elif isinstance(v, str):
            return timedelta(seconds=float(v))

        raise ValueError('`expires_in` must be a `timedelta` or int/str representation in seconds')

    @classmethod
    def from_token(cls, token: DiscordToken) -> dict:
        # https://stackoverflow.com/questions/64446491/pydantic-upgrading-object-to-another-model
        return cls.model_validate(token, from_attributes=True).model_dump()


class ShikimoriTokenInDB:
    @classmethod
    def from_token(cls, token) -> dict:
        ...
