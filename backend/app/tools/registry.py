from typing import Protocol
from sqlmodel import Session, select
from ..models.entities import Company, Person, Evidence, Signal

class Provider(Protocol):
    def account_search(self, industry, min_emp, max_emp, geo): ...
    def person_discovery(self, company_id, target_roles): ...
    def evidence_fetch(self, entity_id, topic): ...
    def enrich_field(self, entity_id, operation): ...

def midpoint(r): 
    a,b = map(int,r.split("-")); return (a+b)//2

class DemoSeedProvider:
    def __init__(self, db: Session): self.db = db

    def account_search(self, industry, min_emp, max_emp, geo):
        companies = self.db.exec(select(Company)).all()
        out=[]
        for c in companies:
            emp=midpoint(c.employee_range)
            ok_ind = industry == "Any" or industry.lower() in c.industry.lower()
            ok_geo = geo == "Any" or geo.lower() in c.location.lower() or (geo == "North America" and any(x in c.location for x in ["USA","Canada"]))
            if min_emp <= emp <= max_emp and ok_ind and ok_geo: out.append(c)
        return out[:15]

    def person_discovery(self, company_id, target_roles):
        people = self.db.exec(select(Person).where(Person.company_id == company_id)).all()
        return [p for p in people if any(r.lower() in p.title.lower() for r in target_roles)]

    def evidence_fetch(self, entity_id, topic):
        return self.db.exec(select(Evidence).where(Evidence.entity_id == entity_id)).all()

    def enrich_field(self, entity_id, operation):
        mapping = {
            "VERIFY_SECURITY_LEADERSHIP": "Security leadership verified from company evidence: CISO/security owner signal found.",
            "TECH_STACK_DETECT": "Technology signal: cloud-native application stack detected.",
            "RECENT_FUNDING": "Funding signal: recent financing activity detected in seed corpus."
        }
        return {"value": mapping.get(operation, f"Completed {operation}")}

class LiveProvider(DemoSeedProvider):
    # Production seam: replace these methods with APIs/browser/search integrations.
    pass

class ToolRegistry:
    def __init__(self, provider): self.provider = provider
    def account_search(self, **p): return self.provider.account_search(**p)
    def person_discovery(self, **p): return self.provider.person_discovery(**p)
    def evidence_fetch(self, **p): return self.provider.evidence_fetch(**p)
    def enrich_field(self, **p): return self.provider.enrich_field(**p)
