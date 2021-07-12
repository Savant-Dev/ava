import random
import string
import asyncpg
import secrets
import hashlib

from os import environ
from dotenv import load_dotenv
from dataclasses import dataclass

from logger import getLogger, LoggerModule


load_dotenv()


@dataclass
class AuthData():
    '''
        Contains User Authentication Data.

        - Application ID
        - Database Token
    '''

    id: int = None
    token: str = None
    status: bool = False


@dataclass
class UserData():
    '''
        Contains information about the Request Client.

        - Application ID
        - API Key
        - Access Token
    '''

    id: int = None
    key: str = None
    secret: str = None


class Authentication():
    ''' Creates & Verifies User Authentication Data '''

    host: str = environ.get('AUTH_PSQL_HOST')
    port: int = int(environ.get('AUTH_PSQL_PORT'))

    database: str = 'Authentication'

    user: str = environ.get('AUTH_PSQL_USER')
    password: str = environ.get('AUTH_PSQL_PASS')

    def __init__(self, logger: LoggerModule = getLogger()):
        self.log = logger

        self.charbank = list(string.ascii_letters + string.digits)
        for char in ['a', 'b', 'c', 'd']:
            self.charbank.remove(char)

    '''
        Authentication Generators
    '''

    def _keygen(self) -> str:
        self.logger.trace('security', 'Generating API Key ...')

        return secrets.token_urlsafe(24)

    def _secretgen(self) -> str:
        self.logger.trace('security', 'Generating Client Secret ...')

        return f'{secrets.choice(12)}.{secrets.token_urlsafe(12)}'

    def _protocolgen(self) -> str:
        self.logger.trace('security', 'Generating Salt Protocol ...')

        def salt(char: str) -> str:
            part = list(char + ''.join(random.choice(self.charbank) for _ in range(3)))
            random.shuffle(part)

            return ''.join(part)

        def finalize(salt: list) -> str:
            separators = ['.', '-', '=']

            protocol = (
                f'{salt[0]}{random.choice(separators)}'
                f'{salt[1]}{random.choice(separators)}'
                f'{salt[2]}{random.choice(separators)}'
                f'{salt[3]}'
            )

            return protocol

        key = salt('a')
        primary = salt('b')
        id = salt('c')
        secondary = salt('d')

        return finalize(random.shuffle([key, primary, id, secondary]))

    @staticmethod
    def _build(*, key: str, id: int, secret: str, salt: str) -> str:
        primary, secondary = secret.split('.')
        mapping = {'a': key, 'b': primary, 'c': id, 'd': secondary}

        token = ''.join([char for char in salt if char in ['a', 'b', 'c', 'd', '.', '-', '=']])
        for part in mapping:
            token = token.replace(part, mapping[part])

        return token

    @staticmethod
    def _digest(token: str) -> str:
        return hashlib.sha256(token.encode('UTF-32')).hexdigest()

    '''
        Database Integrations
    '''

    @classmethod
    async def _connect(cls) -> asyncpg.Connection:
        db = await asyncpg.connect(
            host = cls.host,
            port = cls.port,
            user = cls.user,
            password = cls.password,
            database = cls.database
        )

        return db

    async def store(self, id: int, salt: str, _token: str) -> None:
        self.log.trace('security', 'Storing New Client Credentials ...')

        token = self._digest(_token)

        db = await self._connect()

        query = '''
            INSERT INTO "ClientData"
            ("Application ID", "Protocol", "Value")
            VALUES ($1, $2, $3)
        '''
        args = (id, salt, token)

        await db.execute(query, *args)
        await db.commit()

    async def retrieve(self, *, id: int) -> asyncpg.Record:
        self.log.trace('security', f'Fetching Credentials for Client (ID: {id}) ...')

        db = await self._connect()

        query = ''' SELECT * FROM "ClientData" WHERE "Application ID" = $1 '''
        data = await db.fetchrow(query, id)

        return data

    '''
        Logic Operations
    '''

    async def create_login(self, *, id: int) -> UserData, AuthData:
        self.log.debug('security', f'Generating Credentials for Application (ID: {id}) ...')

        user = UserData()
        auth = AuthData()

        user.id = auth.id = id
        user.key = self._keygen()
        user.secret = self._secretgen()

        salt = self._protocolgen()
        auth.token = self._build(id=user.id, key=user.key, secret=user.secret, salt=salt)

        await self.store(id, salt, auth.token)

        return user, auth

    async def verify(self, *, id: int, key: str, secret: str) -> AuthData:
        self.log.debug('security', f'Attempting to Authenticate Request (ID: {id}) ...')
        _, protocol, hash = await self.retrieve(id=id).values()

        auth = AuthData()
        auth.id = id
        auth.token = self._build(id=id, key=key, secret=secret, salt=protocol)

        if self._digest(auth.token) == hash:
            auth.status = True
            self.log.trace('security', f'Successfully Authenticated Request (ID: {id})')
        else:
            auth.status = False
            self.log.warning('security', f'Failed to Authenticate Request (ID: {id})')

        return auth
