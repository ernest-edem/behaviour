from dataclasses import dataclass
from typing import Optional, Dict, Any
from datetime import datetime


@dataclass
class SecurityEvent:
    event_type: str  # AUTH_SUCCESS | AUTH_DENY | PRIV_ESCALATION | ADMIN_ACTION
    user_id: Optional[int]
    action: str
    resource: Optional[str]
    decision: str  # allow / deny
    reason: str

    ip_address: Optional[str] = None
    metadata: Dict[str, Any] = None

    timestamp: datetime = datetime.utcnow()