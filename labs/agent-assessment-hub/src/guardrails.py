"""Security Guardrails, Policy Plugin, and PII Redaction module.

Implements safety filters, prompt injection defenses, PII masking,
and authorization checks for agent actions.
"""

import re
from typing import Tuple, Dict, Any


# PII Patterns for Redaction
PII_PATTERNS = {
    "EMAIL": re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"),
    "IPV4": re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b"),
    "CREDIT_CARD": re.compile(r"\b(?:\d[ -]*?){13,16}\b"),
    "API_KEY": re.compile(r"(?:AIza[0-9A-Za-z-_]{10,40}|ghp_[0-9A-Za-z]{30,40}|bearer\s+[A-Za-z0-9-_.]+)", re.IGNORECASE),
    "PASSWORD": re.compile(r'(?:"?password"?\s*[:=]\s*)"?([^",\s]+)"?', re.IGNORECASE),
}

# Forbidden command patterns for Agent Armor policy
DISALLOWED_COMMANDS = [
    r"rm\s+-rf\s+/",
    r"drop\s+database",
    r"delete\s+from\s+users",
    r"truncate\s+table",
    r"chmod\s+777",
]


def redact_pii(text: str) -> str:
    """Redacts PII such as emails, IPs, API keys, and passwords from log strings and traces."""
    if not isinstance(text, str):
        return text

    sanitized = text
    for pii_type, pattern in PII_PATTERNS.items():
        sanitized = pattern.sub(f"[REDACTED_{pii_type}]", sanitized)
    return sanitized


class SecurityPolicyPlugin:
    """Agent Policy Plugin evaluating user inputs and tool execution requests for security threats."""

    @staticmethod
    def validate_user_prompt(prompt: str) -> Tuple[bool, str]:
        """Validates incoming prompt for prompt injection or malicious intent."""
        for pattern in DISALLOWED_COMMANDS:
            if re.search(pattern, prompt, re.IGNORECASE):
                return False, f"Blocked by Security Policy Plugin: Dangerous instruction pattern detected ('{pattern}')"

        if "system instructions" in prompt.lower() and "ignore previous" in prompt.lower():
            return False, "Blocked by Security Policy Plugin: Prompt injection attempt detected."

        return True, "Passed"

    @staticmethod
    def validate_tool_execution(tool_name: str, arguments: Dict[str, Any]) -> Tuple[bool, str]:
        """Validates tool execution parameters against SRE safety boundaries."""
        if tool_name == "apply_service_remediation":
            action = arguments.get("action", "").lower()
            if action not in ["restart", "scale_up", "rollback"]:
                return False, f"Unauthorized remediation action: '{action}'."

        return True, "Passed"


security_guardrails = SecurityPolicyPlugin()
