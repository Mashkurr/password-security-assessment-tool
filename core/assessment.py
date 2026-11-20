import re
from pathlib import Path


COMMON_PASSWORDS_PATH = Path(__file__).resolve().parent.parent / "data" / "common_passwords.txt"


def _load_common_passwords():
    with COMMON_PASSWORDS_PATH.open(encoding="utf-8") as file:
        return {line.strip().casefold() for line in file if line.strip()}


COMMON_PASSWORDS = _load_common_passwords()

# NIST SP 800-63B-4 sets different minimum lengths depending on whether the
# password is used as a single authentication factor or only as part of MFA.
# These constants are reported separately from the project-defined score.
MFA_MINIMUM_LENGTH = 8
SINGLE_FACTOR_MINIMUM_LENGTH = 15

SEQUENCES = (
    "0123456789",
    "abcdefghijklmnopqrstuvwxyz",
    "qwertyuiop",
    "asdfghjkl",
    "zxcvbnm",
)


def _length_points(length):
    """Return the project-defined graduated length contribution.

    The 0/10/25/40 values are an explanatory comparison rubric created for
    this prototype. They are not NIST weights and do not determine NIST
    conformity. Standards alignment is reported separately at 8 characters
    for passwords used only within MFA and 15 characters for single-factor
    passwords.
    """
    if length < MFA_MINIMUM_LENGTH:
        return 0
    if length < 12:
        return 10
    if length < 15:
        return 25
    return 40


def _character_variety(password):
    """Award informational credit for represented character classes.

    Variety is not enforced as a composition requirement. The exact
    project-defined mapping is 0 classes=0, 1=3, 2=5, 3=8 and 4-5=10.
    """
    checks = {
        "lowercase": bool(re.search(r"[a-z]", password)),
        "uppercase": bool(re.search(r"[A-Z]", password)),
        "digit": bool(re.search(r"\d", password)),
        "symbol": bool(re.search(r"[^\w\s]", password, flags=re.UNICODE)),
        "space": " " in password,
    }
    count = sum(checks.values())
    points_by_count = {0: 0, 1: 3, 2: 5, 3: 8, 4: 10, 5: 10}
    return checks, points_by_count[count]


def _predictable_patterns(password):
    """Apply one deduction per unique pattern category.

    Repetition, a sequence/keyboard walk and a date-like pattern each deduct
    10 points from the 25-point category. Duplicate detections inside the same
    category are counted once, and total deductions are capped at 25.
    """
    lowered = password.casefold()
    findings = []

    if re.search(r"(.)\1{2,}", lowered):
        findings.append("repeated characters")

    for sequence in SEQUENCES:
        reverse = sequence[::-1]
        for index in range(len(sequence) - 2):
            piece = sequence[index:index + 3]
            reverse_piece = reverse[index:index + 3]
            if piece in lowered or reverse_piece in lowered:
                findings.append("simple or keyboard sequence")
                break
        if "simple or keyboard sequence" in findings:
            break

    if re.search(r"(?:19|20)\d{2}", lowered) or re.search(r"\b\d{1,2}[-/.]\d{1,2}[-/.]\d{2,4}\b", lowered):
        findings.append("date-like pattern")

    unique_findings = list(dict.fromkeys(findings))
    deductions = min(25, len(unique_findings) * 10)
    return unique_findings, 25 - deductions


def _score_band(score):
    if score < 40:
        return "Weak"
    if score < 60:
        return "Fair"
    if score < 80:
        return "Strong"
    return "Very Strong"


def assess_password(password):
    length = len(password)
    common = password.casefold() in COMMON_PASSWORDS
    variety_checks, variety_points = _character_variety(password)
    patterns, pattern_points = _predictable_patterns(password)
    length_points = _length_points(length)
    common_points = 0 if common else 25

    score = length_points + variety_points + pattern_points + common_points
    score = max(0, min(100, int(score)))

    return {
        "score": score,
        "band": _score_band(score),
        "standard": "NIST SP 800-63B-4",
        "standard_checks": {
            "single_factor_length_met": length >= SINGLE_FACTOR_MINIMUM_LENGTH,
            "minimum_single_factor_length": SINGLE_FACTOR_MINIMUM_LENGTH,
            "mfa_length_met": length >= MFA_MINIMUM_LENGTH,
            "minimum_mfa_length": MFA_MINIMUM_LENGTH,
            "common_password_blocked": common,
            "full_password_evaluated": True,
            "composition_required": False,
        },
        "score_breakdown": {
            "length": {"points": length_points, "maximum": 40, "observed": length},
            "character_variety": {
                "points": variety_points,
                "maximum": 10,
                "observed": variety_checks,
                "informational_only": True,
            },
            "predictable_pattern_resistance": {
                "points": pattern_points,
                "maximum": 25,
                "patterns_found": patterns,
            },
            "common_password_resistance": {
                "points": common_points,
                "maximum": 25,
                "found_in_local_blocklist": common,
            },
        },
    }

