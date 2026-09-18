from fastapi import APIRouter, BackgroundTasks, HTTPException
from datetime import datetime, timezone
from sqlmodel import select
from ...core.database import session
from ...models.entities import EnrichmentJob, EnrichmentRow, Evidence
from ...models.schemas import EnrichmentCreate, EnrichmentCreateOut, EnrichmentOut, EnrichmentRowOut
from ...tools.registry import ToolRegistry, DemoSeedProvider

router=APIRouter(prefix="/api/enrichments",tags=["enrichments"])
COSTS={"VERIFY_SECURITY_LEADERSHIP":12,"TECH_STACK_DETECT":8,"RECENT_FUNDING":10}

def run_enrichment(job_id):
    with session() as db:
        job=db.get(EnrichmentJob,job_id)
        if not job: return
        job.status="executing"; db.commit()
        rows=db.exec(select(EnrichmentRow).where(EnrichmentRow.job_id==job_id)).all()
        for i,row in enumerate(rows):
            if row.status=="COMPLETED": continue
            try:
                row.status="RUNNING"; db.commit()
                result=ToolRegistry(DemoSeedProvider(db)).enrich_field(entity_id=row.company_id,operation=row.operation)
                row.value=result["value"]; row.status="COMPLETED"; row.error=None
                db.add(Evidence(entity_id=row.company_id,claim_field=row.operation,observed_value=row.value,
                                source_url="https://demo.outmate.local/verified-enrichment",
                                evidence_type="observed",confidence_score=.86))
            except Exception as e:
                row.status="FAILED"; row.error=str(e); db.add(row)
            job.progress_pct=int((i+1)/len(rows)*100); job.updated_at=datetime.now(timezone.utc); db.commit()
        job.status="completed" if all(r.status=="COMPLETED" for r in rows) else "failed"; db.commit()

@router.post("",response_model=EnrichmentCreateOut)
def create(req:EnrichmentCreate):
    if req.operation not in COSTS: raise HTTPException(400,"Unsupported operation")
    with session() as db:
        job=EnrichmentJob(operation=req.operation,target_company_ids=req.target_company_ids)
        db.add(job); db.flush()
        for cid in req.target_company_ids: db.add(EnrichmentRow(job_id=job.id,company_id=cid,operation=req.operation))
        db.commit()
        return EnrichmentCreateOut(enrichment_job_id=job.id,estimated_unit_cost=COSTS[req.operation]*len(req.target_company_ids))

@router.post("/{job_id}/run")
def run(job_id:str,bg:BackgroundTasks):
    with session() as db:
        if not db.get(EnrichmentJob,job_id): raise HTTPException(404,"Job not found")
    bg.add_task(run_enrichment,job_id)
    return {"status":"started","enrichment_job_id":job_id}

@router.post("/{job_id}/retry/{row_id}")
def retry(job_id:str,row_id:str,bg:BackgroundTasks):
    with session() as db:
        row=db.get(EnrichmentRow,row_id)
        if not row or row.job_id!=job_id: raise HTTPException(404,"Row not found")
        row.status="QUEUED"; row.error=None; db.commit()
    bg.add_task(run_enrichment,job_id)
    return {"status":"retry_queued","row_id":row_id}

@router.get("/{job_id}",response_model=EnrichmentOut)
def get(job_id:str):
    with session() as db:
        job=db.get(EnrichmentJob,job_id)
        if not job: raise HTTPException(404,"Job not found")
        rows=db.exec(select(EnrichmentRow).where(EnrichmentRow.job_id==job_id)).all()
        return EnrichmentOut(id=job.id,status=job.status,progress_pct=job.progress_pct,operation=job.operation,
                             rows=[EnrichmentRowOut.model_validate(r) for r in rows],errors=job.errors)
