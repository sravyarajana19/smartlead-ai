import pytest
from datetime import datetime
from backend.services.scoring_service import LeadScoringEngine


def test_scoring_weights_validation():
    # Weights must sum to 1.0
    with pytest.raises(ValueError):
        LeadScoringEngine(fit_weight=0.5, intent_weight=0.5, engagement_weight=0.5)


def test_lead_score_formula_and_priority():
    engine = LeadScoringEngine()
    
    # High Priority: >= 80.0
    score, priority = engine.compute_lead_score(fit_score=90.0, intent_score=85.0, engagement_score=75.0)
    expected = round((90.0 * 0.40) + (85.0 * 0.35) + (75.0 * 0.25), 2)
    assert score == expected
    assert priority == "High"
    assert 80.0 <= score <= 100.0

    # Medium Priority: 50.0 - 79.99
    score_med, priority_med = engine.compute_lead_score(fit_score=60.0, intent_score=50.0, engagement_score=50.0)
    assert score_med == 54.0
    assert priority_med == "Medium"

    # Low Priority: 0.0 - 49.99
    score_low, priority_low = engine.compute_lead_score(fit_score=30.0, intent_score=20.0, engagement_score=10.0)
    assert score_low == 21.5
    assert priority_low == "Low"


def test_score_boundary_conditions():
    engine = LeadScoringEngine()

    # Minimum boundary
    min_score, min_priority = engine.compute_lead_score(0.0, 0.0, 0.0)
    assert min_score == 0.0
    assert min_priority == "Low"

    # Maximum boundary
    max_score, max_priority = engine.compute_lead_score(100.0, 100.0, 100.0)
    assert max_score == 100.0
    assert max_priority == "High"

    # Exact threshold 50.0
    s_50, p_50 = engine.compute_lead_score(50.0, 50.0, 50.0)
    assert s_50 == 50.0
    assert p_50 == "Medium"

    # Exact threshold 80.0
    s_80, p_80 = engine.compute_lead_score(80.0, 80.0, 80.0)
    assert s_80 == 80.0
    assert p_80 == "High"


def test_fit_score_calculation():
    engine = LeadScoringEngine()
    fit, details = engine.calculate_fit_score(
        employee_count=1500,
        annual_revenue=60_000_000,
        industry="Technology",
        seniority_level="C-Level",
    )
    assert fit == 100.0
    assert details["employee_pts"] == 40.0
    assert details["revenue_pts"] == 30.0
    assert details["industry_pts"] == 20.0
    assert details["seniority_pts"] == 10.0
