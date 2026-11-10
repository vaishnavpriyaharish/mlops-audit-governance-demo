"""training_pipeline.py

Pipeline: Model Training & Governance Validation Gate
Purpose: Simulates data preparation, model training, metric evaluation,
         automated validation against quality gates, and model registration.
"""

from __future__ import annotations

import argparse
import logging
import sys
import uuid
from typing import Any, Dict

from src.audit_logger import AuditEvent, MLOpsAuditLogger
from src.model_registry import ModelMetadata, ModelRegistryManager, ModelStage

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s - %(message)s")
logger = logging.getLogger("TrainingPipeline")


def run_training_pipeline(experiment_name: str, validate_gates: bool = True) -> Dict[str, Any]:
    """Execute end-to-end model training, quality gate checks, and audit logging."""
    logger.info("Starting MLOps training pipeline for experiment: %s", experiment_name)

    audit_logger = MLOpsAuditLogger()
    registry = ModelRegistryManager()

    # 1. Simulated Model Training & Evaluation
    logger.info("Executing training step across dataset: data/silver_features.parquet")
    metrics = {
        "rmse": 14.82,
        "mae": 10.45,
        "mape": 0.086,  # 8.6% error rate
        "r2_score": 0.912,
    }

    # 2. Automated Quality Gate Check (e.g. MAPE < 15%)
    MAPE_THRESHOLD = 0.15
    passed_gate = metrics["mape"] <= MAPE_THRESHOLD

    # 3. Log Audit Trail
    event = AuditEvent(
        event_id=f"evt_{uuid.uuid4().hex[:8]}",
        event_type="TRAINING_RUN",
        model_name="workforce-capacity-forecaster",
        model_version="1.2.0",
        actor="github-actions-runner",
        environment="dev",
        details={
            "experiment": experiment_name,
            "metrics": metrics,
            "gate_threshold": MAPE_THRESHOLD,
            "hyperparameters": {"n_estimators": 150, "max_depth": 6, "learning_rate": 0.05},
        },
        compliance_passed=passed_gate,
    )
    audit_logger.log_event(event)

    # 4. Register to Candidate Pool
    metadata = ModelMetadata(
        model_name="workforce-capacity-forecaster",
        model_version="1.2.0",
        framework="xgboost-1.7.5",
        training_dataset_uri="s3://enterprise-lakehouse/silver/workforce/v1",
        created_by="mlops-service-principal",
        business_unit="Enterprise Field Operations",
        evaluation_metrics=metrics,
        compliance_approved=passed_gate,
    )

    registration_record = registry.register_model_version(
        model_name="workforce-capacity-forecaster",
        artifact_uri="mlflow-artifacts:/models/workforce-capacity-forecaster/1.2.0",
        metadata=metadata,
    )

    logger.info("Training pipeline completed successfully. Model registered.")
    return registration_record


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="MLOps Training & Governance Pipeline")
    parser.add_argument("--experiment-name", type=str, default="governance-audit-demo")
    parser.add_argument("--validate-gates", action="store_true")
    args = parser.parse_args()

    run_training_pipeline(args.experiment_name, args.validate_gates)
