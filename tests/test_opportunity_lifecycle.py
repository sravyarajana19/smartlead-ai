from backend.services.opportunity_service import OpportunityManagementService


def test_valid_sequential_transitions():
    valid, _ = OpportunityManagementService.validate_transition("New", "Qualified")
    assert valid is True

    valid, _ = OpportunityManagementService.validate_transition("Qualified", "Proposal")
    assert valid is True

    valid, _ = OpportunityManagementService.validate_transition("Proposal", "Negotiation")
    assert valid is True

    valid, _ = OpportunityManagementService.validate_transition("Negotiation", "Won")
    assert valid is True


def test_invalid_leap_transitions():
    # Direct jump from New to Won without intermediate stages
    valid, err = OpportunityManagementService.validate_transition("New", "Won")
    assert valid is False
    assert "Invalid stage transition" in err

    # Transitioning out of terminal state
    valid_terminal, _ = OpportunityManagementService.validate_transition("Won", "New")
    assert valid_terminal is False
