import re
from ..models.schemas import ResearchPlan, ResearchStep

class Planner:
    # Deterministic demo adapter: produces the same structured plan for the same prompt.
    def plan(self, query: str) -> ResearchPlan:
        q = query.lower()
        min_emp, max_emp = 1, 1000
        m = re.search(r"(\d+)\s*[–-]\s*(\d+)", q)
        if m:
            min_emp, max_emp = int(m.group(1)), int(m.group(2))
        geo = "North America" if "north america" in q or "north american" in q else "Any"
        industry = "B2B SaaS" if "saas" in q else "Any"
        steps = [
            ResearchStep(tool="account_search", params={"industry": industry, "min_emp": min_emp, "max_emp": min(max_emp, 1000), "geo": geo}),
            ResearchStep(tool="person_discovery", params={"target_roles": ["CTO", "CISO", "VP Sales"]}),
            ResearchStep(tool="evidence_fetch", params={"topic": "buying_intent employee_count tech_stack location"}),
        ]
        return ResearchPlan(
            plan_steps=steps,
            hypotheses=f"Find accounts matching industry={industry}, employee range={min_emp}-{min(max_emp,1000)}, geo={geo}; ground each returned record in stored evidence.",
            estimated_cost_units=min(15, 10) + 2
        )
