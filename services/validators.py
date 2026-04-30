import re

def validate_field(field: str, value: str) -> bool:
    if not value:
        return False

    value = value.strip()

    # ---------------- NAME ----------------
    if field == "full_name":
        return len(value.split()) >= 2

    # ---------------- DOB ----------------
    if field == "date_of_birth":
        # accept 1 or 2 digit month/day
        return bool(re.match(r"^\d{1,2}/\d{1,2}/\d{4}$", value.strip()))

    # ---------------- ZIP ----------------
    if field == "zip_code":
        return bool(re.match(r"\d{5}", value))

    # ---------------- INSURANCE ----------------
    if field == "payer_name":
        # allow "i don't have insurance"
        if "no" in value.lower() or "don't" in value.lower():
            return True
        return len(value) > 1

    # default
    return len(value) > 1