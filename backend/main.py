from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.core.config import PROJECT_NAME, PROJECT_DESCRIPTION, VERSION
from backend.routers import (
    dashboard,
    companies,
    contacts,
    leads,
    scoring,
    campaigns,
    activities,
    consent,
    sales_reps,
    routing,
    tasks,
    opportunities,
    exceptions,
    validation,
    ml,
)

app = FastAPI(
    title=f"{PROJECT_NAME} API",
    description=f"{PROJECT_DESCRIPTION} - Complete REST API for lead scoring, routing, consent enforcement, pipeline management, and ML evaluation.",
    version=VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Enable CORS for Streamlit frontend and local integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all API routers
app.include_router(dashboard.router)
app.include_router(companies.router)
app.include_router(contacts.router)
app.include_router(leads.router)
app.include_router(scoring.router)
app.include_router(campaigns.router)
app.include_router(activities.router)
app.include_router(consent.router)
app.include_router(sales_reps.router)
app.include_router(routing.router)
app.include_router(tasks.router)
app.include_router(opportunities.router)
app.include_router(exceptions.router)
app.include_router(validation.router)
app.include_router(ml.router)


@app.get("/", tags=["Health"])
def root():
    return {
        "status": "online",
        "app": PROJECT_NAME,
        "version": VERSION,
        "documentation": "/docs",
    }


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "healthy", "service": PROJECT_NAME}
