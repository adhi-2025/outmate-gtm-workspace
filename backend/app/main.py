from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .core.config import settings
from .core.database import init_db
from .api.routes import health,research,entities,enrichments,export

app=FastAPI(title="Outmate GTM Intelligence Research & Enrichment Workspace",version="1.0.0")
app.add_middleware(CORSMiddleware,allow_origins=[x.strip() for x in settings.cors_origins.split(",")],
                   allow_credentials=True,allow_methods=["*"],allow_headers=["*"])

@app.on_event("startup")
def startup(): init_db()

app.include_router(health.router)
app.include_router(research.router)
app.include_router(entities.router)
app.include_router(enrichments.router)
app.include_router(export.router)
