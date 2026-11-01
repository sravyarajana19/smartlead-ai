import re
from typing import Dict, Any, List, Optional, Tuple


def normalize_phone(phone: Optional[str]) -> Optional[str]:
    """Strip all non-digits, keeping digits only. Returns None if empty."""
    if not phone:
        return None
    digits = re.sub(r"\D", "", phone)
    if not digits:
        return None
    # If 10 digits in US format, prefix with 1 for standardization
    if len(digits) == 10:
        digits = "1" + digits
    return f"+{digits}"


class DeduplicationService:
    """
    Intelligent Deduplication Engine.
    Detects exact duplicates, potential duplicates, and legitimate repeat leads.
    Preserves original canonical records and creates relationship mappings.
    Detects Case 4: Duplicate leads creating duplicate opportunities.
    """

    @staticmethod
    def compare_leads(
        existing_lead: Dict[str, Any],
        new_lead: Dict[str, Any],
        existing_contact: Dict[str, Any],
        new_contact: Dict[str, Any],
        existing_company: Dict[str, Any],
        new_company: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:
        """
        Compare two lead records to determine if they are duplicate.
        Returns match metadata if duplicate, else None.
        """
        email_1 = (existing_contact.get("email") or "").strip().lower()
        email_2 = (new_contact.get("email") or "").strip().lower()

        phone_1 = normalize_phone(existing_contact.get("phone"))
        phone_2 = normalize_phone(new_contact.get("phone"))

        domain_1 = (existing_company.get("domain") or "").strip().lower()
        domain_2 = (new_company.get("domain") or "").strip().lower()

        last_1 = (existing_contact.get("last_name") or "").strip().lower()
        last_2 = (new_contact.get("last_name") or "").strip().lower()

        product_1 = existing_lead.get("product_interest")
        product_2 = new_lead.get("product_interest")

        created_1 = existing_lead.get("created_at")
        created_2 = new_lead.get("created_at")

        # 1. Exact Duplicate by Email
        if email_1 and email_2 and email_1 == email_2:
            # Check if legitimate repeat (different product and submitted >= 180 days later)
            if product_1 != product_2 and created_1 and created_2:
                try:
                    delta_days = abs((created_2 - created_1).days)
                except Exception:
                    delta_days = 0
                if delta_days >= 180:
                    return {
                        "match_type": "Legitimate Repeat",
                        "match_reason": f"Same email ({email_1}) but new product inquiry ({product_2} vs {product_1}) after {delta_days} days",
                        "similarity_score": 0.85,
                        "is_duplicate": False,  # Not blocked, treated as valid repeat
                    }

            return {
                "match_type": "Exact",
                "match_reason": f"Exact match on email address: {email_1}",
                "similarity_score": 1.0,
                "is_duplicate": True,
            }

        # 2. Exact Duplicate by Normalized Phone
        if phone_1 and phone_2 and phone_1 == phone_2:
            return {
                "match_type": "Exact",
                "match_reason": f"Exact match on normalized phone number: {phone_1}",
                "similarity_score": 1.0,
                "is_duplicate": True,
            }

        # 3. Potential Duplicate by Domain + Last Name
        if domain_1 and domain_2 and domain_1 == domain_2 and last_1 and last_2 and last_1 == last_2:
            return {
                "match_type": "Potential",
                "match_reason": f"Potential match: same company domain ({domain_1}) and contact last name ({last_1})",
                "similarity_score": 0.75,
                "is_duplicate": True,
            }

        return None

    @staticmethod
    def detect_duplicate_opportunity(
        lead_id: str,
        is_lead_duplicate: bool,
        existing_opportunities: List[Dict[str, Any]],
        company_id: Optional[str] = None,
        product_interest: Optional[str] = None,
        canonical_lead_id: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        CASE 4 Detection:
        If a duplicate lead has spawned an opportunity for the same company and same product interest
        as an existing active opportunity, detect Case 4 duplicate opportunity anomaly.
        """
        if not is_lead_duplicate:
            return None

        for opp in existing_opportunities:
            if opp.get("current_stage") in {"Won", "Lost"}:
                continue

            opp_company = opp.get("company_id")
            opp_lead = opp.get("lead_id")

            # When company or canonical lead scope is provided, strictly enforce match
            if company_id is not None or canonical_lead_id is not None:
                matches_company = (company_id is not None and opp_company == company_id)
                matches_canonical = (canonical_lead_id is not None and opp_lead == canonical_lead_id)
                if not (matches_company or matches_canonical):
                    continue

            return {
                "is_duplicate_opportunity": True,
                "canonical_opp_id": opp.get("id"),
                "issue_type": "CASE_4_DUPLICATE_OPPORTUNITY",
                "explanation": f"Lead {lead_id} is marked as duplicate and created duplicate opportunity matching active opportunity {opp.get('id')}",
            }
        return None
