from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from exako.core.i18n import set_locale


class LanguageMiddleware(BaseHTTPMiddleware):
    """
    Middleware for setting the language based on the
    request headers.

    This middleware sets the language of the application
    based on the Accept-Language header in the incoming
    request. It uses the set_locale function from the i18n
    module to determine the appropriate language for the request.
    """

    async def dispatch(self, request: Request, call_next):
        """
        Dispatch method to set the language for the request.

        This method intercepts incoming requests, sets the
        language based on the Accept-Language header, and then
        passes the request to the next middleware or route handler.
        """
        await set_locale(request)
        response = await call_next(request)
        return response
