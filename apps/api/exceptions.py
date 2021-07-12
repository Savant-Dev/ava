from quart import Response
from quart import make_response


class BaseException(Exception):
    ''' Standard Exception with built-in handling '''

    status: int = 400
    default: str = (
        'We encountered an issue while processing your request. '
        'Please try again later or contact support if the problem persists.'
    )

    def __init__(self, reason: str = default):
        self.reason = reason

    async def handle(self) -> quart.Response:
        return await make_response(self.status, self.reason)


class MissingAuthentication(BaseException):
    ''' Client Failed to Provide Required Credentials '''

    status: int = 403
    default: str = 'Request is missing one or more required credentials'


class InvalidAuthentication(BaseException):
    ''' Client Provided Expired/Incorrect Credentials '''

    status: int = 401
    default: str = 'Request utilizes Invalid or Expired Credentials'


class MissingRequestData(BaseException):
    ''' POST Request Missing required data or Invalid content-type '''

    status: int = 400
    default: str = 'Missing or Invalid POST Request Data'
