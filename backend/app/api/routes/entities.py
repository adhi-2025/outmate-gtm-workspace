from fastapi import APIRouter, HTTPException
from sqlmodel import select
from ...core.database import session
from ...models.entities import Company, Person, Evidence, Signal, Score
from ...models.schemas import CompanyOut, EntityDetail, EvidenceOut

router=APIRouter(prefix="/api/entities",tags=["entities"])

@router.get("", response_model=list[CompanyOut])
def list_entities():
    with session() as db:
        cs=db.exec(select(Company)).all()
        out=[]
        for c in cs:
            sc=db.exec(select(Score).where(Score.entity_id==c.id,Score.score_type=="ICP_FIT")).first()
            es=db.exec(select(Evidence).where(Evidence.entity_id==c.id)).all()
            ps=db.exec(select(Person).where(Person.company_id==c.id)).all()
            statuses=[e.evidence_type for e in es]
            status="Conflicting" if "conflicting" in statuses else ("Verified" if len(es)>=4 else "Incomplete")
            out.append(CompanyOut(id=c.id,name=c.name,domain=c.domain,location=c.location,employee_range=c.employee_range,
                                  industry=c.industry,score=sc.score_value if sc else None,
                                  score_breakdown=sc.breakdown if sc else {},evidence_count=len(es),
                                  evidence_status=status,top_decision_maker=ps[0].name if ps else None))
        return out

@router.get("/{entity_id}",response_model=EntityDetail)
def detail(entity_id:str):
    with session() as db:
        c=db.get(Company,entity_id)
        if not c: raise HTTPException(404,"Company not found")
        es=db.exec(select(Evidence).where(Evidence.entity_id==entity_id)).all()
        ps=db.exec(select(Person).where(Person.company_id==entity_id)).all()
        ss=db.exec(select(Signal).where(Signal.entity_id==entity_id)).all()
        sc=db.exec(select(Score).where(Score.entity_id==entity_id,Score.score_type=="ICP_FIT")).first()
        co=CompanyOut(id=c.id,name=c.name,domain=c.domain,location=c.location,employee_range=c.employee_range,industry=c.industry,
                      score=sc.score_value if sc else None,score_breakdown=sc.breakdown if sc else {},evidence_count=len(es),
                      evidence_status="Conflicting" if any(e.evidence_type=="conflicting" for e in es) else ("Verified" if len(es)>=4 else "Incomplete"),
                      top_decision_maker=ps[0].name if ps else None)
        return EntityDetail(company=co,evidence=[EvidenceOut.model_validate(e) for e in es],
                            people=[p.model_dump() for p in ps],signals=[s.model_dump() for s in ss])
