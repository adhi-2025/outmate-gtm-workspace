import csv, io
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from sqlmodel import select
from ...core.database import session
from ...models.entities import Company, Evidence, Score

router=APIRouter(prefix="/api/export",tags=["export"])
@router.get("/csv")
def export_csv():
    with session() as db:
        cs=db.exec(select(Company)).all()
        buf=io.StringIO(); w=csv.writer(buf)
        w.writerow(["Company Name","Domain","Headcount","Location","Industry","ICP Score","Evidence Count"])
        for c in cs:
            s=db.exec(select(Score).where(Score.entity_id==c.id,Score.score_type=="ICP_FIT")).first()
            n=len(db.exec(select(Evidence).where(Evidence.entity_id==c.id)).all())
            w.writerow([c.name,c.domain,c.employee_range,c.location,c.industry,s.score_value if s else "",n])
        buf.seek(0)
        return StreamingResponse(iter([buf.getvalue()]),media_type="text/csv",
                                 headers={"Content-Disposition":"attachment; filename=outmate-results.csv"})
