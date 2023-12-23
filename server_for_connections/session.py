import os

from fastapi import HTTPException
from uuid import UUID, uuid4

from fastapi_sessions.session_verifier import SessionVerifier
from fastapi_sessions.frontends.implementations import SessionCookie, CookieParameters

from backends import MongoDBBackend
from models import Session


SECRET = os.environ.get('SESSION_SECRET', 'SECRET')
if SECRET == 'SECRET':
    print('You really need to change it in production!')  # TODO logging


class BasicVerifier(SessionVerifier[UUID, Session]):
    def __init__(
        self,
        *,
        identifier: str,
        backend: MongoDBBackend[UUID, Session],
        auto_error: bool = True,
        auth_http_exception: HTTPException,
    ):
        self._identifier = identifier
        self._auto_error = auto_error
        self._backend = backend
        self._auth_http_exception = auth_http_exception

    @property
    def identifier(self):
        return self._identifier

    @property
    def backend(self):
        return self._backend

    @property
    def auto_error(self):
        return self._auto_error

    @property
    def auth_http_exception(self):
        return self._auth_http_exception

    def verify_session(self, model: Session) -> bool:
        # If the session exists, it is valid
        return True


cookie = SessionCookie(
    cookie_name="sessionIdentifier",
    identifier='general_verifier',
    auto_error=False,
    secret_key=SECRET,
    cookie_params=CookieParameters(),
)

session_backend = MongoDBBackend[UUID, Session](os.environ['DB_URI'])

verifier = BasicVerifier(
    identifier='general_verifier',
    backend=session_backend,
    auto_error=False,
    auth_http_exception=HTTPException(status_code=403, detail="invalid session"),
)
