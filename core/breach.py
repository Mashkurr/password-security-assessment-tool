import hashlib

import requests


PWNED_PASSWORDS_URL = "https://api.pwnedpasswords.com/range/{prefix}"


def check_breach(password, timeout=4):
    digest = hashlib.sha1(password.encode("utf-8")).hexdigest().upper()
    prefix, suffix = digest[:5], digest[5:]

    try:
        response = requests.get(
            PWNED_PASSWORDS_URL.format(prefix=prefix),
            headers={"Add-Padding": "true", "User-Agent": "PGD-Credential-Assessment-Tool"},
            timeout=timeout,
        )
        response.raise_for_status()
    except requests.RequestException:
        return {
            "status": "Check Unavailable",
            "count": None,
            "message": "The breach service could not be reached. This is not a Not Found result.",
        }

    try:
        for line in response.text.splitlines():
            returned_suffix, count = line.split(":", 1)
            if returned_suffix == suffix:
                return {
                    "status": "Found",
                    "count": int(count),
                    "message": "This exact password appears in the breach corpus and should be replaced.",
                }
    except (TypeError, ValueError):
        return {
            "status": "Check Unavailable",
            "count": None,
            "message": "The breach service returned an invalid response. This is not a Not Found result.",
        }

    return {
        "status": "Not Found",
        "count": 0,
        "message": "No exact match was returned. This does not prove that the password is safe or unique.",
    }
