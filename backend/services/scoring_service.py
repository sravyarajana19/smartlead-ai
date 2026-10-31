from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
from backend.core.config import (
    DEFAULT_FIT_WEIGHT,
    DEFAULT_INTENT_WEIGHT,
    DEFAULT_ENGAGEMENT_WEIGHT,
    HIGH_PRIORITY_MIN,
    MEDIUM_PRIORITY_MIN,
)


class LeadScoringEngine:
    """
    Production-grade Lead Scoring Engine.
    Computes Company Fit (40%), Buying Intent (35%), and Engagement (25%).
    Enforces strict 0-100 bounding, priority classification, temporal leakage prevention,
    and granular explainability.
    """

    def __init__(
        self,
        fit_weight: float = DEFAULT_FIT_WEIGHT,
        intent_weight: float = DEFAULT_INTENT_WEIGHT,
        engagement_weight: float = DEFAULT_ENGAGEMENT_WEIGHT,
        rule_version: str = "v1.0.0",
    ):
        # Validate weights sum to 1.0 (with slight tolerance)
        total_w = fit_weight + intent_weight + engagement_weight
        if abs(total_w - 1.0) > 0.001:
            raise ValueError(f"Scoring weights must sum to 1.0. Got {total_w}")

        self.fit_weight = fit_weight
        self.intent_weight = intent_weight
        self.engagement_weight = engagement_weight
        self.rule_version = rule_version

    def calculate_fit_score(
        self,
        employee_count: int,
        annual_revenue: float,
        industry: str,
        seniority_level: str,
    ) -> Tuple[float, Dict[str, Any]]:
        """Calculate Company Fit score (0-100) based on firmographics and contact persona."""
        breakdown = {}

        # 1. Company Size (40 pts max)
        if employee_count >= 1000:
            size_pts = 40.0
            size_tier = "Enterprise (>=1000)"
        elif employee_count >= 250:
            size_pts = 30.0
            size_tier = "Upper Mid-Market (250-999)"
        elif employee_count >= 50:
            size_pts = 20.0
            size_tier = "Lower Mid-Market (50-249)"
        else:
            size_pts = 10.0
            size_tier = "SMB (<50)"
        breakdown["employee_pts"] = size_pts
        breakdown["employee_tier"] = size_tier

        # 2. Annual Revenue (30 pts max)
        if annual_revenue >= 50_000_000:
            rev_pts = 30.0
            rev_tier = "Tier 1 (>= $50M)"
        elif annual_revenue >= 10_000_000:
            rev_pts = 20.0
            rev_tier = "Tier 2 ($10M - $50M)"
        elif annual_revenue >= 1_000_000:
            rev_pts = 15.0
            rev_tier = "Tier 3 ($1M - $10M)"
        else:
            rev_pts = 5.0
            rev_tier = "Tier 4 (< $1M)"
        breakdown["revenue_pts"] = rev_pts
        breakdown["revenue_tier"] = rev_tier

        # 3. Industry Alignment (20 pts max)
        high_fit_industries = {"Technology", "Financial Services", "Healthcare", "Manufacturing", "Telecommunications"}
        if industry in high_fit_industries:
            ind_pts = 20.0
            ind_match = "Primary Target Industry"
        else:
            ind_pts = 10.0
            ind_match = "Secondary Industry"
        breakdown["industry_pts"] = ind_pts
        breakdown["industry_match"] = ind_match

        # 4. Contact Seniority Authority (10 pts max)
        if seniority_level in {"C-Level", "VP"}:
            sen_pts = 10.0
        elif seniority_level in {"Director", "Head"}:
            sen_pts = 8.0
        elif seniority_level in {"Manager", "Lead"}:
            sen_pts = 5.0
        else:
            sen_pts = 2.0
        breakdown["seniority_pts"] = sen_pts
        breakdown["seniority_level"] = seniority_level

        fit_score = min(100.0, max(0.0, size_pts + rev_pts + ind_pts + sen_pts))
        return round(fit_score, 2), breakdown

    def calculate_intent_score(
        self,
        lead_source: str,
        activities: List[Dict[str, Any]],
        converted_date: Optional[datetime] = None,
        filter_post_conversion: bool = True,
    ) -> Tuple[float, Dict[str, Any], bool]:
        """
        Calculate Buying Intent score (0-100).
        Protects against temporal leakage: ignores activities after converted_date.
        Returns: (intent_score, breakdown, leakage_detected)
        """
        breakdown = {
            "demo_requests": 0,
            "pricing_views": 0,
            "webinar_attends": 0,
            "whitepaper_downloads": 0,
            "source_pts": 0.0,
            "activity_pts": 0.0,
        }
        leakage_detected = False

        # Inbound source intent bonus
        high_intent_sources = {"Website", "Inbound Form", "Referral"}
        if lead_source in high_intent_sources:
            breakdown["source_pts"] = 25.0
        elif lead_source in {"Event", "Organic Search"}:
            breakdown["source_pts"] = 15.0
        else:
            breakdown["source_pts"] = 5.0

        activity_pts = 0.0
        for act in activities:
            act_date = act.get("activity_date")
            act_type = act.get("activity_type", "")
            is_post = act.get("is_post_conversion", False)

            # Check for temporal leakage
            if converted_date and act_date:
                if isinstance(act_date, str):
                    try:
                        act_date = datetime.fromisoformat(act_date)
                    except Exception:
                        pass
                if isinstance(act_date, datetime) and act_date > converted_date:
                    leakage_detected = True
                    if filter_post_conversion:
                        # Exclude post-conversion activity from clean calculation
                        continue

            if is_post and filter_post_conversion:
                leakage_detected = True
                continue

            if act_type == "Demo Request":
                activity_pts += 40.0
                breakdown["demo_requests"] += 1
            elif act_type == "Pricing View":
                activity_pts += 25.0
                breakdown["pricing_views"] += 1
            elif act_type in {"Webinar Attend", "Product Launch"}:
                activity_pts += 20.0
                breakdown["webinar_attends"] += 1
            elif act_type == "Whitepaper Download":
                activity_pts += 15.0
                breakdown["whitepaper_downloads"] += 1
            elif act_type == "Inbound Call":
                activity_pts += 20.0

        breakdown["activity_pts"] = round(activity_pts, 2)
        raw_intent = breakdown["source_pts"] + activity_pts
        intent_score = min(100.0, max(0.0, raw_intent))
        return round(intent_score, 2), breakdown, leakage_detected

    def calculate_engagement_score(
        self,
        activities: List[Dict[str, Any]],
        reference_date: Optional[datetime] = None,
        converted_date: Optional[datetime] = None,
        filter_post_conversion: bool = True,
    ) -> Tuple[float, Dict[str, Any], bool]:
        """
        Calculate Engagement score (0-100) based on recency, frequency, and channel depth.
        Excludes post-conversion activities to prevent temporal leakage.
        """
        if reference_date is None:
            reference_date = datetime.utcnow()

        breakdown = {
            "total_valid_activities": 0,
            "recency_pts": 0.0,
            "frequency_pts": 0.0,
            "channel_depth_pts": 0.0,
        }
        leakage_detected = False

        valid_activities = []
        for act in activities:
            act_date = act.get("activity_date")
            is_post = act.get("is_post_conversion", False)
            if converted_date and act_date:
                if isinstance(act_date, str):
                    try:
                        act_date = datetime.fromisoformat(act_date)
                    except Exception:
                        pass
                if isinstance(act_date, datetime) and act_date > converted_date:
                    leakage_detected = True
                    if filter_post_conversion:
                        continue
            if is_post and filter_post_conversion:
                leakage_detected = True
                continue
            valid_activities.append(act)

        breakdown["total_valid_activities"] = len(valid_activities)

        if not valid_activities:
            return 0.0, breakdown, leakage_detected

        # 1. Frequency (35 pts max)
        count = len(valid_activities)
        if count >= 8:
            freq_pts = 35.0
        elif count >= 5:
            freq_pts = 28.0
        elif count >= 3:
            freq_pts = 20.0
        elif count >= 1:
            freq_pts = 10.0
        else:
            freq_pts = 0.0
        breakdown["frequency_pts"] = freq_pts

        # 2. Recency of most recent valid activity (35 pts max)
        dates = []
        for a in valid_activities:
            d = a.get("activity_date")
            if isinstance(d, str):
                try:
                    d = datetime.fromisoformat(d)
                except Exception:
                    d = None
            if isinstance(d, datetime):
                dates.append(d)

        if dates:
            most_recent = max(dates)
            days_ago = max(0, (reference_date - most_recent).days)
            if days_ago <= 7:
                rec_pts = 35.0
            elif days_ago <= 30:
                rec_pts = 25.0
            elif days_ago <= 90:
                rec_pts = 15.0
            else:
                rec_pts = 5.0
        else:
            days_ago = None
            rec_pts = 5.0
        breakdown["recency_pts"] = rec_pts
        breakdown["days_since_last_activity"] = days_ago

        # 3. Channel Depth (30 pts max)
        has_email_click = any(a.get("activity_type") == "Email Click" for a in valid_activities)
        has_email_open = any(a.get("activity_type") == "Email Open" for a in valid_activities)
        has_web_session = any(a.get("channel") == "Web" for a in valid_activities)

        channel_pts = 0.0
        if has_email_click:
            channel_pts += 15.0
        if has_email_open:
            channel_pts += 8.0
        if has_web_session:
            channel_pts += 7.0
        breakdown["channel_depth_pts"] = min(30.0, channel_pts)

        raw_eng = freq_pts + rec_pts + breakdown["channel_depth_pts"]
        engagement_score = min(100.0, max(0.0, raw_eng))
        return round(engagement_score, 2), breakdown, leakage_detected

    def compute_lead_score(
        self,
        fit_score: float,
        intent_score: float,
        engagement_score: float,
    ) -> Tuple[float, str]:
        """
        Lead Score = (Fit Score * 0.40) + (Intent Score * 0.35) + (Engagement Score * 0.25)
        All component scores and total score must be 0-100.
        Priority:
        - 80-100: High
        - 50-79.99: Medium
        - 0-49.99: Low
        """
        bounded_fit = min(100.0, max(0.0, fit_score))
        bounded_intent = min(100.0, max(0.0, intent_score))
        bounded_eng = min(100.0, max(0.0, engagement_score))

        total_score = (
            (bounded_fit * self.fit_weight)
            + (bounded_intent * self.intent_weight)
            + (bounded_eng * self.engagement_weight)
        )
        total_score = round(min(100.0, max(0.0, total_score)), 2)

        if total_score >= HIGH_PRIORITY_MIN:
            priority = "High"
        elif total_score >= MEDIUM_PRIORITY_MIN:
            priority = "Medium"
        else:
            priority = "Low"

        return total_score, priority

    def evaluate_lead_full(
        self,
        lead_id: str,
        company_data: Dict[str, Any],
        contact_data: Dict[str, Any],
        lead_data: Dict[str, Any],
        activities: List[Dict[str, Any]],
        converted_date: Optional[datetime] = None,
        filter_post_conversion: bool = True,
    ) -> Dict[str, Any]:
        """Full end-to-end explainable lead score calculation."""
        fit_score, fit_details = self.calculate_fit_score(
            employee_count=company_data.get("employee_count", 0),
            annual_revenue=company_data.get("annual_revenue", 0.0),
            industry=company_data.get("industry", ""),
            seniority_level=contact_data.get("seniority_level", ""),
        )

        intent_score, intent_details, intent_leakage = self.calculate_intent_score(
            lead_source=lead_data.get("lead_source", ""),
            activities=activities,
            converted_date=converted_date,
            filter_post_conversion=filter_post_conversion,
        )

        eng_score, eng_details, eng_leakage = self.calculate_engagement_score(
            activities=activities,
            reference_date=lead_data.get("reference_date", datetime.utcnow()),
            converted_date=converted_date,
            filter_post_conversion=filter_post_conversion,
        )

        leakage_detected = intent_leakage or eng_leakage

        lead_score, priority = self.compute_lead_score(
            fit_score=fit_score,
            intent_score=intent_score,
            engagement_score=eng_score,
        )

        return {
            "lead_id": lead_id,
            "fit_score": fit_score,
            "intent_score": intent_score,
            "engagement_score": eng_score,
            "lead_score": lead_score,
            "priority": priority,
            "rule_version": self.rule_version,
            "fit_weight": self.fit_weight,
            "intent_weight": self.intent_weight,
            "engagement_weight": self.engagement_weight,
            "is_leakage_detected": leakage_detected,
            "calculated_at": datetime.utcnow().isoformat(),
            "explanation_details": {
                "fit_breakdown": fit_details,
                "intent_breakdown": intent_details,
                "engagement_breakdown": eng_details,
                "weighted_contributions": {
                    "fit_contribution": round(fit_score * self.fit_weight, 2),
                    "intent_contribution": round(intent_score * self.intent_weight, 2),
                    "engagement_contribution": round(eng_score * self.engagement_weight, 2),
                },
            },
        }
