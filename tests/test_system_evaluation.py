from statistics import median
from time import perf_counter

import pytest

from app import app
from core.assessment import assess_password


SYNTHETIC_PASSWORD_CASES = [
    ("123456", 18, "Weak"),
    ("password", 38, "Weak"),
    ("qwerty", 18, "Weak"),
    ("letmein", 28, "Weak"),
    ("admin", 28, "Weak"),
    ("welcome", 28, "Weak"),
    ("monkey", 28, "Weak"),
    ("football", 38, "Weak"),
    ("abc2024", 35, "Weak"),
    ("secret", 28, "Weak"),
    ("abc123", 20, "Weak"),
    ("dragon", 28, "Weak"),
    ("111111", 18, "Weak"),
    ("abcdefg", 18, "Weak"),
    ("aaaaaaa", 18, "Weak"),
    ("qwerty12", 30, "Weak"),
    ("short!", 55, "Fair"),
    ("test123", 20, "Weak"),
    ("Qwerty2024!", 50, "Fair"),
    ("GlassTree8", 58, "Fair"),
    ("passw0rd", 40, "Fair"),
    ("Password12!", 70, "Strong"),
    ("Hello2024!", 60, "Strong"),
    ("Admin1234!", 60, "Strong"),
    ("Abcd5678!", 60, "Strong"),
    ("Summer2024!", 60, "Strong"),
    ("Welcome1!", 70, "Strong"),
    ("Monkey123!", 60, "Strong"),
    ("CloudRiver7", 68, "Strong"),
    ("BlueSky!99", 70, "Strong"),
    ("River-Mango-Atlas-47!", 100, "Very Strong"),
    ("correct horse battery staple", 95, "Very Strong"),
    ("violet-canvas-orbit-lantern", 95, "Very Strong"),
    ("Maple!Orbit!Cedar!29", 100, "Very Strong"),
    ("Long Unique Phrase 84!", 100, "Very Strong"),
    ("Horizon-Quartz-Maple-71", 100, "Very Strong"),
    ("Gentle River Lantern Cloud", 98, "Very Strong"),
    ("Azure-Cedar-Planet-94!", 100, "Very Strong"),
    ("Copper Meadow Galaxy 82", 100, "Very Strong"),
    ("Silver-Atlas-Breeze-53!", 100, "Very Strong"),
]


@pytest.mark.parametrize("password, expected_score, expected_band", SYNTHETIC_PASSWORD_CASES)
def test_forty_synthetic_passwords_match_expected_scores_and_bands(
    password, expected_score, expected_band
):
    result = assess_password(password)
    assert result["score"] == expected_score
    assert result["band"] == expected_band


def test_thirty_complete_local_assessments_have_median_under_three_seconds(monkeypatch):
    monkeypatch.setattr(
        "app.check_breach",
        lambda _password: {
            "status": "Not Found",
            "count": 0,
            "message": "Synthetic service response for repeatable performance testing.",
        },
    )

    durations = []
    with app.test_client() as client:
        for index in range(30):
            started = perf_counter()
            response = client.post(
                "/api/assess",
                json={"password": f"Performance-Demo-Phrase-{index}!"},
            )
            durations.append(perf_counter() - started)
            assert response.status_code == 200

    assert median(durations) <= 3.0
