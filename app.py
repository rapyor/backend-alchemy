import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers.auth_router import auth_router
from routers.folder_router import folder_router

def create_app() -> FastAPI:
    app = FastAPI(title="Backend Alchemy", version="0")

    # Each router is a group of related endpoints.
    # include_router() registers them with the app so FastAPI knows about them.
    app.include_router(auth_router)
    app.include_router(folder_router)

    @app.get("/health")
    def health():
        return {"status": "ok"}
    
    return app

app = create_app()
    