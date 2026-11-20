"""Measure local Flask processing with the external breach service mocked."""

from statistics import median
from time import perf_counter
from unittest.mock import patch

from app import app


REQUESTS = 1000


def main():
    durations_ms = []
    mock_result = {
        "status": "Not Found",
        "count": 0,
        "message": "Mocked response for repeatable local processing measurement.",
    }

    with patch("app.check_breach", return_value=mock_result):
        with app.test_client() as client:
            for index in range(REQUESTS):
                started = perf_counter()
                response = client.post(
                    "/api/assess",
                    json={"password": f"Performance-Demo-Phrase-{index}!"},
                )
                durations_ms.append((perf_counter() - started) * 1000)
                if response.status_code != 200:
                    raise RuntimeError(f"Unexpected status {response.status_code}")

    print(f"requests={REQUESTS}")
    print(f"median_ms={median(durations_ms):.3f}")
    print(f"minimum_ms={min(durations_ms):.3f}")
    print(f"maximum_ms={max(durations_ms):.3f}")
    print("external_breach_service=mocked")


if __name__ == "__main__":
    main()
