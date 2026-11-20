def build_recommendations(assessment, breach):
    advice = []
    checks = assessment["standard_checks"]
    breakdown = assessment["score_breakdown"]

    if not checks["single_factor_length_met"]:
        advice.append("Use at least 15 characters for a password used without multi-factor authentication.")

    if breakdown["common_password_resistance"]["found_in_local_blocklist"]:
        advice.append("Replace this common password with a unique, memorable passphrase.")

    patterns = breakdown["predictable_pattern_resistance"]["patterns_found"]
    if patterns:
        advice.append("Remove predictable elements: " + ", ".join(patterns) + ".")

    if breach["status"] == "Found":
        advice.insert(0, "Change this password immediately and do not reuse it on another account.")
    elif breach["status"] == "Check Unavailable":
        advice.append("Repeat the breach check later; the service did not return a trustworthy result.")

    if not advice:
        advice.append("Keep the password unique and store it in a reputable password manager.")

    advice.append("Enable multi-factor authentication where it is available.")
    return advice

