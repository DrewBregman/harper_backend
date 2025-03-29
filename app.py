# app.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from routers import companies, forms, voice
import os

def create_app() -> FastAPI:
    app = FastAPI(
        openapi_url="/api/openapi.json",
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        title="Harper API",
        description="API for Harper Insurance Forms",
        version="1.0.0"
    )
    
    app.include_router(companies.router, prefix="/companies", tags=["Companies"])
    app.include_router(forms.router, prefix="/forms", tags=["Forms"])
    app.include_router(voice.router, prefix="/voice", tags=["Voice"])
    # Allow localhost:3000 or any domain
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Allow all origins in development
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["*"]
    )

    # Create static directory if it doesn't exist
    static_dir = os.path.join(os.path.dirname(__file__), "static")
    os.makedirs(static_dir, exist_ok=True)
    
    # Mount static files directory
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

    return app

app = create_app()
