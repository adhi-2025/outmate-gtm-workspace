import json
from pathlib import Path
from datetime import datetime, timezone, timedelta
from sqlmodel import select
from ..core.database import init_db, session
from ..models.entities import Company, Person, Evidence, Signal

ROOT = Path(__file__).resolve().parent
def main():
    init_db()
    data=json.loads((ROOT/"corpus.json").read_text())
    with session() as db:
        db.query(Company).delete(); db.query(Person).delete(); db.query(Evidence).delete(); db.query(Signal).delete()
        ids={}
        for x in data["companies"]:
            c=Company(**x); db.add(c); db.flush(); ids[c.name]=c.id
        for x in data["people"]:
            db.add(Person(company_id=ids[x["company"]], name=x["name"], title=x["title"],
                          relevance_rationale=f"{x['title']} is a target decision-making role for B2B security/GTM research."))
        for x in data["evidence"]:
            retrieved=datetime.now(timezone.utc)-timedelta(days=x["age_days"])
            db.add(Evidence(entity_id=ids[x["company"]], claim_field=x["claim_field"], observed_value=x["observed_value"],
                            source_url=x["source_url"], retrieved_at=retrieved, evidence_type=x["evidence_type"],
                            confidence_score=x["confidence_score"], conflict_note=x.get("conflict_note")))
        for name in ids:
            # Deterministic seed signals.
            st = "HIRING_SURGE" if name in {"Northstar Cloud","MapleOps","HarborStack","PrairieSec"} else "CLOUD_MIGRATION"
            db.add(Signal(entity_id=ids[name], signal_type=st, strength=.78 if st=="HIRING_SURGE" else .66,
                          freshness_days=25 if name not in {"BlueLedger","OrbitHR"} else 220, source_reliability=.88))
        db.commit()
    print(f"Seeded {len(data['companies'])} companies, {len(data['people'])} people, {len(data['evidence'])} evidence records.")
if __name__ == "__main__": main()
