from core.assessment import assess_password
from core.recommendations import build_recommendations


def test_common_short_password_is_weak():
    result = assess_password("password")
    assert result["band"] == "Weak"
    assert result["standard_checks"]["single_factor_length_met"] is False
    assert result["standard_checks"]["common_password_blocked"] is True


def test_long_unique_passphrase_meets_length_threshold():
    result = assess_password("river-lantern-orbit-canvas")
    assert result["standard_checks"]["single_factor_length_met"] is True
    assert result["standard_checks"]["common_password_blocked"] is False
    assert result["score"] >= 80


def test_predictable_sequence_is_reported():
    result = assess_password("longpassword12345")
    findings = result["score_breakdown"]["predictable_pattern_resistance"]["patterns_found"]
    assert "simple or keyboard sequence" in findings


def test_character_composition_is_not_required():
    result = assess_password("a sufficiently long passphrase")
    assert result["standard_checks"]["composition_required"] is False


def test_recommendation_for_breach_match():
    assessment = assess_password("river-lantern-orbit-canvas")
    breach = {"status": "Found", "count": 3}
    advice = build_recommendations(assessment, breach)
    assert "Change this password immediately" in advice[0]

