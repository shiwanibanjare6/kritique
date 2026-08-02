import hashlib
import hmac

from app.core.config import settings


def verify_signature(payload: bytes, signature: str) -> bool:
    """
    Verify GitHub webhook HMAC SHA256 signature.
    """

    expected_signature = (
        "sha256="
        + hmac.new(
            settings.GITHUB_SECRET.encode(),
            payload,
            hashlib.sha256,
        ).hexdigest()
    )

    return hmac.compare_digest(expected_signature, signature)