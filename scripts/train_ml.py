import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.core.database import SessionLocal
from backend.models.entities import Lead, Company, Contact, Activity
from ml.pipeline import MLEvaluationPipeline


def main():
    print("Extracting features from database for ML training & evaluation...")
    db = SessionLocal()
    try:
        leads = [l.__dict__ for l in db.query(Lead).all()]
        companies = [c.__dict__ for c in db.query(Company).all()]
        contacts = [con.__dict__ for con in db.query(Contact).all()]
        activities = [a.__dict__ for a in db.query(Activity).all()]

        pipeline = MLEvaluationPipeline()
        metrics = pipeline.run_training_and_evaluation(leads, companies, contacts, activities)

        print("\nML Evaluation Results (Held-out Test Set):")
        print(f"- Model: {metrics['model_type']}")
        print(f"- Accuracy:  {metrics['accuracy'] * 100:.2f}%")
        print(f"- Precision: {metrics['precision'] * 100:.2f}%")
        print(f"- Recall:    {metrics['recall'] * 100:.2f}%")
        print(f"- F1-Score:  {metrics['f1_score'] * 100:.2f}%")
        print(f"- ROC-AUC:   {metrics['roc_auc']:.4f}")
        print(f"- Confusion Matrix: {metrics['confusion_matrix']}")
        print("\nTop 5 Predictive Signals:")
        for feat, coef in list(metrics["feature_coefficients"].items())[:5]:
            print(f"  * {feat}: {coef:+.4f}")
        print("\nEvaluation artifacts and documentation generated.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
