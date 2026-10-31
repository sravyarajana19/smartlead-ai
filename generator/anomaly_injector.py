import json
import csv
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Tuple
from generator.id_generator import (
    generate_anomaly_id,
    generate_task_id,
    generate_activity_id,
    generate_opportunity_id,
    generate_stage_history_id,
)
from backend.core.config import GROUND_TRUTH_DIR


class AnomalyInjector:
    """
    Deliberately injects labelled anomalies for the 5 required exception scenarios:
    - CASE 1: Opted-out lead contacted (consent violation).
    - CASE 2: Lead score uses activity after conversion (temporal leakage).
    - CASE 3: Lead assigned to rep outside territory (routing violation).
    - CASE 4: Duplicate lead creates duplicate opportunity (duplicate opp).
    - CASE 5: Stage history contains missing transitions (skipped pipeline stages).

    Outputs strictly isolated ground_truth.csv and ground_truth.json datasets.
    """

    def __init__(self, data_records: Dict[str, List[Dict[str, Any]]]):
        self.data = data_records
        self.anomalies: List[Dict[str, Any]] = []

    def inject_all_cases(self, count_per_case: int = 5) -> Tuple[Dict[str, List[Dict[str, Any]]], List[Dict[str, Any]]]:
        """Injects all 5 cases deterministically."""
        self.inject_case_1_consent_violations(count=count_per_case)
        self.inject_case_2_temporal_leakage(count=count_per_case)
        self.inject_case_3_routing_violations(count=count_per_case)
        self.inject_case_4_duplicate_opportunities(count=count_per_case)
        self.inject_case_5_missing_stage_transitions(count=count_per_case)

        # Save ground truth files
        self.export_ground_truth()

        return self.data, self.anomalies

    def inject_case_1_consent_violations(self, count: int = 5):
        """
        CASE 1: Opted-out lead is contacted.
        Injects contact tasks for leads that explicitly opted out.
        """
        opt_out_consents = [c for c in self.data["consents"] if c["consent_status"] == "Opt-Out"]
        leads_dict = {l["id"]: l for l in self.data["leads"]}

        for i in range(min(count, len(opt_out_consents))):
            consent = opt_out_consents[i]
            lead_id = consent["lead_id"]
            lead = leads_dict[lead_id]

            task_id = generate_task_id(lead_id, 99)  # Distinct high sequence for anomaly
            created_time = consent["opt_out_timestamp"] + timedelta(days=2) if consent.get("opt_out_timestamp") else lead["created_at"] + timedelta(days=5)

            # Illegitimate contact task
            task = {
                "id": task_id,
                "lead_id": lead_id,
                "assigned_rep_id": lead["assigned_rep_id"] or self.data["sales_reps"][0]["id"],
                "task_type": "Discovery Call",
                "priority": "Urgent",
                "due_date": created_time + timedelta(days=1),
                "status": "Pending",
                "blocked_reason": "UNAUTHORIZED_OUTREACH_POST_OPTOUT",
                "is_consent_verified": False,
                "created_at": created_time,
                "completed_at": None,
            }
            self.data["tasks"].append(task)

            anomaly_id = generate_anomaly_id(len(self.anomalies) + 1)
            self.anomalies.append({
                "id": anomaly_id,
                "anomaly_id": anomaly_id,
                "entity_type": "Task",
                "entity_id": task_id,
                "issue_type": "CASE_1_CONSENT_VIOLATION",
                "severity": "Critical",
                "ground_truth_label": "OPT_OUT_CONTACTED",
                "expected_decision": "BLOCK_OUTREACH",
                "actual_decision": "CONTACT_ATTEMPTED",
                "explanation": (
                    f"Lead {lead_id} opted out at {consent.get('opt_out_timestamp')}. "
                    f"Outreach task {task_id} was generated in direct violation of marketing consent policy."
                ),
                "detected_at": datetime(2026, 1, 20, 12, 0, 0),
                "resolution_status": "Open",
            })

    def inject_case_2_temporal_leakage(self, count: int = 5):
        """
        CASE 2: A lead score uses an activity that happened after conversion.
        Injects post-conversion activities flagged with is_post_conversion=True.
        """
        converted_leads = [l for l in self.data["leads"] if l["is_converted"] and l["converted_date"]]

        for i in range(min(count, len(converted_leads))):
            lead = converted_leads[i]
            lead_id = lead["id"]
            conv_date = lead["converted_date"]

            # Activity that took place 10 days AFTER conversion
            leakage_date = conv_date + timedelta(days=10)
            act_id = generate_activity_id(lead_id, 99)

            activity = {
                "id": act_id,
                "lead_id": lead_id,
                "activity_type": "Demo Request",
                "channel": "Web",
                "intent_weight": 40.0,
                "engagement_weight": 20.0,
                "activity_date": leakage_date,
                "metadata_json": '{"leakage": true, "note": "Post-conversion activity leakage injected for testing"}',
                "is_post_conversion": True,
                "created_at": leakage_date,
            }
            self.data["activities"].append(activity)

            anomaly_id = generate_anomaly_id(len(self.anomalies) + 1)
            self.anomalies.append({
                "id": anomaly_id,
                "anomaly_id": anomaly_id,
                "entity_type": "Activity",
                "entity_id": act_id,
                "issue_type": "CASE_2_TEMPORAL_LEAKAGE",
                "severity": "High",
                "ground_truth_label": "POST_CONVERSION_ACTIVITY",
                "expected_decision": "EXCLUDE_FROM_SCORING",
                "actual_decision": "POST_CONVERSION_INCLUDED",
                "explanation": (
                    f"Activity {act_id} occurred on {leakage_date.isoformat()}, which is after lead conversion "
                    f"date {conv_date.isoformat()}. Using this activity in scoring creates temporal data leakage."
                ),
                "detected_at": datetime(2026, 1, 20, 12, 0, 0),
                "resolution_status": "Open",
            })

    def inject_case_3_routing_violations(self, count: int = 5):
        """
        CASE 3: A lead is assigned to a representative outside the lead's territory.
        Deliberately switches assigned_rep_id to an active rep in an incompatible territory.
        """
        eligible_leads = [l for l in self.data["leads"] if l["assigned_rep_id"]]
        reps = self.data["sales_reps"]

        for i in range(min(count, len(eligible_leads))):
            lead = eligible_leads[i + 10]  # Pick distinct indices
            lead_territory = lead["territory"]

            # Find a rep in a different territory
            mismatched_reps = [r for r in reps if r["territory"] != lead_territory and r["is_active"]]
            if not mismatched_reps:
                continue

            chosen_rep = mismatched_reps[0]
            original_rep_id = lead["assigned_rep_id"]
            lead["assigned_rep_id"] = chosen_rep["id"]

            anomaly_id = generate_anomaly_id(len(self.anomalies) + 1)
            self.anomalies.append({
                "id": anomaly_id,
                "anomaly_id": anomaly_id,
                "entity_type": "Lead",
                "entity_id": lead["id"],
                "issue_type": "CASE_3_ROUTING_VIOLATION",
                "severity": "High",
                "ground_truth_label": "TERRITORY_MISMATCH",
                "expected_decision": f"ASSIGN_TO_{lead_territory.upper().replace(' ', '_')}_REP",
                "actual_decision": f"ASSIGNED_TO_{chosen_rep['territory'].upper().replace(' ', '_')}_REP",
                "explanation": (
                    f"Lead {lead['id']} is in territory '{lead_territory}' but was erroneously assigned to "
                    f"representative {chosen_rep['name']} ({chosen_rep['id']}) in territory '{chosen_rep['territory']}'."
                ),
                "detected_at": datetime(2026, 1, 20, 12, 0, 0),
                "resolution_status": "Open",
            })

    def inject_case_4_duplicate_opportunities(self, count: int = 5):
        """
        CASE 4: A duplicate lead creates a duplicate opportunity.
        Injects a second opportunity for a duplicate lead pointing to the same company.
        """
        dup_relations = self.data.get("duplicate_relationships", [])
        opps = self.data["opportunities"]

        for i in range(min(count, len(dup_relations))):
            rel = dup_relations[i]
            primary_lead_id = rel["primary_lead_id"]
            duplicate_lead_id = rel["duplicate_lead_id"]

            # Find opportunity associated with primary lead
            primary_opps = [o for o in opps if o["lead_id"] == primary_lead_id]
            if not primary_opps:
                # Use first opp as reference
                ref_opp = opps[0]
            else:
                ref_opp = primary_opps[0]

            dup_opp_id = generate_opportunity_id(len(opps) + 1)
            dup_opp = {
                "id": dup_opp_id,
                "lead_id": duplicate_lead_id,
                "company_id": ref_opp["company_id"],
                "assigned_rep_id": ref_opp["assigned_rep_id"],
                "canonical_opp_id": ref_opp["id"],
                "opportunity_value": ref_opp["opportunity_value"],
                "currency": "USD",
                "current_stage": "New",
                "creation_date": ref_opp["creation_date"] + timedelta(days=2),
                "expected_close_date": ref_opp["expected_close_date"],
                "actual_close_date": None,
                "won_lost_reason": None,
                "is_duplicate": True,
                "created_at": ref_opp["creation_date"] + timedelta(days=2),
                "updated_at": ref_opp["creation_date"] + timedelta(days=2),
            }
            self.data["opportunities"].append(dup_opp)

            anomaly_id = generate_anomaly_id(len(self.anomalies) + 1)
            self.anomalies.append({
                "id": anomaly_id,
                "anomaly_id": anomaly_id,
                "entity_type": "Opportunity",
                "entity_id": dup_opp_id,
                "issue_type": "CASE_4_DUPLICATE_OPPORTUNITY",
                "severity": "Medium",
                "ground_truth_label": "DUPLICATE_OPPORTUNITY",
                "expected_decision": "PRESERVE_AND_FLAG_FOR_MERGE",
                "actual_decision": "DUPLICATE_OPPORTUNITY_CREATED",
                "explanation": (
                    f"Opportunity {dup_opp_id} was generated from duplicate lead {duplicate_lead_id}, "
                    f"duplicating canonical opportunity {ref_opp['id']} for company {ref_opp['company_id']}."
                ),
                "detected_at": datetime(2026, 1, 20, 12, 0, 0),
                "resolution_status": "Open",
            })

    def inject_case_5_missing_stage_transitions(self, count: int = 5):
        """
        CASE 5: Stage history contains missing transitions.
        Direct leap from 'New' straight to 'Won' skipping Qualified, Proposal, Negotiation.
        """
        won_opps = [o for o in self.data["opportunities"] if o["current_stage"] == "Won" and not o["is_duplicate"]]

        for i in range(min(count, len(won_opps))):
            opp = won_opps[i]
            opp_id = opp["id"]

            # Remove existing legitimate intermediate stage histories for this opp
            self.data["stage_histories"] = [h for h in self.data["stage_histories"] if h["opportunity_id"] != opp_id]

            # Inject single invalid leap: New -> Won
            hist_id = generate_stage_history_id(opp_id, 99)
            invalid_hist = {
                "id": hist_id,
                "opportunity_id": opp_id,
                "from_stage": "New",
                "to_stage": "Won",
                "stage_duration_days": 1,
                "transition_date": opp["creation_date"] + timedelta(days=1),
                "changed_by": "Rogue Automation Script",
                "is_valid_transition": False,
                "notes": "INVALID_DIRECT_TRANSITION: Skipped Qualified, Proposal, and Negotiation stages.",
                "created_at": opp["creation_date"] + timedelta(days=1),
            }
            self.data["stage_histories"].append(invalid_hist)

            anomaly_id = generate_anomaly_id(len(self.anomalies) + 1)
            self.anomalies.append({
                "id": anomaly_id,
                "anomaly_id": anomaly_id,
                "entity_type": "StageHistory",
                "entity_id": opp_id,
                "issue_type": "CASE_5_MISSING_STAGE_TRANSITION",
                "severity": "High",
                "ground_truth_label": "MISSING_STAGE_TRANSITIONS",
                "expected_decision": "REJECT_INVALID_TRANSITION",
                "actual_decision": "SKIPPED_INTERMEDIATE_STAGES",
                "explanation": (
                    f"Opportunity {opp_id} jumped directly from 'New' to 'Won' without completing "
                    f"qualification, proposal, or negotiation milestones."
                ),
                "detected_at": datetime(2026, 1, 20, 12, 0, 0),
                "resolution_status": "Open",
            })

    def export_ground_truth(self):
        """Saves ground truth records to CSV and JSON."""
        GROUND_TRUTH_DIR.mkdir(parents=True, exist_ok=True)
        csv_path = GROUND_TRUTH_DIR / "ground_truth.csv"
        json_path = GROUND_TRUTH_DIR / "ground_truth.json"

        fieldnames = [
            "anomaly_id", "entity_type", "entity_id", "issue_type",
            "severity", "ground_truth_label", "expected_decision",
            "actual_decision", "explanation"
        ]

        # Write CSV
        with open(csv_path, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
            writer.writeheader()
            for a in self.anomalies:
                writer.writerow(a)

        # Write JSON
        with open(json_path, mode="w", encoding="utf-8") as f:
            json.dump(self.anomalies, f, indent=2, default=str)
