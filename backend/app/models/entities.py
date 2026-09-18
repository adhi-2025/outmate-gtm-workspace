from datetime import datetime, timezone
from typing import Optional
from sqlmodel import SQLModel, Field, Column, JSON
import uuid

def uid() -> str:
    return str(uuid.uuid4())

class Company(SQLModel, table=True):
    id: str = Field(default_factory=uid, primary_key=True)
    name: str
    domain: str
    location: str
    employee_range: str
    industry: str
    source_metadata: dict = Field(default_factory=dict, sa_column=Column(JSON))

class Person(SQLModel, table=True):
    id: str = Field(default_factory=uid, primary_key=True)
    company_id: str = Field(index=True)
    name: str
    title: str
    relevance_rationale: str
    source_metadata: dict = Field(default_factory=dict, sa_column=Column(JSON))

class Evidence(SQLModel, table=True):
    id: str = Field(default_factory=uid, primary_key=True)
    entity_id: str = Field(index=True)
    claim_field: str
    observed_value: str
    source_url: str
    retrieved_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    evidence_type: str = "observed"
    confidence_score: float = 0.8
    conflict_note: Optional[str] = None

class Signal(SQLModel, table=True):
    id: str = Field(default_factory=uid, primary_key=True)
    entity_id: str = Field(index=True)
    signal_type: str
    strength: float
    freshness_days: int
    source_reliability: float

class Score(SQLModel, table=True):
    id: str = Field(default_factory=uid, primary_key=True)
    entity_id: str = Field(index=True)
    score_type: str = "ICP_FIT"
    score_value: float
    breakdown: dict = Field(default_factory=dict, sa_column=Column(JSON))
    calculated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ResearchJob(SQLModel, table=True):
    id: str = Field(default_factory=uid, primary_key=True)
    status: str = "queued"
    progress_pct: int = 0
    errors: list = Field(default_factory=list, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class EnrichmentJob(SQLModel, table=True):
    id: str = Field(default_factory=uid, primary_key=True)
    status: str = "queued"
    progress_pct: int = 0
    operation: str
    target_company_ids: list = Field(default_factory=list, sa_column=Column(JSON))
    errors: list = Field(default_factory=list, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class EnrichmentRow(SQLModel, table=True):
    id: str = Field(default_factory=uid, primary_key=True)
    job_id: str = Field(index=True)
    company_id: str = Field(index=True)
    operation: str
    status: str = "QUEUED"
    value: Optional[str] = None
    error: Optional[str] = None
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
