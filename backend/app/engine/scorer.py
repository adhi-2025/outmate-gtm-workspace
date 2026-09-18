from datetime import datetime, timezone

def band_midpoint(rng: str) -> int:
    try:
        a, b = [int(x) for x in rng.split("-")]
        return (a + b) // 2
    except Exception:
        return 0

def score_company(company, evidence, signals, query_params):
    # Deterministic code-enforced formula:
    # 0.30 employee + 0.25 geo + 0.25 industry + 0.20 intent
    target_min = int(query_params.get("min_emp", 1))
    target_max = int(query_params.get("max_emp", 1000))
    n = band_midpoint(company.employee_range)
    employee_fit = 1.0 if target_min <= n <= target_max else 0.0

    geo = str(query_params.get("geo", "Any")).lower()
    geo_fit = 1.0 if geo == "any" or geo in company.location.lower() or ("north america" in geo and any(x in company.location.lower() for x in ["usa", "canada"])) else 0.0

    ind = str(query_params.get("industry", "Any")).lower()
    industry_fit = 1.0 if ind == "any" or ind in company.industry.lower() else 0.0

    intent = [s for s in signals if s.entity_id == company.id and s.signal_type in {"HIRING_SURGE","CLOUD_MIGRATION","EXPANSION","BUYING_INTENT"}]
    if intent:
        intent_fit = sum(s.strength * s.source_reliability * max(0, 1 - s.freshness_days/365) for s in intent) / len(intent)
    else:
        intent_fit = 0.0

    # Contradictory/stale evidence reduces the evidence-grounded intent component only.
    conflicts = sum(1 for e in evidence if e.entity_id == company.id and e.evidence_type == "conflicting")
    if conflicts:
        intent_fit *= 0.7
    stale = sum(1 for e in evidence if e.entity_id == company.id and e.evidence_type == "stale")
    if stale:
        intent_fit *= 0.85

    breakdown = {
        "employee_fit": round(employee_fit, 6),
        "employee_weight": 0.30,
        "geo_fit": round(geo_fit, 6),
        "geo_weight": 0.25,
        "industry_fit": round(industry_fit, 6),
        "industry_weight": 0.25,
        "intent_fit": round(intent_fit, 6),
        "intent_weight": 0.20,
        "formula": "(0.30 × EmployeeBandFit) + (0.25 × GeoFit) + (0.25 × IndustryFit) + (0.20 × IntentSignalFit)",
        "evidence_ids": [e.id for e in evidence if e.entity_id == company.id],
    }
    value = 100 * (
        0.30 * employee_fit +
        0.25 * geo_fit +
        0.25 * industry_fit +
        0.20 * intent_fit
    )
    return round(value, 4), breakdown
