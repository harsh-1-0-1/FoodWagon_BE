import re

def format_phone_uber(phone_number: str | None, default_country_code: str = "+1") -> str:
    """
    Formats a phone number into the E.164 format required by Uber (+15125551212).
    """
    if not phone_number:
        return "+15125551212"  # Fallback to a valid test number if none provided

    # Remove all non-numeric characters except '+'
    cleaned = re.sub(r"[^\d+]", "", phone_number)

    # If it starts with '+', assume it's already in E.164
    if cleaned.startswith("+"):
        return cleaned

    # If it starts with '00', replace it with '+'
    if cleaned.startswith("00"):
        return "+" + cleaned[2:]

    # If it doesn't have a '+', prepend the default country code
    # If the number already has 10 digits and default is +1, prepend it
    if len(cleaned) == 10:
        return default_country_code + cleaned

    # Otherwise, just prepend '+' if it doesn't have it
    return "+" + cleaned
