"""Compare the transparent project score with the zxcvbn estimator.

This script is evaluation evidence only. zxcvbn is not part of the production
assessment path because it estimates guessability while the project score is
an explainable rule-based comparison rubric.
"""

import csv
from pathlib import Path
from statistics import mean

from zxcvbn import zxcvbn

from core.assessment import assess_password
from tests.test_system_evaluation import SYNTHETIC_PASSWORD_CASES


ZXCVBN_TO_PROJECT_BAND = {
    0: "Weak",
    1: "Weak",
    2: "Fair",
    3: "Strong",
    4: "Very Strong",
}


def _average_ranks(values):
    order = sorted(range(len(values)), key=values.__getitem__)
    ranks = [0.0] * len(values)
    index = 0
    while index < len(order):
        end = index
        while end + 1 < len(order) and values[order[end + 1]] == values[order[index]]:
            end += 1
        average_rank = (index + end + 2) / 2
        for position in range(index, end + 1):
            ranks[order[position]] = average_rank
        index = end + 1
    return ranks


def _correlation(left, right):
    left_mean = mean(left)
    right_mean = mean(right)
    numerator = sum(
        (left_value - left_mean) * (right_value - right_mean)
        for left_value, right_value in zip(left, right)
    )
    denominator = (
        sum((value - left_mean) ** 2 for value in left)
        * sum((value - right_mean) ** 2 for value in right)
    ) ** 0.5
    return numerator / denominator


def main():
    output_path = Path(__file__).with_name("zxcvbn_comparison.csv")
    rows = []
    project_scores = []
    zxcvbn_scores = []
    agreements = 0

    for password, expected_score, expected_band in SYNTHETIC_PASSWORD_CASES:
        project = assess_password(password)
        zxcvbn_score = zxcvbn(password)["score"]
        mapped_band = ZXCVBN_TO_PROJECT_BAND[zxcvbn_score]
        agreement = project["band"] == mapped_band
        agreements += int(agreement)
        project_scores.append(project["score"])
        zxcvbn_scores.append(zxcvbn_score)
        rows.append(
            {
                "password_case": password,
                "expected_project_score": expected_score,
                "project_score": project["score"],
                "project_band": expected_band,
                "zxcvbn_score": zxcvbn_score,
                "mapped_zxcvbn_band": mapped_band,
                "band_agreement": agreement,
            }
        )

    with output_path.open("w", newline="", encoding="utf-8") as output_file:
        writer = csv.DictWriter(output_file, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    spearman_rho = _correlation(
        _average_ranks(project_scores), _average_ranks(zxcvbn_scores)
    )
    print(f"cases={len(rows)}")
    print(f"mapped_band_agreement={agreements}/{len(rows)} ({agreements / len(rows):.1%})")
    print(f"spearman_rho={spearman_rho:.3f}")
    print(f"csv={output_path}")


if __name__ == "__main__":
    main()
