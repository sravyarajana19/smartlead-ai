from backend.services.routing_service import SalesRoutingEngine


def test_routing_specialist_match():
    reps = [
        {"id": "REP-001", "name": "Elena", "territory": "EMEA", "product_specialization": "Cloud Platform", "is_active": True, "capacity": 50, "current_load": 10},
        {"id": "REP-002", "name": "Marcus", "territory": "North America", "product_specialization": "Cloud Platform", "is_active": True, "capacity": 50, "current_load": 5},
    ]

    chosen, status, expl = SalesRoutingEngine.route_lead("EMEA", "Cloud Platform", reps)
    assert chosen is not None
    assert chosen["id"] == "REP-001"
    assert status == "Assigned"


def test_routing_capacity_limit():
    reps = [
        {"id": "REP-001", "name": "Elena", "territory": "EMEA", "product_specialization": "Cloud Platform", "is_active": True, "capacity": 50, "current_load": 50},
    ]

    chosen, status, expl = SalesRoutingEngine.route_lead("EMEA", "Cloud Platform", reps)
    assert chosen is None
    assert status == "No_Capacity"


def test_case_3_routing_violation_detection():
    rep = {"id": "REP-001", "name": "Marcus", "territory": "North America"}
    anomaly = SalesRoutingEngine.detect_case_3_routing_violation("LEAD-001", "EMEA", rep)

    assert anomaly is not None
    assert anomaly["issue_type"] == "CASE_3_ROUTING_VIOLATION"
    assert anomaly["expected_territory"] == "EMEA"
    assert anomaly["actual_territory"] == "North America"
