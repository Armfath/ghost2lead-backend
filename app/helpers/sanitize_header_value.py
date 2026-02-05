import re


def sanitize_header_value(value: str) -> str:
    """Sanitize a string for use in HTTP headers by removing invalid characters."""
    # Remove newlines, carriage returns, and other control characters
    sanitized = re.sub(r"[\r\n\t\x00-\x1f\x7f-\x9f]", " ", str(value))
    # Replace multiple spaces with single space
    sanitized = re.sub(r" +", " ", sanitized)
    # Strip and limit length to avoid header size issues
    return sanitized.strip()[:200]
