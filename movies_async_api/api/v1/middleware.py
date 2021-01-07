import logging
from http import HTTPStatus

from aiohttp import ClientSession
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from core.config import AUTH_CHECK_ENDPOINT

logger = logging.getLogger(__name__)


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        token = request.headers.get("Authorization")
        if not token:
            logger.debug("No token provided, impossible to authorize")
            return self.auth_failed()

        async with ClientSession() as session, session.get(AUTH_CHECK_ENDPOINT, json={"token": token}) as response:
            await response.read()
            if response.status != 200:
                logging.error(f"Auth failed with code {response.status}")
                return self.auth_failed()

        response = await call_next(request)
        return response

    @staticmethod
    def auth_failed() -> Response:
        return Response(content="Access denied", status_code=HTTPStatus.UNAUTHORIZED)

