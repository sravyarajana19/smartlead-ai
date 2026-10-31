from typing import Dict, Any, List, Optional, Tuple


class SalesRoutingEngine:
    """
    Deterministic Sales Routing Engine.
    Routes incoming leads based on:
    1. Territory match
    2. Product specialization
    3. Active representative status (is_active == True)
    4. Available capacity (current_load < capacity)
    Deterministic tie-breaker: Lowest current_load, then rep.id alphabetical order.
    Fallback: Clear unassigned / default fallback flag.
    Detects CASE 3: Routing violation (assigned representative outside lead's territory).
    """

    @staticmethod
    def route_lead(
        lead_territory: str,
        product_interest: str,
        available_reps: List[Dict[str, Any]],
    ) -> Tuple[Optional[Dict[str, Any]], str, str]:
        """
        Deterministically assign lead to the best matching active rep with capacity.
        Returns: (assigned_rep, status, explanation)
        status: 'Assigned', 'Fallback_Territory_Only', 'Fallback_Unassigned', 'No_Capacity'
        """
        # Tier 1: Exact Territory + Product match + Active + Available Capacity
        tier1_candidates = [
            rep for rep in available_reps
            if rep.get("is_active", True)
            and rep.get("territory") == lead_territory
            and rep.get("product_specialization") == product_interest
            and rep.get("current_load", 0) < rep.get("capacity", 50)
        ]

        if tier1_candidates:
            # Deterministic sort: lowest load, then rep ID
            tier1_candidates.sort(key=lambda r: (r.get("current_load", 0), r.get("id")))
            chosen = tier1_candidates[0]
            return (
                chosen,
                "Assigned",
                f"Routed to primary specialist {chosen['name']} ({chosen['id']}) for {lead_territory} and {product_interest}."
            )

        # Tier 2: Territory Match + Active + Available Capacity (cross-product within territory)
        tier2_candidates = [
            rep for rep in available_reps
            if rep.get("is_active", True)
            and rep.get("territory") == lead_territory
            and rep.get("current_load", 0) < rep.get("capacity", 50)
        ]

        if tier2_candidates:
            tier2_candidates.sort(key=lambda r: (r.get("current_load", 0), r.get("id")))
            chosen = tier2_candidates[0]
            return (
                chosen,
                "Fallback_Territory_Only",
                f"Assigned to territory rep {chosen['name']} ({chosen['id']}) with capacity in {lead_territory}."
            )

        # Tier 3: Check if territory reps exist but are at max capacity
        territory_reps_full = [
            rep for rep in available_reps
            if rep.get("is_active", True)
            and rep.get("territory") == lead_territory
        ]
        if territory_reps_full:
            return (
                None,
                "No_Capacity",
                f"All active representatives in territory '{lead_territory}' are at maximum capacity."
            )

        # Tier 4: Fallback - No rep in territory
        return (
            None,
            "Fallback_Unassigned",
            f"No active representative available in territory '{lead_territory}'. Lead moved to General Triage Queue."
        )

    @staticmethod
    def detect_case_3_routing_violation(
        lead_id: str,
        lead_territory: str,
        assigned_rep: Optional[Dict[str, Any]],
    ) -> Optional[Dict[str, Any]]:
        """
        CASE 3 Detection:
        If a lead is assigned to a sales representative whose territory does not match the lead territory.
        """
        if not assigned_rep:
            return None

        rep_territory = assigned_rep.get("territory")
        if rep_territory and rep_territory != lead_territory:
            return {
                "issue_type": "CASE_3_ROUTING_VIOLATION",
                "entity_id": lead_id,
                "severity": "High",
                "ground_truth_label": "TERRITORY_MISMATCH",
                "expected_decision": f"ASSIGN_TO_{lead_territory.upper().replace(' ', '_')}_REP",
                "actual_decision": f"ASSIGNED_TO_{rep_territory.upper().replace(' ', '_')}_REP",
                "explanation": (
                    f"Lead {lead_id} belongs to territory '{lead_territory}' but was assigned to representative "
                    f"{assigned_rep.get('name')} ({assigned_rep.get('id')}) in territory '{rep_territory}'."
                ),
                "expected_territory": lead_territory,
                "actual_territory": rep_territory,
            }
        return None
