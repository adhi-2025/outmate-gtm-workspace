from fastapi import APIRouter, BackgroundTasks
from fastapi import HTTPException
from sqlmodel import select
from .. import __init__
from ...core.database import session
from ...models.entities import ResearchJob, Company, Person, Evidence, Score, Signal
from ...models.schemas import ResearchRequest
from ...engine.planner import Planner
from ...engine.executor import ResearchExecutor
from ...tools.registry import ToolRegistry, DemoSeedProvider

router=APIRouter(prefix="/api/research", tags=["research"])

def run_job(job_id, query):
    with session() as db:
        job=db.get(ResearchJob, job_id); job.status="planning"; job.progress_pct=10; db.commit()
        try:
            plan=Planner().plan(query)
            job.status="executing"; job.progress_pct=25; db.commit()
            ResearchExecutor(db, ToolRegistry(DemoSeedProvider(db))).execute(plan)
            job.status="completed"; job.progress_pct=100; db.commit()
        except Exception as e:
            job.status="failed"; job.errors=[str(e)]; db.commit()

@router.post("")
def research(req: ResearchRequest, bg: BackgroundTasks):
    with session() as db:
        job=ResearchJob(status="queued"); db.add(job); db.commit(); db.refresh(job)
        bg.add_task(run_job, job.id, req.query)
        plan=Planner().plan(req.query)
        return {"research_job_id":job.id,"plan":plan.model_dump()}

@router.get("/{job_id}")
def get_job(job_id: str):
    with session() as db:
        job=db.get(ResearchJob,job_id)
        if not job: raise HTTPException(404,"Job not found")
        return job
