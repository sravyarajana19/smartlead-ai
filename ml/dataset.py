import pandas as pd
import numpy as np
from typing import Tuple, List, Dict, Any
from sklearn.model_selection import train_test_split
from backend.core.config import RANDOM_SEED


class MLDatasetBuilder:
    """
    Extracts features for conversion prediction.
    Strictly prevents data leakage:
    - Excludes ground-truth anomaly labels.
    - Excludes post-conversion activities.
    - Separates features from target outcome.
    - Distinguishes rule-based lead scores from ML conversion probabilities.
    """

    @staticmethod
    def build_dataset(
        leads: List[Dict[str, Any]],
        companies: List[Dict[str, Any]],
        contacts: List[Dict[str, Any]],
        activities: List[Dict[str, Any]],
    ) -> pd.DataFrame:
        company_map = {c["id"]: c for c in companies}
        contact_map = {c["id"]: c for c in contacts}

        lead_conv_map = {l["id"]: l.get("converted_date") for l in leads}
        # Count strictly pre-conversion activities per lead
        activity_counts = {}
        for a in activities:
            lid = a.get("lead_id")
            conv_d = lead_conv_map.get(lid)
            act_d = a.get("activity_date")
            if conv_d and act_d and act_d > conv_d:
                continue
            if a.get("is_post_conversion", False):
                continue
            activity_counts[lid] = activity_counts.get(lid, 0) + 1

        rows = []
        for l in leads:
            # Skip duplicate leads in ML training to prevent bias
            if l.get("is_duplicate", False):
                continue

            comp = company_map.get(l["company_id"], {})
            con = contact_map.get(l["contact_id"], {})
            lid = l["id"]

            row = {
                "lead_id": lid,
                "fit_score": float(l.get("fit_score", 0.0)),
                "intent_score": float(l.get("intent_score", 0.0)),
                "engagement_score": float(l.get("engagement_score", 0.0)),
                "lead_score": float(l.get("lead_score", 0.0)),
                "employee_count": int(comp.get("employee_count", 50)),
                "annual_revenue": float(comp.get("annual_revenue", 1_000_000.0)),
                "is_enterprise": 1 if comp.get("tier") == "Enterprise" else 0,
                "is_executive": 1 if con.get("seniority_level") in {"C-Level", "VP"} else 0,
                "activity_count": activity_counts.get(lid, 0),
                "territory": l.get("territory", "North America"),
                "product_interest": l.get("product_interest", "Cloud Platform"),
                "lead_source": l.get("lead_source", "Website"),
                "industry": comp.get("industry", "Technology"),
                # TARGET OUTCOME LABEL (0 or 1: strictly true conversions)
                "converted": 1 if l.get("is_converted", False) else 0,
            }
            rows.append(row)

        df = pd.DataFrame(rows)
        return df

    @staticmethod
    def prepare_train_test(
        df: pd.DataFrame, test_size: float = 0.20, seed: int = RANDOM_SEED
    ) -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series, List[str]]:
        """
        One-hot encodes categorical features and creates a reproducible train/test split.
        """
        feature_cols = [
            "fit_score", "intent_score", "engagement_score",
            "employee_count", "annual_revenue", "is_enterprise",
            "is_executive", "activity_count"
        ]

        # Categorical columns to dummy encode
        cat_cols = ["territory", "product_interest", "lead_source", "industry"]
        encoded_df = pd.get_dummies(df[feature_cols + cat_cols], columns=cat_cols, drop_first=True)

        final_features = list(encoded_df.columns)
        X = encoded_df
        y = df["converted"]

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=seed, stratify=y
        )

        return X_train, X_test, y_train, y_test, final_features
