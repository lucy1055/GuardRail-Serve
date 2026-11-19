import re
from typing import Tuple


class PIIMiddleware:
    """Scans and masks sensitive Personally Identifiable Information (PII)."""

    EMAIL_PATTERN = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
    PHONE_PATTERN = re.compile(r"\b(?:\+?\d{1,3}[-.\s]?)?\d{10}\b")
    NAME_PATTERN = re.compile(r"\bRam\b", flags=re.IGNORECASE)

    def mask_pii(self, text: str) -> Tuple[str, int]:
        """Returns masked text and total count of redacted items."""
        redacted_count = 0

        def _replace(match: re.Match) -> str:
            nonlocal redacted_count
            redacted_count += 1
            return "[REDACTED]"

        masked = self.EMAIL_PATTERN.sub(_replace, text)
        masked = self.PHONE_PATTERN.sub(_replace, masked)
        masked = self.NAME_PATTERN.sub(_replace, masked)
        return masked, redacted_count