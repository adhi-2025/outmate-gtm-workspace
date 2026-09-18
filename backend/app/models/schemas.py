from datetime import datetime
from typing import Any, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


ToolName = Literal[
    "account_search",
    "person_discovery",
    "evidence_fetch",
]


class ResearchStep(BaseModel):
    tool: ToolName
    params: dict[str, Any] = Field(default_factory=dict)


class ResearchPlan(BaseModel):
    plan_steps: list[ResearchStep] = Field(min_length=1, max_length=10)
    hypotheses: str
    estimated_cost_units: int = Field(ge=0, le=500)


class ResearchRequest(BaseModel):
    query: str = Field(min_length=3, max_length=2000)


class CompanyOut(BaseModel):
    id: str
    name: str
    domain: str
    location: str
    employee_range: str
    industry: str
    score: Optional[float] = None
    score_breakdown: dict = {}
    evidence_count: int = 0
    evidence_status: str = "Incomplete"
    top_decision_maker: Optional[str] = None


class EnrichmentCreate(BaseModel):
    target_company_ids: list[str] = Field(min_length=1, max_length=15)
    operation: str


class EnrichmentCreateOut(BaseModel):
    enrichment_job_id: str
    estimated_unit_cost: int


class EnrichmentRowOut(BaseModel):
    id: str
    company_id: str
    operation: str
    status: str
    value: Optional[str] = None
    error: Optional[str] = None


class EnrichmentOut(BaseModel):
    id: str
    status: str
    progress_pct: int
    operation: str
    rows: list[EnrichmentRowOut]
    errors: list[str]


class EvidenceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    entity_id: str
    claim_field: str
    observed_value: str
    source_url: str
    retrieved_at: datetime
    evidence_type: str
    confidence_score: float
    conflict_note: Optional[str] = None


class EntityDetail(BaseModel):
    company: CompanyOut
    evidence: list[EvidenceOut]
    people: list[dict]
    signals: list[dict]