from flask import Flask, jsonify, render_template, request

from core.assessment import assess_password
from core.breach import check_breach
from core.recommendations import build_recommendations


app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024


@app.after_request
def add_security_headers(response):
    response.headers["Cache-Control"] = "no-store"
    response.headers["Pragma"] = "no-cache"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; style-src 'self'; script-src 'self'; "
        "img-src 'self' data:; base-uri 'none'; form-action 'self'"
    )
    return response


@app.get("/")
def index():
    return render_template("index.html")


@app.post("/api/assess")
def assess():
    payload = request.get_json(silent=True) or {}
    password = payload.get("password")

    if not isinstance(password, str) or not password:
        return jsonify({"error": "Enter a password to assess."}), 400
    if len(password) > 128:
        return jsonify({"error": "The maximum supported length is 128 characters."}), 400

    assessment = assess_password(password)
    breach = check_breach(password)
    recommendations = build_recommendations(assessment, breach)

    result = {
        "assessment": assessment,
        "breach": breach,
        "recommendations": recommendations,
        "notice": (
            "This is a comparative assessment, not a guarantee of security. "
            "Do not test a password you currently use."
        ),
    }

    password = None
    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=False)

