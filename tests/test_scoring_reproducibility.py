from datetime import datetime
from backend.services.scoring_service import LeadScoringEngine


def test_score_reproducibility():
    engine = LeadScoringEngine()

    company = {
        "employee_count": 500,
        "annual_revenue": 25_000_000,
        "industry": "Financial Services",
    }
    contact = {
        "seniority_level": "VP",
    }
    lead = {
        "lead_source": "Website",
        "reference_date": datetime(2026, 1, 15),
    }
    activities = [
        {"activity_type": "Demo Request", "activity_date": datetime(2026, 1, 10), "channel": "Web", "is_post_conversion": False},
        {"activity_type": "Pricing View", "activity_date": datetime(2026, 1, 12), "channel": "Web", "is_post_conversion": False},
        {"activity_type": "Email Click", "activity_date": datetime(2026, 1, 14), "channel": "Email", "is_post_conversion": False},
    ]

    res1 = engine.evaluate_lead_full("LEAD-001", company, contact, lead, activities)
    res2 = engine.evaluate_lead_full("LEAD-001", company, contact, lead, activities)

    assert res1["fit_score"] == res2["fit_score"]
    assert res1["intent_score"] == res2["intent_score"]
    assert res1["engagement_score"] == res2["engagement_score"]
    assert res1["lead_score"] == res2["lead_score"]
    assert res1["priority"] == res2["priority"]
