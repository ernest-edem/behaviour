from datetime import datetime
from typing import Dict, Any, Optional, List
from enum import Enum

from sqlalchemy.orm import Session

from app.models.user import User
from app.core.rbac import Permission


# =========================================================
# SECURITY EVENT TYPES
# =========================================================
class SecurityEventType(str, Enum):
    AUTH_SUCCESS = "auth_success"
    AUTH_DENIED = "auth_denied"

    PERMISSION_CHECK = "permission_check"
    ROLE_CHECK = "role_check"

    POLICY_MATCH = "policy_match"
    POLICY_DENY = "policy_deny"

    PRIVILEGE_ESCALATION_ATTEMPT = "privilege_escalation_attempt"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"


# =========================================================
# SECURITY EVENT MODEL (IN-MEMORY STRUCT)
# =========================================================
class SecurityEvent:
    def __init__(
        self,
        event_type: SecurityEventType,
        user_id: Optional[int],
        action: Optional[str],
        resource: Optional[str],
        decision: str,
        metadata: Dict[str, Any],
    ):
        self.timestamp = datetime.utcnow()
        self.event_type = event_type
        self.user_id = user_id
        self.action = action
        self.resource = resource
        self.decision = decision
        self.metadata = metadata


# =========================================================
# SOC ENGINE (SECURITY OBSERVABILITY CORE)
# =========================================================
class SOCEngine:
    """
    SOC-grade IAM observability layer.

    Responsibilities:
    - Capture IAM decisions
    - Detect suspicious patterns
    - Store security events (extendable to DB/SIEM)
    """

    def __init__(self):
        self._events: List[SecurityEvent] = []

    # =====================================================
    # EVENT LOGGER
    # =====================================================
    def log_event(
        self,
        event_type: SecurityEventType,
        user: Optional[User],
        action: Optional[Permission],
        resource: Optional[str],
        decision: str,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        event = SecurityEvent(
            event_type=event_type,
            user_id=user.id if user else None,
            action=action.value if action else None,
            resource=resource,
            decision=decision,
            metadata=metadata or {},
        )

        self._events.append(event)

        # Hook for future DB persistence or SIEM streaming
        self._persist(event)

    # =====================================================
    # BASIC PERSISTENCE HOOK (EXTEND LATER)
    # =====================================================
    def _persist(self, event: SecurityEvent):
        """
        Placeholder for:
        - DB insert
        - Kafka event stream
        - ELK/Splunk export
        """
        pass

    # =====================================================
    # SUSPICIOUS ACTIVITY DETECTION
    # =====================================================
    def detect_anomalies(self, user_id: int) -> List[str]:
        """
        Simple rule-based anomaly detection.

        Returns list of detected issues.
        """

        issues = []

        user_events = [
            e for e in self._events
            if e.user_id == user_id
        ]

        if not user_events:
            return issues

        # -------------------------
        # Rule 1: Too many denied requests
        # -------------------------
        denied_count = sum(
            1 for e in user_events
            if e.event_type == SecurityEventType.AUTH_DENIED
        )

        if denied_count >= 5:
            issues.append("High number of denied access attempts")

        # -------------------------
        # Rule 2: Privilege escalation attempts
        # -------------------------
        escalation_attempts = sum(
            1 for e in user_events
            if e.event_type == SecurityEventType.PRIVILEGE_ESCALATION_ATTEMPT
        )

        if escalation_attempts > 0:
            issues.append("Privilege escalation attempt detected")

        return issues

    # =====================================================
    # QUERY EVENTS
    # =====================================================
    def get_events(
        self,
        user_id: Optional[int] = None,
        event_type: Optional[SecurityEventType] = None,
        limit: int = 100,
    ) -> List[SecurityEvent]:

        results = self._events

        if user_id is not None:
            results = [e for e in results if e.user_id == user_id]

        if event_type is not None:
            results = [e for e in results if e.event_type == event_type]

        return results[-limit:]


# =========================================================
# GLOBAL SOC INSTANCE
# =========================================================
soc_engine = SOCEngine()