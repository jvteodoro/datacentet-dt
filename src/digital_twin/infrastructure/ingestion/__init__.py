"""Shared ingestion contract and normalization helpers."""

from .message_contract import TelemetryMessage, TelemetryValidationError, validate_message
from .normalize import normalize_message_to_domain_event

__all__ = [
    "TelemetryMessage",
    "TelemetryValidationError",
    "validate_message",
    "normalize_message_to_domain_event",
]
