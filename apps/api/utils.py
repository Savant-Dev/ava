import asyncpg
import functools

import typing as t

from os import environ
from quart import request
from dotenv import load_dotenv

from security import AuthData
from security import UserData
from security import Authentication

from exceptions import MissingAuthentication
from exceptions import InvalidAuthentication


load_dotenv()


class DataEngine():
    ''' Database Utilities '''

    host: str = environ.get('PSQL_HOST')
    port: int = int(environ.get('PQSL_PORT'))

    @staticmethod
    async def connect(name: str, *, auth: AuthData) -> asyncpg.Connection:
        database = await asyncpg.connect(
            host = DataEngine.host,
            port = DataEngine.port,

            user = auth.id,
            password = auth.token,
            database = name
        )

        return database


class Decorators():
    ''' Custom Route/Function Decorators '''

    @staticmethod
    def modifier(f: t.Callable):
        @functools.wraps(f)
        async def wrapper(*args, **kwargs):
            data = await request.get_json()
            if not data:
                raise MissingRequestData()

            return await f(*args, **kwargs)

        return wrapper

    @staticmethod
    def protected(f: t.Callable):
        @functools.wraps(f)
        async def wrapper(*args, **kwargs):
            key = request.args.get('key', None)
            if not key:
                raise MissingAuthentication()

            try:
                client_auth = request.headers['Authentication']
                id = client_auth['client-id']
                secret = client_auth['client-secret']
            except KeyError:
                raise MissingAuthentication()

            auth_data = await Authentication().verify(
                id = id,
                key = key,
                secret = secret
            )

            if not auth_data.status:
                raise InvalidAuthentication()

            return await f(*args, **kwargs)

        return wrapper

    @staticmethod
    def connected(name: str):
        def decorator(f: t.Callable):
            @functools.wraps(f)
            async def wrapper(*args, **kwargs):
                key = request.args.get('key', None)
                if not key:
                    raise MissingAuthentication()

                try:
                    client_auth = request.headers['Authentication']
                    id = client_auth['client-id']
                    secret = client_auth['client-secret']
                except KeyError:
                    raise MissingAuthentication()

                auth_data = await Authentication().verify(
                    id = id,
                    key = key,
                    secret = secret
                )

                if not auth_data.status:
                    raise InvalidAuthentication()

                database = await DataEngine.connect(name, auth=auth_data)

                return await f(database, *args, **kwargs)
            return wrapper
        return decorator
