import re
from typing import Tuple

try:
    import spacy
    _NLP = spacy.load("en_core_web_sm")
except Exception:
    _NLP = None


class PIIMiddleware:
    """Scans and masks PII including emails, phone numbers, and names."""

    EMAIL_PATTERN = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
    PHONE_PATTERN = re.compile(r"\b(?:\+?\d{1,3}[-.\s]?)?\d{10}\b")

    # Matches greeting/intro + Name (e.g., "Hello Ram", "Hi Lucy", "My name is Aman")
    CONTEXT_NAME_PATTERN = re.compile(
        r"\b(?:my name is|i am|i'm|hi|hello|hey|dear)\s+([A-Za-z]{2,20})\b",
        flags=re.IGNORECASE,
    )

    SKIP_WORDS = {
        "please", "here", "fine", "good", "okay", "ok", "thanks", "thank",
        "checking", "testing", "asking", "looking", "trying", "able", "ready",
        "sir", "madam", "team", "all", "everyone", "process", "this", "request",
    }

    def mask_pii(self, text: str) -> Tuple[str, int]:
        """Returns masked text and total count of redacted items."""
        redacted_count = 0

        def _count_replace(_: re.Match) -> str:
            nonlocal redacted_count
            redacted_count += 1
            return "[REDACTED]"

        # 1. Mask emails and phone numbers
        masked = self.EMAIL_PATTERN.sub(_count_replace, text)
        masked = self.PHONE_PATTERN.sub(_count_replace, masked)

        # 2. Mask PERSON entities via spaCy if available
        if _NLP is not None:
            doc = _NLP(masked)
            spans = [
                (ent.start_char, ent.end_char)
                for ent in doc.ents
                if ent.label_ == "PERSON"
            ]
            for start, end in sorted(spans, reverse=True):
                masked = masked[:start] + "[REDACTED]" + masked[end:]
                redacted_count += 1

        # 3. Mask names after greetings / introductions
        def _replace_context_name(match: re.Match) -> str:
            nonlocal redacted_count
            name = match.group(1)
            if name.lower() in self.SKIP_WORDS or name.lower() == "redacted":
                return match.group(0)
            redacted_count += 1
            start_idx = match.group(0).lower().rfind(name.lower())
            prefix = match.group(0)[:start_idx]
            return f"{prefix}[REDACTED]"

        masked = self.CONTEXT_NAME_PATTERN.sub(_replace_context_name, masked)
        return masked, redacted_count