from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from database import create_db_and_tables
from models import *  # Import all models
from config import get_settings

settings = get_settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    create_db_and_tables()
    yield
    # Shutdown
    pass

app = FastAPI(
    title="School Copy API",
    description="Backend API for School Copy Manufacturing Business Management",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",  # Keep docs at root for easier access
    openapi_url="/openapi.json",  # Keep OpenAPI spec at root
    redirect_slashes=False  # Disable to prevent 307 redirects
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite dev server
        "http://localhost:5174",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
        *settings.allowed_origins
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

@app.get("/")
async def root():
    return {"message": "School Copy API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Import and register routers
from routers import auth, schools, products, orders, payments, expenses, dashboard, leaders

app.include_router(auth.router, prefix="/api/v1")
app.include_router(schools.router, prefix="/api/v1")
app.include_router(leaders.router, prefix="/api/v1")
app.include_router(products.router, prefix="/api/v1")
app.include_router(orders.router, prefix="/api/v1")
app.include_router(payments.router, prefix="/api/v1")
app.include_router(expenses.router, prefix="/api/v1")
app.include_router(dashboard.router, prefix="/api/v1")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
