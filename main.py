from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import companies, forms

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Include routers
app.include_router(companies.router)
app.include_router(forms.router) 