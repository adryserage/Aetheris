"""Secret detection patterns for security scanning.

These patterns detect common credentials and secrets that should never
be committed to version control or included in packages.

Pattern categories:
- HIGH_CONFIDENCE: Very specific patterns, low false positive rate
- MEDIUM_CONFIDENCE: Less specific, may have some false positives
- PROVIDER_PATTERNS: Cloud provider and service-specific patterns
"""

import re
from typing import NamedTuple


class SecretPatternDef(NamedTuple):
    """Definition of a secret detection pattern."""

    name: str
    regex: str
    description: str
    confidence: str  # "high", "medium", "low"


# High confidence patterns - very specific, low false positive rate
HIGH_CONFIDENCE_PATTERNS: list[SecretPatternDef] = [
    SecretPatternDef(
        name="aws_access_key",
        regex=r"AKIA[0-9A-Z]{16}",
        description="AWS Access Key ID",
        confidence="high",
    ),
    SecretPatternDef(
        name="aws_secret_key",
        regex=r"(?i)aws[_\-]?secret[_\-]?(?:access[_\-]?)?key[\s]*[=:]\s*['\"]?([A-Za-z0-9/+=]{40})['\"]?",
        description="AWS Secret Access Key",
        confidence="high",
    ),
    SecretPatternDef(
        name="github_token",
        regex=r"gh[pousr]_[A-Za-z0-9_]{36,255}",
        description="GitHub Personal Access Token",
        confidence="high",
    ),
    SecretPatternDef(
        name="github_oauth",
        regex=r"gho_[A-Za-z0-9]{36}",
        description="GitHub OAuth Access Token",
        confidence="high",
    ),
    SecretPatternDef(
        name="gitlab_token",
        regex=r"glpat-[A-Za-z0-9\-_]{20,}",
        description="GitLab Personal Access Token",
        confidence="high",
    ),
    SecretPatternDef(
        name="slack_token",
        regex=r"xox[baprs]-[0-9]{10,13}-[0-9]{10,13}[a-zA-Z0-9-]*",
        description="Slack Token",
        confidence="high",
    ),
    SecretPatternDef(
        name="slack_webhook",
        regex=r"https://hooks\.slack\.com/services/T[A-Z0-9]+/B[A-Z0-9]+/[A-Za-z0-9]+",
        description="Slack Webhook URL",
        confidence="high",
    ),
    SecretPatternDef(
        name="private_key_header",
        regex=r"-----BEGIN (?:RSA |EC |DSA |OPENSSH |PGP )?PRIVATE KEY-----",
        description="Private Key Header",
        confidence="high",
    ),
]

# Medium confidence patterns - may have some false positives
MEDIUM_CONFIDENCE_PATTERNS: list[SecretPatternDef] = [
    SecretPatternDef(
        name="generic_api_key",
        regex=r"(?i)(?:api[_\-]?key|apikey)[\s]*[=:]\s*['\"]?([A-Za-z0-9_\-]{20,})['\"]?",
        description="Generic API Key",
        confidence="medium",
    ),
    SecretPatternDef(
        name="generic_secret",
        regex=r"(?i)(?:secret|token|password|passwd|pwd)[\s]*[=:]\s*['\"]?([^\s'\"]{8,})['\"]?",
        description="Generic Secret/Password",
        confidence="medium",
    ),
    SecretPatternDef(
        name="jwt_token",
        regex=r"eyJ[A-Za-z0-9_-]*\.eyJ[A-Za-z0-9_-]*\.[A-Za-z0-9_-]*",
        description="JWT Token",
        confidence="medium",
    ),
    SecretPatternDef(
        name="bearer_token",
        regex=r"(?i)bearer\s+[A-Za-z0-9_\-\.=]+",
        description="Bearer Token",
        confidence="medium",
    ),
    SecretPatternDef(
        name="basic_auth",
        regex=r"(?i)basic\s+[A-Za-z0-9+/=]{20,}",
        description="Basic Auth Credentials",
        confidence="medium",
    ),
    SecretPatternDef(
        name="connection_string",
        regex=r"(?i)(?:mysql|postgres|postgresql|mongodb|redis|amqp)://[^\s'\"]+:[^\s'\"]+@[^\s'\"]+",
        description="Database Connection String",
        confidence="medium",
    ),
]

