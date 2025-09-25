# core/services/security_logger.py
from datetime import datetime
from core.config import SECURITY_LOG_PATH



def log_event(event_type: str, message: str) -> None:
    """Append dans storage/security.log"""
    SECURITY_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(SECURITY_LOG_PATH, "a", encoding="utf-8") as f:
        ts = datetime.now().isoformat(sep=" ", timespec="seconds")
        f.write(f"[{ts}] {event_type}: {message}\n")
