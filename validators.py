import re
from email_validator import validate_email as _validate_email, EmailNotValidError


def validate_email(email):
    """Returns (is_valid, error_message)."""
    if not email:
        return False, "Email is required."
    try:
        _validate_email(email, check_deliverability=False)
        return True, None
    except EmailNotValidError as e:
        return False, str(e)


def validate_password(password):
    """Require at least 8 chars, one letter, one number."""
    if not password or len(password) < 8:
        return False, "Password must be at least 8 characters long."
    if not re.search(r"[A-Za-z]", password) or not re.search(r"\d", password):
        return False, "Password must contain both letters and numbers."
    return True, None