# Cloud provider and service-specific patterns
PROVIDER_PATTERNS: list[SecretPatternDef] = [
    # Google Cloud
    SecretPatternDef(
        name="gcp_api_key",
        regex=r"AIza[0-9A-Za-z_-]{35}",
        description="Google Cloud API Key",
        confidence="high",
    ),
    SecretPatternDef(
        name="gcp_service_account",
        regex=r'"type":\s*"service_account"',
        description="GCP Service Account JSON",
        confidence="high",
    ),
    # Azure
    SecretPatternDef(
        name="azure_storage_key",
        regex=r"(?i)DefaultEndpointsProtocol=https;AccountName=[^;]+;AccountKey=[A-Za-z0-9+/=]{88}",
        description="Azure Storage Connection String",
        confidence="high",
    ),
    # Stripe
    SecretPatternDef(
        name="stripe_secret_key",
        regex=r"sk_(?:live|test)_[A-Za-z0-9]{24,}",
        description="Stripe Secret Key",
        confidence="high",
    ),
    SecretPatternDef(
        name="stripe_publishable_key",
        regex=r"pk_(?:live|test)_[A-Za-z0-9]{24,}",
        description="Stripe Publishable Key",
        confidence="medium",
    ),
    # SendGrid
    SecretPatternDef(
        name="sendgrid_api_key",
        regex=r"SG\.[A-Za-z0-9_-]{22}\.[A-Za-z0-9_-]{43}",
        description="SendGrid API Key",
        confidence="high",
    ),
    # Twilio
    SecretPatternDef(
        name="twilio_api_key",
        regex=r"SK[a-f0-9]{32}",
        description="Twilio API Key",
        confidence="high",
    ),
    SecretPatternDef(
        name="twilio_auth_token",
        regex=r"(?i)twilio[_\-]?auth[_\-]?token[\s]*[=:]\s*['\"]?([a-f0-9]{32})['\"]?",
        description="Twilio Auth Token",
        confidence="high",
    ),
    # Anthropic/OpenAI
    SecretPatternDef(
        name="anthropic_api_key",
        regex=r"sk-ant-[A-Za-z0-9_-]{95,}",
        description="Anthropic API Key",
        confidence="high",
    ),
    SecretPatternDef(
        name="openai_api_key",
        regex=r"sk-[A-Za-z0-9]{48,}",
        description="OpenAI API Key",
        confidence="high",
    ),
    # Mailgun
    SecretPatternDef(
        name="mailgun_api_key",
        regex=r"key-[A-Za-z0-9]{32}",
        description="Mailgun API Key",
        confidence="high",
    ),
    # npm
    SecretPatternDef(
        name="npm_token",
        regex=r"npm_[A-Za-z0-9]{36}",
        description="npm Access Token",
        confidence="high",
    ),
    # PyPI
    SecretPatternDef(
        name="pypi_token",
        regex=r"pypi-[A-Za-z0-9_-]{100,}",
        description="PyPI API Token",
        confidence="high",
    ),
    # Heroku
    SecretPatternDef(
        name="heroku_api_key",
        regex=r"[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}",
        description="Heroku API Key (UUID format)",
        confidence="low",
    ),
    # Firebase
    SecretPatternDef(
        name="firebase_api_key",
        regex=r"(?i)firebase[_\-]?api[_\-]?key[\s]*[=:]\s*['\"]?([A-Za-z0-9_-]{39})['\"]?",
        description="Firebase API Key",
        confidence="medium",
    ),
]

# Combined list of all patterns
SECRET_PATTERNS: list[SecretPatternDef] = (
    HIGH_CONFIDENCE_PATTERNS + MEDIUM_CONFIDENCE_PATTERNS + PROVIDER_PATTERNS
)


def compile_patterns() -> list[tuple[SecretPatternDef, re.Pattern]]:
    """Compile all secret patterns into regex objects.

    Returns:
        List of tuples containing (pattern_def, compiled_regex)
    """
    return [(p, re.compile(p.regex)) for p in SECRET_PATTERNS]


def get_patterns_by_confidence(
    confidence: str, include_lower: bool = True
) -> list[SecretPatternDef]:
    """Get patterns filtered by confidence level.

    Args:
        confidence: Target confidence level ("high", "medium", "low")
        include_lower: Include patterns with lower confidence than target

    Returns:
        Filtered list of patterns
    """
    levels = ["high", "medium", "low"]
    if confidence not in levels:
        raise ValueError(f"Invalid confidence: {confidence}")

    target_index = levels.index(confidence)

    if include_lower:
        valid_levels = set(levels[: target_index + 1])
    else:
        valid_levels = {confidence}

    return [p for p in SECRET_PATTERNS if p.confidence in valid_levels]
