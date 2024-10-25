from fastapi import FastAPI
from fastapi_pagination import add_pagination

from exako.apps.term.routers.term import term_router
from exako.core.middleware import LanguageMiddleware

app = FastAPI()

app.add_middleware(LanguageMiddleware)

add_pagination(app)

app.include_router(term_router, prefix='/term', tags=['term'])
