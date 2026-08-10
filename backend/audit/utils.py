import uuid
import hashlib


def generate_correlation_id():
    """Generate a unique correlation ID."""
    return str(uuid.uuid4())


def mask_sensitive_data(data, sensitive_keys=None):
    """
    Mask sensitive data in a dictionary.
    """
    if sensitive_keys is None:
        sensitive_keys = {"password", "token", "refresh_token", "access_token", "secret", "otp"}
    if not isinstance(data, dict):
        return data
    masked = {}
    for k, v in data.items():
        if k.lower() in sensitive_keys:
            masked[k] = "***MASKED***"
        elif isinstance(v, dict):
            masked[k] = mask_sensitive_data(v, sensitive_keys)
        elif isinstance(v, list):
            masked[k] = [
                mask_sensitive_data(item, sensitive_keys) if isinstance(item, dict) else item
                for item in v
            ]
        else:
            masked[k] = v
    return masked