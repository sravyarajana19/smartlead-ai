from ml.dataset import MLDatasetBuilder


def test_ground_truth_and_anomaly_separation():
    leads = [
        {"id": "LEAD-001", "company_id": "CO-001", "contact_id": "CON-001", "fit_score": 80.0, "intent_score": 70.0, "engagement_score": 60.0, "lead_score": 71.5, "is_converted": False, "status": "New", "is_duplicate": False, "territory": "North America", "product_interest": "Cloud Platform", "lead_source": "Website"}
    ]
    companies = [{"id": "CO-001", "employee_count": 500, "annual_revenue": 10000000.0, "tier": "Mid-Market", "industry": "Technology"}]
    contacts = [{"id": "CON-001", "seniority_level": "Director"}]
    activities = [{"lead_id": "LEAD-001", "is_post_conversion": False}]

    df = MLDatasetBuilder.build_dataset(leads, companies, contacts, activities)

    # Ground truth columns MUST NOT be present in dataset
    forbidden_cols = ["anomaly_id", "issue_type", "ground_truth_label", "expected_decision", "actual_decision"]
    for col in forbidden_cols:
        assert col not in df.columns, f"Forbidden ground-truth column '{col}' leaked into ML dataset"
