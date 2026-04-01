from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from db.database import init_db
from services.ml_models import init_models
from routers import auth, satellite, stress_index, simulation, violations, catch_logs, blockchain

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize DB tables on startup
    await init_db()
    # Initialize ML models on startup
    init_models()
    yield

app = FastAPI(
    title="Ocean Governance Digital Twin API",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS — allow Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register all routers
app.include_router(auth.router)
app.include_router(satellite.router)
app.include_router(stress_index.router)
app.include_router(simulation.router)
app.include_router(violations.router)
app.include_router(catch_logs.router)
app.include_router(blockchain.router)

@app.get("/")
async def root():
    return {"message": "Ocean Governance Digital Twin API", "status": "running"}

@app.get("/health")
async def health():
    return {"status": "healthy"}
