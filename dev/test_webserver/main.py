from pathlib import Path

import uvicorn

# from app_routes import router as auth_router
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.cors import CORSMiddleware

app = FastAPI(
    title='Sample Static Webserver',
    redoc_url=None,
)

# app.include_router(
#     auth_router,
#     prefix="/auth",
#     tags=["admin"]
# )

app.mount("/apps", StaticFiles(directory=Path(__file__).resolve().parent / "shinyapps", html=True), name="shinylive")

app.add_middleware(
        CORSMiddleware, 
        allow_origins=["http://localhost:8000", "http://localhost:5000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

uvicorn.run(app=app, port=8000)