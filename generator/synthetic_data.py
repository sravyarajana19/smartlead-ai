import os
import random
from datetime import datetime, timedelta, date
from typing import Dict, Any, List, Optional
import numpy as np
from faker import Faker

from backend.core.config import RANDOM_SEED, VALID_TERRITORIES, VALID_PRODUCTS
from generator.id_generator import (
    generate_company_id,
    generate_contact_id,
    generate_lead_id,
    generate_activity_id,
    generate_opportunity_id,
    generate_task_id,
    generate_campaign_id,
    generate_sales_rep_id,
    generate_consent_id,
    generate_score_rule_id,
    generate_stage_history_id,
    generate_duplicate_id,
    generate_consent_history_id,
)
from backend.services.scoring_service import LeadScoringEngine
from backend.services.dedup_service import normalize_phone, DeduplicationService
from backend.services.routing_service import SalesRoutingEngine


def get_dataset_scale_config(scale: str = "small") -> Dict[str, int]:
    """
    Returns baseline volume configurations.
    'small' is optimized for rapid local testing and development.
    'full' matches the exact prompt specification:
    - 5,000 companies
    - 10,000 contacts
    - 20,000 leads
    - 3,000 opportunities
    """
    if scale == "full":
        return {
            "num_companies": 5000,
            "num_contacts": 10000,
            "num_leads": 20000,
            "num_opportunities": 3000,
            "num_campaigns": 30,
            "num_sales_reps": 40,
        }
    else:  # small
        return {
            "num_companies": 150,
            "num_contacts": 300,
            "num_leads": 600,
            "num_opportunities": 90,
            "num_campaigns": 10,
            "num_sales_reps": 12,
        }


