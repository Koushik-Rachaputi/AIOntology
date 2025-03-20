from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import database, openai

app = FastAPI(title="FastAPI + Neo4j + OpenAI")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"],  # Allow frontend origin
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

# Include routers
app.include_router(database.router)
app.include_router(openai.router)

@app.get("/")
def home():
    return {"message": "Welcome to FastAPI with Neo4j & OpenAI"}