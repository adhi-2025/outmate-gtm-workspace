from sqlmodel import select
from ..models.entities import Company, Person, Evidence, Signal, Score
from .scorer import score_company

class ResearchExecutor:
    def __init__(self, db, registry): self.db, self.registry = db, registry

    def execute(self, plan):
        search = next(s for s in plan.plan_steps if s.tool == "account_search")
        p = search.params
        companies = self.registry.account_search(**p)
        scores=[]
        for c in companies:
            people = self.registry.person_discovery(company_id=c.id, target_roles=["CTO","CISO","VP Sales"])
            evidence = self.registry.evidence_fetch(entity_id=c.id, topic="all")
            signals = self.db.exec(select(Signal).where(Signal.entity_id == c.id)).all()
            value, breakdown = score_company(c, evidence, signals, p)
            old = self.db.exec(select(Score).where(Score.entity_id == c.id, Score.score_type=="ICP_FIT")).first()
            if old: old.score_value, old.breakdown = value, breakdown
            else: self.db.add(Score(entity_id=c.id, score_value=value, breakdown=breakdown))
            scores.append((c, people, evidence, value, breakdown))
        self.db.commit()
        return scores
