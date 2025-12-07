from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .db import Base, engine
from .routers import tasks, health, agent, debug_tx, tools, auth, advisor, wallet, approvals, scanner, strategy
from .services.market_scanner import scanner as market_scanner
from .services.deposit_listener import deposit_listener

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Create DB tables
    Base.metadata.create_all(bind=engine)
    
    # Start Background Services
    market_scanner.start()
    deposit_listener.start()
    
    yield
    # Shutdown: cleanup if needed
    market_scanner.stop()
    deposit_listener.stop()

app = FastAPI(
    title="Qubic Autopilot Worker",
    version="1.0.0",
    description="AI-powered autonomous agent for Qubic blockchain with DeFi, RWA, and infrastructure tools",
    lifespan=lifespan
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
# Public routes
app.include_router(health.router)
app.include_router(auth.router)

# Protected routes (require authentication)
app.include_router(wallet.router)
app.include_router(approvals.router)
app.include_router(advisor.router)
app.include_router(tasks.router)
app.include_router(agent.router)
app.include_router(debug_tx.router)
app.include_router(tools.router)
app.include_router(scanner.router)
app.include_router(strategy.router)