class SyntheticDataGenerator:
    """
    Deterministic Synthetic Data Generator for SmartLead AI.
    Generates realistic business distributions, strict parent-child relationships,
    temporal integrity, and deterministic zero-padded IDs.
    """

    def __init__(self, seed: int = RANDOM_SEED, scale: str = "small"):
        self.seed = seed
        self.scale = scale
        self.config = get_dataset_scale_config(scale)

        # Set deterministic seeds
        random.seed(seed)
        np.random.seed(seed)
        self.fake = Faker()
        self.fake.seed_instance(seed)

        self.scoring_engine = LeadScoringEngine()

        # Storage for generated records
        self.companies: List[Dict[str, Any]] = []
        self.contacts: List[Dict[str, Any]] = []
        self.campaigns: List[Dict[str, Any]] = []
        self.sales_reps: List[Dict[str, Any]] = []
        self.score_rules: List[Dict[str, Any]] = []
        self.leads: List[Dict[str, Any]] = []
        self.activities: List[Dict[str, Any]] = []
        self.consents: List[Dict[str, Any]] = []
        self.consent_histories: List[Dict[str, Any]] = []
        self.duplicate_relationships: List[Dict[str, Any]] = []
        self.tasks: List[Dict[str, Any]] = []
        self.opportunities: List[Dict[str, Any]] = []
        self.stage_histories: List[Dict[str, Any]] = []

    def generate_all(self) -> Dict[str, List[Dict[str, Any]]]:
        """Generate full synthetic ecosystem in strict master-to-dependent sequence."""
        self.generate_score_rules()
        self.generate_campaigns()
        self.generate_sales_reps()
        self.generate_companies()
        self.generate_contacts()
        self.generate_leads_and_activities()
        self.generate_consents()
        self.generate_opportunities_and_stages()
        self.generate_tasks()

        return {
            "score_rules": self.score_rules,
            "campaigns": self.campaigns,
            "sales_reps": self.sales_reps,
            "companies": self.companies,
            "contacts": self.contacts,
            "leads": self.leads,
            "activities": self.activities,
            "consents": self.consents,
            "consent_histories": self.consent_histories,
            "duplicate_relationships": self.duplicate_relationships,
            "opportunities": self.opportunities,
            "stage_histories": self.stage_histories,
            "tasks": self.tasks,
        }

    def generate_score_rules(self):
        """Generates lead scoring rule versions."""
        self.score_rules = [
            {
                "id": generate_score_rule_id(1),
                "rule_version": "v1.0.0",
                "fit_weight": 0.40,
                "intent_weight": 0.35,
                "engagement_weight": 0.25,
                "is_active": True,
                "description": "Standard corporate baseline rule: 40% Fit, 35% Intent, 25% Engagement",
                "effective_start_date": datetime(2025, 1, 1),
                "effective_end_date": None,
                "created_at": datetime(2025, 1, 1),
            },
            {
                "id": generate_score_rule_id(2),
                "rule_version": "v0.9.0",
                "fit_weight": 0.50,
                "intent_weight": 0.30,
                "engagement_weight": 0.20,
                "is_active": False,
                "description": "Legacy 2024 rule: heavy enterprise firmographic focus",
                "effective_start_date": datetime(2024, 1, 1),
                "effective_end_date": datetime(2024, 12, 31),
                "created_at": datetime(2024, 1, 1),
            },
        ]

    def generate_campaigns(self):
        """Generates realistic marketing campaigns."""
        campaign_types = ["Webinar", "Whitepaper", "Product Launch", "Email Blast", "Search Ads", "Partner Co-Marketing"]
        channels = ["Web", "Email", "Social", "Search", "Event"]
        names = [
            "Q1 Cloud Summit", "Enterprise AI Webinar", "DevSecOps Whitepaper",
            "NextGen Security Launch", "Global Analytics Forum", "Spring Inbound Campaign",
            "Tech Leaders Executive Breakfast", "Cloud Migration Masterclass", "Automated Ops Showcase",
            "AI Innovation Series", "EMEA Enterprise Roundtable", "APAC Digital Transformation Expo"
        ]

        count = self.config["num_campaigns"]
        for i in range(1, count + 1):
            start = date(2025, random.randint(1, 12), random.randint(1, 28))
            duration = random.randint(30, 90)
            end = start + timedelta(days=duration)
            self.campaigns.append({
                "id": generate_campaign_id(i),
                "name": f"{names[(i - 1) % len(names)]} {2025 if i <= 12 else 2026}",
                "campaign_type": random.choice(campaign_types),
                "channel": random.choice(channels),
                "budget": round(random.uniform(5000, 100000), 2),
                "start_date": start,
                "end_date": end,
                "target_territory": random.choice(VALID_TERRITORIES),
                "target_product": random.choice(VALID_PRODUCTS),
                "status": "Active" if end >= date(2026, 1, 1) else "Completed",
                "created_at": datetime(start.year, start.month, start.day, 9, 0, 0),
            })

    def generate_sales_reps(self):
        """Generates sales representatives with territories, products, capacity."""
        reps_count = self.config["num_sales_reps"]
        rep_names = [
            "Marcus Vance", "Elena Rostova", "Hiroshi Tanaka", "Camila Santos",
            "David Chen", "Sarah Jenkins", "Amara Okafor", "Liam O'Connor",
            "Sophia Martinez", "Julian Meyer", "Aisha Al-Mansoor", "Lucas Silva",
            "Priya Sharma", "Benjamin Becker", "Chloe Dubois", "Klaus Fischer"
        ]

        for i in range(1, reps_count + 1):
            territory = VALID_TERRITORIES[(i - 1) % len(VALID_TERRITORIES)]
            product = VALID_PRODUCTS[(i - 1) % len(VALID_PRODUCTS)]
            name = rep_names[(i - 1) % len(rep_names)] if i <= len(rep_names) else f"{self.fake.first_name()} {self.fake.last_name()}"
            clean_name = name.lower().replace(' ', '.').replace("'", "")
            self.sales_reps.append({
                "id": generate_sales_rep_id(i),
                "name": name,
                "email": f"{clean_name}{i}@smartlead.ai",
                "territory": territory,
                "product_specialization": product,
                "is_active": True if i % 15 != 0 else False,  # 93% active
                "capacity": random.choice([40, 50, 60, 75]),
                "current_load": 0,  # Will be calculated dynamically
                "created_at": datetime(2025, 1, 15, 8, 30, 0),
                "updated_at": datetime(2025, 1, 15, 8, 30, 0),
            })

    def generate_companies(self):
        """Generates realistic B2B companies with firmographics."""
        industries = [
            "Technology", "Financial Services", "Healthcare",
            "Manufacturing", "Retail", "Professional Services"
        ]
        industry_weights = [0.25, 0.20, 0.18, 0.15, 0.12, 0.10]

        territory_weights = [0.45, 0.30, 0.15, 0.10]
        countries_by_terr = {
            "North America": ["United States", "Canada"],
            "EMEA": ["United Kingdom", "Germany", "France", "Netherlands", "Sweden"],
            "APAC": ["Singapore", "Australia", "Japan", "India"],
            "LATAM": ["Brazil", "Mexico", "Colombia", "Chile"]
        }

        count = self.config["num_companies"]
        for i in range(1, count + 1):
            industry = random.choices(industries, weights=industry_weights)[0]
            territory = random.choices(VALID_TERRITORIES, weights=territory_weights)[0]
            country = random.choice(countries_by_terr[territory])

            # Tier and employee counts
            tier_choice = random.choices(["Enterprise", "Mid-Market", "SMB"], weights=[0.20, 0.55, 0.25])[0]
            if tier_choice == "Enterprise":
                emp_count = random.randint(1000, 25000)
                revenue = round(random.uniform(55_000_000, 1_500_000_000), 2)
            elif tier_choice == "Mid-Market":
                emp_count = random.randint(100, 999)
                revenue = round(random.uniform(5_000_000, 50_000_000), 2)
            else:
                emp_count = random.randint(10, 99)
                revenue = round(random.uniform(250_000, 4_900_000), 2)

            company_name = self.fake.company()
            # Clean domain
            domain = company_name.lower().replace(",", "").replace(".", "").replace(" ", "").replace("-", "")[:18] + ".com"

            created_date = datetime(2025, 1, 1) + timedelta(days=random.randint(0, 360), hours=random.randint(0, 23))

            self.companies.append({
                "id": generate_company_id(i),
                "name": company_name,
                "domain": domain,
                "industry": industry,
                "employee_count": emp_count,
                "annual_revenue": revenue,
                "country": country,
                "territory": territory,
                "tier": tier_choice,
                "created_at": created_date,
                "updated_at": created_date,
            })

    def generate_contacts(self):
        """Generates business contacts tied to companies."""
        seniorities = ["C-Level", "VP", "Director", "Manager", "Individual"]
        sen_weights = [0.15, 0.20, 0.30, 0.25, 0.10]

        departments = ["Information Technology", "Engineering", "Operations", "Finance", "Sales", "Marketing"]

        job_titles_by_seniority = {
            "C-Level": ["Chief Technology Officer", "Chief Information Officer", "Chief Executive Officer", "Chief Security Officer"],
            "VP": ["VP of Engineering", "VP of Enterprise Infrastructure", "VP of Product Strategy", "VP of IT Operations"],
            "Director": ["Director of Cloud Architecture", "Director of IT Security", "Director of Data Engineering"],
            "Manager": ["IT Operations Manager", "Infrastructure Manager", "Security Lead", "DevOps Manager"],
            "Individual": ["Senior Cloud Architect", "Enterprise Systems Engineer", "Data Engineer", "Technical Specialist"],
        }

        count = self.config["num_contacts"]
        companies_count = len(self.companies)

        for i in range(1, count + 1):
            # Deterministically assign company
            company_idx = (i - 1) % companies_count
            company = self.companies[company_idx]

            first_name = self.fake.first_name()
            last_name = self.fake.last_name()
            domain = company["domain"]
            email = f"{first_name.lower()}.{last_name.lower()}@{domain}"
            raw_phone = f"+1-{random.randint(200,999)}-{random.randint(200,999)}-{random.randint(1000,9999)}"
            norm_phone = normalize_phone(raw_phone)

            seniority = random.choices(seniorities, weights=sen_weights)[0]
            title = random.choice(job_titles_by_seniority[seniority])
            dept = random.choice(departments)

            created_date = company["created_at"] + timedelta(days=random.randint(0, 30))

            self.contacts.append({
                "id": generate_contact_id(i),
                "company_id": company["id"],
                "first_name": first_name,
                "last_name": last_name,
                "email": email,
                "phone": raw_phone,
                "normalized_phone": norm_phone,
                "job_title": title,
                "seniority_level": seniority,
                "department": dept,
                "is_primary": (i % 2 == 1),
                "created_at": created_date,
                "updated_at": created_date,
            })

    def generate_leads_and_activities(self):
        """Generates leads and associated activity touchpoints."""
        lead_sources = [
            "Website", "Inbound Form", "Referral", "Event",
            "Organic Search", "Paid Campaign", "Outbound"
        ]
        source_weights = [0.25, 0.20, 0.15, 0.15, 0.10, 0.10, 0.05]

        count = self.config["num_leads"]
        contacts_count = len(self.contacts)
        campaigns_count = len(self.campaigns)
        act_counter = 1

        for i in range(1, count + 1):
            contact_idx = (i - 1) % contacts_count
            contact = self.contacts[contact_idx]
            # Lookup parent company
            company_id = contact["company_id"]
            company_idx = int(company_id.split("-")[1]) - 1
            company = self.companies[company_idx]

            lead_id = generate_lead_id(i)
            lead_source = random.choices(lead_sources, weights=source_weights)[0]
            product_interest = random.choice(VALID_PRODUCTS)
            territory = company["territory"]

            campaign_id = None
            if i % 3 != 0 and campaigns_count > 0:
                campaign_id = self.campaigns[(i - 1) % campaigns_count]["id"]

            created_at = contact["created_at"] + timedelta(days=random.randint(1, 45), hours=random.randint(1, 12))

            # Simulate activities for this lead prior to scoring
            lead_activities = []
            num_activities = random.choices([1, 2, 3, 4, 6, 8, 12], weights=[0.15, 0.20, 0.25, 0.20, 0.10, 0.07, 0.03])[0]

            act_types = ["Page View", "Pricing View", "Whitepaper Download", "Webinar Attend", "Demo Request", "Email Open", "Email Click"]
            act_weights = [0.30, 0.15, 0.15, 0.10, 0.10, 0.12, 0.08]

            for a_idx in range(1, num_activities + 1):
                act_id = generate_activity_id(lead_id, a_idx)
                act_type = random.choices(act_types, weights=act_weights)[0]
                channel = "Web" if "Page" in act_type or "Pricing" in act_type else ("Email" if "Email" in act_type else "Event")

                act_time = created_at + timedelta(days=random.randint(0, 30), hours=random.randint(1, 10))

                activity_dict = {
                    "id": act_id,
                    "lead_id": lead_id,
                    "activity_type": act_type,
                    "channel": channel,
                    "intent_weight": 40.0 if act_type == "Demo Request" else (25.0 if act_type == "Pricing View" else 15.0),
                    "engagement_weight": 15.0 if act_type == "Email Click" else 10.0,
                    "activity_date": act_time,
                    "metadata_json": f'{{"url": "/solutions/{product_interest.lower().replace(" ", "-")}", "device": "Desktop"}}',
                    "is_post_conversion": False,
                    "created_at": act_time,
                }
                lead_activities.append(activity_dict)
                self.activities.append(activity_dict)
                act_counter += 1

            # Compute Lead Score deterministically
            eval_res = self.scoring_engine.evaluate_lead_full(
                lead_id=lead_id,
                company_data=company,
                contact_data=contact,
                lead_data={"lead_source": lead_source, "reference_date": datetime(2026, 1, 15)},
                activities=lead_activities,
                converted_date=None,
                filter_post_conversion=True,
            )

            # Assign Representative deterministically using SalesRoutingEngine
            assigned_rep, r_status, r_explanation = SalesRoutingEngine.route_lead(
                lead_territory=territory,
                product_interest=product_interest,
                available_reps=self.sales_reps,
            )
            assigned_rep_id = assigned_rep["id"] if assigned_rep else None
            if assigned_rep:
                assigned_rep["current_load"] = assigned_rep.get("current_load", 0) + 1

            # Determine lifecycle status based on score
            score = eval_res["lead_score"]
            if score >= 75:
                status = random.choices(["Qualified", "Working", "Contacted"], weights=[0.60, 0.25, 0.15])[0]
            elif score >= 50:
                status = random.choices(["Working", "Contacted", "Qualified"], weights=[0.50, 0.35, 0.15])[0]
            else:
                status = random.choices(["New", "Contacted", "Unqualified"], weights=[0.40, 0.40, 0.20])[0]

            is_converted = False
            converted_date = None

            # Generate duplicate flag for a small subset (~3%)
            is_duplicate = False
            canonical_lead_id = None
            if i > 50 and i % 30 == 0:
                is_duplicate = True
                target_idx = max(0, i - 26)
                target_lead = self.leads[target_idx]
                canonical_lead_id = target_lead["id"]
                # Reuse target lead's contact and company for genuine identity match
                contact = next((c for c in self.contacts if c["id"] == target_lead["contact_id"]), contact)
                company = next((co for co in self.companies if co["id"] == target_lead["company_id"]), company)
                territory = company["territory"]

                # Derive relationship using DeduplicationService
                match_meta = DeduplicationService.compare_leads(
                    existing_lead=target_lead,
                    new_lead={"product_interest": product_interest, "created_at": created_at},
                    existing_contact=contact,
                    new_contact=contact,
                    existing_company=company,
                    new_company=company,
                ) or {
                    "match_type": "Exact",
                    "match_reason": f"Exact match on contact email {contact['email']}",
                    "similarity_score": 1.0,
                }

                self.duplicate_relationships.append({
                    "id": generate_duplicate_id(len(self.duplicate_relationships) + 1),
                    "primary_lead_id": canonical_lead_id,
                    "duplicate_lead_id": lead_id,
                    "match_type": match_meta.get("match_type", "Exact"),
                    "match_reason": match_meta.get("match_reason", f"Exact match on email: {contact['email']}"),
                    "similarity_score": match_meta.get("similarity_score", 1.0),
                    "status": "Detected",
                    "detected_at": created_at,
                })

            self.leads.append({
                "id": lead_id,
                "company_id": company["id"],
                "contact_id": contact["id"],
                "campaign_id": campaign_id,
                "assigned_rep_id": assigned_rep_id,
                "canonical_lead_id": canonical_lead_id,
                "lead_source": lead_source,
                "product_interest": product_interest,
                "territory": territory,
                "status": status,
                "fit_score": eval_res["fit_score"],
                "intent_score": eval_res["intent_score"],
                "engagement_score": eval_res["engagement_score"],
                "lead_score": score,
                "priority": eval_res["priority"],
                "is_duplicate": is_duplicate,
                "is_converted": is_converted,
                "converted_date": converted_date,
                "created_at": created_at,
                "updated_at": converted_date if converted_date else created_at,
            })

    def generate_consents(self):
        """Generates consent records for leads (Opt-In, Opt-Out, Pending)."""
        consent_statuses = ["Opt-In", "Opt-Out", "Pending"]
        weights = [0.80, 0.12, 0.08]

        for idx, lead in enumerate(self.leads, 1):
            status = random.choices(consent_statuses, weights=weights)[0]
            eff_date = lead["created_at"]
            opt_out_time = (eff_date + timedelta(days=random.randint(1, 10))) if status == "Opt-Out" else None

            self.consents.append({
                "id": generate_consent_id(idx),
                "lead_id": lead["id"],
                "contact_id": lead["contact_id"],
                "consent_status": status,
                "consent_type": "All",
                "channel": "Email",
                "effective_date": eff_date,
                "expiry_date": eff_date + timedelta(days=365) if status == "Opt-In" else None,
                "opt_out_timestamp": opt_out_time,
                "notes": "Marketing opt-out requested via unsubscribe link" if status == "Opt-Out" else "Standard explicit web form consent",
                "created_at": eff_date,
                "updated_at": opt_out_time if opt_out_time else eff_date,
            })

            if status == "Opt-Out":
                self.consent_histories.append({
                    "id": generate_consent_history_id(len(self.consent_histories) + 1),
                    "lead_id": lead["id"],
                    "old_status": "Opt-In",
                    "new_status": "Opt-Out",
                    "reason": "Unsubscribed from marketing communications",
                    "changed_at": opt_out_time or eff_date,
                })

    def generate_opportunities_and_stages(self):
        """Generates opportunities and complete StageHistory sequences."""
        target_opp_count = self.config["num_opportunities"]
        # Filter eligible leads: skip duplicate leads to avoid duplicate opportunity anomalies in baseline
        eligible_leads = [
            l for l in self.leads
            if not l.get("is_duplicate", False) and (l["status"] in {"Qualified", "Working"} or l["lead_score"] >= 65)
        ]

        if len(eligible_leads) < target_opp_count:
            eligible_leads = [l for l in self.leads if not l.get("is_duplicate", False)]

        opp_idx = 1
        converted_lead_ids = set()

        for lead in eligible_leads:
            if opp_idx > target_opp_count:
                break

            opp_id = generate_opportunity_id(opp_idx)
            val = round(random.uniform(15000, 250000), 2)
            creation_date = lead["created_at"] + timedelta(days=random.randint(5, 20))
            expected_close = creation_date + timedelta(days=random.randint(30, 90))

            # Determine stage outcome
            # High score leads have higher won probability
            score = lead["lead_score"]
            if score >= 80:
                stage = random.choices(["Won", "Negotiation", "Proposal", "Lost"], weights=[0.55, 0.25, 0.15, 0.05])[0]
            elif score >= 50:
                stage = random.choices(["Proposal", "Negotiation", "Won", "Lost"], weights=[0.40, 0.25, 0.20, 0.15])[0]
            else:
                stage = random.choices(["Lost", "Qualified", "New"], weights=[0.60, 0.25, 0.15])[0]

            won_lost_reason = None
            if stage == "Won":
                won_lost_reason = random.choice([
                    "Superior Product Fit", "Executive Champion Alignment",
                    "Strong ROI Proof of Concept", "Competitive Feature Superiority"
                ])
            elif stage == "Lost":
                won_lost_reason = random.choice([
                    "Budget Freeze", "Competitor Selected", "No Immediate Need", "Timing Postponed"
                ])

            # Generate Stage History progression and get exact final transition date
            final_trans_date = self._generate_stage_history_for_opp(opp_id, creation_date, stage)
            actual_close = final_trans_date if stage in {"Won", "Lost"} else None

            self.opportunities.append({
                "id": opp_id,
                "lead_id": lead["id"],
                "company_id": lead["company_id"],
                "assigned_rep_id": lead["assigned_rep_id"] or self.sales_reps[0]["id"],
                "canonical_opp_id": None,
                "opportunity_value": val,
                "currency": "USD",
                "current_stage": stage,
                "creation_date": creation_date,
                "expected_close_date": expected_close,
                "actual_close_date": actual_close,
                "won_lost_reason": won_lost_reason,
                "is_duplicate": False,
                "created_at": creation_date,
                "updated_at": actual_close if actual_close else final_trans_date,
            })

            # Reconcile lead conversion status with opportunity
            lead["is_converted"] = True
            lead["converted_date"] = creation_date
            lead["status"] = "Converted"
            converted_lead_ids.add(lead["id"])
            opp_idx += 1

        # Reconcile remaining leads that did not convert into opportunities
        for l in self.leads:
            if l["id"] not in converted_lead_ids:
                l["is_converted"] = False
                l["converted_date"] = None
                if l["status"] == "Converted":
                    l["status"] = "Qualified"

    def _generate_stage_history_for_opp(self, opp_id: str, start_date: datetime, final_stage: str) -> datetime:
        """Generates standard, valid sequential stage history entries and returns final transition date."""
        stage_sequence = ["New"]
        if final_stage == "New":
            pass
        elif final_stage == "Qualified":
            stage_sequence.extend(["Qualified"])
        elif final_stage == "Proposal":
            stage_sequence.extend(["Qualified", "Proposal"])
        elif final_stage == "Negotiation":
            stage_sequence.extend(["Qualified", "Proposal", "Negotiation"])
        elif final_stage == "Won":
            stage_sequence.extend(["Qualified", "Proposal", "Negotiation", "Won"])
        elif final_stage == "Lost":
            stage_sequence.extend(["Qualified", "Lost"])

        cur_date = start_date
        for s_idx in range(len(stage_sequence)):
            to_s = stage_sequence[s_idx]
            from_s = stage_sequence[s_idx - 1] if s_idx > 0 else None
            dur = random.randint(3, 14) if s_idx > 0 else 0
            cur_date = cur_date + timedelta(days=dur)

            hist_id = generate_stage_history_id(opp_id, s_idx + 1)
            self.stage_histories.append({
                "id": hist_id,
                "opportunity_id": opp_id,
                "from_stage": from_s,
                "to_stage": to_s,
                "stage_duration_days": dur,
                "transition_date": cur_date,
                "changed_by": "Automated Pipeline Engine",
                "is_valid_transition": True,
                "notes": f"Progressed from {from_s} to {to_s}",
                "created_at": cur_date,
            })
        return cur_date

    def generate_tasks(self):
        """Generates follow-up tasks adhering to consent status and priorities."""
        consent_map = {c["lead_id"]: c for c in self.consents}
        task_seq = 1

        for lead in self.leads:
            lead_id = lead["id"]
            consent = consent_map.get(lead_id)

            # Strict rule: DO NOT create contact tasks for opted-out or pending leads (only Opt-In)
            if not consent or consent["consent_status"] != "Opt-In":
                continue

            # Prioritize High and Medium leads
            score = lead["lead_score"]
            if score >= 50 or random.random() < 0.25:
                task_id = generate_task_id(lead_id, 1)
                task_type = "Discovery Call" if lead["priority"] == "High" else "Email Outreach"
                task_priority = "Urgent" if lead["priority"] == "High" else "Normal"
                due_date = lead["created_at"] + timedelta(days=2 if task_priority == "Urgent" else 5)

                t_status = random.choice(["Completed", "Pending", "In Progress"])
                comp_at = (due_date + timedelta(hours=random.randint(1, 24))) if t_status == "Completed" else None

                self.tasks.append({
                    "id": task_id,
                    "lead_id": lead_id,
                    "assigned_rep_id": lead["assigned_rep_id"] or self.sales_reps[0]["id"],
                    "task_type": task_type,
                    "priority": task_priority,
                    "due_date": due_date,
                    "status": t_status,
                    "blocked_reason": None,
                    "is_consent_verified": True,
                    "created_at": lead["created_at"],
                    "completed_at": comp_at,
                })
                task_seq += 1
