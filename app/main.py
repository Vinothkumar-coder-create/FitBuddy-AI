from fastapi import FastAPI

from fastapi.staticfiles import StaticFiles

from app.database import init_db

from app.routes import router


app = FastAPI(

    title="FitBuddy - AI Fitness Plan Generator",

    version="1.0.0",

    description=(
        "AI-powered personalized "
        "fitness plan generator."
    ),
)


app.mount(

    "/static",

    StaticFiles(
        directory="static"
    ),

    name="static",
)


app.include_router(router)


@app.on_event("startup")
def startup():

    init_db()