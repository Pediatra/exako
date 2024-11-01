from fastapi import FastAPI
from fastapi_pagination import add_pagination

from exako.apps.exercise.router import exercise_router
from exako.apps.term.routers.term import term_router

app = FastAPI()

add_pagination(app)

app.include_router(term_router, prefix='/term')
app.include_router(exercise_router, prefix='/exercise', tags=['exercise'])
