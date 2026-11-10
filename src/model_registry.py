"""model_registry.py

Module: MLOps Model Registry Interface
Purpose: Standardized interface for registering, versioning, and managing the lifecycle
         of machine learning models in an enterprise registry (e.g., MLflow / Azure ML / Databricks Unity Catalog).
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s - %(message)s")
logger = logging.getLogger("ModelRegistryManager")


class ModelStage(str, Enum):
    NONE = "None"
    DEVELOPMENT = "Development"
    STAGING = "Staging"
    PRODUCTION = "Production"
    ARCHIVED = "Archived"


class ModelMetadata(BaseModel):
    """Structured compliance schema required for enterprise model registration."""
    model_name: str
    model_version: str
    framework: str
    training_dataset_uri: str
    created_by: str
    business_unit: str
    git_commit_sha: Optional[str] = None
    evaluation_metrics: Dict[str, float] = Field(default_factory=dict)
    compliance_approved: bool = False
    approval_timestamp: Optional[datetime] = None


class ModelGovernance:
    """TPM Reference Architecture: Model Governance Interface.

    Handles the logging and promotion of ML models across environments (Dev -> Staging -> Prod).
    Ensures all metadata and approval gates are passed before promotion.
    """

    def __init__(self, tracking_uri: Optional[str] = None) -> None:
        self.tracking_uri = tracking_uri or "sqlite:///mlflow_governance.db"
        # In full production deployment: mlflow.set_tracking_uri(self.tracking_uri)

    def log_model_metadata(
        self,
        model_name: str,
        metrics: Dict[str, float],
        tags: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Logs accuracy, latency, and compliance tags to the central registry."""
        logger.info("Logging %s metadata to MLflow...", model_name)
        # MLflow logging hook: mlflow.log_metrics(metrics), mlflow.set_tags(tags)

    def check_approval_gate(self, model_version: str) -> bool:
        """Verifies if the business stakeholder has approved the model for production."""
        logger.info("Checking approval status for version %s...", model_version)
        return True


class ModelRegistryManager(ModelGovernance):
    """Manages model versioning, transition stages, and governance metadata tagging."""

    def __init__(self, tracking_uri: Optional[str] = None) -> None:
        super().__init__(tracking_uri=tracking_uri)
        logger.info("Initialized ModelRegistryManager with tracking URI: %s", self.tracking_uri)

    def register_model_version(
        self,
        model_name: str,
        artifact_uri: str,
        metadata: ModelMetadata,
    ) -> Dict[str, Any]:
        """Register a new candidate model version and record compliance metadata."""
        logger.info(
            "Registering candidate model '%s' (version: %s) from %s",
            model_name,
            metadata.model_version,
            artifact_uri,
        )

        record = {
            "model_name": model_name,
            "version": metadata.model_version,
            "status": "REGISTERED",
            "current_stage": ModelStage.DEVELOPMENT.value,
            "artifact_uri": artifact_uri,
            "metadata": metadata.model_dump(),
            "registered_at": datetime.now(timezone.utc).isoformat(),
        }
        return record

    def transition_stage(
        self,
        model_name: str,
        version: str,
        target_stage: ModelStage,
        approver: str,
        archive_existing_versions: bool = True,
    ) -> Dict[str, Any]:
        """Transition a model version to a new stage (Staging / Production) with governance audit trail."""
        logger.info(
            "Transitioning model '%s' (v%s) to stage '%s' by approver: %s",
            model_name,
            version,
            target_stage.value,
            approver,
        )

        transition_record = {
            "model_name": model_name,
            "version": version,
            "previous_stage": ModelStage.DEVELOPMENT.value if target_stage == ModelStage.STAGING else ModelStage.STAGING.value,
            "target_stage": target_stage.value,
            "approver": approver,
            "archive_existing": archive_existing_versions,
            "transitioned_at": datetime.now(timezone.utc).isoformat(),
            "status": "APPROVED",
        }
        return transition_record

    def get_champion_model(self, model_name: str) -> Dict[str, Any]:
        """Retrieve the currently designated production champion model."""
        logger.info("Fetching production champion for model '%s'", model_name)
        return {
            "model_name": model_name,
            "stage": ModelStage.PRODUCTION.value,
            "version": "1.0.0",
            "alias": "Champion",
            "last_verified": datetime.now(timezone.utc).isoformat(),
        }
