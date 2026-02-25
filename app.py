import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers.auth_router import auth_router

def create_app() -> FastAPI:
    app = FastAPI(title="Backend Alchemy", version="0")

    app.include_router(auth_router)

    @app.get("/health")
    def health():
        return {"status": "ok"}
    
    return app

app = create_app()
    