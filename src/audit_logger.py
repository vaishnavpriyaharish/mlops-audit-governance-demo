"""audit_logger.py

Module: MLOps Compliance & Governance Audit Logger
Purpose: Structured logging and persistence of critical MLOps events:
         training runs, hyperparameter changes, validation gate decisions,
         stage promotions, and drift alerts for enterprise auditability.
"""

from __future__ import annotations

import json
import logging
import os
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s - %(message)s")
logger = logging.getLogger("MLOpsAuditLogger")


class AuditEvent(BaseModel):
    """Schema for SOC 2 / ISO compliant MLOps audit records."""
    event_id: str
    event_type: str  # TRAINING, VALIDATION_GATE, STAGE_TRANSITION, DRIFT_ALERT
    model_name: str
    model_version: str
    actor: str  # Pipeline service principal, GitHub Actions, or named engineer
    environment: str  # dev, staging, prod
    details: Dict[str, Any] = Field(default_factory=dict)
    compliance_passed: bool = True
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class MLOpsAuditLogger:
    """Handles structured logging and export of audit trail records."""

    def __init__(self, log_filepath: Optional[str] = None) -> None:
        self.log_filepath = log_filepath or os.path.join("logs", "mlops_audit_trail.jsonl")
        os.makedirs(os.path.dirname(self.log_filepath), exist_ok=True)
        self._history: List[Dict[str, Any]] = []

    def log_event(self, event: AuditEvent) -> Dict[str, Any]:
        """Record an immutable compliance event to the audit ledger."""
        record = event.model_dump()
        self._history.append(record)

        # Write to JSONL ledger
        with open(self.log_filepath, "a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")

        logger.info(
            "[AUDIT] Event: %s | Model: %s (v%s) | Actor: %s | Passed: %s",
            event.event_type,
            event.model_name,
            event.model_version,
            event.actor,
            event.compliance_passed,
        )
        return record

    def get_audit_trail(self, model_name: str) -> List[Dict[str, Any]]:
        """Retrieve historical compliance records for a designated model."""
        return [e for e in self._history if e["model_name"] == model_name]
