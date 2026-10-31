from datetime import datetime, timedelta
from backend.services.scoring_service import LeadScoringEngine


def test_post_conversion_temporal_leakage():
    engine = LeadScoringEngine()
    conv_date = datetime(2026, 1, 10)

    # Activity after conversion
    leakage_act = {
        "activity_type": "Demo Request",
        "activity_date": conv_date + timedelta(days=5),
        "channel": "Web",
        "is_post_conversion": True,
    }
    # Activity before conversion
    valid_act = {
        "activity_type": "Page View",
        "activity_date": conv_date - timedelta(days=5),
        "channel": "Web",
        "is_post_conversion": False,
    }

    # Intent score with leakage filtering
    intent_score, breakdown, leakage_detected = engine.calculate_intent_score(
        lead_source="Website",
        activities=[valid_act, leakage_act],
        converted_date=conv_date,
        filter_post_conversion=True,
    )

    assert leakage_detected is True
    # Demo request points should NOT be included in intent score
    assert breakdown["demo_requests"] == 0
